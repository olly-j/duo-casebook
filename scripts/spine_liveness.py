#!/usr/bin/env python3
"""Lazy capability observations and compact restart state, never a scheduler.

Only reviewed read-only registry commands execute. Runtime notes, process IDs,
blocker prose and suggested alternatives are data, never executable authority.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import platform
import re
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

SCHEMA = 1
STATE_LIMIT = 65536
ACTIVE_LIMIT = 16384
OUTPUT_LIMIT = 16384
PHASES = ("implementation", "integration", "archive", "internal-distribution",
          "internal-acceptance", "public-submission")
PURPOSES = ("use", "mutation", "escalation", "final")
COMMANDS = {"active", "resume", "probe", "live-status", "gate-plan"}


class LivenessError(ValueError):
    """An unknown fact stays unknown; an invalid record confers no permission."""


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                       separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def timestamp(value):
    if not isinstance(value, str):
        raise LivenessError("A timezone-aware observation timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise LivenessError("Observation timestamps require a timezone")
    return parsed.timestamp()


def utc(value=None):
    return datetime.fromtimestamp(time.time() if value is None else value, timezone.utc).isoformat()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value) or ".." in value:
        raise LivenessError("Invalid bounded identifier")
    return value


def text(value, maximum=512):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or "\x00" in value:
        raise LivenessError("Missing or oversized text")
    if re.search(r"(?:gh[pousr]_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,}|sk-[A-Za-z0-9_-]{12,}|Bearer\s+\S+)", value):
        raise LivenessError("Do not retain credentials in workflow state")
    return value


def read_json(path, limit=STATE_LIMIT):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise LivenessError("Missing, unsafe or oversized state file")
    value = json.loads(path.read_bytes(), parse_constant=lambda _: (_ for _ in ()).throw(LivenessError("Non-finite JSON")))
    if not isinstance(value, dict):
        raise LivenessError("Expected a JSON object")
    return value


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=10)
    if result.returncode:
        raise LivenessError("Git context unavailable: " + " ".join(args))
    return result.stdout.decode().strip()


def directory(root, create=False):
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    common = (root / common).resolve() if not common.is_absolute() else common.resolve()
    path = common / "spine-workflow"
    if path.is_symlink():
        raise LivenessError("Unsafe runtime directory")
    if create:
        path.mkdir(mode=0o700, exist_ok=True)
    return path


@contextmanager
def lock(root, name):
    # Kernel-owned locks expire when their owning process exits. No stale-PID kill.
    import fcntl
    path = directory(root, True) / ("liveness-" + identifier(name) + ".lock")
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise LivenessError("State is in use; continue independent work and retry at the next boundary") from exc
        yield
    finally:
        os.close(fd)


def atomic(path, value, limit=STATE_LIMIT):
    data = encoded(value)
    if len(data) > limit or path.is_symlink():
        raise LivenessError("State budget or safe-path constraint exceeded")
    fd, temporary = tempfile.mkstemp(prefix=".liveness-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def config(root):
    path = root / ".spine/liveness.json"
    if not path.exists():
        path = root / "template/.spine/liveness.json"
    data = read_json(path)
    if data.get("schemaVersion") != SCHEMA or set(data) - {"schemaVersion", "probes", "routes"}:
        raise LivenessError("Unsupported liveness configuration")
    probes = data.get("probes", {})
    if not isinstance(probes, dict) or len(probes) > 32:
        raise LivenessError("Probe registry must be bounded")
    for name, spec in probes.items():
        identifier(name)
        if not isinstance(spec, dict) or set(spec) != {"command", "readOnly", "target", "maxAgeSeconds", "timeoutSeconds"}:
            raise LivenessError("Probes require explicit reviewed read-only command, target and budgets")
        if spec["readOnly"] is not True:
            raise LivenessError("Mutation is not a capability probe")
        command = spec["command"]
        if not isinstance(command, list) or not command or len(command) > 40:
            raise LivenessError("A literal argv is required; no shell or handoff commands")
        for arg in command:
            text(arg, 1024)
        if Path(command[0]).name in {"sh", "bash", "zsh", "fish", "cmd", "powershell", "pwsh"}:
            raise LivenessError("Shell probes are not supported")
        text(spec["target"], 256)
        for field, upper in (("maxAgeSeconds", 3600), ("timeoutSeconds", 30)):
            if type(spec[field]) not in {int, float} or not math.isfinite(spec[field]) or not 0 < spec[field] <= upper:
                raise LivenessError("Invalid probe budget")
    routes = data.get("routes", {})
    if not isinstance(routes, dict) or len(routes) > 10:
        raise LivenessError("Invalid alternative-route registry")
    for category, names in routes.items():
        identifier(category)
        if not isinstance(names, list) or len(names) > 8:
            raise LivenessError("Invalid route list")
        for name in names:
            text(name, 256)
    return data


def execution_context(root, spec, salt):
    """Fingerprint execution identity without returning/logging credential values."""
    env_names = ("GH_HOST", "GH_CONFIG_DIR", "XDG_CONFIG_HOME", "HOME", "GITHUB_ACTIONS")
    source = next((key for key in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN") if os.environ.get(key)), "stored-credential")
    config_dir = Path(os.environ.get("GH_CONFIG_DIR") or Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "gh")
    hosts = config_dir / "hosts.yml"
    material = {"environment": {key: os.environ.get(key) for key in env_names}, "credentialSource": source}
    material["credential"] = os.environ.get(source) if source != "stored-credential" else None
    material["storedConfig"] = digest(hosts.read_bytes()) if hosts.is_file() and hosts.stat().st_size < STATE_LIMIT else None
    executable = shutil.which(spec["command"][0])
    identity = {"machine": platform.node(), "user": str(os.getuid()) if hasattr(os, "getuid") else os.environ.get("USERNAME"),
                "commonDirectory": str(directory(root)), "executable": executable,
                "executableStamp": None if not executable else [os.stat(executable).st_mtime_ns, os.stat(executable).st_size],
                "registry": digest(encoded(spec)),
                "credentialContext": hmac.new(salt.encode(), encoded(material), hashlib.sha256).hexdigest()}
    return digest(encoded(identity)), source


def check_context(root, command, target):
    """Credential-context metadata for the existing verifier; performs no probe."""
    with lock(root, "observations"):
        path, data = load_live(root)
        if not path.exists():
            atomic(path, data)
    return execution_context(root, {"command": command, "target": target}, data["salt"])[0]


def freshness(observation, context, session, now, maximum, purpose="use"):
    if not observation:
        return "unknown"
    if observation.get("context") != context:
        return "context-changed"
    if observation.get("status") not in {"passed", "blocked"}:
        raise LivenessError("Invalid capability observation")
    age = now - timestamp(observation.get("observedAt"))
    if not 0 <= age <= maximum:
        return "stale"
    if observation["status"] == "blocked" and observation.get("sessionId") != session:
        return "decision-recheck"
    if purpose in {"mutation", "escalation", "final"}:
        if observation.get("sessionId") != session or observation.get("purpose") != purpose:
            return "decision-recheck"
    return "fresh"


def run_probe(root, command, timeout):
    """Bounded read-only argv; kill only our own child group on timeout/overflow."""
    env = dict(os.environ, GH_PROMPT_DISABLED="1", GIT_TERMINAL_PROMPT="0", GH_SPINNER_DISABLED="1")
    try:
        process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, start_new_session=True)
    except OSError:
        return {"exitCode": None, "outputSha256": digest(b""), "reason": "executable-unavailable"}
    output = bytearray()
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    reason = "completed"
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                reason = "timeout"
                break
            for key, _ in selector.select(min(remaining, 0.2)):
                chunk = os.read(key.fileobj.fileno(), 4096)
                if not chunk:
                    selector.unregister(key.fileobj)
                else:
                    output.extend(chunk)
            if len(output) > OUTPUT_LIMIT:
                reason = "output-limit"
                break
        if reason == "completed":
            try:
                process.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                reason = "timeout"
    except BaseException:
        reason = "interrupted"
        raise
    finally:
        selector.close()
        if reason != "completed":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait()
        process.stdout.close()
    # Output can contain secrets. Retain only its digest and a fixed diagnostic.
    return {"exitCode": process.returncode, "outputSha256": digest(bytes(output[:OUTPUT_LIMIT])),
            "reason": reason if reason != "completed" or process.returncode == 0 else "capability-command-failed"}


def load_live(root):
    path = directory(root) / "live-observations.json"
    data = read_json(path) if path.exists() else {"schemaVersion": SCHEMA, "salt": uuid.uuid4().hex, "observations": {}}
    if set(data) != {"schemaVersion", "salt", "observations"} or data["schemaVersion"] != SCHEMA or not isinstance(data["observations"], dict):
        raise LivenessError("Invalid observation store")
    return path, data


def observe(root, capability, session, purpose="use", event=None, runner=run_probe, now=None):
    if purpose not in PURPOSES:
        raise LivenessError("Unsupported decision purpose")
    identifier(session)
    definition = config(root)
    if capability not in definition["probes"]:
        raise LivenessError("Capability has no reviewed probe; record an explicit gap")
    spec = definition["probes"][capability]
    with lock(root, "probe-" + identifier(capability)):
        with lock(root, "observations"):
            path, data = load_live(root)
            if not path.exists():
                atomic(path, data)
        context, credential_source = execution_context(root, spec, data["salt"])
        key = capability + ":" + context
        prior = data["observations"].get(key)
        moment = time.time() if now is None else now
        if prior and moment < timestamp(prior["observedAt"]):
            raise LivenessError("An older observation cannot replace a newer one")
        condition = freshness(prior, context, session, moment, spec["maxAgeSeconds"], purpose)
        event_hash = digest(text(event, 160).encode()) if event else None
        if condition == "fresh" and (not event or prior.get("eventHash") == event_hash):
            return {"observation": prior, "freshness": condition, "executed": False, "credentialSource": credential_source}
        if event:
            text(event, 160)
        result = runner(root, spec["command"], spec["timeoutSeconds"])
        moment = time.time() if now is None else now
        status = "passed" if result["exitCode"] == 0 and result["reason"] == "completed" else "blocked"
        streak = prior.get("failureStreak", 0) + 1 if prior and status == "blocked" and not event else int(status == "blocked")
        item = {"id": uuid.uuid4().hex, "capability": capability, "status": status, "context": context,
                "target": spec["target"], "sessionId": session, "purpose": purpose,
                "observedAt": utc(moment), "maxAgeSeconds": spec["maxAgeSeconds"],
                "supersedes": prior["id"] if prior else None, "failureStreak": streak, "eventHash": event_hash,
                "exitCode": result["exitCode"], "outputSha256": result["outputSha256"], "reason": result["reason"]}
        # Keep old failures as historical evidence; never feed that history to resume.
        if prior and prior["status"] == "blocked":
            history = directory(root, True) / "live-history"
            if history.is_symlink():
                raise LivenessError("Unsafe history path")
            history.mkdir(mode=0o700, exist_ok=True)
            atomic(history / (identifier(prior["id"]) + ".json"), prior)
        with lock(root, "observations"):
            path, data = load_live(root)
            if key not in data["observations"] and len(data["observations"]) >= 64:
                oldest = min(data["observations"], key=lambda name: timestamp(data["observations"][name]["observedAt"]))
                retired = data["observations"][oldest]
                history = directory(root, True) / "live-history"
                if history.is_symlink():
                    raise LivenessError("Unsafe history path")
                history.mkdir(mode=0o700, exist_ok=True)
                atomic(history / (identifier(retired["id"]) + ".json"), retired)
                del data["observations"][oldest]
            data["observations"][key] = item
            atomic(path, data)
    return {"observation": item, "freshness": "fresh", "executed": True, "credentialSource": credential_source,
            "advice": "Reassess the cause; use an approved alternative or continue independent work" if streak >= 2 else None,
            "alternativeRoutes": definition.get("routes", {}) if streak >= 2 else {}}


def active_path(root, work_item):
    return directory(root) / ("active-" + identifier(work_item) + ".json")


def validate_active(value):
    required = {"goal", "phase", "nextAction"}
    optional = {"processes", "evidence", "capabilities"}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - optional:
        raise LivenessError("Active input requires goal, phase and nextAction; no duplicate project status")
    text(value["goal"], 512)
    text(value["nextAction"], 512)
    if value["phase"] not in PHASES:
        raise LivenessError("Invalid work phase")
    for key in optional:
        if not isinstance(value.get(key, []), list) or len(value.get(key, [])) > 16:
            raise LivenessError("Active references must be small and bounded")
    for name in value.get("capabilities", []):
        identifier(name)
    for receipt in value.get("evidence", []):
        text(receipt, 1024)
    for process in value.get("processes", []):
        if not isinstance(process, dict) or set(process) != {"pid", "startedAt", "identity", "resultPath", "state"}:
            raise LivenessError("Processes require PID, start identity and durable result path")
        if type(process["pid"]) is not int or process["pid"] <= 0 or process["state"] not in {"running", "uncollected"}:
            raise LivenessError("Invalid process reference")
        timestamp(process["startedAt"])
        text(process["identity"], 512)
        text(process["resultPath"], 1024)
    if len(encoded(value)) > ACTIVE_LIMIT:
        raise LivenessError("Active checkpoint is too large")


def read_active(root, work_item):
    value = read_json(active_path(root, work_item), ACTIVE_LIMIT)
    metadata = {"schemaVersion", "workItem", "revision", "sessionId", "head", "worktree", "updatedAt"}
    if not metadata <= set(value) or value["schemaVersion"] != SCHEMA or value["workItem"] != work_item:
        raise LivenessError("Invalid active checkpoint identity")
    if type(value["revision"]) is not int or value["revision"] < 1:
        raise LivenessError("Invalid active revision")
    identifier(value["sessionId"])
    timestamp(value["updatedAt"])
    validate_active({key: item for key, item in value.items() if key not in metadata})
    return value


def save_active(root, work_item, value, expected_revision=0):
    validate_active(value)
    with lock(root, "active-" + identifier(work_item)):
        path = active_path(root, work_item)
        previous = read_active(root, work_item) if path.exists() else None
        revision = previous["revision"] if previous else 0
        if expected_revision != revision:
            raise LivenessError("Active state changed; read the current revision instead of overwriting it")
        record = {"schemaVersion": SCHEMA, "workItem": work_item, "revision": revision + 1,
                  "sessionId": previous["sessionId"] if previous else uuid.uuid4().hex,
                  "head": git(root, "rev-parse", "HEAD"), "worktree": str(root.resolve()),
                  "updatedAt": utc(), **value}
        atomic(path, record, ACTIVE_LIMIT)
    return record


def live_status(root, capabilities, session, purpose="use", now=None):
    """No network, no probe execution, no interpretation of expiry as success."""
    definition = config(root)
    _, data = load_live(root)
    answer = []
    for capability in dict.fromkeys(capabilities):
        spec = definition["probes"].get(capability)
        if not spec:
            answer.append({"capability": capability, "freshness": "unconfigured", "status": "not_run"})
            continue
        context, _ = execution_context(root, spec, data["salt"])
        item = data["observations"].get(capability + ":" + context)
        state = freshness(item, context, session, time.time() if now is None else now, spec["maxAgeSeconds"], purpose)
        answer.append({"capability": capability, "freshness": state,
                       "status": item["status"] if item else "not_run", "observationId": item["id"] if item else None,
                       "context": context, "observedAt": item["observedAt"] if item else None,
                       "currentBlocker": state == "fresh" and item["status"] == "blocked" if item else False,
                       "needsDecisionProbe": state != "fresh"})
    return answer


def blocker_claim(root, blocker, session):
    """A report must cite fresh observation state, not copied blocker prose."""
    if blocker.get("kind") != "live":
        return {"id": blocker.get("id"), "state": "retain-existing-gate"}
    capability = blocker.get("capability")
    if not capability:
        return {"id": blocker.get("id"), "state": "recheck-required"}
    current = live_status(root, [capability], session, "final")[0]
    if current.get("freshness") != "fresh" or current.get("context") != blocker.get("context"):
        state = "recheck-required"
    elif current["status"] == "passed":
        state = "resolved-in-current-context"
    elif current.get("observationId") != blocker.get("observationId"):
        state = "refresh-blocker-evidence"
    else:
        state = "current-blocker"
    return {"id": blocker.get("id"), "capability": capability, "state": state,
            "observationId": current.get("observationId"), "networkCalls": 0}


def source_relation(root, retained, current):
    if retained == current:
        return "unchanged"
    for old, new, relation in ((retained, current, "advanced"), (current, retained, "behind-checkpoint")):
        result = subprocess.run(["git", "merge-base", "--is-ancestor", old, new], cwd=root,
                                capture_output=True, timeout=10)
        if result.returncode == 0:
            return relation
        if result.returncode != 1:
            return "unverified"
    return "different-branch"


def resume(root, work_item):
    path = active_path(root, work_item)
    if not path.exists():
        return {"workItem": work_item, "status": "not_run", "nextAction": "Create one compact active checkpoint from current approved scope", "networkCalls": 0}
    with lock(root, "active-" + identifier(work_item)):
        record = read_active(root, work_item)
        record.update(sessionId=uuid.uuid4().hex, revision=record["revision"] + 1, updatedAt=utc())
        atomic(path, record, ACTIVE_LIMIT)
    current_head = git(root, "rev-parse", "HEAD")
    relation = source_relation(root, record["head"], current_head)
    processes = record.get("processes", [])
    next_action = ("Collect retained result before rerunning: " + processes[0]["resultPath"]) if processes else record["nextAction"]
    return {"workItem": work_item, "goal": record["goal"], "phase": record["phase"],
            "sessionId": record["sessionId"], "revision": record["revision"], "nextAction": next_action,
            "headChanged": current_head != record["head"], "dirtyWorktree": bool(git(root, "status", "--porcelain=v1")), "sourceRelation": relation, "retainedHead": record["head"], "currentHead": current_head,
            "worktreeChanged": str(root.resolve()) != record["worktree"],
            "processes": processes, "evidenceReferences": record.get("evidence", []),
            "liveObservations": live_status(root, record.get("capabilities", []), record["sessionId"]),
            "networkCalls": 0, "note": "References require exact-source validation; PIDs are not proof of process identity. No tests or probes launched."}


def gate_plan(gates, phase):
    """Check a reviewed phase assignment; never move or waive an existing gate."""
    if phase not in PHASES or not isinstance(gates, list) or len(gates) > 64:
        raise LivenessError("Invalid bounded gate plan")
    by_id = {}
    for gate in gates:
        if not isinstance(gate, dict) or set(gate) != {"id", "phase", "authority", "after"}:
            raise LivenessError("Each gate needs its phase, authority and dependencies")
        name = identifier(gate["id"])
        if name in by_id or gate["phase"] not in PHASES or not isinstance(gate["after"], list):
            raise LivenessError("Duplicate gate or invalid phase/dependency")
        text(gate["authority"], 512)
        by_id[name] = gate
    visited, active = set(), set()
    def visit(name):
        if name in active:
            raise LivenessError("Circular gate dependency")
        if name in visited:
            return
        if name not in by_id:
            raise LivenessError("Unknown gate dependency")
        active.add(name)
        for dependency in by_id[name]["after"]:
            visit(dependency)
            if PHASES.index(by_id[dependency]["phase"]) > PHASES.index(by_id[name]["phase"]):
                raise LivenessError("A gate depends on a later phase; reconcile the authority instead of creating a circular hold")
        active.remove(name)
        visited.add(name)
    for name in by_id:
        visit(name)
    return {"phase": phase, "requiredThroughPhase": [g for g in gates if PHASES.index(g["phase"]) <= PHASES.index(phase)],
            "later": [g for g in gates if PHASES.index(g["phase"]) > PHASES.index(phase)],
            "authorization": False, "note": "Validate assignments against current item-level authority; a plan is not acceptance evidence."}


def add_parsers(subparsers):
    for command in ("active", "resume", "probe", "live-status"):
        sub = subparsers.add_parser(command, help="Lazy restart state; no periodic work")
        sub.add_argument("--backlog", required=True)
        sub.add_argument("--json", action="store_true")
        if command == "active":
            sub.add_argument("--input", type=Path, required=True)
            sub.add_argument("--expected-revision", type=int, default=0)
        elif command in {"probe", "live-status"}:
            sub.add_argument("--capability", nargs="+", required=True)
            sub.add_argument("--purpose", choices=PURPOSES, default="use")
            if command == "probe":
                sub.add_argument("--event", help="Relevant change or reason to recheck; never a timer")
    gates = subparsers.add_parser("gate-plan", help="Detect phase cycles without changing gates or running checks")
    gates.add_argument("--input", type=Path, required=True)
    gates.add_argument("--phase", choices=PHASES, required=True)


def dispatch(root, args):
    if args.command == "active":
        output = save_active(root, args.backlog, read_json(args.input, ACTIVE_LIMIT), args.expected_revision)
    elif args.command == "resume":
        output = resume(root, args.backlog)
    elif args.command == "gate-plan":
        output = gate_plan(read_json(args.input)["gates"], args.phase)
    else:
        active = read_active(root, args.backlog)
        if args.command == "live-status":
            output = {"observations": live_status(root, args.capability, active["sessionId"], args.purpose), "networkCalls": 0}
        else:
            output = {"observations": [observe(root, name, active["sessionId"], args.purpose, args.event) for name in dict.fromkeys(args.capability)]}
    rendered = output
    if not getattr(args, "json", False) and args.command == "probe":
        rendered = {"observations": [{"capability": item["observation"]["capability"],
                    "status": item["observation"]["status"], "executed": item["executed"],
                    "advice": item.get("advice")} for item in output["observations"]]}
    print(json.dumps(rendered, indent=2, ensure_ascii=False, allow_nan=False))
    if args.command == "probe":
        return 3 if any(item["observation"]["status"] != "passed" for item in output["observations"]) else 0
    if args.command == "live-status":
        return 3 if any(item.get("needsDecisionProbe", True) or item["status"] != "passed" for item in output["observations"]) else 0
    return 3 if output.get("status") == "not_run" else 0
