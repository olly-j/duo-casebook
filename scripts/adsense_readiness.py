#!/usr/bin/env python3
"""CB-003 read-only AdSense preflight. No JS execution or account access."""
import argparse
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000


def parse_config(source):
    """Read only the scaffold's literal grammar, never evaluate JavaScript."""
    tokens = re.findall(r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][\w$]*|\d+|[^\s]', source)
    tokens = [t for t in tokens if not t.startswith(('/*', '//'))]
    prefix = ['window', '.', 'CASEBOOK_ADS_CONFIG', '=']
    if tokens[:4] != prefix:
        raise ValueError('Unsupported configuration')
    pos = 4

    def value():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token == 'Object':
            if tokens[pos:pos + 3] != ['.', 'freeze', '(']:
                raise ValueError('Unsupported expression')
            pos += 3
            result = value()
            if tokens[pos] != ')':
                raise ValueError('Missing freeze terminator')
            pos += 1
            return result
        if token in ('{', '['):
            result = {} if token == '{' else []
            closing = '}' if token == '{' else ']'
            while tokens[pos] != closing:
                if token == '{':
                    key = tokens[pos]
                    pos += 1
                    key = ast.literal_eval(key) if key.startswith(('"', "'")) else key
                    if not isinstance(key, str) or key in result or tokens[pos] != ':':
                        raise ValueError('Invalid or duplicate key')
                    pos += 1
                    result[key] = value()
                else:
                    result.append(value())
                if tokens[pos] != ',':
                    break
                pos += 1
            if tokens[pos] != closing:
                raise ValueError('Missing closing delimiter')
            pos += 1
            return result
        if token in ('true', 'false', 'null'):
            return {'true': True, 'false': False, 'null': None}[token]
        if token.startswith(('"', "'")):
            return ast.literal_eval(token)
        if token.isdigit():
            return int(token)
        raise ValueError('Nonliteral configuration')

    try:
        result = value()
        if tokens[pos:] not in ([], [';']) or not isinstance(result, dict):
            raise ValueError('Unexpected configuration content')
        return result
    except (IndexError, SyntaxError, TypeError) as exc:
        raise ValueError('Malformed configuration') from exc


def valid_id(value, prefix='ca-pub-', digits=16):
    return (isinstance(value, str) and
            re.fullmatch(re.escape(prefix) + r'\d{' + str(digits) + '}', value) is not None and
            len(set(value[len(prefix):])) > 1)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.meta, self.scripts, self.hints, self.inline = [], [], [], []
        self.in_script = False
        self.in_head = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if tag == 'meta' and self.in_head and attrs.get('name') == 'google-adsense-account':
            self.meta.append(attrs.get('content'))
        if tag == 'script':
            self.in_script = True
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('preconnect', 'dns-prefetch', 'preload'):
            self.hints.append(attrs.get('href', ''))

    def handle_data(self, data):
        if self.in_script:
            self.inline.append(data)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        if tag == 'head':
            self.in_head = False


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url):
    """Bounded unauthenticated GET; redirects are reported, never followed."""
    try:
        request = Request(url, headers={'User-Agent': 'CASEBOOK-readiness/1.0'})
        with build_opener(NoRedirect).open(request, timeout=10) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return {'status': 'oversize'}
            return {'status': response.status, 'body': body}
    except HTTPError as exc:
        return {'status': exc.code}
    except (URLError, OSError, ValueError):
        return {'status': 'unreachable'}


def scan(root=ROOT, site_url=None, evidence=None, remote=False, fetcher=fetch):
    """Evidence is owner-supplied assertions, not authenticated approval proof."""
    root = Path(root)
    evidence = evidence if isinstance(evidence, dict) else {}
    checks = {}

    def check(name, passed, missing='missing', basis='local'):
        checks[name] = {'status': 'pass' if passed else missing, 'basis': basis}

    try:
        config = parse_config((root / 'web/ads-config.js').read_text())
        check('config', True)
    except (OSError, ValueError, RecursionError):
        config = {}
        check('config', False, 'malformed_or_missing')
    parts = urlsplit(site_url or '')
    site_valid = (parts.scheme == 'https' and bool(parts.hostname) and
                  not parts.username and not parts.password and parts.port in (None, 443) and
                  not parts.query and not parts.fragment)
    check('site_url', site_valid)
    publisher = config.get('publisherId')
    check('publisher_id_shape', valid_id(publisher))
    check('ad_unit_shapes', isinstance(config.get('slots'), dict) and all(
        valid_id(config['slots'].get(key), '', 10) for key in ('catalogue', 'article')))
    check('host_allowlist', site_valid and isinstance(config.get('approvedHosts'), list) and
          parts.hostname in config['approvedHosts'])
    for name, key in [('publisher_approval', 'publisherApproved'), ('site_approval', 'siteApproved')]:
        check(name, config.get(key) is True and evidence.get(key) is True,
              'unverified', 'owner_assertion_required')
    for key in ('ownerActivationApproved', 'privacyReviewed', 'browserConsentTestsPassed'):
        check(key, evidence.get(key) is True, 'unverified', 'owner_assertion_required')
    cmp = evidence.get('cmp')
    cmp_ok = (isinstance(cmp, dict) and cmp.get('certified') is True and
              type(cmp.get('id')) is int and cmp['id'] > 0 and
              isinstance(cmp.get('configId'), str) and bool(cmp['configId'].strip()) and
              cmp.get('configId') == config.get('consentConfigId') and
              cmp.get('threeButtons') is True and cmp.get('adapterReviewed') is True and
              config.get('consentReady') is True)
    check('certified_cmp', cmp_ok, 'unverified', 'owner_assertion_required')
    google = config.get('googleCMP')
    purposes = config.get('requiredPurposes')
    google_ok = (isinstance(google, dict) and
                 all(google.get(k) is True for k in
                     ('reviewed', 'certifiedConfigurationReviewed', 'legalBasesReviewed', 'googleOnly')) and
                 google.get('additionalConsentRequired') is False and
                 google.get('publisherId') == publisher and valid_id(publisher) and
                 google.get('configId') == config.get('consentConfigId') and
                 bool(config.get('consentConfigId')) and site_valid and
                 google.get('approvedOrigin') == 'https://' + parts.netloc and
                 google.get('approvedPath') == '/duo-casebook/' and
                 isinstance(google.get('allowedCmpIds'), list) and bool(google['allowedCmpIds']) and
                 all(type(i) is int and i > 0 for i in google['allowedCmpIds']) and
                 isinstance(cmp, dict) and cmp.get('id') in google['allowedCmpIds'] and
                 all(type(google.get(k)) is int and google[k] > 0 for k in
                     ('vendorListVersion', 'tcfPolicyVersion')) and
                 isinstance(purposes, list) and all(type(p) is int and 1 <= p <= 10 for p in purposes) and
                 set([1, 2, 3, 4, 7, 9, 10]).issubset(purposes))
    check('google_cmp_configuration', google_ok, 'malformed_or_missing')
    try:
        manifest = json.loads((root / 'docs/build-manifest.json').read_text())
        files = manifest['files']
        if not isinstance(files, dict) or not all(isinstance(n, str) for n in files):
            raise ValueError('Invalid manifest files')
        names = [n for n in files if n.endswith(('.html', '.js'))]
        if (not isinstance(files, dict) or manifest.get('algorithm') != 'sha256' or
                not {'ads-config.js', 'ads.js', 'ads-boot.js', 'index.html'} <= files.keys()):
            raise ValueError('Invalid manifest')
        local_ok = True
        html = []
        for name in names:
            path = root / 'docs' / name
            if (Path(name).is_absolute() or '..' in Path(name).parts or
                    any(c in name for c in (':', '\\', '?', '#'))):
                raise ValueError('Invalid manifest path')
            body = path.read_bytes()
            local_ok &= hashlib.sha256(body).hexdigest() == files[name]
            if name.endswith('.html'):
                html.append(body.decode('utf-8'))
        config_bytes = (root / 'docs/ads-config.js').read_bytes()
        local_ok &= config_bytes == (root / 'web/ads-config.js').read_bytes()
        check('build_manifest', local_ok, 'mismatch')
        pages = [Page(text) for text in html]
        check('verification_meta', bool(pages) and valid_id(publisher) and
              all(page.meta == [publisher] for page in pages))
        # Static inspection cannot detect dynamic injection. Browser tests remain mandatory.
        ad_hosts = ('googlesyndication.com', 'doubleclick.net', 'googleadservices.com')
        check('no_direct_ad_scripts_or_hints', not any(
            any((urlsplit(url).hostname or '').endswith(host) for host in ad_hosts)
            for page in pages for url in page.scripts + page.hints) and not any(
                any(host in text for host in ad_hosts) or 'adsbygoogle' in text
                for page in pages for text in page.inline))
    except (OSError, KeyError, ValueError, TypeError, UnicodeError):
        files, names = {}, []
        check('build_manifest', False, 'malformed_or_missing')
        check('verification_meta', False)
        check('no_direct_ad_scripts_or_hints', False, 'unknown')
    check('hosted_manifest_references', False, 'not_checked', 'remote')
    check('root_site', False, 'not_checked', 'remote')
    check('root_ads_txt', False, 'not_checked', 'remote')
    if remote and site_valid:
        origin = 'https://' + parts.netloc
        root_response = fetcher(origin + '/')
        check('root_site', root_response.get('status') == 200, 'unavailable', 'remote')
        ads = fetcher(origin + '/ads.txt')
        expected = ['google.com', publisher.removeprefix('ca-') if valid_id(publisher) else '',
                    'DIRECT', 'f08c47fec0942fa0']
        lines = ads.get('body', b'').decode('utf-8', errors='replace').splitlines()
        check('root_ads_txt', ads.get('status') == 200 and bool(expected[1]) and any(
            [v.strip() for v in line.split('#', 1)[0].split(',')] == expected for line in lines),
            'missing_or_mismatch', 'remote')
        matches = bool(names)
        for name in names:
            response = fetcher(urljoin(site_url.rstrip('/') + '/', name))
            matches &= (response.get('status') == 200 and
                        hashlib.sha256(response.get('body', b'')).hexdigest() == files[name])
        check('hosted_manifest_references', matches, 'mismatch_or_unavailable', 'remote')
    missing = [name for name, result in checks.items() if result['status'] != 'pass']
    return {'work_id': 'CB-003', 'schema_version': 1,
            'advertising_enabled': config.get('enabled') is True,
            'status': 'prerequisites_recorded' if not missing else 'blocked',
            'activation_authorized': False, 'checks': checks, 'missing_prerequisites': missing,
            'limits': 'Static preflight and supplied assertions do not authenticate account approval, '
                      'CMP certification, runtime consent or legal compliance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--site-url', help='Public HTTPS project base URL; no credentials or query')
    parser.add_argument('--evidence', type=Path, help='Optional owner-reviewed JSON assertions')
    parser.add_argument('--remote', action='store_true', help='Read public root and manifest references')
    args = parser.parse_args()
    try:
        evidence = json.loads(args.evidence.read_text()) if args.evidence else None
        result = scan(args.root, args.site_url, evidence, args.remote)
    except (OSError, ValueError, TypeError):
        result = {'work_id': 'CB-003', 'status': 'invalid_input', 'activation_authorized': False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'prerequisites_recorded' else 1


if __name__ == '__main__':
    raise SystemExit(main())
