"""Prepare the reviewed public assets and source-backed discovery pages."""
from pathlib import Path
import shutil
from scripts.build_discovery import build_discovery
ROOT = Path(__file__).resolve().parent
PUBLIC = ['index.html','styles.css','app.js','data.js','catalogue.json','icon.svg',
          'manifest.webmanifest','reading.css','reading.js','ads-config.js','ads.js',
          'ads.css','ads-boot.js','privacy-center.js','privacy-center.css','google-cmp-provider.js','google-cmp-boot.js', 'liquid-ui.js']
out = ROOT / 'docs'
out.mkdir(exist_ok=True)
for name in PUBLIC:
    source = ROOT / 'web' / name
    if source.is_symlink() or not source.is_file():
        raise ValueError('Missing or unsafe public asset: ' + name)
    shutil.copy2(source, out / name)
assets = ROOT / 'web/assets'
for source in sorted(assets.rglob('*')):
    if source.is_symlink():
        raise ValueError('Symlink public asset')
    if source.is_file():
        if source.suffix.lower() not in {'.png','.svg','.webp','.jpg','.jpeg','.ico'}:
            raise ValueError('Unreviewed asset type: ' + source.name)
        target = out / 'assets' / source.relative_to(assets)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
# Pin the verified MIT source locally; it is requested only by eligible desktop UI.
vendor = ROOT / 'web/vendor'
for name in ('liquidGL.js','LICENSE.txt'):
    source = vendor / name
    if source.is_symlink() or not source.is_file():
        raise ValueError('Missing or unsafe pinned liquidGL asset: ' + name)
    (out / 'vendor').mkdir(exist_ok=True)
    shutil.copy2(source, out / 'vendor' / name)
(out / '.nojekyll').write_text('')
print(build_discovery(ROOT, out))
