"""CB-002 source-preserving discovery integration checks (standard library)."""
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_discovery', ROOT / 'scripts/build_discovery.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.schemas, self.titles = [], [], [], []
        self.capture = None
        self.buffer = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])
        if tag == 'title' or (tag == 'script' and attrs.get('type') == 'application/ld+json'):
            self.capture, self.buffer = tag, ''

    def handle_data(self, data):
        if self.capture:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == self.capture:
            if tag == 'title':
                self.titles.append(self.buffer)
            else:
                self.schemas.append(json.loads(self.buffer))
            self.capture = None


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='casebook-discovery-')
        self.root = Path(self.tmp.name)
        (self.root / 'web').mkdir()
        for name in ('catalogue.json', 'index.html', 'reading.css', 'reading.js'):
            shutil.copyfile(ROOT / 'web' / name, self.root / 'web' / name)
        self.output = self.root / 'site'
        self.output.mkdir()
        for name in ('styles.css', 'icon.svg'):
            shutil.copyfile(ROOT / 'web' / name, self.output / name)
        self.catalogue = json.loads((self.root / 'web/catalogue.json').read_text())
        self.original = {p.name: p.read_bytes() for p in (self.root / 'web').iterdir()}

    def tearDown(self):
        self.tmp.cleanup()

    def build(self):
        return builder.build_discovery(self.root, self.output)

    def test_full_catalogue_metadata_links_and_schema(self):
        result = self.build()
        self.assertEqual(result['products'], 92)
        pages = list(self.output.rglob('*.html'))
        self.assertEqual(len(pages), 97)
        titles, canonicals = [], []
        home = Document((self.output / 'index.html').read_text())
        for p in self.catalogue['products']:
            self.assertIn('cases/' + p['id'] + '/', home.links)
            text = (self.output / 'cases' / p['id'] / 'index.html').read_text()
            self.assertIn(builder.esc(p['summary']), text)
            self.assertIn(p['checkedAt'], text)
            self.assertNotIn('src="../../data.js"', text)
            for key, label in builder.SPECS:
                self.assertIn(label, text)
            schema = Document(text).schemas[0]['@graph'][0]
            self.assertEqual(schema['@type'], 'Product')
            self.assertEqual(schema['name'], p['brand'] + ' ' + p['name'])
            for forbidden in ('offers', 'aggregateRating', 'review', 'ratingValue'):
                self.assertNotIn(forbidden, schema)
        for file in pages:
            text = file.read_text()
            document = Document(text)
            self.assertEqual(len(document.titles), 1, file)
            self.assertEqual(len(document.canonicals), 1, file)
            titles.extend(document.titles)
            canonicals.extend(document.canonicals)
            self.assertIn('property="og:url" content="' + document.canonicals[0] + '"', text)
            for href in document.links:
                full = urljoin(document.canonicals[0], href)
                if full.startswith(builder.BASE):
                    route = urlsplit(full).path[len(urlsplit(builder.BASE).path):]
                    target = self.output / route
                    if full.endswith('/') or not Path(route).suffix:
                        target = target / 'index.html'
                    self.assertTrue(target.is_file(), (file, href))
        self.assertEqual(len(titles), len(set(titles)))
        self.assertEqual(len(canonicals), len(set(canonicals)))
        urls = ET.parse(self.output / 'sitemap.xml').getroot()
        locations = [entry.find('{*}loc').text for entry in urls]
        self.assertEqual(set(locations), set(canonicals) - {builder.BASE + '404.html'})
        self.assertTrue(all(re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', entry.find('{*}lastmod').text) for entry in urls))
        self.assertIn('name="robots" content="noindex"', (self.output / '404.html').read_text())

    def test_source_preservation_and_repeated_build(self):
        (self.output / 'authority.md').write_text('Preserve authority')
        self.build()
        first = (self.output / 'build-manifest.json').read_bytes()
        self.build()
        self.assertEqual(first, (self.output / 'build-manifest.json').read_bytes())
        self.assertEqual((self.output / 'authority.md').read_text(), 'Preserve authority')
        for p in (self.root / 'web').iterdir():
            self.assertEqual(self.original[p.name], p.read_bytes())
        manifest = json.loads(first)['files']
        self.assertNotIn('build-manifest.json', manifest)
        self.assertFalse(any('research/' in p or 'agents/' in p or p.startswith('.') for p in manifest))
        for name, digest in manifest.items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), digest)

    def test_path_and_script_safety(self):
        for output in (self.root, self.root / 'web', self.root / 'web/nested'):
            with self.assertRaises(ValueError):
                builder.build_discovery(self.root, output)
        self.catalogue['products'][0]['id'] = '../escape'
        (self.root / 'web/catalogue.json').write_text(json.dumps(self.catalogue))
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(builder.safe_url('javascript:alert(1)'), '')
        self.assertEqual(builder.safe_url('https://example.com@evil.test/x'), '')
        self.assertEqual(builder.safe_url('assets/../../private'), '')
        encoded = builder.ld({'text': '</script><script>alert(1)</script>'})
        self.assertEqual(encoded.count('</script>'), 1)
        self.assertNotIn('<script>alert', encoded)
        self.assertIn('&lt;script&gt;', builder.esc('<script>'))

    def test_markers_fallback_and_ads_boundaries(self):
        for template in ('<div id="results"></div>', '<div id="results">' + builder.START + 'old' + builder.END + '</div>'):
            self.assertIn('new', builder.inject_cards(template, 'new'))
            self.assertNotIn('old', builder.inject_cards(template, 'new'))
        for name in ('ads-config.js', 'ads.js', 'ads.css', 'ads-boot.js'):
            (self.output / name).write_text('/* supplied asset */')
        self.build()
        for file in self.output.rglob('*.html'):
            text = file.read_text()
            eligible = file == self.output / 'index.html' or 'choose-a-case' in str(file)
            self.assertEqual('src="' in text and 'ads.js' in text, eligible)
            self.assertEqual('data-ad-placement="article"' in text, 'choose-a-case' in str(file))
            if eligible:
                self.assertEqual(text.count('src="' + ('../../' if 'choose-a-case' in str(file) else '') + 'ads.js"'), 1)


if __name__ == '__main__':
    unittest.main()
