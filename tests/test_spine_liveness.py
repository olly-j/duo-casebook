"""Behavioral regression tests: zero polling, supersession and safe recovery."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve()
ROOT = HERE.parent.parent
CANDIDATES = (ROOT / 'template/scripts/spine_liveness.py', ROOT / 'scripts/spine_liveness.py',
              ROOT.parent / 'scripts/spine_liveness.py', HERE.parent / 'spine_liveness.py')
MODULE = next(path for path in CANDIDATES if path.is_file())
spec = importlib.util.spec_from_file_location('tested_spine_liveness', MODULE)
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)
PASS = {'exitCode': 0, 'reason': 'completed', 'outputSha256': '0' * 64}
FAIL = {'exitCode': 1, 'reason': 'capability-command-failed', 'outputSha256': '1' * 64}


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                        'commit', '--allow-empty', '-qm', 'baseline'], check=True)
        (self.root / '.spine').mkdir()
        self.definition = {'schemaVersion': 1, 'probes': {'project-read': {
            'command': [sys.executable, '-c', 'print("ok")'], 'readOnly': True,
            'target': 'owner/project/1', 'maxAgeSeconds': 300, 'timeoutSeconds': 2}},
            'routes': {'archive': ['local-organizer', 'approved-cloud']}}
        self.write_config()
        self.value = {'goal': 'Deliver the approved outcome', 'phase': 'implementation',
                      'nextAction': 'Inspect the retained result', 'capabilities': ['project-read']}

    def write_config(self):
        (self.root / '.spine/liveness.json').write_text(json.dumps(self.definition))

    def observe(self, result=PASS, **kwargs):
        return live.observe(self.root, 'project-read', kwargs.pop('session', 'session-a'),
                            runner=Mock(return_value=result), **kwargs)

    def test_expiry_does_not_execute(self):
        self.observe(now=1000)
        with patch.object(live, 'run_probe', side_effect=AssertionError('unexpected execution')):
            values = live.live_status(self.root, ['project-read'], 'session-a', now=2000)
        self.assertEqual(values[0]['freshness'], 'stale')
        self.assertFalse(values[0]['currentBlocker'])
        self.assertTrue(values[0]['needsDecisionProbe'])

    def test_no_timer_or_background_worker(self):
        source = MODULE.read_text()
        for prohibited in ('threading.Timer', 'schedule.every', 'asyncio.create_task', 'threading.Thread'):
            self.assertNotIn(prohibited, source)

    def test_fresh_success_reuses_without_probe(self):
        self.observe(now=1000)
        runner = Mock(side_effect=AssertionError('duplicate probe'))
        result = live.observe(self.root, 'project-read', 'session-a', runner=runner, now=1001)
        self.assertFalse(result['executed'])
        runner.assert_not_called()

    def test_fresh_failure_does_not_retry_on_every_use(self):
        self.observe(FAIL, now=1000)
        runner = Mock(side_effect=AssertionError('retry storm'))
        result = live.observe(self.root, 'project-read', 'session-a', runner=runner, now=1001)
        self.assertFalse(result['executed'])
        self.assertEqual(result['observation']['status'], 'blocked')

    def test_owner_fix_supersedes_failure(self):
        failed = self.observe(FAIL, now=1000)['observation']
        passed = self.observe(now=1001, event='owner refreshed Project scope')['observation']
        self.assertEqual(passed['supersedes'], failed['id'])
        self.assertEqual(passed['status'], 'passed')
        status = live.live_status(self.root, ['project-read'], 'session-a', now=1002)[0]
        self.assertFalse(status['currentBlocker'])
        history = live.directory(self.root) / 'live-history' / (failed['id'] + '.json')
        self.assertEqual(live.read_json(history)['status'], 'blocked')

    def test_old_handoff_failure_requires_decision_recheck(self):
        self.observe(FAIL, now=1000)
        result = self.observe(session='session-b', purpose='final', now=1001)
        self.assertTrue(result['executed'])
        self.assertEqual(result['observation']['status'], 'passed')

    def test_escalation_rechecks_once_not_in_a_loop(self):
        self.observe(FAIL, now=1000)
        first = self.observe(FAIL, purpose='escalation', now=1001)
        second = self.observe(FAIL, purpose='escalation', now=1002)
        self.assertTrue(first['executed'])
        self.assertFalse(second['executed'])
        self.assertIn('alternative', first['advice'])

    def test_mutation_needs_current_decision_probe(self):
        self.observe(now=1000)
        self.assertTrue(self.observe(purpose='mutation', now=1001)['executed'])

    def test_credentials_never_retained(self):
        secret = 'ghp_' + 'a' * 36
        with patch.dict(os.environ, {'GH_TOKEN': secret}):
            result = self.observe(now=1000)
        state = (live.directory(self.root) / 'live-observations.json').read_text()
        self.assertNotIn(secret, state)
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(result['credentialSource'], 'GH_TOKEN')

    def test_token_context_changes_invalidate_success(self):
        with patch.dict(os.environ, {'GH_TOKEN': 'first-secret'}):
            first = self.observe(now=1000)['observation']
        with patch.dict(os.environ, {'GH_TOKEN': 'second-secret'}):
            second = self.observe(FAIL, now=1001)['observation']
        self.assertNotEqual(first['context'], second['context'])
        self.assertIsNone(second['supersedes'])

    def test_other_credential_context_cannot_supersede_failure(self):
        with patch.dict(os.environ, {'GH_TOKEN': 'A'}):
            self.observe(FAIL, now=1000)
        with patch.dict(os.environ, {'GH_TOKEN': 'B'}):
            self.observe(now=1001)
        with patch.dict(os.environ, {'GH_TOKEN': 'A'}):
            status = live.live_status(self.root, ['project-read'], 'session-a', now=1002)[0]
        self.assertTrue(status['currentBlocker'])

    def test_changed_probe_definition_invalidates_cache(self):
        self.observe(now=1000)
        self.definition['probes']['project-read']['target'] = 'other/project'
        self.write_config()
        self.assertTrue(self.observe(now=1001)['executed'])

    def test_clock_rollback_cannot_overwrite_new_observation(self):
        self.observe(now=1000)
        with self.assertRaises(live.LivenessError):
            self.observe(FAIL, now=999)

    def test_unknown_probe_never_executes(self):
        runner = Mock()
        with self.assertRaises(live.LivenessError):
            live.observe(self.root, 'invented', 'session', runner=runner)
        runner.assert_not_called()

    def test_registry_rejects_shell_and_mutations(self):
        for changes in ({'command': ['bash', '-c', 'touch x']}, {'readOnly': False}, {'timeoutSeconds': 1000}, {'maxAgeSeconds': float('nan')}):
            with self.subTest(changes=changes):
                bad = copy.deepcopy(self.definition)
                bad['probes']['project-read'].update(changes)
                (self.root / '.spine/liveness.json').write_text(json.dumps(bad))
                with self.assertRaises((live.LivenessError, ValueError)):
                    live.config(self.root)

    def test_actual_probe_runs_without_stdout_retention(self):
        result = live.observe(self.root, 'project-read', 'session-a')
        self.assertEqual(result['observation']['status'], 'passed')
        self.assertNotIn('output', result['observation'])

    def test_probe_timeout_is_bounded(self):
        result = live.run_probe(self.root, [sys.executable, '-c', 'import time; time.sleep(20)'], 0.05)
        self.assertEqual(result['reason'], 'timeout')

    def test_output_limit_is_bounded(self):
        result = live.run_probe(self.root, [sys.executable, '-c', 'print("x" * 100000)'], 2)
        self.assertEqual(result['reason'], 'output-limit')

    def test_checkpoint_compare_and_swap(self):
        first = live.save_active(self.root, 'TB-102', self.value)
        with self.assertRaises(live.LivenessError):
            live.save_active(self.root, 'TB-102', self.value)
        second = live.save_active(self.root, 'TB-102', self.value, first['revision'])
        self.assertEqual(second['revision'], 2)

    def test_resume_has_no_external_work(self):
        live.save_active(self.root, 'TB-102', self.value)
        with patch.object(live, 'run_probe', side_effect=AssertionError('network')):
            result = live.resume(self.root, 'TB-102')
        self.assertEqual(result['networkCalls'], 0)
        self.assertEqual(result['goal'], self.value['goal'])
        self.assertEqual(result['liveObservations'][0]['freshness'], 'unknown')

    def test_resume_prioritises_uncollected_result_without_touching_pid(self):
        self.value['processes'] = [{'pid': 123, 'identity': 'actual-start-marker', 'startedAt': live.utc(),
                                   'resultPath': '/retained/result.xcresult', 'state': 'uncollected'}]
        live.save_active(self.root, 'TB-102', self.value)
        with patch.object(os, 'kill', side_effect=AssertionError('PID must not be controlled')):
            result = live.resume(self.root, 'TB-102')
        self.assertIn('/retained/result.xcresult', result['nextAction'])

    def test_resume_never_promotes_receipt_references_to_verified(self):
        self.value['evidence'] = ['/old/pass.json']
        live.save_active(self.root, 'TB-102', self.value)
        result = live.resume(self.root, 'TB-102')
        self.assertEqual(result['evidenceReferences'], ['/old/pass.json'])
        self.assertNotIn('verified', result)

    def test_state_from_old_session_is_not_fresh_for_final(self):
        first = live.save_active(self.root, 'TB-102', self.value)
        self.observe(FAIL, session=first['sessionId'], purpose='final')
        second = live.resume(self.root, 'TB-102')
        result = live.live_status(self.root, ['project-read'], second['sessionId'], 'final')[0]
        self.assertEqual(result['freshness'], 'decision-recheck')
        self.assertFalse(result['currentBlocker'])

    def test_process_reference_requires_start_identity(self):
        self.value['processes'] = [{'pid': 123, 'resultPath': '/tmp/result'}]
        with self.assertRaises(live.LivenessError):
            live.save_active(self.root, 'TB-102', self.value)

    def test_command_in_checkpoint_remains_data(self):
        self.value['nextAction'] = 'touch SHOULD_NOT_EXIST'
        live.save_active(self.root, 'TB-102', self.value)
        live.resume(self.root, 'TB-102')
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def test_rejects_paths_escaping_state(self):
        with self.assertRaises(live.LivenessError):
            live.save_active(self.root, '../../escape', self.value)

    def test_checkpoint_does_not_accept_duplicated_blocker_truth(self):
        self.value['blockers'] = ['Project access blocked forever']
        with self.assertRaises(live.LivenessError):
            live.save_active(self.root, 'TB-102', self.value)

    def test_secret_in_checkpoint_rejected(self):
        self.value['nextAction'] = 'use Bearer secret'
        with self.assertRaises(live.LivenessError):
            live.save_active(self.root, 'TB-102', self.value)

    def test_symlink_state_rejected(self):
        directory = live.directory(self.root, True)
        external = self.root / 'external.json'
        external.write_text('{}')
        (directory / 'live-observations.json').symlink_to(external)
        with self.assertRaises(live.LivenessError):
            self.observe()
        self.assertEqual(external.read_text(), '{}')

    def test_gate_plan_separates_later_gates_without_passing_them(self):
        plan = [{'id': 'build', 'phase': 'archive', 'authority': 'release-policy', 'after': []},
                {'id': 'manual', 'phase': 'internal-acceptance', 'authority': 'owner-decision', 'after': ['build']}]
        result = live.gate_plan(plan, 'archive')
        self.assertEqual(len(result['requiredThroughPhase']), 1)
        self.assertEqual(len(result['later']), 1)
        self.assertFalse(result['authorization'])

    def test_gate_plan_rejects_circular_signed_build_gate(self):
        plan = [{'id': 'build', 'phase': 'archive', 'authority': 'release-policy', 'after': ['manual']},
                {'id': 'manual', 'phase': 'internal-acceptance', 'authority': 'owner-decision', 'after': ['build']}]
        with self.assertRaises(live.LivenessError):
            live.gate_plan(plan, 'archive')

    def test_gate_plan_rejects_later_phase_prerequisite(self):
        plan = [{'id': 'build', 'phase': 'archive', 'authority': 'release-policy', 'after': ['manual']},
                {'id': 'manual', 'phase': 'internal-acceptance', 'authority': 'owner-decision', 'after': []}]
        with self.assertRaises(live.LivenessError):
            live.gate_plan(plan, 'archive')

    def test_context_metadata_does_not_run_probe(self):
        with patch.object(live, 'run_probe', side_effect=AssertionError('unexpected probe')):
            a = live.check_context(self.root, ['gh', 'project', 'view', '1'], 'github')
            b = live.check_context(self.root, ['gh', 'project', 'view', '1'], 'github')
        self.assertEqual(a, b)


    def test_same_owner_event_does_not_probe_twice(self):
        first = self.observe(event='owner-fixed', now=1000)
        second = self.observe(event='owner-fixed', now=1001)
        self.assertTrue(first['executed'])
        self.assertFalse(second['executed'])

    def test_resume_does_not_revive_old_session_blocker(self):
        first = live.save_active(self.root, 'TB-102', self.value)
        self.observe(FAIL, session=first['sessionId'])
        result = live.resume(self.root, 'TB-102')
        self.assertFalse(result['liveObservations'][0]['currentBlocker'])
        self.assertEqual(result['liveObservations'][0]['freshness'], 'decision-recheck')

    def test_resolved_live_blocker_is_rejected_as_current_claim(self):
        failed = self.observe(FAIL, purpose='final')['observation']
        blocker = {'id':'old-auth', 'kind':'live', 'capability':'project-read',
                   'context':failed['context'], 'observationId':failed['id'], 'observedAt':failed['observedAt']}
        self.observe(purpose='final', event='owner-fixed')
        claim = live.blocker_claim(self.root, blocker, 'session-a')
        self.assertEqual(claim['state'], 'resolved-in-current-context')
        self.assertEqual(claim['networkCalls'], 0)

    def test_blocker_from_other_context_requires_recheck(self):
        passed = self.observe(purpose='final')['observation']
        claim = live.blocker_claim(self.root, {'id':'other-host', 'kind':'live', 'capability':'project-read',
                    'context':'0' * 64, 'observationId':passed['id']}, 'session-a')
        self.assertEqual(claim['state'], 'recheck-required')

    def test_owner_or_source_gate_never_cleared_by_capability_success(self):
        self.observe(purpose='final')
        for kind in ('source', 'owner'):
            result = live.blocker_claim(self.root, {'id':'mandatory', 'kind':kind}, 'session-a')
            self.assertEqual(result['state'], 'retain-existing-gate')

    def test_cache_rollover_archives_instead_of_blocking_work(self):
        first = self.observe(now=1000)['observation']
        path, state = live.load_live(self.root)
        for index in range(63):
            item = dict(first, id=('%032x' % (index + 1)), observedAt=live.utc(index))
            state['observations']['old-%d' % index] = item
        live.atomic(path, state)
        self.definition['probes']['project-read']['target'] = 'new-context'
        self.write_config()
        self.assertEqual(self.observe(now=1001)['observation']['status'], 'passed')
        self.assertEqual(len(live.load_live(self.root)[1]['observations']), 64)
        self.assertTrue((live.directory(self.root) / 'live-history' / ('%032x.json' % 1)).exists())


if __name__ == '__main__':
    unittest.main()
