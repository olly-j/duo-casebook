#!/usr/bin/env python3
"""Read-only CASEBOOK contract, catalogue and publication audit."""
from __future__ import annotations
import argparse,json,re,subprocess,sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['AGENTS.md','.spine/manifest.json','docs/README.md','docs/product-backlog.md','docs/user-feedback.md','docs/change-management.md','docs/project-profile.md','docs/human-behaviour-ux.md','docs/tooling.md','docs/github-capabilities.md','docs/release-management.md','web/catalogue.json','web/data.js','docs/catalogue.json','docs/data.js']
SECRET=re.compile(r'(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
def safe_image(value:str)->bool:
    if value.startswith('assets/cases/') and '..' not in value:return True
    try:return urlparse(value).scheme=='https' and bool(urlparse(value).netloc)
    except:return False
def fail(errors:list[str],message:str):errors.append(message)
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['audit','release'],default='audit');args=ap.parse_args();errors=[]
    for rel in REQUIRED:
        if not (ROOT/rel).is_file():fail(errors,f'missing authority or artifact: {rel}')
    if errors:
        print('\n'.join('ERROR '+x for x in errors));return 1
    manifest=json.loads((ROOT/'.spine/manifest.json').read_text())
    if manifest.get('schemaVersion')!=1:fail(errors,'manifest schemaVersion must be 1')
    if manifest.get('project',{}).get('profile')!=['core','web-backend']:fail(errors,'profiles must be core + web-backend')
    if manifest.get('project',{}).get('github')!='olly-j/duo-casebook':fail(errors,'manifest repository mismatch')
    data=json.loads((ROOT/'web/catalogue.json').read_text());products=data.get('products',[]);ids=[str(p.get('id','')) for p in products]
    if len(ids)!=len(set(ids)):fail(errors,'duplicate product ids')
    if not products:fail(errors,'empty catalogue')
    for p in products:
        label=f"{p.get('brand')} {p.get('name')} ({p.get('id')})"
        if not p.get('sources') or not p.get('url'):fail(errors,f'{label}: missing source')
        if not p.get('image'):fail(errors,f'{label}: missing primary image')
        if not p.get('imageCaption') or not p.get('imageSource'):fail(errors,f'{label}: missing image provenance')
        if p.get('image') and not safe_image(p['image']):fail(errors,f'{label}: unsafe image URL')
        if p.get('imageSource') and urlparse(p['imageSource']).scheme!='https':fail(errors,f'{label}: image source must be HTTPS')
        gallery=p.get('images') or []
        if not gallery:fail(errors,f'{label}: empty image gallery')
        for image in gallery:
            if not safe_image(str(image.get('url',''))):fail(errors,f'{label}: unsafe gallery image')
            if not image.get('caption') or not image.get('sourceUrl'):fail(errors,f'{label}: incomplete gallery attribution')
        if re.search(r'placeholder|no-image',str(p.get('image')),re.I):fail(errors,f'{label}: placeholder image')
        if 'waitlist' in str(p.get('name','')).lower() or 'family unannounced' in str(p.get('name','')).lower():fail(errors,f'{label}: unnamed preview belongs in registry')
    if (ROOT/'web/catalogue.json').read_bytes()!=(ROOT/'docs/catalogue.json').read_bytes():fail(errors,'published catalogue is not prepared from web source')
    if (ROOT/'web/data.js').read_bytes()!=(ROOT/'docs/data.js').read_bytes():fail(errors,'published data.js is not prepared from web source')
    inventory=ROOT/'docs/build-manifest.json'
    if inventory.is_file():
        import hashlib
        for rel,digest in json.loads(inventory.read_text()).get('files',{}).items():
            path=(ROOT/'docs'/rel).resolve()
            if not path.is_relative_to((ROOT/'docs').resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest: fail(errors,f'deployment inventory mismatch: {rel}')
    summary=json.loads((ROOT/'research/catalogue-summary.json').read_text())
    if summary.get('records')!=len(products):fail(errors,'catalogue summary record count mismatch')
    if summary.get('images')!=len(products) or not summary.get('imageComplete'):fail(errors,'catalogue summary does not prove complete images')
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True).stdout.split(b'\0')
    for raw in tracked:
        if not raw:continue
        rel=raw.decode(errors='replace');path=ROOT/rel
        try:text=path.read_text()
        except (UnicodeDecodeError,IsADirectoryError):continue
        if SECRET.search(text):fail(errors,f'possible secret in {rel}')
        if ('/Users'+'/' in text) or ('/home'+'/' in text):fail(errors,f'private absolute path in {rel}')
    if args.mode=='release':
        try: date.fromisoformat(data['meta']['checkedAt'])
        except (KeyError, TypeError, ValueError): fail(errors,'research snapshot must use a valid ISO date')
        if not (ROOT/'QA.md').is_file():fail(errors,'QA.md required for release')
    if errors:
        print('\n'.join('ERROR '+x for x in errors));return 1
    print(json.dumps({'mode':args.mode,'records':len(products),'brands':len({p.get('brand') for p in products}),'images':sum(bool(p.get('image')) for p in products),'galleryImages':sum(len(p.get('images') or []) for p in products),'status':'pass'},indent=2));return 0
if __name__=='__main__':sys.exit(main())
