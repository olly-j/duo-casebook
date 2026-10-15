#!/usr/bin/env python3
"""Verify the public CASEBOOK identity and exact deployed catalogue."""
from __future__ import annotations
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fetch(url:str)->bytes:
    req=urllib.request.Request(url,headers={'User-Agent':'CASEBOOK deployment verifier'})
    with urllib.request.urlopen(req,timeout=30) as response:
        if response.status!=200:raise RuntimeError(f'{url}: HTTP {response.status}')
        return response.read()
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='https://olly-j.github.io/duo-casebook/');ap.add_argument('--allow-stale',action='store_true');args=ap.parse_args();base=args.url.rstrip('/')+'/'
    remote_html=fetch(base+'index.html').decode('utf-8');remote_catalogue=fetch(base+'catalogue.json');local=(ROOT/'docs/catalogue.json').read_bytes()
    identity='CASEBOOK' in remote_html and 'iPhone Duo' in remote_html
    exact=hashlib.sha256(remote_catalogue).digest()==hashlib.sha256(local).digest()
    data=json.loads(remote_catalogue);complete=all(p.get('image') and p.get('imageCaption') and p.get('imageSource') for p in data.get('products',[]))
    report={'url':base,'identity':identity,'exactCatalogueRevision':exact,'records':len(data.get('products',[])),'completeImageProvenance':complete}
    print(json.dumps(report,indent=2))
    if args.allow_stale:return 0 if identity else 1
    if not identity or not complete:return 1
    if not exact:return 1
    return 0
if __name__=='__main__':sys.exit(main())
