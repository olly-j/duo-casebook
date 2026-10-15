const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'); const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const url=process.env.CASEBOOK_TEST_URL||'file://'+path.resolve('web/index.html');
 const results=[],errors=[];fs.mkdirSync('tests/screenshots',{recursive:true});
 for(const width of [320,390,430,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push({width,message:e.message}));
  await page.goto(url,{waitUntil:'domcontentloaded'});await page.waitForTimeout(800);
  const info=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,cards:document.querySelectorAll('.card').length,products:window.CASEBOOK?.products.length,title:document.title}));
  await page.screenshot({path:'tests/screenshots/home-'+width+'.png'});
  await page.locator('#catalogue').scrollIntoViewIfNeeded();await page.waitForTimeout(300);
  await page.screenshot({path:'tests/screenshots/catalogue-'+width+'.png'});
  results.push(info);await page.close();
 }
 fs.writeFileSync('tests/browser-smoke.json',JSON.stringify({target:url.startsWith('file:')?'local static app':url,results,errors},null,2));
 console.log(JSON.stringify({results,errors},null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
