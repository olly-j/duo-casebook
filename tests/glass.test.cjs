/* CB-005: library loader is optional, lazy, and never a requirement to use CASEBOOK. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const code=fs.readFileSync('web/glass.js','utf8');
function run({mobile=false,small=false,reduced=false,contrast=false,slow=false,long=false}={}){
  const scripts=[], calls=[], listeners={}, dock={};
  let destroyed=false;
  const win={
    WebGL2RenderingContext:function(){},
    matchMedia(query){return {matches:query.includes('min-width')?!small:query.includes('contrast')?contrast:reduced}},
    requestIdleCallback(fn){fn()},setTimeout(fn){fn()},
    liquidGL(opts){calls.push(opts);return {destroy(){destroyed=true}}},
    addEventListener(name,fn){listeners[name]=fn}
  };
  const doc={
    currentScript:{src:'https://olly-j.github.io/duo-casebook/glass.js'},
    readyState:'complete',
    visibilityState:'visible',
    documentElement:{scrollHeight:long?9000:1800},
    querySelector(sel){return sel==='.glass-dock'?dock:null},
    createElement(){return {async:false,src:'',onload:null,onerror:null}},
    head:{appendChild(e){scripts.push(e)}}
  };
  const navigator={
    userAgent:mobile?'Mozilla/5.0 (iPhone; CPU iPhone OS 27_0)':'Mozilla/5.0 (Macintosh; Intel Mac OS X)',
    deviceMemory:8,hardwareConcurrency:10,
    connection:slow?{saveData:true}:undefined,
    gpu:null
  };
  const context={window:win,document:doc,navigator,
    location:{href:'https://olly-j.github.io/duo-casebook/about/'},URL};
  vm.runInNewContext(code,context);
  return {scripts,calls,listeners,win,get destroyed(){return destroyed}};
}
test('native CSS is sufficient on iPhone and narrow screens',()=>{
  for(const options of [{mobile:true},{small:true},{reduced:true},{contrast:true},{slow:true},{long:true}]){
    const r=run(options);assert.equal(r.scripts.length,0,JSON.stringify(options));
  }
});
test('eligible short desktop page lazily loads only pinned local runtime',()=>{
  const r=run();
  assert.equal(r.scripts.length,1);
  assert.equal(r.scripts[0].src,'https://olly-j.github.io/duo-casebook/vendor/liquidGL.js');
  assert.equal(r.calls.length,0);
  r.scripts[0].onload();
  assert.equal(r.calls.length,1);
  const x=r.calls[0];
  assert.equal(x.target,'.glass-dock');
  assert.ok(x.resolution<=0.5);
  assert.equal(x.interaction,'none');
  assert.equal(x.draggable,false);
  assert.equal(x.specular,false);
  assert.equal(x.shadow,false);
  assert.equal(x.tilt,false);
  r.listeners.pagehide();
  assert.equal(r.destroyed,true);
});
test('no runtime or failed renderer does not break site',()=>{
  const r=run();delete r.win.liquidGL;
  assert.doesNotThrow(()=>r.scripts[0].onload());
  r.listeners.pagehide();assert.equal(r.destroyed,false);
});
test('project retains readable controls under reduced-transparency and high contrast',()=>{
  const css=fs.readFileSync('web/styles.css','utf8');
  const reading=fs.readFileSync('web/reading.css','utf8');
  const privacy=fs.readFileSync('web/privacy-center.css','utf8');
  assert.ok(css.includes('--paper:#ffffff') && css.includes('--ink:#1d1d1f'));
  assert.ok(!css.includes('#536447') && !css.includes('#b2c69e'));
  assert.ok(css.includes('prefers-reduced-transparency:reduce'));
  assert.ok(css.includes('prefers-contrast:more'));
  assert.ok(css.includes('prefers-reduced-motion:reduce'));
  assert.ok(css.includes('.glass-dock'));
  assert.ok(css.includes('.photo{background:#fff'));
  assert.ok(reading.includes('body.reading .glass-dock'));
  assert.ok(privacy.includes('dialog.privacy-center'));
  assert.ok(!code.includes('https://cdn.'));
});
