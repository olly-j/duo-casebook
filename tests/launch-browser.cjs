/* CB-002: candidate or hosted release checks. Advertising endpoints are never exercised. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const BASE='https://olly-j.github.io/duo-casebook/';
const LIVE=!!process.env.CASEBOOK_TEST_URL;
const ROOT=path.resolve('docs');
const MIME={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.xml':'application/xml','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.webmanifest':'application/manifest+json'};
const counts={checks:[],viewports:[],accessibility:[],errors:[],blockedAdvertising:[]};
const check=(name,ok)=>{assert.ok(ok,name);counts.checks.push(name)};
async function setup(browser,options={}){
 const context=await browser.newContext(options);
 await context.route('**/*',async route=>{
  const u=new URL(route.request().url());
  if(/(^|\.)(googlesyndication\.com|doubleclick\.net|google-analytics\.com|googletagmanager\.com|fundingchoicesmessages\.google\.com)$/.test(u.hostname)){
   counts.blockedAdvertising.push(u.origin);return route.abort();
  }
  if(!LIVE&&u.href.startsWith(BASE)){
   const part=decodeURIComponent(u.pathname.slice('/duo-casebook/'.length));let file=path.resolve(ROOT,part||'index.html');
   if(!file.startsWith(ROOT+path.sep))return route.fulfill({status:404,body:'Not found'});
   if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
   if(!fs.existsSync(file))return route.fulfill({status:404,contentType:'text/html',body:fs.readFileSync(path.join(ROOT,'404.html'))});
   return route.fulfill({status:200,contentType:MIME[path.extname(file)]||'text/plain',body:fs.readFileSync(file)});
  }
  return route.continue();
 });
 return context;
}
(async()=>{fs.mkdirSync('tests/screenshots',{recursive:true});fs.mkdirSync('evidence',{recursive:true});
 const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  const data=JSON.parse(fs.readFileSync('web/catalogue.json','utf8'));
  for(const colour of ['light','dark'])for(const width of [320,390,430,768,1440]){
   const context=await setup(browser,{viewport:{width,height:844},colorScheme:colour});const page=await context.newPage();
   page.on('pageerror',e=>counts.errors.push(e.message));await page.goto(BASE,{waitUntil:'domcontentloaded'});await page.waitForTimeout(300);
   const result=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,cards:document.querySelectorAll('.card').length,background:getComputedStyle(document.body).backgroundColor,ads:window.CASEBOOK_ADS_CONFIG?.enabled,adHeight:document.querySelector('[data-ad-placement]')?.getBoundingClientRect().height}));
   check(`${colour} ${width}px: catalogue and no overflow`,result.cards===data.products.length&&result.scroll<=width);check(`${colour} ${width}px: inactive ads occupy no space`,result.ads===false&&result.adHeight===0);counts.viewports.push({...result,colour});
   if([390,1440].includes(width))await page.screenshot({path:`tests/screenshots/launch-${colour}-${width}.png`});
   await context.close();
  }
  const nojs=await setup(browser,{javaScriptEnabled:false,viewport:{width:390,height:844}});const np=await nojs.newPage();await np.goto(BASE,{waitUntil:'domcontentloaded'});
  check('Full source-rendered catalogue without JavaScript',(await np.locator('.card').count())===data.products.length);
  await np.locator('.card h3 a').first().click();check('No-JS case links open substantive case pages',np.url().includes('/cases/')&&(await np.locator('.reading-specs dt').count())>15);
  check('No-JS case page retains seller and provenance',(await np.locator('a').allTextContents()).includes('Image source'));
  await np.screenshot({path:'tests/screenshots/case-nojs-390.png'});await nojs.close();
  const context=await setup(browser,{viewport:{width:390,height:844}});const page=await context.newPage();page.on('pageerror',e=>counts.errors.push(e.message));
  await page.goto(BASE+'?case=apple-case',{waitUntil:'domcontentloaded'});check('Case deep link opens correct details',await page.locator('#detail-dialog').isVisible());check('Case share and canonical page are available',await page.locator('[data-share-case="apple-case"]').isVisible());await page.keyboard.press('Escape');
  await page.locator('#search').fill('Spigen');await page.locator('#filter-open').click();check('Filter sheet opens',await page.locator('#filters-dialog').isVisible());await page.screenshot({path:'tests/screenshots/launch-filters-390.png'});await page.keyboard.press('Escape');
  const multi=data.products.find(p=>p.images?.length>1);await page.goto(BASE+'?case='+multi.id,{waitUntil:'domcontentloaded'});await page.locator('#detail-gallery img').first().evaluate(i=>i.decode().catch(()=>{}));await page.screenshot({path:'tests/screenshots/launch-detail-390.png'});
  const enlarged=page.locator('[data-enlarge]').first();if(await enlarged.count()){await enlarged.click();check('Enlarged photo viewer opens',await page.locator('#image-dialog').isVisible());await page.keyboard.press('ArrowRight');await page.keyboard.press('Escape');check('Photo viewer closes back to details',await page.locator('#detail-dialog').isVisible());}
  await page.goto(BASE,{waitUntil:'domcontentloaded'});
  await page.locator('[data-compare="apple-case"]').check();await page.locator('[data-compare="apple-folio"]').check();await page.locator('#compare-open').click();check('Side-by-side comparison opens',await page.locator('#compare-dialog').isVisible());check('Comparison scroll stays inside the page',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:'tests/screenshots/launch-compare-390.png'});await page.keyboard.press('Escape');
  if(process.env.AXE_PATH){
   for(const route of ['', 'cases/apple-case/', 'guides/choose-a-case/', 'about/', 'privacy/']){
    await page.goto(BASE+route,{waitUntil:'domcontentloaded'});await page.addScriptTag({path:process.env.AXE_PATH});
    const scan=await page.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary})).slice(0,5)}));});counts.accessibility.push({route,violations:scan});
   }
  }
  await page.goto(BASE,{waitUntil:'domcontentloaded'});await page.emulateMedia({reducedMotion:'reduce',colorScheme:'dark'});await page.evaluate(()=>document.documentElement.style.fontSize='200%');check('200% text size has no page-wide overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:'tests/screenshots/launch-large-text.png'});await context.close();
  check('No advertising or analytics requests with shipped configuration',counts.blockedAdvertising.length===0);check('No uncaught browser errors',counts.errors.length===0);
  counts.target=LIVE?'public deployment':'candidate served from exact docs files';counts.testedAt=new Date().toISOString();counts.contentHash=require('node:crypto').createHash('sha256').update(fs.readFileSync('docs/build-manifest.json')).digest('hex');
  fs.writeFileSync('evidence/launch-browser.json',JSON.stringify(counts,null,2));console.log(JSON.stringify(counts,null,2));
  if(counts.accessibility.some(x=>x.violations.length))process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
