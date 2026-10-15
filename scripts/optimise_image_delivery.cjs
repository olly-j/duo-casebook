/* Create size-limited WebP delivery copies from the exact attributed source image.
   No content generation, retouching, cropping or watermark removal. Originals stay linked. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const data=JSON.parse(fs.readFileSync('web/catalogue.json','utf8'));
 const output='web/assets/cases';fs.mkdirSync(output,{recursive:true});
 const old=fs.existsSync('research/image-delivery.json')?JSON.parse(fs.readFileSync('research/image-delivery.json','utf8')).images:{};
 const images={},failures=[];
 const browser=await chromium.launch({headless:true,chromiumSandbox:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  const context=await browser.newContext();let next=0;
  async function worker(){const page=await context.newPage();try{
   while(next<data.products.length){const p=data.products[next++];
    try{
     const previous=old[p.id];if(previous&&previous.sourceUrl===p.image&&previous.renditions.every(r=>fs.existsSync('web/'+r.path)&&hash(fs.readFileSync('web/'+r.path))===r.sha256)){images[p.id]=previous;continue;}
     if(!p.image?.startsWith('https://'))throw Error('Only attributed HTTPS source images are accepted');
     const response=await context.request.get(p.image,{timeout:25000});if(!response.ok())throw Error('Source returned '+response.status());
     const body=await response.body();const type=(response.headers()['content-type']||'').split(';')[0];if(!type.startsWith('image/')||body.length>15000000)throw Error('Invalid or oversized image response');
     const uri='data:'+type+';base64,'+body.toString('base64');
     const renditions=await page.evaluate(async(uri)=>{const image=new Image();image.src=uri;await image.decode();const result=[];for(const limit of [480,960]){const scale=Math.min(1,limit/Math.max(image.naturalWidth,image.naturalHeight));const canvas=document.createElement('canvas');canvas.width=Math.round(image.naturalWidth*scale);canvas.height=Math.round(image.naturalHeight*scale);const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0,canvas.width,canvas.height);result.push({limit,width:canvas.width,height:canvas.height,data:canvas.toDataURL('image/webp',.82).split(',')[1]});}return{width:image.naturalWidth,height:image.naturalHeight,images:result}},uri);
     const record={sourceUrl:p.image,sourcePage:p.imageSource,sourceSha256:hash(body),sourceBytes:body.length,width:renditions.width,height:renditions.height,renditions:[]};
     for(const r of renditions.images){const relative='assets/cases/'+p.id+'-'+r.limit+'.webp';const bytes=Buffer.from(r.data,'base64');fs.writeFileSync('web/'+relative,bytes);record.renditions.push({path:relative,maxDimension:r.limit,width:r.width,height:r.height,bytes:bytes.length,sha256:hash(bytes)});}
     images[p.id]=record;console.log(p.id,body.length,'->',record.renditions[0].bytes);
    }catch(e){failures.push({id:p.id,reason:e.message});console.error('FAILED',p.id,e.message);}
   }
  }finally{await page.close()}}
  await Promise.all([worker(),worker(),worker(),worker()]);
  fs.writeFileSync('research/image-delivery.json',JSON.stringify({method:'Uncropped resize and WebP encoding from attributed source bytes. No image generation or retouching.',images:Object.fromEntries(Object.entries(images).sort()),failures},null,2)+'\n');
  console.log(JSON.stringify({processed:Object.keys(images).length,failures,sourceBytes:Object.values(images).reduce((n,r)=>n+r.sourceBytes,0),thumbnailBytes:Object.values(images).reduce((n,r)=>n+r.renditions[0].bytes,0)},null,2));
  if(failures.length)process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
