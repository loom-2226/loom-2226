/* Read-only Pixel-sized measurement of existing clients. No prototype renderer. */
const fs=require('node:fs');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const out={browser:browser.version(),viewport:{width:412,height:915,dpr:3},physical_device:false,cpu_throttling:1,network:'loopback, unthrottled',runs:[]};
 try {
 for(const kind of ['archive','inspector']) for(let run=0;run<3;run++){
  const page=await browser.newPage({viewport:{width:412,height:915},deviceScaleFactor:3,isMobile:true,hasTouch:true});
  const requests=[],errors=[];page.on('request',r=>requests.push({url:r.url(),method:r.method()}));page.on('pageerror',e=>errors.push(e.message));
  if(kind==='archive'){
   const html=fs.readFileSync(process.env.LEGACY_HTML,'utf8');
   await page.route('**/*',route=>route.request().url()==='http://archive.invalid/'?route.fulfill({body:html,contentType:'text/html'}):route.fulfill({body:'{}',contentType:'application/json'}));
  }
  const start=performance.now();await page.goto(kind==='archive'?'http://archive.invalid/':(process.env.SOLAR_INSPECTOR_URL||'http://127.0.0.1:8765'));
  if(kind==='inspector')await page.waitForFunction(()=>window.__solarInspectorReconcile?.()?.objects.some(x=>x.markerSubmitted),{},{timeout:300000});
  else await page.waitForFunction(()=>document.querySelectorAll('svg circle').length>5,{},{timeout:30000});
  const firstUsefulMs=performance.now()-start;
  const metrics=await page.evaluate(async()=>{
   const frames=[];let last=performance.now();for(let i=0;i<31;i++){await new Promise(requestAnimationFrame);const t=performance.now();if(i)frames.push(t-last);last=t;}
   return {frames_ms:frames,heap_bytes:performance.memory?.usedJSHeapSize||null,svg_elements:document.querySelectorAll('svg *').length,
    resources:performance.getEntriesByType('resource').map(x=>({name:x.name,bytes:x.decodedBodySize,transfer:x.transferSize,duration:x.duration})),
    scene:window.__solarInspectorReconcile?{objects:window.__solarInspectorReconcile().objects.length,renderCalls:window.__solarInspectorReconcile().renderCalls}:null};
  });
  out.runs.push({kind,run,firstUsefulMs,requests,errors,...metrics});await page.close();
 }
 const corpus=JSON.parse(fs.readFileSync(process.env.CORPUS,'utf8'));const arrays=Object.values(corpus.paths).map(p=>p.points.map(x=>x.relative.position_km));
 const page=await browser.newPage();out.parse=await page.evaluate(arrays=>{
  const results=[];
  for(const a of arrays){const s=JSON.stringify(a);const times=[];for(let j=0;j<100;j++){const t=performance.now();const p=JSON.parse(s);new Float64Array(p.flat());times.push(performance.now()-t);}times.sort((a,b)=>a-b);results.push({vertices:a.length,median_ms:times[50],p95_ms:times[95]});}return results;
 },arrays);
 fs.writeFileSync(process.env.OUTPUT,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out.runs.map(x=>({kind:x.kind,firstUsefulMs:x.firstUsefulMs,heap:x.heap_bytes,errors:x.errors}))));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
