"""Rebuild the public catalogue from dated source records, without fetching or inventing facts."""
import json,re,pathlib,copy
ROOT=pathlib.Path(__file__).resolve().parent
load=lambda n:json.loads((ROOT/'research'/n).read_text())
inputs=[load(n) for n in ['main-a.json','main-b.json','main-c.json','additional-cases.json','core-cases.json','final-sweep.json']]
brand_data=load('brand-evidence.json')['brands']
brand_map={b['brand']:b for b in brand_data}
patches=load('image-patches.json')['patches']
all_products=[]
nulls=['price','currency','ukListing','hinge','magsafe','stand','wallet','strap','weightG','thicknessMm','thicknessNote','dimensions','closedWidthMm','closedDepthMm','releaseDate','releaseNote','image','shippingNote']
valid_coverage={'front-and-back','back-only','front-only','folio','sleeve','unknown'}
def canonical_coverage(text):
 if text in valid_coverage:return text
 s=(text or '').lower()
 if 'sleeve' in s:return 'sleeve'
 if 'folio' in s or 'front cover and back' in s:return 'folio'
 if 'back-only' in s:return 'back-only'
 if any(t in s for t in ['front frame and back','front frame, back','front frame and rear','front bezel and back','back case and reinforced front','back case, reinforced front','front/back','both exterior panels','full-body coverage','separate front and rear']):return 'front-and-back'
 return 'unknown'
def mat(m):
 s=m.lower()
 if 'aramid' in s or 'kevlar' in s:return 'Aramid fibre'
 if 'pu leather' in s or 'synthetic leather' in s:return 'Synthetic leather'
 if 'leather' in s:return 'Leather'
 if 'polycarbonate' in s or s=='pc':return 'Polycarbonate'
 if 'silicone' in s:return 'Silicone'
 if 'microfibre' in s:return 'Microfibre'
 if 'tpu' in s:return 'TPU'
 if 'elastomer' in s or s=='tpe':return 'TPE'
 if 'tempered glass' in s:return 'Tempered glass'
 if 'aluminium' in s:return 'Aluminium'
 if 'steel' in s:return 'Steel'
 if 'metal' in s:return 'Metal'
 if 'plastic' in s:return 'Plastic'
 if 'resin' in s:return 'Resin'
 return m[0].upper()+m[1:]
for ds in inputs:
 for original in ds['products']:
  p=copy.deepcopy(original)
  original_name=p['name']; original_coverage=p.get('coverage')
  for k in nulls:p.setdefault(k,None)
  for k in ['materials','colours','limitations','sources','variants']:p[k]=p.get(k) or []
  p['id']=p.get('id') or re.sub('[^a-z0-9]+','-',p['brand'].lower()+'-'+original_name.lower()).strip('-')
  p['name']=re.sub(r'\s+for iPhone Duo\b|\biPhone Duo\s*','',p['name'],flags=re.I).strip(' ,')
  p['coverage']=canonical_coverage(original_coverage)
  if original_coverage and original_coverage not in valid_coverage:p['coverageNote']=original_coverage
  p['materialNotes']=p['materials'][:]
  p['materials']=list(dict.fromkeys(mat(m) for m in p['materials']))
  p['status']={'in-stock':'listed','out-of-stock':'sold-out'}.get(p.get('status'),p.get('status') or 'listed')
  p['evidence']=p.get('evidence') or ('retailer' if p['brand']=='Noreve' else 'official')
  p['brandEvidence']=brand_map.get(p['brand'],{}).get('evidenceLevel','not-established')
  p['checkedAt']='2026-10-15'
  if isinstance(p['ukListing'],str):p['ukListing']=True
  if p['currency']=='GBP' and any(s in p.get('url','') for s in ['.co.uk','uk.','/en-gb/']):p['ukListing']=True
  if not p['sources']:
   facts=[p.get('summary','')]
   if p['price'] is not None:facts.append(str(p['price'])+' '+p['currency']+' listed price.')
   facts += [p[k] for k in ['releaseNote','thicknessNote'] if p[k]]
   p['sources']=[dict(url=p['url'],title=p['brand']+': '+p['name'],type='manufacturer',facts=facts)]
  p['url']=p.get('url') or p['sources'][0]['url']
  p['summary']=p.get('summary') or 'Public product listing. Check source for the selected configuration.'
  for patch in patches:
   if patch['brand']==p['brand'] and patch['name']==original_name and not p['image']:
    p['image']=patch['image'];p['imageNote']='Manufacturer gallery and caption match; not independently photographed.'
  if p['brand']=='Ringke':
   p['strap']=True
   if 'Film' in p['name']:
    p['hinge']=False
    p['priceFrom']=True
    p['limitations'].insert(0,'Includes a flexible hinge film, not a structural hinge guard. Excluded from the protective hinge-cover filter.')
  if p['brand']=='Latercase':p['limitations'].append('The displayed review total pools other phone models. It is not a Duo review count.')
  if p['brand']=='Elago':
   p['thicknessNote']=next((x for x in p['limitations'] if 'mm is' in x),'Maker-listed rear-panel thickness, not closed-device depth.')
   if 'Silicone' in p['name']:
    p['colours']=['Stone','White','Light Blue','Lovely Pink','Burgundy','Jean Indigo','Black']
    p['limitations']=[x for x in p['limitations'] if 'Seven colours' not in x]
  if p['id']=='rokform-rugged':p['releaseDate']='2026-10-30'
  if p['brand']=='Snakehive':p['coverage']='folio'
  if p['brand'] in ['Vaja','BlackBrook','Snakehive'] and 'Wallet' in original_name:p['wallet']=True
  if p['brand']=='PITAKA' and p['coverage']=='front-only':p['limitations'].insert(0,'This is an accessory component, not a complete case. Compare coverage before price or weight.')
  if p['image']:p['limitations']=[x for x in p['limitations'] if 'product-image URL not recovered' not in x]
  if p['thicknessMm'] is not None and not p['thicknessNote']:p['thicknessNote']='Manufacturer-listed case profile; not total closed-device depth unless explicitly stated.'
  if p['price'] is not None and not p['currency']:raise ValueError('Price without currency: '+p['id'])
  all_products.append(p)
# Decorative finishes share one case entry, while functional stand versions remain separate.
floral=next(p for p in all_products if p['brand']=='Case-Mate' and p['name'].startswith('Floral Gems'))
twinkle=next(p for p in all_products if p['brand']=='Case-Mate' and p['name'].startswith('Sheer Twinkle'))
floral['name']='Decorative MagSafe';floral['colours']=['Floral Gems','Sheer Twinkle Silver']
floral['variants']=[dict(name=x['name'],price=x['price'],currency=x['currency'],url=x['url'],image=x['image']) for x in [floral,twinkle]]
floral['variants'][0]['name']='Floral Gems MagSafe'
floral['summary']='One folding case format with Floral Gems or Sheer Twinkle Silver decorative finishes.'
floral['limitations'].append('Select the named finish at the manufacturer. The shared source URL can open a different default variant.')
all_products.remove(twinkle)
assert len({p['id'] for p in all_products})==len(all_products)
for p in all_products:
 if p['id']=='thinborne-600d':p['sources'].append(dict(url='https://www.amazon.com/Thinborne-iPhone-Duo-Case-Unbelievably/dp/B0HKYGS4R4',title='Thinborne front-and-back listing',type='retailer',facts=['Title corroborates front-and-back configuration.']))
 if p['brand']=='Apple':p['sources'].append(dict(url='https://www.techradar.com/phones/phone-accessories/best-iphone-duo-cases',title='TechRadar: Apple colour options',type='announcement',facts=['Colour corroboration: '+', '.join(p['colours'])]))
registry={}
for ds in inputs:
 for c in ds.get('coverage',[])+ds.get('unverified',[]):registry[c['brand']]=c
for brand in sorted({p['brand'] for p in all_products}):
 if brand not in registry:
  ps=[p for p in all_products if p['brand']==brand]
  registry[brand]=dict(brand=brand,status='verified-with-gaps',note=str(len(ps))+' public case designs or configurations located. Unpublished measurements and availability gaps are retained in each product file.',sourceUrls=list(dict.fromkeys(p['url'] for p in ps)))
meta=dict(checkedAt='2026-10-15',device='iPhone Duo',deviceUrl='https://www.apple.com/uk/iphone-duo/',preorderDate='2026-10-16',releaseDate='2026-10-23',coverageNote='A dated index of publicly discoverable cases, configurations, waitlists and concepts. Decorative finishes are grouped where they share a design. Unannounced products, unindexed sellers and later changes cannot be guaranteed. The coverage registry records searched brands and gaps; no automated monitoring is running.')
data=dict(meta=meta,products=all_products,brands=brand_data,coverage=sorted(registry.values(),key=lambda x:x['brand'].lower()))
text=json.dumps(data,ensure_ascii=False,indent=2).replace('\u2014',', ')
(ROOT/'web'/'data.js').write_text('window.CASEBOOK = '+text+';\n')
(ROOT/'web'/'catalogue.json').write_text(text+'\n')
(ROOT/'research'/'catalogue-summary.json').write_text(json.dumps(dict(records=len(all_products),brands=len({p['brand'] for p in all_products}),registry=len(registry),images=sum(bool(p['image']) for p in all_products),weightPublished=sum(p['weightG'] is not None for p in all_products),pricePublished=sum(p['price'] is not None for p in all_products)),indent=2))
print((ROOT/'research'/'catalogue-summary.json').read_text())
