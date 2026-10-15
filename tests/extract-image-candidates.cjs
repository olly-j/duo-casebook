const fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const data=JSON.parse(fs.readFileSync('web/catalogue.json','utf8'));
const targets=data.products.filter(p=>!p.image);
const clean=(v,base)=>{try{if(!v)return null;const u=new URL(String(v).replace(/&amp;/g,'&'),base);return /^https?:$/.test(u.protocol)?u.href:null}catch{return null}};
(async()=>{
 const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const out=[];
 for(const p of targets){
  const page=await browser.newPage({viewport:{width:1280,height:900}});const responses=[];
  page.on('response',r=>{const t=r.headers()['content-type']||'';if(t.startsWith('image/'))responses.push(r.url())});
  try{
   const response=await page.goto(p.url,{waitUntil:'domcontentloaded',timeout:25000});await page.waitForTimeout(1200);
   const facts=await page.evaluate(async()=>{
    const metas=[...document.querySelectorAll('meta[property="og:image"],meta[name="twitter:image"],meta[property="og:image:secure_url"]')].map(x=>({url:x.content,kind:x.getAttribute('property')||x.name}));
    const imgs=[...document.images].map(i=>({url:i.currentSrc||i.src||i.dataset.src||i.dataset.original,alt:i.alt||'',width:i.naturalWidth||i.width,height:i.naturalHeight||i.height}));
    const json=[];for(const s of document.querySelectorAll('script[type="application/ld+json"]')){try{const value=JSON.parse(s.textContent);for(const x of (Array.isArray(value)?value:[value])){if(x?.image)json.push(...(Array.isArray(x.image)?x.image:[x.image]).map(v=>({url:typeof v==='string'?v:v?.url,kind:'jsonld'})));}}catch{}}
    let product=null;try{const r=await fetch(location.pathname.replace(/\/$/,'')+'.js',{credentials:'omit'});if(r.ok){const j=await r.json();product={title:j.title,featured_image:j.featured_image,images:j.images,media:j.media};}}catch{}
    return {title:document.title,url:location.href,metas,imgs,json,product};
   });
   const candidates=[];for(const x of [...facts.metas,...facts.imgs,...facts.json]){const u=clean(x.url,facts.url);if(u)candidates.push({...x,url:u})}
   if(facts.product){for(const x of [facts.product.featured_image,...(facts.product.images||[])]){const u=clean(typeof x==='string'?x:x?.src,facts.url);if(u)candidates.push({url:u,kind:'product-json',alt:facts.product.title||''})}}
   for(const u of responses.slice(0,300))candidates.push({url:u,kind:'network'});
   const dedup=[];const seen=new Set();for(const x of candidates){if(!seen.has(x.url)){seen.add(x.url);dedup.push(x)}}
   out.push({id:p.id,brand:p.brand,name:p.name,source:p.url,status:response?.status(),pageTitle:facts.title,finalURL:facts.url,productTitle:facts.product?.title||null,candidates:dedup.slice(0,500)});
   console.log(p.id,response?.status(),dedup.length,facts.product?.title||facts.title);
  }catch(e){out.push({id:p.id,brand:p.brand,name:p.name,source:p.url,error:e.message,candidates:[]});console.log(p.id,'ERROR',e.message)}finally{await page.close()}
 }
 fs.writeFileSync('research/image-candidates.json',JSON.stringify({checkedAt:'2026-10-15',targets:out},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
