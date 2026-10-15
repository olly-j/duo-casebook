"""Copy only the approved static site assets into the Pages publishing directory."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
files=['index.html','styles.css','app.js','data.js','catalogue.json','icon.svg','manifest.webmanifest']
out=ROOT/'docs'
out.mkdir(exist_ok=True)
for name in files:
    source=ROOT/'web'/name
    if not source.is_file():
        raise FileNotFoundError(source)
    shutil.copy2(source,out/name)
(out/'.nojekyll').write_text('')
print('Prepared',len(files),'static assets; no fixtures, logs or private files included.')
