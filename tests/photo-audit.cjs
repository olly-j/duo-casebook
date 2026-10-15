const fs=require('node:fs');const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const b=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  const p=await b.newPage({viewport:{width:1200,height:1000}});const data=JSON.parse(fs.readFileSync('web/catalogue.json'));const esc=x=>String(x||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  fs.mkdirSync('tests/screenshots',{recursive:true});
  const all=[];for(let start=0;start<data.products.length;start+=20){const slice=data.products.slice(start,start+20);const html='<style>body{margin:0;background:#fff;font:13px system-ui}.grid{display:grid;grid-template-columns:repeat(5,1fr)}article{height:244px;padding:10px;box-sizing:border-box;border:1px solid #ddd}img{width:100%;height:177px;object-fit:contain}p{margin:2px 0}small{font-size:11px}</style><div class="grid">'+slice.map(x=>'<article data-id="'+esc(x.id)+'">'+(x.image?'<img src="'+esc(x.image)+'" referrerpolicy="no-referrer">':'<div style="height:177px">No source image</div>')+'<p>'+esc(x.brand)+'</p><small>'+esc(x.name)+'</small></article>').join('')+'</div>';
   await p.setContent(html,{waitUntil:'domcontentloaded'});await p.evaluate(async()=>Promise.race([Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r}))),new Promise(r=>setTimeout(r,18000))]));
   all.push(...await p.locator('article').evaluateAll(xs=>xs.map(x=>{const i=x.querySelector('img');return{id:x.dataset.id,url:i?.src||null,loaded:!!(i&&i.complete&&i.naturalWidth),width:i?.naturalWidth||0,height:i?.naturalHeight||0}})));
   await p.screenshot({path:'tests/screenshots/photo-audit-'+Math.floor(start/20)+'.png',fullPage:true});
  }
  const report={checkedAt:data.meta?.checkedAt||null,total:all.length,loaded:all.filter(x=>x.loaded).length,missing:all.filter(x=>!x.url),broken:all.filter(x=>x.url&&!x.loaded),images:all};fs.writeFileSync('tests/photo-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({total:report.total,loaded:report.loaded,missing:report.missing.length,broken:report.broken},null,2));
 }finally{await b.close()}
})().catch(e=>{console.error(e);process.exit(1)});
