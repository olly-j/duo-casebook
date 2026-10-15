/* CB-003: offline protocol doubles, no certified CMP or live TC strings. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('web/google-cmp-provider.js', 'utf8');
function fixture(change = {}, delayed = false) {
  const calls = [], signals = [], queue = [];
  let callback, opened = 0;
  const trap = () => { throw Error('Unexpected network, DOM, storage or timer access'); };
  const doc = {createElement: trap, head: {appendChild: trap}};
  Object.defineProperty(doc, 'cookie', {get: trap, set: trap});
  const win = {
    location: {origin: 'https://olly-j.github.io', hostname: 'olly-j.github.io', protocol: 'https:', pathname: '/duo-casebook/'},
    navigator: {}, fetch: trap, setTimeout: trap, setInterval: trap,
    googlefc: {callbackQueue: {push(entry) {queue.push(entry); if (!delayed) entry.CONSENT_API_READY();}}, showRevocationMessage() {opened++;}},
    __tcfapi(command, version, cb, id) {calls.push({command, version, id}); if (command === 'addEventListener') callback = cb;}
  };
  Object.defineProperty(win, 'localStorage', {get: trap});
  const config = {enabled: true, publisherApproved: true, siteApproved: true, consentReady: true,
    publisherId: 'ca-pub-1234567890123456', consentConfigId: 'offline-review',
    approvedHosts: ['olly-j.github.io'], requiredPurposes: [1,2,3,4,7,9,10],
    googleCMP: {reviewed: true, certifiedConfigurationReviewed: true, legalBasesReviewed: true,
      googleOnly: true, additionalConsentRequired: false, publisherId: 'ca-pub-1234567890123456',
      configId: 'offline-review', approvedOrigin: 'https://olly-j.github.io', approvedPath: '/duo-casebook/',
      allowedCmpIds: [999], vendorListVersion: 999, tcfPolicyVersion: 5}, ...change};
  vm.runInNewContext(code, {window: win});
  const provider = win.CasebookGoogleCMP.create(win, doc, config);
  return {win, config, provider, signals, calls, queue, get opened() {return opened;},
    subscribe: () => provider.subscribe(s => signals.push(s)),
    emit: (t = grant(), success = true) => callback?.(t, success)};
}
function grant() {
  return {cmpStatus: 'loaded', eventStatus: 'tcloaded', gdprApplies: true, cmpId: 999,
    listenerId: 17, vendorListVersion: 999, tcfPolicyVersion: 5,
    tcString: 'OfflineFixtureNotARealTCString', vendor: {consents: {755: true}},
    purpose: {consents: {1:true,2:true,3:true,4:true,7:true,9:true,10:true}},
    publisher: {restrictions: {2:{755:1},7:{755:1},9:{755:1},10:{755:1}}}};
}
for (const change of [{enabled:false},{publisherApproved:false},{siteApproved:false},{consentReady:false},
  {googleCMP:{}},{requiredPurposes:[1,3,4,7,9,10]},{consentConfigId:'other'},{publisherId:'invalid'},{approvedHosts:[]}]) {
  test('inert gate '+JSON.stringify(change), () => {
    const x = fixture(change); x.subscribe(); x.emit();
    assert.equal(x.calls.length, 0); assert.equal(x.queue.length, 0);
    assert.equal(x.signals.at(-1).authorized, false); assert.equal(x.provider.openPreferences(), false);
  });
}
test('initial denial, stable events, duplicates and revocation are forwarded', () => {
  const x = fixture(); x.subscribe(); assert.equal(x.signals[0].authorized, false);
  x.emit(); x.emit(); assert.equal(x.signals.length, 3);
  assert.equal(x.signals.at(-1).fullLegalBases, true);
  const t = grant(); t.eventStatus = 'useractioncomplete'; x.emit(t);
  assert.equal(x.signals.at(-1).authorized, true);
  t.vendor.consents[755] = false; x.emit(t);
  assert.equal(x.signals.at(-1).authorized, false);
  assert.equal(x.calls[0].command, 'addEventListener'); assert.equal(x.calls[0].version, 2);
});
const invalid = [null, {}, [], {cmpId:999}];
for (const [key, value] of [['cmpId',7],['cmpId','999'],['listenerId',undefined],['cmpStatus','loading'],
  ['eventStatus','cmpuishown'],['gdprApplies',false],['gdprApplies',undefined],['tcString',''],
  ['tcString','not a string'],['vendorListVersion',1],['tcfPolicyVersion',1],['publisher',{}],['purpose',{}],['vendor',{}]]) {
  invalid.push({...grant(), [key]:value});
}
for (const p of [1,2,3,4,7,9,10]) {
  const t = grant(); t.purpose.consents[p] = false; invalid.push(t);
  for (const restriction of [0,2,'1',null]) {
    const t = grant(); t.publisher.restrictions[p] = {755:restriction}; invalid.push(t);
  }
}
for (const restrictions of [null, [], {2:null}, {2:[]}, {}]) {
  const t = grant(); t.publisher.restrictions = restrictions; invalid.push(t);
}
for (const value of [false, undefined, 'true']) {
  const t = grant(); t.vendor.consents[755] = value; invalid.push(t);
}
invalid.forEach((t, i) => test('malformed, refused or incomplete '+i, () => {
  const x = fixture(); x.subscribe(); x.emit(t); assert.equal(x.signals.at(-1).authorized, false);
}));
test('CMP unavailable or throws fails closed', () => {
  for (const kind of ['tcf','google','queue','throws']) {
    const x = fixture();
    if (kind === 'tcf') delete x.win.__tcfapi;
    if (kind === 'google') delete x.win.googlefc;
    if (kind === 'queue') delete x.win.googlefc.callbackQueue;
    if (kind === 'throws') x.win.__tcfapi = () => {throw Error('CMP failure');};
    x.subscribe(); assert.equal(x.signals.at(-1).authorized, false);
  }
});
test('failure and GPC after a grant emit denial', () => {
  const x = fixture(); x.subscribe(); x.emit(); x.emit(grant(), false);
  assert.equal(x.signals.at(-1).authorized, false);
  x.emit(); x.win.navigator.globalPrivacyControl = true; x.emit();
  assert.equal(x.signals.at(-1).authorized, false);
});
test('unsubscribe removes listener by ID once and ignores late signals', () => {
  const x = fixture(); const stop = x.subscribe(); x.emit(); stop(); stop();
  const count = x.signals.length; x.emit(); assert.equal(x.signals.length, count);
  assert.deepEqual(x.calls.at(-1), {command:'removeEventListener',version:2,id:17});
  assert.equal(x.calls.filter(c => c.command === 'removeEventListener').length, 1);
});
test('unsubscribe before readiness or before listener ID prevents stale grants', () => {
  const x = fixture({}, true); const stop = x.subscribe(); stop(); x.queue[0].CONSENT_API_READY();
  assert.equal(x.calls.length, 0);
  const y = fixture(); const end = y.subscribe(); end(); y.emit();
  assert.equal(y.signals.length, 1); assert.equal(y.calls.at(-1).command, 'removeEventListener');
});
test('preferences uses ready Google API and immediately denies pending decision', () => {
  const x = fixture({}, true); x.subscribe(); assert.equal(x.provider.openPreferences(), false);
  x.queue[0].CONSENT_API_READY(); x.emit(); assert.equal(x.provider.openPreferences(), true);
  assert.equal(x.opened, 1); assert.equal(x.signals.at(-1).authorized, false);
  delete x.win.googlefc.showRevocationMessage; assert.equal(x.provider.openPreferences(), false);
});
test('reviewed config is not mutated or activated by later mutation', () => {
  const x = fixture({enabled:false}); const before = JSON.stringify(x.config);
  x.subscribe(); assert.equal(JSON.stringify(x.config), before);
  x.config.enabled = true; x.subscribe(); assert.equal(x.calls.length, 0);
});
test('wrong site, replacement API and observer mutation cannot reuse grant', () => {
  const x = fixture(); x.subscribe(); x.emit(); x.signals.at(-1).tcData.vendor.consents[755] = false;
  x.emit(); assert.equal(x.signals.at(-1).authorized, true);
  x.win.location.pathname = '/other/'; x.emit(); assert.equal(x.signals.at(-1).authorized, false);
  x.win.location.pathname = '/duo-casebook/'; x.win.__tcfapi = () => {}; x.emit();
  assert.equal(x.signals.at(-1).authorized, false);
});
for (const change of [{reviewed:false},{certifiedConfigurationReviewed:false},{legalBasesReviewed:false},
  {googleOnly:false},{additionalConsentRequired:true},{allowedCmpIds:[]},{allowedCmpIds:['999']},
  {publisherId:'other'},{configId:'other'},{approvedOrigin:'https://other.invalid'},
  {approvedPath:'/'},{vendorListVersion:undefined},{tcfPolicyVersion:undefined}]) {
  test('reviewed CMP scope required '+JSON.stringify(change), () => {
    const seed = fixture();
    const x = fixture({googleCMP:{...seed.config.googleCMP,...change}}); x.subscribe();
    assert.equal(x.calls.length, 0); assert.equal(x.provider.openPreferences(), false);
  });
}
test('unserializable data and throwing properties revoke without throwing', () => {
  const x = fixture(); x.subscribe(); x.emit();
  const t = grant(); t.cycle = t; x.emit(t); assert.equal(x.signals.at(-1).authorized, false);
  x.emit(); x.emit(Object.defineProperty({}, 'listenerId', {get() {throw Error('bad data');}}));
  assert.equal(x.signals.at(-1).authorized, false);
});
test('preferences failure denies and observers do not disrupt other subscribers', () => {
  const x = fixture(); x.subscribe(); x.provider.subscribe(() => {throw Error('observer');}); x.emit();
  x.win.googlefc.showRevocationMessage = () => {throw Error('blocked');};
  assert.equal(x.provider.openPreferences(), false); assert.equal(x.signals.at(-1).authorized, false);
});
