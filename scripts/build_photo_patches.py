"""Build reviewed photo patches from exact product-page browser evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
raw={x['id']:x for x in json.loads((ROOT/'research/image-candidates.json').read_text())['targets']}
patches=[]
def add(pid, urls, caption, source, note):
    images=[{'url':u,'caption':caption if i==0 else f'{caption} View {i+1}.','sourceUrl':source} for i,u in enumerate(urls)]
    patches.append({'id':pid,'image':urls[0],'images':images,'imageSource':source,'imageCaption':caption,'verificationNote':note})
def product(pid,count,caption,note=None):
    urls=[]
    for x in raw[pid]['candidates']:
        if x.get('kind')=='product-json' and x['url'] not in urls: urls.append(x['url'])
    if not urls: raise ValueError(f'No product JSON images for {pid}')
    add(pid,urls[:count],caption,raw[pid]['source'],note or 'Exact current product page and public product JSON; visually inspected in the CASEBOOK contact sheet.')
def exact_alt(pid,count,caption):
    xs=[]
    for x in raw[pid]['candidates']:
        if (x.get('width') or 0)>=470 and (x.get('height') or 0)>=470 and pid.split('-for-')[0].split('-',1)[-1].split('-with-')[0].replace('-',' ')[:8].lower() in (x.get('alt') or '').lower(): xs.append(x)
    xs=sorted(xs,key=lambda x:((x.get('width') or 0)*(x.get('height') or 0)),reverse=True)
    if not xs: xs=sorted([x for x in raw[pid]['candidates'] if (x.get('width') or 0)>=470 and (x.get('height') or 0)>=470],key=lambda x:(x.get('width') or 0)*(x.get('height') or 0),reverse=True)
    add(pid,[x['url'] for x in xs[:count]],caption,raw[pid]['source'],'Exact current manufacturer page, matching alt text and visually inspected product configuration.')
for pid,caption in [
 ('ringke-fusion-for-iphone-duo','Ringke Fusion for iPhone Duo, clear'),
 ('ringke-fusion-hinge-film-2p-for-iphone-duo','Ringke Fusion with two hinge films; case and included film shown'),
 ('ringke-fusion-magnetic-for-iphone-duo','Ringke Fusion Magnetic for iPhone Duo, clear'),
 ('ringke-fusion-magnetic-hinge-film-2p-for-iphone-duo','Ringke Fusion Magnetic with two hinge films; case and included film shown'),
 ('incipio-survivor-clear-for-magsafe-for-iphone-duo','Incipio Survivor Clear for MagSafe for iPhone Duo')]: product(pid,3,caption)
for pid,caption in [
 ('jetech-clear-case-with-hinge-protection-for-iphone-duo','JETech Clear Case with Hinge Protection'),
 ('jetech-vegan-leather-case-with-hinge-protection-for-iphone-duo','JETech Vegan Leather Case with Hinge Protection'),
 ('jetech-matte-case-with-hinge-protection-for-iphone-duo','JETech Matte Case with Hinge Protection')]: exact_alt(pid,3,caption)
for pid,caption in [
 ('vaja-folio-leather-case-with-magsafe-for-iphone-duo','Vaja Folio Leather Case with MagSafe, Floater Latte'),
 ('vaja-wallet-leather-case-with-magsafe-for-iphone-duo','Vaja Wallet Leather Case with MagSafe, Floater Latte'),
 ('vaja-leather-folio-wrap-with-aramid-shell-for-iphone-duo','Vaja Leather Folio Wrap with Aramid Shell'),
 ('vaja-leather-wallet-wrap-with-aramid-shell-for-iphone-duo','Vaja Leather Wallet Wrap with Aramid Shell'),
 ('torro-wallet','TORRO Leather Wallet Case for iPhone Duo'),
 ('torro-detachable-wallet','TORRO 2-in-1 Detachable Leather Wallet Case for iPhone Duo'),
 ('torro-slim-folio-stand','TORRO Slim Leather Folio with Rotating Stand for iPhone Duo'),
 ('torro-slim-folio','TORRO Slim Leather Folio for iPhone Duo')]: product(pid,3,caption,'Exact current Duo product page and product JSON; visual form/configuration inspected. Publisher asset filenames retain its earlier Ultra codename.')
product('elago-magsafe-hybrid-clear-case-for-iphone-duo',3,'Elago MagSafe Hybrid Clear Case for iPhone Duo')
# Elago silicone exposes the exact current product through page metadata rather than the JSON image list.
elago=[x['url'] for x in raw['elago-magsafe-silicone-case-for-iphone-duo']['candidates'] if 'SFOLD-MSSC' in x['url'] and x['url'].startswith('https://') and 'airpods' not in x['url'].lower()]
add('elago-magsafe-silicone-case-for-iphone-duo',list(dict.fromkeys(elago))[:3],'Elago MagSafe Silicone Case for iPhone Duo','https://www.elago.com/products/magsafe-silicone-case-7-colors-ultra','Exact current product metadata and visually inspected Duo form. Publisher page title retains an older model string.')
add('cygnett-aeroshield-clear-for-iphone-duo',['https://www.cygnett.com/cdn/shop/files/CY6124CPAEG-1_429a9dfd-604c-4c3c-831f-1b37cc271091_1024x1024.png?v=1788927363'],'Cygnett AeroShield Slim Clear Case for iPhone Duo','https://www.cygnett.com/products/aeroshield-slim-clear-case-for-iphone-foldable','Exact official SKU CY6124CPAEG image and Duo product result; visually inspected.')
add('burga-elite',['https://cdn.burga.photos/_variants/767/Storefront/Phone%20Case/HG_01EL_IP18PROFOLD_EL-dark-gold-magsafe/1__device-color=star%20white.webp','https://cdn.burga.photos/_variants/767/Storefront/Phone%20Case/HG_02EL_IP18PROFOLD_EL-dark-gold-magsafe/1__device-color=star%20white.webp'],'BURGA Elite Dark for iPhone Duo, Gold MagSafe','https://uk.burga.com/collections/iphone-duo-cases','Exact current iPhone Duo collection assets and foldable form visually inspected.')
add('qdos-duo-coming-soon',['https://www.qdossound.com/cdn/shop/files/QDOS_iPhone_Duo_HYBRIDSNAP_Clear_ProductImage_HR_4.png?v=1789386210&width=3840','https://www.qdossound.com/cdn/shop/files/QDOS_iPhone_Duo_HYBRIDSNAP_Clear_ProductImage_HR_7.png?v=1789386209&width=3840','https://www.qdossound.com/cdn/shop/files/QDOS_iPhone_Duo_HYBRIDSNAP_Clear_ProductImage_HR_8.png?v=1789386209&width=3840'],'QDOS Hybrid SNAP Case for iPhone Duo, Clear','https://www.qdossound.com/products/iphone-duo-hybrid-snap-magsafe-case-clear','Exact current product gallery, product code QDG-MS18U33-CL; visually inspected.')
(ROOT/'research/photos-parent.json').write_text(json.dumps({'checkedAt':'2026-10-15','patches':patches},indent=2)+'\n')
print(f'Wrote {len(patches)} reviewed parent patches')
