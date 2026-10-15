#!/usr/bin/env python3
"""Read-only exact-file verification of the public CASEBOOK release."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, sys, urllib.error, urllib.request
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
BASE='https://olly-j.github.io/duo-casebook/'
def digest(body):return hashlib.sha256(body).hexdigest()
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'CASEBOOK release verifier','Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=30) as response:
        if response.status!=200:raise RuntimeError('Unexpected HTTP status')
        return response.read()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default=BASE);parser.add_argument('--allow-stale',action='store_true')
    parser.add_argument('--all-files',action='store_true');parser.add_argument('--report')
    args=parser.parse_args();base=args.url.rstrip('/')+'/'
    report={'url':base,'identity':False,'exactCatalogueRevision':False,'exactReleaseManifest':False,'filesVerified':0,'failures':[]}
    try:
        html=fetch(base).decode('utf-8');remote=fetch(base+'catalogue.json');data=json.loads(remote)
        report.update(identity='CASEBOOK' in html and 'iPhone Duo' in html,exactCatalogueRevision=digest(remote)==digest((ROOT/'docs/catalogue.json').read_bytes()),records=len(data.get('products',[])),completeImageProvenance=all(p.get('image') and p.get('imageSource') and p.get('imageCaption') for p in data.get('products',[])))
        try:
            remote_manifest=fetch(base+'build-manifest.json');expected=json.loads((ROOT/'docs/build-manifest.json').read_text())
            report['exactReleaseManifest']=digest(remote_manifest)==digest((ROOT/'docs/build-manifest.json').read_bytes())
        except (urllib.error.HTTPError,FileNotFoundError):expected={'files':{}}
        if args.all_files and report['exactReleaseManifest']:
            def check(item):
                name,wanted=item
                if name.startswith('/') or '..' in Path(name).parts:return name,'unsafe manifest path'
                try:return name,None if digest(fetch(base+quote(name,safe='/')))==wanted else 'content mismatch'
                except Exception as error:return name,type(error).__name__
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                for name,error in pool.map(check,expected['files'].items()):
                    if error:report['failures'].append({'path':name,'reason':error})
                    else:report['filesVerified']+=1
        report['status']='verified' if report['identity'] and report['exactCatalogueRevision'] and report['exactReleaseManifest'] and not report['failures'] else 'not-current'
    except Exception as error:
        report['failures'].append({'reason':type(error).__name__});report['status']='unverified'
    print(json.dumps(report,indent=2))
    if args.report:
        destination=(ROOT/args.report).resolve()
        if not destination.is_relative_to(ROOT):raise ValueError('Report must be inside project')
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(report,indent=2)+'\n')
    return 0 if (report['identity'] if args.allow_stale else report['status']=='verified') else 1
if __name__=='__main__':sys.exit(main())
