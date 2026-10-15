#!/usr/bin/env python3
"""CB-002: render source-backed discovery pages, with no runtime dependencies."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

BASE = 'https://olly-j.github.io/duo-casebook/'
REPO = 'https://github.com/olly-j/duo-casebook'
START = '<!-- CASEBOOK_STATIC_START -->'
END = '<!-- CASEBOOK_STATIC_END -->'


def esc(value):
    return html.escape(str(value), quote=True)


def safe_url(value):
    value = str(value or '')
    parts = urlsplit(value)
    if parts.scheme == 'https' and parts.netloc and not parts.username and not parts.password:
        return value
    if not parts.scheme and not parts.netloc and value.startswith('assets/') and '..' not in parts.path.split('/') and '\\' not in value:
        return BASE + value
    return ''


def link(url, label):
    target = safe_url(url)
    return f'<a href="{esc(target)}">{esc(label)}</a>' if target else esc(label)


def value(v):
    if v is None:
        return 'Not published'
    if isinstance(v, bool):
        return 'Yes, source-listed' if v else 'No, source-listed'
    if isinstance(v, list):
        return ', '.join(map(str, v)) or 'Not published'
    if isinstance(v, dict):
        return '; '.join(f'{k}: {value(x)}' for k, x in v.items())
    return str(v)


def price(p):
    if p.get('price') is None:
        return 'Price not published'
    return ('From ' if p.get('priceFrom') else '') + {'GBP':'£','USD':'US$','EUR':'€','AUD':'A$','CHF':'CHF '}.get(p.get('currency'), '') + format(p['price'], '.2f').rstrip('0').rstrip('.')


def ld(data):
    # Escaping < also neutralises a literal closing script element in source text.
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + '</script>'


def metadata(title, description, path, schema, image=None, noindex=False):
    url = BASE + path
    tags = f'<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{url}">'
    for attr, key, val in [('property', 'og:type', 'website'), ('property', 'og:site_name', 'CASEBOOK'), ('property', 'og:title', title), ('property', 'og:description', description), ('property', 'og:url', url), ('name', 'twitter:card', 'summary_large_image' if image else 'summary'), ('name', 'twitter:title', title), ('name', 'twitter:description', description)]:
        tags += f'<meta {attr}="{key}" content="{esc(val)}">'
    if image and safe_url(image):
        tags += f'<meta property="og:image" content="{esc(safe_url(image))}"><meta name="twitter:image" content="{esc(safe_url(image))}">'
    if noindex:
        tags += '<meta name="robots" content="noindex">'
    tags += '<meta name="referrer" content="strict-origin-when-cross-origin"><meta name="robots" content="max-image-preview:large">'
    if image and safe_url(image):
        tags += '<meta property="og:image:alt" content="' + esc(title) + '">'
    return tags + ld({'@context': 'https://schema.org', '@graph': schema})


def breadcrumbs(path, title):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'CASEBOOK', 'item': BASE}, {'@type': 'ListItem', 'position': 2, 'name': title, 'item': BASE + path}]}


def ads_assets(output, prefix):
    if all((output / name).is_file() for name in ('ads-config.js', 'ads.js', 'ads.css', 'ads-boot.js')):
        return f'<link rel="stylesheet" href="{prefix}ads.css"><script defer src="{prefix}ads-config.js"></script><script defer src="{prefix}ads.js"></script><script defer src="{prefix}ads-boot.js"></script>'
    return ''


def page(title, description, path, body, schema, output, image=None, noindex=False, ads=False):
    prefix = '../' * path.count('/') if path.endswith('/') else './'
    return '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + metadata(title, description, path, schema, image, noindex) + f'<link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}reading.css"><link rel="icon" href="{prefix}icon.svg"><script defer src="{prefix}reading.js"></script>' + (ads_assets(output, prefix) if ads else '') + f'</head><body class="reading"><a class="reading-skip" href="#content">Skip to content</a><header class="reading-header"><a href="{BASE}" class="wordmark">CASEBOOK</a><nav aria-label="Main"><a href="{BASE}">Browse cases</a><a href="{BASE}guides/choose-a-case/">Choosing a case</a><a href="{BASE}about/">About</a></nav></header><main id="content" class="reading-main">' + body + f'</main><footer class="reading-footer"><a href="{BASE}privacy/">Privacy</a> · <a href="{REPO}/issues/new">Suggest a correction</a> · <a href="{BASE}">Browse cases</a></footer></body></html>'


SPECS = [('materials', 'Materials'), ('materialNotes', 'Material notes'), ('coverage', 'Coverage'), ('coverageNote', 'Coverage notes'), ('hinge', 'Structural hinge cover'), ('magsafe', 'Magnetic attachment'), ('stand', 'Stand'), ('wallet', 'Wallet'), ('strap', 'Strap'), ('weightG', 'Case weight (g)'), ('thicknessMm', 'Wall thickness (mm)'), ('thicknessNote', 'Thickness and weight context'), ('dimensions', 'Published dimensions'), ('closedWidthMm', 'Closed width (mm)'), ('closedDepthMm', 'Closed depth (mm)'), ('ukListing', 'UK listing'), ('releaseDate', 'Published release date'), ('releaseNote', 'Release / dispatch notes'), ('shippingNote', 'Delivery notes'), ('evidence', 'Product source evidence')]


def items(values):
    return '<ul>' + ''.join('<li>' + esc(value(x)) + '</li>' for x in values) + '</ul>'


def photo(p):
    url = safe_url(p.get('preview') or p.get('image'))
    return (f'<figure><img width="1000" height="1000" loading="eager" src="{esc(url)}" alt="{esc(p.get("imageCaption") or p["name"])}"><figcaption>{esc(p.get("imageCaption", ""))} {link(p.get("imageSource"), "Image source")}</figcaption></figure>' if url else '')


def sources(entries):
    return '<ul class="reading-sources">' + ''.join('<li>' + link(s.get('url'), s.get('title') or 'Source') + '<p>' + esc(' · '.join(str(s[k]) for k in ('type', 'date', 'kind', 'modelTested') if s.get(k))) + '</p>' + items(s.get('facts', s.get('findings', []))) + ('<p>Sponsorship: ' + esc('Disclosed' if s.get('sponsored') is True else 'Not sponsored, as recorded' if s.get('sponsored') is False else 'Unknown') + '</p>' if 'sponsored' in s else '') + '</li>' for s in entries) + '</ul>'


def case_body(p, brand):
    name = p['brand'] + ' ' + p['name']
    body = f'<p class="eyebrow">iPhone Duo · {esc(p["brand"])}</p><h1>{esc(name)}</h1><p class="reading-lead">{esc(p.get("summary", ""))}</p><p><strong>{esc(price(p))}</strong> · {esc(human(p.get("status")))}</p><p>Research checked: <time datetime="{esc(p.get("checkedAt", ""))}">{esc(datetime.strptime(p['checkedAt'],'%Y-%m-%d').strftime('%d %b %Y').lstrip('0') if p.get('checkedAt') else 'Date not recorded')}</time>. Confirm the current price, availability and delivery with the seller.</p>'
    body += photo(p) + f'<p>{link(p.get("url"), "Visit seller")}</p><div class="reading-actions"><a href="{BASE}?case={esc(p["id"])}">Save or compare this case</a><a href="{BASE}?compare={esc(p["id"])}">Start comparison with this case</a></div>'
    body += '<h2>Published specifications</h2><p>Yes and No record source claims. “Not published” means the checked sources did not establish the fact. Wall thickness, closed depth and package weight are different measurements.</p><dl class="reading-specs">' + ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(human(p.get(key)) if key in ('coverage','evidence') else value(p.get(key)))}</dd></div>' for key, label in SPECS) + '</dl>'
    body += '<h2>Colours and variants</h2><p>' + esc(value(p.get('colours'))) + '</p><ul>' + ''.join('<li>' + link(v.get('url'), v.get('name') or 'Variant') + ' · ' + esc(price(v)) + '</li>' for v in p.get('variants', [])) + '</ul>'
    body += '<h2>Limitations and cautions</h2>' + items(p.get('limitations') or ['No additional limitations recorded. This does not establish an absence of tradeoffs.'])
    body += '<h2>Photo provenance</h2><p>' + esc(value(p.get('imageVerification'))) + '</p>'
    for key in ('imageNote',):
        if p.get(key):
            body += '<p>' + esc(p[key]) + '</p>'
    gallery = p.get('images', [])[1:]
    if gallery:
        body += '<ul>' + ''.join('<li>' + link(i.get('url'), i.get('caption') or 'Additional source image') + ' · ' + link(i.get('sourceUrl'), 'Published source') + '</li>' for i in gallery) + '</ul>'
    body += '<h2>Previous-model brand evidence</h2><p>These records concern the exact models named below. They do not establish this Duo case’s performance. CASEBOOK has not independently tested this case or assigned a review score.</p><p>' + esc(brand.get('summary') or 'No historical hands-on evidence established in this dataset.') + '</p>' + items(brand.get('cautions', []))
    for key in ('warranty', 'returns'):
        evidence = brand.get(key)
        body += f'<p>{key.capitalize()}: ' + (link(evidence.get('url'), evidence.get('summary', 'See policy')) if isinstance(evidence, dict) else esc(value(evidence))) + '</p>'
    body += sources(brand.get('sources', [])) + '<h2>Product sources</h2><p>Manufacturer and seller descriptions remain claims by those sources unless independent testing is explicitly identified.</p>' + sources(p.get('sources', []))
    return body


def human(v):
    return {'unknown':'Not published','official':'Manufacturer','retailer':'Retailer',
            'announcement':'Announcement','front-and-back':'Front and back',
            'front-only':'Front only','back-only':'Back only','coming-soon':'Coming soon',
            'sold-out':'Sold out'}.get(v, str(v).replace('-', ' ').capitalize() if v else 'Not published')


def card(p, eager=False):
    ident, name = esc(p['id']), esc(p['name'])
    href = 'cases/' + ident + '/'
    features = [label for key,label in [('magsafe','MagSafe'),('hinge','Structural hinge cover'),('stand','Stand'),('wallet','Card storage'),('strap','Strap')] if p.get(key) is True]
    summary = ', '.join(p.get('materials',[])) or 'Materials not published'
    if features: summary += ' · ' + ', '.join(features)
    hinge = 'Yes' if p.get('hinge') is True else 'No' if p.get('hinge') is False else 'Not published'
    loading = 'eager' if eager else 'lazy'
    priority = ' fetchpriority="high"' if eager else ''
    image = f'<div class="photo"><a class="photo-open" data-detail="{ident}" href="{href}" aria-label="View {esc(p["brand"])} {name} details"><img src="{esc(p.get("thumbnail") or safe_url(p.get("image")))}" alt="{esc(p["brand"])} {name}" width="600" height="600" loading="{loading}"{priority} referrerpolicy="no-referrer"></a><button class="save" data-save="{ident}" aria-pressed="false" disabled>Save</button></div>'
    weight = str(p['weightG']) + ' g' if p.get('weightG') is not None else 'Not published'
    return f'<article class="card">{image}<div class="card-body"><p class="brand">{esc(p["brand"])}</p><h3><a class="title-button" href="{href}">{name}</a></h3><p class="price">{esc(price(p))}</p><p class="coverage-label">{esc(human(p.get("coverage")))} · Hinge: {hinge}</p><p class="card-summary">{esc(summary)}</p><p class="card-meta">{esc(human(p.get("status")))} · {esc(human(p.get("evidence")))} source<br>Weight: {esc(weight)}</p><div class="card-actions"><a class="button-link" href="{href}">Details</a><label><input type="checkbox" data-compare="{ident}" disabled>Compare<span class="sr"> {name}</span></label></div></div></article>'


def inject_cards(source, cards):
    if START in source and END in source:
        return source[:source.index(START) + len(START)] + cards + source[source.index(END):]
    # Preserve controls when #results wraps the narrower #products container.
    for ident in ('products', 'results'):
        match = re.search(r'<div\b[^>]*\bid=["\']' + ident + r'["\'][^>]*>', source, re.I)
        if not match:
            continue
        depth = 1
        for tag in re.finditer(r'</?div\b[^>]*>', source[match.end():], re.I):
            depth += -1 if tag[0].startswith('</') else 1
            if depth == 0:
                end = match.end() + tag.start()
                return source[:match.end()] + START + cards + END + source[end:]
    raise ValueError('Missing static catalogue markers or results container')


def replace_head(source, head):
    source = re.sub(r'<title\b[^>]*>.*?</title>|<meta\b[^>]*(?:name=["\'](?:description|twitter:[^"\']+)["\']|property=["\']og:[^"\']+["\'])[^>]*>|<link\b[^>]*rel=["\']canonical["\'][^>]*>|<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>', '', source, flags=re.S | re.I)
    return re.sub(r'</head>', lambda _: head + '</head>', source, count=1, flags=re.I)


def write_manifest(output: Path):
    extensions = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.svg', '.png', '.webmanifest', '.webp', '.ico'}
    hashes = {}
    for file in sorted(output.rglob('*')):
        relative = file.relative_to(output)
        if file.is_symlink():
            raise ValueError(f'Symlink in deployment: {relative}')
        if file.is_file() and file.suffix in extensions and file.name != 'build-manifest.json' and not any(part.startswith('.') for part in relative.parts):
            hashes[relative.as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    (output / 'build-manifest.json').write_text(json.dumps({'algorithm': 'sha256', 'files': hashes}, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def build_discovery(root: Path, output: Path):
    if Path(output).is_symlink():
        raise ValueError('Symlink deployment directory')
    root, output = Path(root).resolve(), Path(output).resolve()
    web = root / 'web'
    if output == root or output == web or web in output.parents or output in root.parents:
        raise ValueError('Output must be a separate deployment directory')
    catalogue = json.loads((web / 'catalogue.json').read_text(encoding='utf-8'))
    products = catalogue['products']
    ids = [p['id'] for p in products]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) for ident in ids):
        raise ValueError('Unsafe or duplicate product ID')
    output.mkdir(parents=True, exist_ok=True)
    if any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('Symlink in deployment tree')
    old_pages = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*.html')}
    old_dates = {}
    old_hashes = {}
    if (output / 'build-manifest.json').is_file():
        try:
            old_hashes = json.loads((output / 'build-manifest.json').read_text(encoding='utf-8')).get('files', {})
        except (ValueError, AttributeError):
            pass
    if (output / 'sitemap.xml').is_file():
        try:
            for entry in ET.parse(output / 'sitemap.xml').getroot():
                fields = {child.tag.rsplit('}', 1)[-1]: child.text for child in entry}
                if fields.get('loc') and fields.get('lastmod'):
                    old_dates[fields['loc']] = fields['lastmod']
        except ET.ParseError:
            pass
    modified_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for asset in ('reading.css', 'reading.js'):
        (output / asset).write_bytes((web / asset).read_bytes())
    brands = {b['brand']: b for b in catalogue.get('brands', [])}
    routes = ['']
    root_schema = [{'@type': 'WebSite', '@id': BASE + '#website', 'name': 'CASEBOOK', 'url': BASE}, {'@type': 'CollectionPage', 'name': 'iPhone Duo case catalogue', 'url': BASE, 'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(products), 'itemListElement': [{'@type': 'ListItem', 'position': n, 'url': BASE + 'cases/' + p['id'] + '/', 'name': p['brand'] + ' ' + p['name']} for n, p in enumerate(products, 1)]}}]
    home = inject_cards((web / 'index.html').read_text(encoding='utf-8'), ''.join(card(p,n == 0) for n,p in enumerate(sorted(products,key=lambda p:(p['brand'].lower(),p['name'].lower())))))
    home = home.replace('<p id="result-count" role="status" aria-live="polite"></p>', f'<p id="result-count" role="status" aria-live="polite">{len(products)} of {len(products)} cases</p>')
    home = home.replace('<div id="presets"></div>', '<div id="presets">' + ''.join(f'<button data-preset="{n}">{esc(label)}</button>' for n,label in enumerate(['Slim & light','Hinge covered','With a stand','Leather & folio','Under £50'])) + '</div>')
    home = home.replace('<span id="snapshot" class="muted"></span>', '<span id="snapshot" class="muted">Sources checked: ' + datetime.strptime(catalogue['meta']['checkedAt'],'%Y-%m-%d').strftime('%d %b %Y').lstrip('0') + '</span>')
    home = home.replace('</head>', '<link rel="apple-touch-icon" href="assets/icon-180.png"><meta name="color-scheme" content="light dark">' + '</head>')
    first_product=sorted(products,key=lambda p:(p['brand'].lower(),p['name'].lower()))[0]
    first_image=first_product.get('thumbnail') or safe_url(first_product.get('image'))
    home=home.replace('<link rel="stylesheet"', '<link rel="preload" as="image" href="'+esc(first_image)+'" fetchpriority="high" referrerpolicy="no-referrer"><link rel="stylesheet"', 1)
    home = replace_head(home, metadata('Compare iPhone Duo cases | CASEBOOK', f'Compare {len(products)} iPhone Duo cases. Browse photos, check prices and coverage, and shortlist cases by published features. Sources checked {catalogue["meta"]["checkedAt"]}.', '', root_schema, BASE+'assets/share-card.png'))
    # Parent may have already authored these includes; append only missing assets.
    if ads_assets(output, ''):
        for tag in re.findall(r'<link[^>]+>|<script.*?</script>', ads_assets(output, '')):
            filename = re.search(r'(?:href|src)="([^"]+)"', tag)[1]
            if not re.search(r'(?:href|src)=["\']' + re.escape(filename) + r'["\']', home):
                home = home.replace('</head>', tag + '</head>')
    (output / 'index.html').write_text(home, encoding='utf-8')
    for p in products:
        path = 'cases/' + p['id'] + '/'
        name = p['brand'] + ' ' + p['name']
        schema = [{'@type': 'Product', 'name': name, 'description': p.get('summary', ''), 'image': safe_url(p.get('image')), 'brand': {'@type': 'Brand', 'name': p['brand']}, 'url': BASE + path, 'material': ', '.join(p.get('materials', []))}, breadcrumbs(path, name)]
        content = page(name + ' · iPhone Duo case · CASEBOOK', name + ': ' + p.get('summary', '') + ' Source-linked specifications and limitations.', path, case_body(p, brands.get(p['brand'], {})), schema, output, p.get('image'))
        destination = output / path / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
        routes.append(path)
    for path, title, description, body in editorial_pages():
        schema = [{'@type': 'WebPage', 'name': title, 'url': BASE + path, 'publisher': {'@type': 'Organization', 'name': 'CASEBOOK'}}, breadcrumbs(path, title)]
        destination = output / path / 'index.html'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page(title + ' · CASEBOOK', description, path, body, schema, output, image=BASE+'assets/share-card.png', ads=path.startswith('guides/')), encoding='utf-8')
        routes.append(path)
    (output / '404.html').write_text(page('Page not found · CASEBOOK', 'This CASEBOOK page could not be found. Browse the case catalogue.', '404.html', f'<h1>Page not found</h1><p>The link may be old or incomplete.</p><p><a href="{BASE}">Browse the case catalogue</a></p>', [], output, noindex=True), encoding='utf-8')
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.Element('{' + namespace + '}urlset')
    for route in routes:
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = BASE + route
        filename = route + 'index.html'
        content = (output / filename).read_bytes()
        unchanged = old_hashes.get(filename) == hashlib.sha256(content).hexdigest() if filename in old_hashes else old_pages.get(filename) == content
        ET.SubElement(entry, 'lastmod').text = old_dates.get(BASE + route, modified_at) if unchanged else modified_at
    ET.ElementTree(sitemap).write(output / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (output / 'robots.txt').write_text('# Project-path artifact only. Crawlers consult origin /robots.txt.\n# This file does not control olly-j.github.io.\nUser-agent: *\nAllow: /duo-casebook/\nSitemap: ' + BASE + 'sitemap.xml\n', encoding='utf-8')
    write_manifest(output)
    return {'products': len(products), 'indexablePages': len(routes)}


def editorial_pages():
    guide = f'''<p class="eyebrow">Buying guide</p><h1>Choose coverage before comparing price or weight</h1><p class="reading-lead">Start with the parts of the phone you want covered. Then compare materials, measurements and delivery terms within that group.</p>
<h2>Front, back and hinge are separate choices</h2><p>A front frame protects a different area from a back shell. A low price or weight for one component does not describe a complete set. A two-part case can cover front and back while leaving the hinge exposed.</p><p>A flexible hinge film is not a structural hinge cover. Check the recorded hinge field and the source photographs. A folio flap also needs its own coverage check; its name alone does not establish protection around every edge.</p><p><a href="{BASE}?coverage=front-and-back">Browse front-and-back cases</a> · <a href="{BASE}?coverage=front-only">See front-only components</a> · <a href="{BASE}?hinge=1">Find source-listed hinge covers</a></p>
<h2>Read the material, then the construction</h2><p>Aramid fibre is a material description, not a drop-test result. A thin aramid back can leave the front and hinge uncovered. Compare the complete assembly, including frames, glass and any separate parts.</p><p>TPU and polycarbonate describe different plastics used in flexible sections and rigid shells. Neither label establishes corner protection, long-term discolouration or survival in a fall. Source-published drop claims do not form a comparable laboratory ranking.</p><p>Leather, synthetic leather and technical fabric are separate materials. A leather-like product name can describe a synthetic finish. Read material notes and limitations before choosing by feel or appearance. Previous-model wear evidence applies only to the named material and model tested.</p><p><a href="{BASE}?q=aramid">Browse aramid records</a> · <a href="{BASE}?q=TPU">Browse TPU records</a> · <a href="{BASE}?q=leather">Read leather and synthetic-leather records</a></p>
<h2>Keep measurements in context</h2><p>Case weight is not package weight or magnetic holding force. Wall thickness is not the depth of a closed phone with its case fitted. A front-only component cannot be compared fairly with a full set on weight alone.</p><p>Unknown measurements stay unknown. They are not zero and cannot prove that a case is lighter or thinner. Read the measurement notes for tolerances, selected variants and what was actually measured.</p><p><a href="{BASE}?sort=weight">Compare published case weights</a> · <a href="{BASE}?sort=depth">Compare published closed depths</a></p>
<h2>Check price and UK delivery separately</h2><p>Prices retain the seller’s currency. A USD price and a GBP price are not directly comparable numbers. A UK listing does not establish live stock, UK delivery, tax, import duty or a final delivered total.</p><p>Preorders, coming-soon pages and source-published concepts have different purchase implications. Read the dated status and dispatch note, then confirm the selected colour and model at the seller before paying.</p>
<h2>Use sorting as a shortlist tool</h2><p>Preference matching uses published attributes. It is not an independent quality score or a product endorsement. Historical brand reviews offer context for the exact older case tested; they do not demonstrate Duo performance.</p><p>Choose two to four cases with comparable coverage in the catalogue. Check their limitations, colour options, source dates and seller pages together. If a missing dimension matters to your pocket or grip, ask the seller rather than estimating from a photograph.</p><p><a href="{BASE}">Build your shortlist</a> · <a href="{BASE}about/">How CASEBOOK handles evidence</a></p><aside data-ad-placement="article" hidden aria-label="Advertisement"></aside>'''
    about = f'''<h1>About CASEBOOK</h1><p class="reading-lead">CASEBOOK is a source-led iPhone Duo case catalogue published as CASEBOOK and maintained by <a href="https://github.com/olly-j">olly-j</a>.</p><h2>How the catalogue is made</h2><p>AI-assisted research brings together publicly available manufacturer pages, retailer listings, announcements and clearly identified previous-model review evidence. Each case links to its product sources and records the research date. Source-published photographs or renders retain their attribution and any representation caveats.</p><p>CASEBOOK has not independently handled or drop-tested these Duo cases. Manufacturer descriptions are claims by those sources. Previous-model reviews remain tied to the exact model tested. The catalogue assigns no numeric brand rating or product review score.</p><h2>What the records mean</h2><p>Unknown facts remain unknown. Price currencies are preserved. Listing status reflects the checked page, not live inventory. Shipping, warranty and return terms can depend on the seller and selected variant. Confirm them before buying.</p><p>Decorative variants may be grouped when they share a design. Unnamed future lineups without verifiable case visuals belong in the coverage registry, rather than the product grid. Public discovery cannot guarantee every seller or unannounced product. No automatic monitoring is running.</p><h2>Corrections and transparency</h2><p><a href="{REPO}/issues/new">Report a correction through GitHub Issues</a>. Include the case name, source URL and the fact that needs checking. Avoid including personal order details in a public issue.</p><p>CASEBOOK is an independent catalogue with no affiliation to Apple or the case manufacturers. Source code and research records are available in the <a href="{REPO}">project repository</a>. Advertising is currently off; any future activation requires publisher setup and certified consent configuration. <a href="{BASE}privacy/">Read the privacy information</a>.</p>'''
    privacy = f'''<h1>Privacy</h1><p class="reading-lead">CASEBOOK has no account system or analytics. Your saved cases stay in your browser.</p><h2>Saved cases and shared links</h2><p>The shortlist uses browser-local storage. Remove saved cases in the catalogue, or clear this site’s data in your browser to erase it. Storage belongs to this browser and is not an account or a synchronised backup.</p><p>Shared URLs can contain selected filters, a case ID or comparison IDs. Anyone receiving the link can read those selections. Avoid adding private information to shared URLs.</p><h2>Hosting and source images</h2><p>GitHub Pages hosts this site. Visiting it makes normal web requests to GitHub’s hosting infrastructure. Optimised catalogue images are served by this site. Full-size gallery images may be fetched from their recorded external hosts, which receive image requests and network information such as your IP address. Following a seller link opens that seller’s service under its own policies.</p><p><a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub privacy statement</a></p><h2>Advertising is currently off</h2><p>Optional Google AdSense is not active. It may be activated only after real publisher and ad-unit setup, site approval and certified consent-management configuration are verified. Required consent must be established before ad requests. Browsing the catalogue does not give consent to advertising.</p><p>If advertising is activated, this notice must be updated to describe the actual configuration and consent controls. <a href="{REPO}/issues/new">Raise a privacy question through the public repository</a>; do not post sensitive personal data.</p>'''
    return [('guides/choose-a-case/', 'How to choose an iPhone Duo case', 'Compare coverage, materials, case weight and delivery terms before shortlisting an iPhone Duo case.', guide), ('about/', 'About CASEBOOK and its research method', 'Who publishes CASEBOOK, how AI-assisted source research is recorded, and how to suggest corrections.', about), ('privacy/', 'Privacy and browser-local saved cases', 'How CASEBOOK handles browser-local favourites, shared selections, external images, hosting and inactive advertising.', privacy)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, help='Deployment directory; defaults to ROOT/docs')
    args = parser.parse_args()
    print(json.dumps(build_discovery(args.root, args.output or args.root / 'docs'), sort_keys=True))


if __name__ == '__main__':
    main()
