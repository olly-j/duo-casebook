#!/usr/bin/env python3
"""Locate existing Playwright tooling and run CASEBOOK browser evidence."""
from __future__ import annotations
import argparse,glob,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def first(paths):
    for value in paths:
        if value and Path(value).exists():return str(Path(value))
    return None
def main()->int:
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--functional',action='store_true');g.add_argument('--all',action='store_true');ap.add_argument('--url');args=ap.parse_args()
    home=Path.home();module=first([os.getenv('PLAYWRIGHT_MODULE'),ROOT/'node_modules/playwright',*glob.glob(str(home/'.npm/_npx/*/node_modules/playwright'))])
    chrome=first([os.getenv('CHROME_PATH'),*glob.glob(str(home/'Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')), *glob.glob(str(home/'.cache/ms-playwright/chromium-*/chrome-linux/chrome'))])
    if not module or not chrome:
        print('Playwright module or cached Chromium not found. Set PLAYWRIGHT_MODULE and CHROME_PATH.',file=sys.stderr);return 2
    env=os.environ.copy();env.update(PLAYWRIGHT_MODULE=module,CHROME_PATH=chrome)
    if args.url:env['CASEBOOK_TEST_URL']=args.url
    axe=first([os.getenv('AXE_PATH'),*glob.glob(str(home/'.npm/_npx/*/node_modules/axe-core/axe.min.js'))])
    if axe:env['AXE_PATH']=axe
    scripts=['tests/browser-functional.cjs']
    if args.all:scripts+=['tests/browser-smoke.cjs','tests/photo-audit.cjs','tests/launch-browser.cjs']
    for script in scripts:
        print('+ node',script,flush=True);result=subprocess.run(['node',script],cwd=ROOT,env=env)
        if result.returncode:return result.returncode
    return 0
if __name__=='__main__':sys.exit(main())
