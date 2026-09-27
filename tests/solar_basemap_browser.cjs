#!/usr/bin/env node
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('/home/ubuntu/LOOM_SOLAR_INSPECTOR/node_modules/playwright');
const args=process.argv.slice(2);function option(name,def){const i=args.indexOf(name);return i>=0?args[i+1]:def;}
const profile=option('--profile','pixel'),delivery=option('--delivery','progressive'),trialIndex=option('--trial-index',null),base=process.env.SOLAR_BASEMAP_URL||'http://127.0.0.1:8770';
if(!['pixel','desktop'].includes(profile)||!['progressive','monolithic'].includes(delivery))throw Error('invalid profile/delivery');
const trialIds=trialIndex===null?[0,1,2,3,4]:[Number(trialIndex)];if(trialIds.some(x=>!Number.isInteger(x)||x<0||x>4))throw Error('trial index must be 0..4');
const evidence=process.env.SOLAR_BASEMAP_EVIDENCE||'/tmp/solar-basemap-browser';fs.mkdirSync(evidence,{recursive:true});
const width=profile==='pixel'?412:1280,height=profile==='pixel'?915:800,dpr=profile==='pixel'?3:1,AU=149597870.7;
function compactScene(s){return s?{...s,lines:(s.lines||[]).map(({float32Input,cameraRelativeKm,...line})=>line)}:null;}
function compactReconcile(r){return {...r,renderer_lines:(r.renderer_lines||[]).map(({float32Input,cameraRelativeKm,...line})=>line)};}
async function main(){
 const browser=await chromium.launch({headless:true});const trials=[];
 try{
  for(const throttled of [false,true])for(const n of trialIds){
   const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:dpr,hasTouch:profile==='pixel'});const page=await context.newPage();const cdp=await context.newCDPSession(page);await cdp.send('Network.enable');
   if(throttled)await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:80,downloadThroughput:10*1024*1024/8,uploadThroughput:2*1024*1024/8,connectionType:'cellular3g'});
   if(throttled)await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
   const productRequests=[],allRequests=[];page.on('request',r=>{allRequests.push(r.url());if(r.url().includes('/product/'))productRequests.push({url:r.url(),time:Date.now()})});
   const consoleErrors=[];page.on('pageerror',e=>consoleErrors.push(String(e)));
   const t0=Date.now();await page.goto(`${base}${base.includes('?')?'&':'?'}delivery=${delivery}`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__solarBasemapReady||window.__solarBasemapError,{timeout:120000});
   if(await page.evaluate(()=>!!window.__solarBasemapError))throw Error(await page.evaluate(()=>window.__solarBasemapError));
   await page.waitForFunction(()=>window.__solarBasemapScene&&window.__solarBasemapScene.markers>0&&window.__solarBasemapScene.lines.length>0,{timeout:30000});
   const usefulMs=Date.now()-t0;const initial=await page.evaluate(()=>({scene:(()=>{const s=window.__solarBasemapScene;return s?{...s,lines:s.lines.map(({float32Input,cameraRelativeKm,...line})=>line)}:null})(),report:window.__solarBasemapReport(),product:performance.getEntriesByType('resource').filter(x=>x.name.includes('/product/')).map(x=>({name:x.name,transfer:x.transferSize,encoded:x.encodedBodySize,decoded:x.decodedBodySize,duration:x.duration})),shell:performance.getEntriesByType('resource').filter(x=>!x.name.includes('/product/')&&x.name.startsWith(location.origin)).map(x=>({name:x.name.replace(location.origin,''),transfer:x.transferSize,encoded:x.encodedBodySize,decoded:x.decodedBodySize,duration:x.duration}))}));
   assert.equal(productRequests.length,delivery==='progressive'?2:1,'initial scene must require only manifest/root or the monolithic control');if(delivery==='progressive')assert(initial.product.reduce((s,x)=>s+x.encoded,0)<=49920,'progressive manifest+root gzip bytes must meet the 49,920-byte coarse-context budget');
   const cold={index:n,throttled,useful_ms:usefulMs,requests:productRequests.length,product_resources:initial.product,shell_requests:initial.shell,shell_request_count:initial.shell.length,scene:initial.scene,cache:initial.report.cache,transfer_bytes:initial.product.reduce((s,x)=>s+x.transfer,0)};
   async function cameraSequence(tag){
    const route=[],tMars=Date.now();route.push(await page.evaluate(()=>window.LoomRenderer.replayApproach('MARS',50*149597870.7,100000,60)));
    await page.waitForFunction(()=>window.__solarBasemapScene&&window.__solarBasemapScene.lines.some(x=>x.feature_id==='PHOBOS'),{timeout:120000});const marsReadyMs=Date.now()-tMars;
    await page.screenshot({path:path.join(evidence,`${profile}-${delivery}-${throttled?'throttled':'plain'}-${n}-${tag}-mars.png`)});
    const mars=await page.evaluate(async()=>{window.LoomRenderer.isolate('PHOBOS');await new Promise(requestAnimationFrame);const isolatedPixels=window.__solarBasemapReadPixels();window.LoomRenderer.isolate(null);await new Promise(requestAnimationFrame);return {report:window.__solarBasemapReport(),pixels:window.__solarBasemapReadPixels(),isolatedPixels,reconcile:window.__solarBasemapReconcile()};});
    assert(mars.isolatedPixels.mint_line_pixels>0,'Phobos reference curve must contribute visible pixels when isolated');assert.equal(mars.reconcile.features.length,110,'every governed catalog identity must reconcile');assert(mars.report.error_budget.max_gpu_conversion_css_px<.25,'Float32 camera-relative conversion must stay below 0.25 CSS px');assert(mars.report.error_budget.total_css_px<=1,'settled Mars view geometry debt must stay within 1 CSS px');
    const tPluto=Date.now();route.push(await page.evaluate(()=>{LoomRenderer.fit();return new Promise(resolve=>requestAnimationFrame(()=>resolve(LoomRenderer.replayApproach('PLUTO',50*149597870.7,250000,60))))}));
    await page.waitForFunction(()=>window.__solarBasemapScene&&window.__solarBasemapScene.lines.some(x=>x.feature_id==='CHARON'),{timeout:120000});const plutoReadyMs=Date.now()-tPluto;
    await page.screenshot({path:path.join(evidence,`${profile}-${delivery}-${throttled?'throttled':'plain'}-${n}-${tag}-pluto.png`)});
    const end=await page.evaluate(async()=>{window.LoomRenderer.isolate('CHARON');await new Promise(requestAnimationFrame);const isolatedPixels=window.__solarBasemapReadPixels();window.LoomRenderer.isolate(null);await new Promise(requestAnimationFrame);return {report:window.__solarBasemapReport(),pixels:window.__solarBasemapReadPixels(),isolatedPixels,reconcile:window.__solarBasemapReconcile()};});
    assert(end.isolatedPixels.mint_line_pixels>0,'Charon reference curve must contribute visible pixels when isolated');assert.equal(end.reconcile.features.length,110,'every governed catalog identity must reconcile');assert(end.report.error_budget.max_gpu_conversion_css_px<.25,'Float32 camera-relative conversion must stay below 0.25 CSS px');assert(end.report.error_budget.total_css_px<=1,'settled Pluto view geometry debt must stay within 1 CSS px');
    return {route,marsReadyMs,plutoReadyMs,mars:{selected:mars.report.draw_list.filter(x=>['PHOBOS','DEIMOS'].includes(x.feature_id)),scene:compactScene(mars.report.scene),pixels:mars.pixels,isolated:mars.isolatedPixels,reconcile:compactReconcile(mars.reconcile)},
      pluto:{selected:end.report.draw_list.filter(x=>x.feature_id==='CHARON'),scene:compactScene(end.report.scene),pixels:end.pixels,isolated:end.isolatedPixels,reconcile:compactReconcile(end.reconcile)},cache:end.report.cache};
   }
   const coldPath=await cameraSequence('cold');
   // A same-context revisit after the complete Mars and Pluto routes exercises retained HTTP/browser caches.
   await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.__solarBasemapReady,{timeout:120000});await page.waitForTimeout(50);
   const before=productRequests.length;const warmPath=await cameraSequence('warm');
   let revisit=null;if(profile==='pixel'&&n===0&&!throttled){for(let i=0;i<10;i++){await page.evaluate(()=>LoomRenderer.replayApproach('MARS',50*149597870.7,100000,30));await page.waitForFunction(()=>window.__solarBasemapScene?.lines.some(x=>x.feature_id==='PHOBOS'),{timeout:30000});await page.evaluate(()=>LoomRenderer.fit());await page.evaluate(()=>LoomRenderer.replayApproach('PLUTO',50*149597870.7,250000,30));await page.waitForFunction(()=>window.__solarBasemapScene?.lines.some(x=>x.feature_id==='CHARON'),{timeout:30000});}revisit=await page.evaluate(()=>({cache:window.__solarBasemap.cacheStats(),frame:window.__solarBasemapScene.max_frame_interval_ms}));assert.equal(revisit.cache.memory_limit,false,'ten back/forth visits must stay within measured cache budget');}
   let interaction=null;if(n===0&&!throttled){
    await page.evaluate(()=>LoomRenderer.fit());await page.waitForTimeout(50);
    const before=await page.evaluate(()=>({distance:LoomRenderer.state.distance,target:[...LoomRenderer.state.target],rotation:[...LoomRenderer.state.rotation]}));
    await page.mouse.move(width/2,height/2);await page.mouse.wheel(0,-80);await page.waitForTimeout(80);
    const wheeled=await page.evaluate(()=>LoomRenderer.state.distance);assert(wheeled<before.distance,'wheel zoom must continuously change camera distance');
    await page.mouse.move(width/2,height/2);await page.mouse.down({button:'right'});await page.mouse.move(width/2+24,height/2+18,{steps:2});await page.mouse.up({button:'right'});
    const panned=await page.evaluate(()=>[...LoomRenderer.state.target]);assert.notDeepEqual(panned,before.target,'pan must continuously move the scene target');
    await page.mouse.move(width/2,height/2);await page.mouse.down({button:'left'});await page.mouse.move(width/2,height/2-100,{steps:3});await page.mouse.up({button:'left'});
    const rotated=await page.evaluate(()=>[...LoomRenderer.state.rotation]);assert.notDeepEqual(rotated,before.rotation,'drag rotation must continuously change camera orientation');
    let pinch=null;if(profile==='pixel'){
      const d0=await page.evaluate(()=>LoomRenderer.state.distance);await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:width/2-50,y:height/2,radiusX:2,radiusY:2,force:1,id:1},{x:width/2+50,y:height/2,radiusX:2,radiusY:2,force:1,id:2}]});
      await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:width/2-90,y:height/2,radiusX:2,radiusY:2,force:1,id:1},{x:width/2+90,y:height/2,radiusX:2,radiusY:2,force:1,id:2}]});
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(80);pinch=await page.evaluate(()=>LoomRenderer.state.distance);assert(pinch<d0,'two-finger pinch must continuously change camera distance');
    }
    const final=await page.evaluate(()=>({scene:window.__solarBasemapScene,overflow:document.documentElement.scrollWidth>innerWidth,report:window.__solarBasemapReport()}));assert.equal(final.overflow,false,'viewport must not overflow horizontally');assert(final.scene.markers>0,'camera gestures must not create an empty-frame transition');interaction={before,wheeled,panned,rotated,pinch,overflow:final.overflow,visible_markers:final.scene.markers,edge_on_error:final.report.error_budget};
   }
   const warmResources=await page.evaluate(()=>performance.getEntriesByType('resource').filter(x=>x.name.includes('/product/')).map(x=>({name:x.name,transfer:x.transferSize,encoded:x.encodedBodySize,decoded:x.decodedBodySize,duration:x.duration})));
   assert.equal(allRequests.filter(x=>/authority|resolver|ephemeris|state-api/i.test(x)).length,0,'browser must never call authority/resolver/state APIs');
   const warm={index:n,throttled,cold_path:coldPath,warm_path:warmPath,interaction,additional_requests:productRequests.length-before,resources:warmResources,
     immutable_chunk_transfer_bytes:warmResources.filter(x=>/\/objects\//.test(x.name)).reduce((s,x)=>s+x.transfer,0),revisit,
     diagnostics:{catalog:warmPath.catalog,authority_calls:allRequests.filter(x=>/authority|resolver|ephemeris|state-api/i.test(x)).length,console_errors:consoleErrors}};assert.equal(warm.immutable_chunk_transfer_bytes,0,'warm visit must not redownload immutable product chunks');
   trials.push({profile,delivery,cold,warm});
   await context.close();
   fs.writeFileSync(path.join(evidence,`${profile}-${delivery}-partial.json`),JSON.stringify({profile,delivery,trials},null,2));
  }
 } finally {await browser.close();}
 const series=(key)=>trials.map(t=>key(t)).filter(Number.isFinite).sort((a,b)=>a-b);const stats=a=>a.length?({n:a.length,median:a[(a.length-1)>>1],p95:a[Math.ceil(a.length*.95)-1],max:a[a.length-1],values:a}):({n:0,values:[]});
 const result={schema:'loom.solar-basemap.browser-evidence/0.1',profile,delivery,viewport:{width,height,dpr,render_dpr_cap:2},network_profiles:['unthrottled','10Mbps_80ms_cpu4'],trials,
   summary:{cold_useful_ms_plain:stats(series(t=>t.cold.throttled?NaN:t.cold.useful_ms)),cold_useful_ms_throttled:stats(series(t=>t.cold.throttled?t.cold.useful_ms:NaN)),
   warm_product_requests:stats(series(t=>t.warm.additional_requests)),frame_samples_plain:stats(trials.filter(t=>!t.throttled).flatMap(t=>t.warm.warm_path.pluto.scene?.frame_interval_ms||[]).sort((a,b)=>a-b)),
   frame_samples_throttled:stats(trials.filter(t=>t.throttled).flatMap(t=>t.warm.warm_path.pluto.scene?.frame_interval_ms||[]).sort((a,b)=>a-b)),trial_max_frame_interval_plain:stats(series(t=>t.throttled?NaN:t.warm.warm_path.pluto.scene?.max_frame_interval_ms)),trial_max_frame_interval_throttled:stats(series(t=>t.throttled?t.warm.warm_path.pluto.scene?.max_frame_interval_ms:NaN))}};
 const target=path.join(evidence,`${profile}-${delivery}${trialIndex===null?'':`-trial-${trialIndex}`}.json`);fs.writeFileSync(target,JSON.stringify(result,null,2));console.log(JSON.stringify({evidence:target,trials:trials.length,summary:result.summary}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
