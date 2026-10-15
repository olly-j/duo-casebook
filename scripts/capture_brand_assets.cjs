/* Render original CASEBOOK identity assets with an existing local Chromium. No product imagery is generated. */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});try{
 const out=path.resolve('web/assets');fs.mkdirSync(out,{recursive:true});
 const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
 await page.setContent(`<!doctype html><html lang="en"><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;background:#f8f9f7;color:#20251f;font-family:system-ui,-apple-system,sans-serif}.frame{padding:68px 76px;height:630px;display:flex;flex-direction:column}.brand{font-size:27px;letter-spacing:.14em;font-weight:650}h1{font-size:80px;letter-spacing:-.055em;line-height:1.06;font-weight:650;margin:68px 0 22px;max-width:950px}p{font-size:27px;line-height:1.5;margin:0;color:#4e584c}.rule{margin-top:auto;border-top:1px solid #d6ddd2;padding-top:23px;font-size:22px;display:flex;justify-content:space-between}.mark{color:#48613c}</style><div class="frame"><div class="brand">CASEBOOK</div><h1>Compare iPhone Duo cases.</h1><p>See the photos. Check the details.<br>Choose what matters to you.</p><div class="rule"><span class="mark">Prices · Materials · Coverage</span><span>The iPhone Duo case finder</span></div></div></html>`);
 await page.screenshot({path:path.join(out,'share-card.png')});
 const svg=fs.readFileSync('web/icon.svg','utf8');
 for(const size of [180,192,512]){await page.setViewportSize({width:size,height:size});await page.setContent('<style>body{margin:0}svg{display:block;width:100vw;height:100vh}</style>'+svg);await page.screenshot({path:path.join(out,'icon-'+size+'.png')});}
 console.log('Rendered share-card.png (1200×630) and 180/192/512px original CASEBOOK icons.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
