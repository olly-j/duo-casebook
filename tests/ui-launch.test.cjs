const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('web/app.js','utf8');
function start({query='',data=true}={}){
 const nodes=new Map(),events={},shared=[],writes=[];
 const node=()=>({innerHTML:'static case links',textContent:'',value:'',dataset:{},style:{},querySelectorAll:()=>[],setAttribute(){},addEventListener(name,fn){this[name]=fn},showModal(){this.open=true},close(){this.open=false;this.closeEvent?.()},focus(){},scrollIntoView(){}});
 const document={querySelector(k){if(!nodes.has(k))nodes.set(k,node());return nodes.get(k)},querySelectorAll:()=>[],addEventListener(n,fn){events[n]=fn},createElement:node};
 const product={id:'moss-case',name:'Moss case',brand:'Maker',price:null,currency:'GBP',coverage:'front-only',hinge:null,materials:[],sources:[]};
 const context={window:{...(data?{CASEBOOK:{products:[product]}}:{}),addEventListener(n,fn){events[n]=fn}},document,URL,URLSearchParams,location:{search:query,pathname:'/',href:'https://example.com/?'+query.replace(/^\?/,''),hash:''},history:{replaceState(a,b,u){writes.push(u)}},navigator:{share:async v=>shared.push(v)},localStorage:{getItem:()=>null},setTimeout,clearTimeout};
 vm.createContext(context);vm.runInContext(source.replace("window.addEventListener('popstate'","window.qa={card,detail,share,readURL,writeURL,getResults,get state(){return state}};window.addEventListener('popstate'"),context);
 return {context,nodes,events,shared,writes,product,qa:context.window.qa};
}
test('failed data resource leaves static case links untouched and gives recovery feedback',()=>{
 const {nodes}=start({data:false});assert.equal(nodes.has('#products'),false);assert.equal(nodes.has('#results'),false);assert.match(nodes.get('#result-count').textContent,/Open a case below or reload/);
});
test('case query opens detail while preserving active filters and null facts',()=>{
 const {nodes,writes,qa}=start({query:'?case=moss-case&brand=Maker&currency=EUR&budget=0&unknown=0'});
 assert.equal(nodes.get('#detail-dialog').open,true);assert.match(nodes.get('#detail-content').innerHTML,/Not published/);assert.equal(qa.state.currency,'EUR');assert.equal(qa.state.budget,'0');assert.equal(qa.state.unknown,false);const u=new URL(writes.at(-1),'https://example.com');assert.equal(u.searchParams.get('case'),'moss-case');assert.equal(u.searchParams.get('brand'),'Maker');assert.equal(u.searchParams.get('budget'),'0');
});
test('titles are crawlable case anchors; photo buttons and selector contracts remain',()=>{
 const {qa,product}=start();const html=qa.card(product);assert.match(html,/<a class="title-button" href="cases\/moss-case\/">Moss case<\/a>/);for(const attr of ['data-detail','data-save','data-compare'])assert.ok(html.includes(attr));assert.match(html,/Front only · Hinge: Not published/);assert.doesNotMatch(html,/data-share-case/);
});
test('product sharing uses the static case URL, independent of filters',async()=>{
 const {qa,shared,nodes}=start({query:'?q=leather&compare=moss-case'});qa.detail('moss-case');assert.match(nodes.get('#detail-content').innerHTML,/data-share-case="moss-case"/);await qa.share(false,'moss-case');assert.equal(shared[0].url,'https://example.com/cases/moss-case/');
});
test('unknown case query is safe and does not open an empty dialog',()=>{const {nodes,qa}=start({query:'?case=missing&q=Maker'});assert.equal(nodes.get('#detail-dialog')?.open,undefined);assert.equal(qa.state.q,'Maker');});
test('static insertion boundary stays inside results; ad slot stays outside catalogue',()=>{
 const html=fs.readFileSync('web/index.html','utf8');const start=html.indexOf('id="results"'),marker=html.indexOf('<!-- CASEBOOK_STATIC_START -->'),end=html.indexOf('<!-- CASEBOOK_STATIC_END -->'),ad=html.indexOf('id="catalogue-ad"');assert.ok(start<marker&&marker<end&&end<ad);assert.match(html.slice(end,ad),/<\/section>/);assert.ok(ad<html.indexOf('id="research"'));assert.match(html,/<aside id="catalogue-ad"[^>]+hidden aria-label="Advertisement"><\/aside>/);for(const href of ['guides/choose-a-case/','about/','privacy/'])assert.ok(html.includes('href="'+href+'"'));assert.match(html,/data-ad-privacy hidden/);
});

test('unpublished starting prices do not imply a known lower bound',()=>{const {qa,product}=start();product.priceFrom=true;const html=qa.card(product);assert.match(html,/<p class="price">Not published<\/p>/);assert.doesNotMatch(html,/From Not published/);});

test('initial source cards are enhanced without replacing the first image',()=>{assert.match(fs.readFileSync('web/app.js','utf8'),/keepStatic/);assert.match(fs.readFileSync('web/app.js','utf8'),/control.disabled=false/);assert.match(fs.readFileSync('web/app.js','utf8'),/anchor.tagName==='A'/);assert.match(fs.readFileSync('web/app.js','utf8'),/imageURL\(p.preview\)/);});
