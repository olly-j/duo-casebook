/* CB-003: physical-like Chromium checks on the exact prepared tree. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const URLBASE='https://olly-j.github.io/duo-casebook/';
const ROOT=path.resolve('docs'),results=[],unwanted=[],errors=[];
async function contextFor(browser,viewport,colorScheme='light'){
 const ctx=await browser.newContext({viewport,colorScheme});
 await ctx.route('**/*',async route=>{
   const raw=route.request().url();
   if(raw.includes('googlesyndication.com')||raw.includes('fundingchoicesmessages.google.com')||raw.includes('doubleclick.net')||raw.includes('google-analytics.com')){
    unwanted.push(raw);return route.abort();
   }
   if(!process.env.CASEBOOK_TEST_URL && raw.startsWith(URLBASE)){
    const url=new URL(raw);let relative=decodeURIComponent(url.pathname.slice('/duo-casebook/'.length));
    let file=path.resolve(ROOT,relative||'index.html');
    if(!file.startsWith(ROOT+path.sep))return route.fulfill({status:400,body:'Invalid path'});
    if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
    if(!fs.existsSync(file))return route.fulfill({status:404,body:'Not found'});
    const type={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.webp':'image/webp','.json':'application/json','.svg':'image/svg+xml'}[path.extname(file)]||'text/plain';
    return route.fulfill({status:200,contentType:type,body:fs.readFileSync(file)});
   }
   return route.continue();
 });
 return ctx;
}
(async()=>{
 const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  const widths=[320,390,430];
  for(const width of widths)for(const theme of ['light','dark']){
   const ctx=await contextFor(browser,{width,height:844},theme);
   const page=await ctx.newPage();
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(URLBASE,{waitUntil:'domcontentloaded'});
   const trigger=page.locator('footer .privacy-center-trigger');
   assert.equal(await trigger.count(),1,'Privacy control must exist');
   assert.equal(await trigger.isVisible(),true,'Privacy control must be visible');
   await trigger.click();
   const dialog=page.locator('dialog.privacy-center');
   assert.equal(await dialog.isVisible(),true,'Native privacy dialog opens');
   const text=await dialog.innerText();
   assert.ok(text.includes('Optional advertising is off'));
   assert.equal(await dialog.locator('[data-privacy-ad]').isVisible(),false,'No phantom consent choice');
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow');
   if(width===390){fs.mkdirSync('tests/screenshots',{recursive:true});await page.screenshot({path:'tests/screenshots/privacy-'+theme+'-390.png'});}
   await page.keyboard.press('Escape');
   assert.equal(await dialog.isVisible(),false,'Escape closes privacy dialog');
   results.push({width,theme,dialog:true,escape:true,noPhantomConsent:true});
   await ctx.close();
  }
  const ctx=await contextFor(browser,{width:390,height:844});
  const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto(URLBASE,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{localStorage.setItem('casebook-saved',JSON.stringify(['apple-case']));localStorage.setItem('other-preferences-test','keep');});
  await page.locator('.privacy-center-trigger').click();
  await page.locator('[data-privacy-clear]').click();
  await page.locator('[data-privacy-keep]').click();
  assert.equal(await page.evaluate(()=>localStorage.getItem('casebook-saved')),'["apple-case"]','Cancel preserves saved cases');
  await page.locator('[data-privacy-clear]').click();
  await page.locator('[data-privacy-delete]').click();
  assert.equal(await page.evaluate(()=>localStorage.getItem('casebook-saved')),null,'Confirm clears saved cases');
  assert.equal(await page.evaluate(()=>localStorage.getItem('other-preferences-test')),'keep','Unrelated browser storage preserved');
  assert.equal(await page.locator('[data-privacy-status]').isVisible(),true,'Feedback shown');
  await page.locator('[data-privacy-close]').click();
  for(const pagePath of ['cases/apple-case/','guides/choose-a-case/','about/','privacy/']){
   await page.goto(URLBASE+pagePath,{waitUntil:'domcontentloaded'});
   assert.equal(await page.locator('footer .privacy-center-trigger').count(),1,'Privacy control on '+pagePath);
   await page.locator('footer .privacy-center-trigger').click();
   assert.equal(await page.locator('dialog.privacy-center').isVisible(),true,'Privacy dialog on '+pagePath);
   await page.locator('[data-privacy-close]').click();
  }
  if(process.env.AXE_PATH){
   await page.goto(URLBASE,{waitUntil:'domcontentloaded'});
   await page.locator('.privacy-center-trigger').click();
   await page.addScriptTag({path:process.env.AXE_PATH});
   const violations=await page.evaluate(async()=>{const result=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return result.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>n.target)}))});
   assert.equal(violations.length,0,'Privacy dialog axe findings: '+JSON.stringify(violations));
  }
  await ctx.close();
  assert.equal(unwanted.length,0,'No optional advertising requests while disabled');
  assert.equal(errors.length,0,'No runtime errors');
  const report={checks:results.length,controlsPresent:true,savedCaseDeletion:true,standalonePages:true,adRequests:unwanted.length,errors,accessibilityScan:!!process.env.AXE_PATH,target:process.env.CASEBOOK_TEST_URL?'live':'exact local public build'};
  fs.mkdirSync('evidence',{recursive:true});fs.writeFileSync('evidence/consent-browser.json',JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
