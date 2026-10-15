const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const script=fs.readFileSync('web/google-cmp-boot.js','utf8');
const publisher='ca-pub-1234567890123456';
const googleScript='https://fundingchoicesmessages.google.com/i/pub-1234567890123456?ers=1';
function setup(override={}){
 const g={reviewed:true,certifiedConfigurationReviewed:true,legalBasesReviewed:true,googleOnly:true,additionalConsentRequired:false,
   publisherId:publisher,configId:'casebook-approved',approvedOrigin:'https://olly-j.github.io',approvedPath:'/duo-casebook/',
   allowedCmpIds:[300],vendorListVersion:3,tcfPolicyVersion:4,bootstrapScriptURL:googleScript,...(override.googleCMP||{})};
 const config={enabled:true,publisherApproved:true,siteApproved:true,consentReady:true,publisherId:publisher,
    consentConfigId:'casebook-approved',approvedHosts:['olly-j.github.io'],requiredPurposes:[1,2,3,4,7,9,10],...override,googleCMP:g};
 const nodes=[],events=[],scriptLoads=[];
 const provider={subscribe(){return()=>{}},openPreferences(){return true}};
 const win={CASEBOOK_ADS_CONFIG:config,CasebookGoogleCMP:{create(){return provider}},googlefc:undefined,dispatchEvent(e){events.push(e.type)},addEventListener(){}};
 const doc={createElement(type){const el={tag:type,async:false,src:'',crossOrigin:'',onerror:null};nodes.push(el);return el;},head:{appendChild(el){scriptLoads.push(el.src)}}};
 const context={window:win,document:doc,location:{protocol:'https:',hostname:'olly-j.github.io',origin:'https://olly-j.github.io',pathname:'/duo-casebook/'},navigator:{globalPrivacyControl:false},Event:class{constructor(type){this.type=type}}};
 vm.createContext(context);vm.runInContext(script,context);
 return {config,win,doc,nodes,events,scriptLoads,provider};
}
test('No approval is a complete no-op, including missing consent review',()=>{
 for(const key of ['enabled','publisherApproved','siteApproved','consentReady']){
  const r=setup({[key]:false});assert.deepEqual(r.scriptLoads,[]);assert.equal(r.win.googlefc,undefined);
 }
});
test('Published Google script only after exact reviewed account and site configuration',()=>{
 const x=setup();assert.deepEqual(x.scriptLoads,[googleScript]);assert.equal(x.win.CASEBOOK_CONSENT_PROVIDER,undefined);
 assert.equal(x.win.googlefc.callbackQueue.length,1);
 x.win.__tcfapi=function(){};x.win.googlefc.callbackQueue[0].CONSENT_API_READY();
 assert.equal(x.win.CASEBOOK_CONSENT_PROVIDER,x.provider);assert.deepEqual(x.events,['casebook-cmp-ready']);
});
test('Malformed publisher or wrong account script cannot load',()=>{
 for(const p of [{publisherId:'ca-pub-0000000000000000'},{googleCMP:{bootstrapScriptURL:'https://other.example/cmp.js'}},
  {googleCMP:{publisherId:'ca-pub-5678901234567890'}},{googleCMP:{approvedOrigin:'https://example.org'}},
  {approvedHosts:['other.example']},{googleCMP:{approvedPath:'/other/'}},{googleCMP:{allowedCmpIds:[]}},
  {googleCMP:{reviewed:false}},{googleCMP:{additionalConsentRequired:true}}]){
  const x=setup(p);assert.deepEqual(x.scriptLoads,[],JSON.stringify(p));
 }
});
test('Google CMP script error denies provider and never loads an ad SDK',()=>{
 const x=setup();x.win.CASEBOOK_CONSENT_PROVIDER=x.provider;
 x.nodes[0].onerror();assert.equal(x.win.CASEBOOK_CONSENT_PROVIDER,null);
 assert.deepEqual(x.scriptLoads,[googleScript]);
});
test('Google consent callback cannot claim ready until the actual TCF API exists',()=>{
 const x=setup();x.win.googlefc.callbackQueue[0].CONSENT_API_READY();assert.equal(x.win.CASEBOOK_CONSENT_PROVIDER,undefined);assert.equal(x.events.length,0);
});
