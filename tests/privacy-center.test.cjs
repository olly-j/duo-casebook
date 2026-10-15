/* CB-003: native dialog boundary doubles, no runtime dependencies. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const code=fs.readFileSync('web/privacy-center.js','utf8');
function fixture(config={enabled:false},provider){
 const nodes={},removed=[],writes=[];
 let doc;
 class Element {
  constructor(){this.listeners={};this.hidden=false;this.isConnected=true;this.classList={add(){},remove(){}};this.textContent='';}
  addEventListener(k,fn){this.listeners[k]=fn;}
  removeEventListener(k){delete this.listeners[k];}
  setAttribute(){}
  appendChild(e){return e;}
  querySelector(k){return nodes[k] ||= new Element();}
  showModal(){this.open=true;}
  close(){this.open=false;this.listeners.close?.({});}
  focus(){doc.activeElement=this;}
  remove(){this.isConnected=false;removed.push(this);}
 }
 const footer=new Element();const trigger=footer.querySelector('[data-ad-privacy]');trigger.hidden=true;
 const dialogs=[];
 doc={readyState:'complete',activeElement:trigger,body:new Element(),querySelector:()=>footer,createElement(tag){const e=new Element();if(tag==='dialog')dialogs.push(e);return e;},removeEventListener(){}};
 const win={CASEBOOK_ADS_CONFIG:config,CASEBOOK_CONSENT_PROVIDER:provider,localStorage:{removeItem:k=>writes.push(k)}};
 for(const name of ['fetch','setTimeout','setInterval'])win[name]=()=>{throw Error(name);};
 Object.defineProperty(doc,'cookie',{get(){throw Error('cookie');},set(){throw Error('cookie');}});
 vm.runInNewContext(code,{window:win,document:doc,Promise});
 const dialog=dialogs[0];
 function click(selector){dialog.listeners.click({target:nodes[selector]});}
 function open(){trigger.focus();trigger.listeners.click({preventDefault(){},stopImmediatePropagation(){}});}
 return {win,doc,dialog,nodes,trigger,writes,open,click};
}
test('disabled mode explains local privacy without phantom consent or persistence',()=>{
 const x=fixture();x.open();assert.match(x.nodes['[data-privacy-message]'].textContent,/Optional advertising is off/);assert.equal(x.nodes['[data-privacy-ad]'].hidden,true);
 assert.doesNotMatch(x.dialog.innerHTML,/Accept all|Reject all|data-privacy-accept|data-privacy-reject/);assert.deepEqual(x.writes,[]);
});
test('delete requires explicit confirmation and removes only shortlist key',()=>{
 const x=fixture();x.open();x.click('[data-privacy-delete]');assert.deepEqual(x.writes,[]);
 x.click('[data-privacy-clear]');assert.equal(x.doc.activeElement,x.nodes['[data-privacy-keep]']);
 x.click('[data-privacy-keep]');assert.deepEqual(x.writes,[]);
 x.click('[data-privacy-clear]');x.click('[data-privacy-delete]');assert.deepEqual(x.writes,['casebook-saved']);assert.match(x.nodes['[data-privacy-status]'].textContent,/Reload/);
});
test('native keyboard dialog supports Escape, explicit close and return focus',()=>{
 const x=fixture();x.open();assert.equal(x.dialog.open,true);assert.equal(x.doc.activeElement,x.nodes['[data-privacy-close]']);
 let prevented=false;x.dialog.listeners.cancel({preventDefault(){prevented=true;}});assert.ok(prevented);assert.equal(x.dialog.open,false);assert.equal(x.doc.activeElement,x.trigger);
 x.open();x.click('[data-privacy-close]');assert.equal(x.dialog.open,false);
});
test('enabled but missing or unready provider explains unavailable advertising',()=>{
 for(const ready of [false,true]){const x=fixture({enabled:true,consentReady:ready});x.open();assert.match(x.nodes['[data-privacy-message]'].textContent,/Advertising is unavailable/);assert.equal(x.nodes['[data-privacy-ad]'].hidden,true);}
});
test('provider owns advertising choices and receives no local consent',async()=>{
 let calls=0;const x=fixture({enabled:true,consentReady:true},{openPreferences(){calls++;assert.equal(x.dialog.open,false);}});
 x.open();assert.equal(x.nodes['[data-privacy-ad]'].hidden,false);x.click('[data-privacy-ad]');await Promise.resolve();assert.equal(calls,1);assert.deepEqual(x.writes,[]);
});
test('disabled mode never calls even an available provider',()=>{
 const x=fixture({enabled:false,consentReady:true},{openPreferences(){throw Error('must not call');}});x.open();x.click('[data-privacy-ad]');assert.equal(x.nodes['[data-privacy-ad]'].hidden,true);
});
test('provider throw and rejected promise show recoverable status without consent marker',async()=>{
 for(const asyncError of [false,true]){const x=fixture({enabled:true,consentReady:true},{openPreferences(){if(asyncError)return Promise.reject(Error('unavailable'));throw Error('unavailable');}});x.open();x.click('[data-privacy-ad]');await Promise.resolve();assert.equal(x.dialog.open,true);assert.match(x.nodes['[data-privacy-message]'].textContent,/could not open/);assert.deepEqual(x.writes,[]);}
});
test('destroy removes listeners and ignores late provider rejection; remount is explicit',async()=>{
 let reject;const x=fixture({enabled:true,consentReady:true},{openPreferences(){return new Promise((_,r)=>{reject=r;});}});x.open();x.click('[data-privacy-ad]');x.win.CasebookPrivacyCenter.destroy();reject(Error('late'));await Promise.resolve();assert.equal(x.dialog.isConnected,false);assert.deepEqual(Object.keys(x.trigger.listeners),[]);assert.equal(x.trigger.hidden,true);x.win.CasebookPrivacyCenter.mount();assert.equal(x.trigger.hidden,false);
});
test('storage denial reports failure without clearing unrelated data',()=>{
 const x=fixture();x.win.localStorage.removeItem=()=>{throw Error('denied');};x.open();x.click('[data-privacy-clear]');x.click('[data-privacy-delete]');assert.match(x.nodes['[data-privacy-status]'].textContent,/could not be cleared/);
});
