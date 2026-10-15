/* CB-002: VM DOM/network doubles only. Never loads the Google SDK. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const code=fs.readFileSync('web/ads.js','utf8');
function fixture(overrides={}) {
 const requests=[],observers=[];
 let listener, subscriptions=0, top=1000;
 class Element {
  constructor(){this.dataset={casebookAd:'catalogue'};this.children=[];this.style={};this.attrs={};this.hidden=true;this.classList={add(){}};}
  appendChild(e){this.children.push(e);e.parent=this;return e;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(e=>e!==this);}
  closest(){return null;}
  setAttribute(k,v){this.attrs[k]=v;}
  getAttribute(k){return this.attrs[k];}
  removeAttribute(k){delete this.attrs[k];}
  getBoundingClientRect(){return {top,bottom:top+280,width:600};}
  getClientRects(){return [1];}
 }
 const target=new Element(),head=new Element();
 target.previousElementSibling={getBoundingClientRect:()=>({bottom:top})};
 head.appendChild=e=>{requests.push(e);return e;};
 const doc={head,createElement:()=>new Element()};
 Object.defineProperty(doc,'cookie',{get(){throw Error('cookie read');},set(){throw Error('cookie write');}});
 const win={location:{hostname:'olly-j.github.io',protocol:'https:'},innerHeight:800,navigator:{},
  MutationObserver:class {constructor(cb){this.cb=cb;observers.push(this);}observe(){}disconnect(){}},
  IntersectionObserver:class {constructor(cb){this.cb=cb;observers.push(this);}observe(){}disconnect(){}},
  adsbygoogle:[],setTimeout(){throw Error('timer');},setInterval(){throw Error('refresh');}};
 Object.defineProperty(win,'localStorage',{get(){throw Error('storage access');}});
 const config={enabled:true,publisherId:'ca-pub-1234567890123456',slots:{catalogue:'1234567890',article:'2345678901'},publisherApproved:true,siteApproved:true,consentReady:true,approvedHosts:['olly-j.github.io'],consentConfigId:'reviewed-config',requiredPurposes:[1,3,4,7,9,10],...overrides};
 vm.runInNewContext(code,{window:win});
 const provider={subscribe(cb){subscriptions++;listener=cb;return ()=>{};}};
 const api=win.CasebookAds.create(win,doc,config);
 const options={target,pageType:'catalogue',isEligible:()=>true,consentProvider:provider};
 return {win,doc,config,api,options,requests,target,observers,start:()=>api.start(options),emit:s=>listener?.(s),get subscriptions(){return subscriptions;},visible(){top=200;},below(){top=1000;}};
}
function grant(){return {authorized:true,fullLegalBases:true,configId:'reviewed-config',success:true,tcData:{cmpStatus:'loaded',eventStatus:'tcloaded',gdprApplies:true,tcString:'offline-fixture',vendor:{consents:{755:true}},purpose:{consents:{1:true,3:true,4:true,7:true,9:true,10:true}},publisher:{restrictions:{}}}};}
test('shipped config off, inert without storage, timers or requests',()=>{const x=fixture();vm.runInNewContext(fs.readFileSync('web/ads-config.js','utf8'),{window:x.win});const a=x.win.CasebookAds.create(x.win,x.doc,x.win.CASEBOOK_ADS_CONFIG);assert.equal(a.start(x.options),false);assert.equal(x.requests.length,0);assert.equal(x.subscriptions,0);assert.equal(x.target.children.length,0);});
for(const change of [{enabled:false},{publisherApproved:false},{siteApproved:false},{consentReady:false},{consentConfigId:null},{publisherId:'fake'},{publisherId:'ca-pub-0000000000000000'},{approvedHosts:[]},{requiredPurposes:[1,3,4]},{slots:{catalogue:'0000000000'}}])test('rejects config '+JSON.stringify(change),()=>{const x=fixture(change);assert.equal(x.start(),false);assert.equal(x.subscriptions,0);assert.equal(x.requests.length,0);});
for(const host of ['localhost','127.0.0.1','site.test','dev.site.com','staging.site.com','wrong.com'])test('host rejected '+host,()=>{const x=fixture({approvedHosts:[host==='wrong.com'?'olly-j.github.io':host]});x.win.location.hostname=host;assert.equal(x.start(),false);});
test('HTTP, GPC and missing CMP denied',()=>{for(const kind of ['http','gpc','cmp']){const x=fixture();if(kind==='http')x.win.location.protocol='http:';if(kind==='gpc')x.win.navigator.globalPrivacyControl=true;if(kind==='cmp')delete x.options.consentProvider;assert.equal(x.start(),false);assert.equal(x.requests.length,0);}});
const invalid=[undefined,{}, {...grant(),authorized:false},{...grant(),fullLegalBases:false},{...grant(),success:false},{...grant(),configId:'other'}];
for(const [key,value] of [['cmpStatus','loading'],['eventStatus','cmpuishown'],['gdprApplies',false],['gdprApplies',undefined],['tcString','']]){const s=grant();s.tcData[key]=value;invalid.push(s);}
for(const p of [1,3,4,7,9,10]){const s=grant();s.tcData.purpose.consents[p]=false;invalid.push(s);}
for(const v of [false,undefined]){const s=grant();s.tcData.vendor.consents[755]=v;invalid.push(s);}
for(const restriction of [0,2,'1']){const s=grant();s.tcData.publisher.restrictions[1]={755:restriction};invalid.push(s);}
for(const [i,s] of invalid.entries())test('unknown/refused signal '+i,()=>{const x=fixture();x.start();x.emit(s);assert.equal(x.requests.length,0);assert.equal(x.target.hidden,true);});
test('consent then load then visibility: one async standard script, one push',()=>{const x=fixture();x.start();assert.equal(x.requests.length,0);x.emit(grant());x.emit(grant());assert.equal(x.requests.length,1);const script=x.requests[0];assert.equal(script.async,true);assert.equal(script.crossOrigin,'anonymous');assert.match(script.src,/^https:\/\/pagead2\.googlesyndication\.com\/pagead\/js\/adsbygoogle.js\?client=ca-pub-\d{16}$/);assert.equal(x.win.adsbygoogle.length,0);script.onload();assert.equal(x.win.adsbygoogle.length,0);x.visible();x.observers.at(-1).cb();x.observers.at(-1).cb();x.emit(grant());assert.equal(x.win.adsbygoogle.length,1);assert.equal(x.requests.length,1);});
test('revocation before delayed load, including regrant, cannot reuse stale unit',()=>{const x=fixture();x.start();x.emit(grant());x.emit({});x.emit(grant());x.visible();x.requests[0].onload();assert.equal(x.win.adsbygoogle.length,0);assert.equal(x.target.children.filter(e=>e.className==='adsbygoogle').length,0);});
test('revocation after push removes ad, never refreshes on regrant',()=>{const x=fixture();x.start();x.emit(grant());x.visible();x.requests[0].onload();assert.equal(x.win.adsbygoogle.length,1);x.emit({});assert.equal(x.target.style.visibility,'hidden');x.emit(grant());assert.equal(x.requests.length,1);assert.equal(x.win.adsbygoogle.length,1);});
for(const failure of ['sdk','push','nofill','gpc','eligibility'])test('safe failure '+failure,()=>{const x=fixture();x.start();x.emit(grant());if(failure==='sdk')x.requests[0].onerror();if(failure==='push')x.win.adsbygoogle={push(){throw Error('SDK failure');}};if(failure==='gpc')x.win.navigator.globalPrivacyControl=true;if(failure==='eligibility')x.options.isEligible=()=>false;if(failure==='nofill'){const unit=x.target.children.at(-1);unit.setAttribute('data-ad-status','unfilled');x.observers[0].cb();}x.visible();x.requests[0].onload();assert.equal(x.target.style.visibility,'hidden');});
test('ineligible page, dialog, hidden placement and late consent never request',()=>{for(const kind of ['privacy','case','404','saved','dialog','late']){const x=fixture();if(['privacy','case','404'].includes(kind))x.options.pageType=kind;if(kind==='saved')x.options.isEligible=()=>false;if(kind==='dialog')x.target.closest=()=>({});if(kind==='late')x.visible();x.start();x.emit(grant());assert.equal(x.requests.length,0);}});
test('one placement per document across controllers',()=>{const x=fixture();assert.equal(x.start(),true);assert.equal(x.api.start(x.options),false);const second=x.win.CasebookAds.create(x.win,x.doc,x.config);assert.equal(second.start(x.options),false);});
test('suppression and destroy prevent delayed requests',()=>{for(const action of ['suppress','destroy']){const x=fixture();x.start();x.api[action]();x.emit(grant());assert.equal(x.requests.length,0);}});

test('missing preceding content denies reservation and network',()=>{const x=fixture();delete x.target.previousElementSibling;x.start();x.emit(grant());assert.equal(x.requests.length,0);});
