"""CB-003 standard-library readiness tests. No live Google calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('adsense_readiness', ROOT / 'scripts/adsense_readiness.py')
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='casebook-readiness-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'web').mkdir()
        (self.root / 'docs').mkdir()
        self.publisher = 'ca-pub-1234567890123456'  # Synthetic shape fixture only.
        self.config = dict(enabled=False, publisherId=self.publisher,
                           slots={'catalogue': '1234567890', 'article': '2345678901'},
                           publisherApproved=True, siteApproved=True, consentReady=True,
                           approvedHosts=['example.test'], consentConfigId='reviewed-fixture',
                           requiredPurposes=[1, 2, 3, 4, 7, 9, 10],
                           googleCMP=dict(reviewed=True, certifiedConfigurationReviewed=True,
                                          legalBasesReviewed=True, googleOnly=True,
                                          additionalConsentRequired=False, publisherId=self.publisher,
                                          configId='reviewed-fixture', approvedOrigin='https://example.test',
                                          approvedPath='/duo-casebook/', allowedCmpIds=[123],
                                          vendorListVersion=1, tcfPolicyVersion=1))
        self.evidence = dict(publisherApproved=True, siteApproved=True,
                             ownerActivationApproved=True, privacyReviewed=True,
                             browserConsentTestsPassed=True,
                             cmp=dict(certified=True, id=123, configId='reviewed-fixture',
                                      threeButtons=True, adapterReviewed=True))
        self.html = '<html><head><meta name="google-adsense-account" content="' + self.publisher + '"></head><body>Cases</body></html>'
        self.write()

    def write(self):
        source = 'window.CASEBOOK_ADS_CONFIG = Object.freeze(' + json.dumps(self.config) + ');'
        (self.root / 'web/ads-config.js').write_text(source)
        (self.root / 'docs/ads-config.js').write_text(source)
        (self.root / 'docs/index.html').write_text(self.html)
        for name in ('ads.js', 'ads-boot.js'):
            (self.root / 'docs' / name).write_text('// Offline fixture')
        self.files = {name: hashlib.sha256((self.root / 'docs' / name).read_bytes()).hexdigest()
                      for name in ('index.html', 'ads-config.js', 'ads.js', 'ads-boot.js')}
        (self.root / 'docs/build-manifest.json').write_text(json.dumps(
            {'algorithm': 'sha256', 'files': self.files}))

    def remote(self, url):
        if url == 'https://example.test/':
            return {'status': 200, 'body': b'Root'}
        if url == 'https://example.test/ads.txt':
            return {'status': 200, 'body': b'google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0\n'}
        name = url.removeprefix('https://example.test/duo-casebook/')
        if name in self.files:
            return {'status': 200, 'body': (self.root / 'docs' / name).read_bytes()}
        return {'status': 404}

    def scan(self, **kwargs):
        return readiness.scan(self.root, 'https://example.test/duo-casebook/',
                              self.evidence, True, kwargs.get('fetcher', self.remote))

    def test_current_disabled_scaffold_is_blocked(self):
        result = readiness.scan(ROOT)
        self.assertFalse(result['advertising_enabled'])
        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['activation_authorized'])

    def test_missing_site_never_fetches(self):
        result = readiness.scan(self.root, remote=True,
                                fetcher=lambda _: self.fail('Unexpected network'))
        self.assertIn('site_url', result['missing_prerequisites'])
        self.assertEqual(result['checks']['root_ads_txt']['status'], 'not_checked')

    def test_id_shape_is_not_approval(self):
        self.assertTrue(readiness.valid_id(self.publisher))
        for value in (None, 'pub-1234567890123456', 'ca-pub-0000000000000000', self.publisher + 'x'):
            self.assertFalse(readiness.valid_id(value))
        result = readiness.scan(self.root, 'https://example.test/', {})
        self.assertIn('publisher_approval', result['missing_prerequisites'])

    def test_every_approval_gate_fails_closed(self):
        for key in ('publisherApproved', 'siteApproved', 'ownerActivationApproved',
                    'privacyReviewed', 'browserConsentTestsPassed'):
            with self.subTest(key=key):
                previous = self.evidence.pop(key)
                self.assertEqual(self.scan()['status'], 'blocked')
                self.evidence[key] = previous
        self.config['siteApproved'] = False
        self.write()
        self.assertIn('site_approval', self.scan()['missing_prerequisites'])

    def test_missing_root_ads_txt_and_root(self):
        def missing(url):
            return {'status': 404} if url in ('https://example.test/', 'https://example.test/ads.txt') else self.remote(url)
        result = self.scan(fetcher=missing)
        self.assertIn('root_ads_txt', result['missing_prerequisites'])
        self.assertIn('root_site', result['missing_prerequisites'])

    def test_all_prerequisites_recorded_never_authorizes_activation(self):
        result = self.scan()
        self.assertEqual(result['status'], 'prerequisites_recorded')
        self.assertEqual(result['missing_prerequisites'], [])
        self.assertFalse(result['activation_authorized'])
        self.assertFalse(result['advertising_enabled'])

    def test_malformed_cmp(self):
        for cmp in (None, [], 'certified', {}, {'id': True, 'certified': True},
                    {**self.evidence['cmp'], 'configId': 'stale'},
                    {**self.evidence['cmp'], 'threeButtons': False}):
            with self.subTest(cmp=cmp):
                evidence = {**self.evidence, 'cmp': cmp}
                result = readiness.scan(self.root, 'https://example.test/', evidence)
                self.assertIn('certified_cmp', result['missing_prerequisites'])

    def test_malformed_google_configuration(self):
        for change in ({'allowedCmpIds': [True]}, {'allowedCmpIds': []},
                       {'additionalConsentRequired': True}, {'approvedOrigin': 'https://other.test'},
                       {'vendorListVersion': '1'}, {'configId': 'stale'}):
            with self.subTest(change=change):
                original = self.config['googleCMP'].copy()
                self.config['googleCMP'].update(change)
                self.write()
                self.assertIn('google_cmp_configuration', self.scan()['missing_prerequisites'])
                self.config['googleCMP'] = original

    def test_direct_scripts_and_resource_hints(self):
        for element in ('<script src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>',
                        '<link rel="preconnect" href="https://googleads.g.doubleclick.net">',
                        '<script>(adsbygoogle = []).push({});</script>'):
            with self.subTest(element=element):
                self.html += element
                self.write()
                self.assertIn('no_direct_ad_scripts_or_hints', self.scan()['missing_prerequisites'])

    def test_manifest_and_hosted_drift(self):
        (self.root / 'docs/index.html').write_text('changed')
        result = self.scan()
        self.assertIn('build_manifest', result['missing_prerequisites'])
        self.assertIn('hosted_manifest_references', result['missing_prerequisites'])

    def test_literal_parser_rejects_executable_or_duplicate_config(self):
        for source in ('window.CASEBOOK_ADS_CONFIG = run();',
                       'window.CASEBOOK_ADS_CONFIG = {enabled:false,enabled:true};',
                       'window.CASEBOOK_ADS_CONFIG = {}; alert(1);'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                readiness.parse_config(source)
        config = readiness.parse_config((ROOT / 'web/ads-config.js').read_text())
        self.assertIs(config['enabled'], False)

    def test_missing_scripts_and_malformed_manifest(self):
        for manifest in ({'algorithm': 'sha256', 'files': {'index.html': self.files['index.html']}},
                         {'files': [1]}, {'files': None}):
            with self.subTest(manifest=manifest):
                (self.root / 'docs/build-manifest.json').write_text(json.dumps(manifest))
                self.assertIn('build_manifest', self.scan()['missing_prerequisites'])

    def test_remote_redirect_or_error_is_not_success(self):
        for status in (302, 404, 'unreachable', 'oversize'):
            result = self.scan(fetcher=lambda _, s=status: {'status': s})
            self.assertIn('hosted_manifest_references', result['missing_prerequisites'])
            self.assertIn('root_ads_txt', result['missing_prerequisites'])


if __name__ == '__main__':
    unittest.main()
