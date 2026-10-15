const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),crypto=require('node:crypto');
const read=p=>fs.readFileSync(p,'utf8');
const ui=read('web/liquid-ui.js'),css=read('web/styles.css');

function harness(options={}){
 const opts={width:1440,scrollHeight:2800,items:3,hidden:false,memory:8,cores:8,saveData:false,userAgent:'Chromium/120',...options};
 const media=[],jobs=[],scripts=[],calls=[],listeners={};
 const tray={hidden:opts.hidden,dataset:{},removeAttribute(k){delete this.dataset.glassRendered;},getBoundingClientRect(){return{width:Math.min(570,opts.width*.45)}}};
 const products={querySelectorAll(){return Array.from({length:opts.items},(_,i)=>i);}};
 const lens={destroy(){calls.push('destroy');}};
 const win={
   innerWidth:opts.width,
   matchMedia(q){const m={query:q,matches:q.includes('min-width')?opts.width>=1100:
     q.includes('pointer')?true:q.includes('reduce')?!!opts.reduced:
     q.includes('more')?!!opts.contrast:q.includes('forced-colors')?false:false,
     addEventListener(event,callback){media.push({q,event,callback})},
     removeEventListener(){}};return m;},
   requestIdleCallback(fn){jobs.push(fn);},addEventListener(name,fn){listeners[name]=fn;},
   liquidGL(params){calls.push(params);return lens;}
 };
 const doc={
   visibilityState:'visible',documentElement:{scrollHeight:opts.scrollHeight},
   getElementById(x){return x==='compare-tray'?tray:x==='products'?products:null;},
   createElement(type){return{tagName:type,src:'',async:false,onload:null,onerror:null}},
   head:{appendChild(el){scripts.push(el)}},
   addEventListener(name,fn){listeners[name]=fn;},removeEventListener(){}
 };
 const nav={userAgent:opts.userAgent,deviceMemory:opts.memory,hardwareConcurrency:opts.cores,connection:{saveData:opts.saveData}};
 let observer=null;
 class MutationObserverMock{constructor(fn){observer=fn}observe(){}disconnect(){calls.push('disconnect')}}
 const ctx={window:win,document:doc,navigator:nav,MutationObserver:MutationObserverMock,setTimeout:fn=>jobs.push(fn)};
 vm.runInNewContext(ui,ctx,{timeout:1000});
 return{tray,products,win,doc,nav,jobs,scripts,calls,listeners,trigger(){observer?.()}};
}

test('neutral system palette replaces green and remains accessible',()=>{
 assert.match(css,/--paper:#fbfbfd/);assert.match(css,/--ink:#1d1d1f/);
 assert.match(css,/--action:#1d1d1f/);assert.match(css,/--focus:#007aff/);
 assert.match(css,/--paper:#111113/);assert.match(css,/--focus:#0a84ff/);
 assert.doesNotMatch(css,/#536447|#b2c69e|#46503e|--moss:/i);
 assert.match(css,/prefers-reduced-motion:reduce/);
 assert.match(css,/prefers-reduced-transparency:reduce/);
 assert.match(css,/forced-colors:active/);
 assert.match(css,/#compare-tray:not\(\[hidden\]\)/);
});
test('photography and content do not become glass panels',()=>{
 assert.match(css,/\.photo\{[^}]*background:#fff/);
 assert.doesNotMatch(css,/\.products\s*\{[^}]*backdrop-filter/);
 assert.doesNotMatch(css,/\.card\s*\{[^}]*backdrop-filter/);
});
test('iPhone, Safari and touch-first browsers keep the CSS-only experience',()=>{
 for(const x of [{width:390},{userAgent:'Mozilla/5.0 Safari/605.1.15'},
  {userAgent:'iPhone Safari/605.1.15'},{width:768},{saveData:true}]){
  const h=harness(x);h.jobs.forEach(f=>f());assert.equal(h.scripts.length,0,JSON.stringify(x));
 }
});
test('reduced motion, transparency, contrast and resource limits never load GPU',()=>{
 for(const x of [{reduced:true},{contrast:true},{memory:2},{cores:2},{scrollHeight:12000},{items:92},{hidden:true}]){
  const h=harness(x);h.jobs.forEach(f=>f());assert.equal(h.scripts.length,0,JSON.stringify(x));
 }
});
test('the small, visible desktop compare control lazily loads its own pinned library',()=>{
 const h=harness();assert.equal(h.scripts.length,0);
 assert.equal(h.jobs.length,1);
 h.jobs[0]();
 assert.equal(h.scripts.length,1);
 assert.equal(h.scripts[0].src,'vendor/liquidGL.js');
 h.scripts[0].onload();
 assert.equal(h.calls.length,1);
 assert.equal(h.calls[0].target,'#compare-tray');
 assert.equal(h.calls[0].specular,false);
 assert.equal(h.calls[0].tilt,false);
 assert.equal(h.calls[0].interaction,'none');
 assert.equal(h.calls[0].resolution,1);
});
test('the renderer is destroyed if the compare tray is hidden',()=>{
 const h=harness();h.jobs[0]();h.scripts[0].onload();
 h.tray.hidden=true;h.trigger();
 assert.ok(h.calls.includes('destroy'));
});
test('vendored source exactly matches the reviewed MIT v3.0.0 blob',()=>{
 const s=fs.readFileSync('web/vendor/liquidGL.js');
 const git=crypto.createHash('sha1').update('blob '+s.length+'\0').update(s).digest('hex');
 assert.equal(git,'b76e6872bf1c93ecacff646d09a77f5ce5f24ddb');
 assert.deepEqual(s,fs.readFileSync('docs/vendor/liquidGL.js'));
 assert.match(read('web/vendor/LICENSE.txt'),/MIT License/);
});
test('all important controls have safe native fallback and no tracking dependency',()=>{
 const html=read('web/index.html'),prep=read('prepare_site.py');
 assert.match(html,/src="liquid-ui.js"/);
 assert.match(prep,/liquid-ui\.js/);
 assert.match(prep,/vendor = ROOT/);
 assert.doesNotMatch(ui,/https?:\/\/|fetch\(|XMLHttpRequest|sendBeacon|localStorage/);
});
