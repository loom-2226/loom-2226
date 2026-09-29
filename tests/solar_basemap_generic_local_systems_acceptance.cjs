#!/usr/bin/env node
// Real touch route through the published client; diagnostics are read-only.
const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('/home/ubuntu/LOOM_SOLAR_INSPECTOR/node_modules/playwright');
const base=process.env.SOLAR_BASEMAP_URL||'http://127.0.0.1:8771';
const output=process.env.SOLAR_BASEMAP_GENERIC_EVIDENCE||'/tmp/solar-basemap-generic-local-systems-acceptance.json';
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const read=page=>page.evaluate(()=>window.__solarBasemapPilotState());
const point=s=>({x:(s.clip[0]+1)*206,y:(1-s.clip[1])*457.5});
async function touch(cdp,type,points){await cdp.send('Input.dispatchTouchEvent',{type,touchPoints:points.map(([x,y,id])=>({x,y,id,radiusX:3,radiusY:3,force:1}))});}
async function tap(cdp,p){await touch(cdp,'touchStart',[[p.x,p.y,1]]);await touch(cdp,'touchEnd',[]);}
async function pinch(cdp,x,y,ratio){const a=40,b=a*ratio;await touch(cdp,'touchStart',[[x-a,y,1],[x+a,y,2]]);await touch(cdp,'touchMove',[[x-b,y,1],[x+b,y,2]]);await touch(cdp,'touchEnd',[]);}
async function main(){
  const browser=await chromium.launch({headless:true}),errors=[],requests=[];
  try{
    const page=await browser.newPage({viewport:{width:412,height:915},deviceScaleFactor:3,hasTouch:true});
    const cdp=await page.context().newCDPSession(page);page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
    await page.goto(`${base}/?delivery=progressive`,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.__solarBasemapReady&&!window.__solarBasemapError&&window.__solarBasemapScene?.markers>0,{timeout:120000});
    const initial=await read(page),localNode=await page.evaluate(()=>window.__solarBasemap.catalog().find(x=>x.body_id==='IO').node_id),localAnchor=await page.evaluate(node=>window.__solarBasemap.root.nodes.find(x=>x.node_id===node).anchor_id,localNode);
    assert(initial.product_local_nodes.includes(localNode),'Jupiter local node must be present in the published hierarchy');
    const jupiter=initial.symbols.find(x=>x.body_id==='JUPITER');assert(jupiter?.clip,'Jupiter must have a governed selectable marker');
    await tap(cdp,point(jupiter));await page.waitForFunction(()=>window.__solarBasemapPilotState().selected_body_id==='JUPITER',{timeout:15000});
    await page.waitForFunction(async()=>{const s=window.__solarBasemapPilotState(),f=await window.__solarBasemap.catalog().find(x=>x.body_id==='JUPITER');return Math.hypot(...s.camera.target_km.map((v,i)=>v-f.position_km[i]))<1;},{timeout:30000});
    const pinchTrace=[];
    for(let i=0;i<16;i++){
      const before=await read(page),target=before.symbols.find(x=>x.body_id==='JUPITER');assert(target?.clip,'selected Jupiter marker must remain visible');const at=point(target);
      await pinch(cdp,at.x,at.y,2.0);await wait(100);const after=await read(page),ratio=after.camera.distance_km/before.camera.distance_km;
      assert(ratio>=1/3-.001&&ratio<1,'each touch pinch must retain the accepted per-gesture zoom bound');
      const localCurveIds=after.lines.filter(x=>x.node_id===localNode&&x.clip_vertices>0).map(x=>x.feature_id);
      pinchTrace.push({distance_km:after.camera.distance_km,ratio,local_curve_ids:localCurveIds});
      if(localCurveIds.includes('IO'))break;
    }
    await page.waitForFunction(node=>window.__solarBasemapPilotState().lines.some(x=>x.node_id===node&&x.feature_id==='IO'&&x.clip_vertices>0),localNode,{timeout:120000});
    const final=await read(page),report=await page.evaluate(()=>window.__solarBasemapReport());
    assert(final.lines.some(x=>x.feature_id===localAnchor&&x.node_id==='solar'&&x.presentation_context==='LOCAL_PARENT_ARC'),'Jupiter governed anchor arc must appear as generic local parent context');
    const ids=['IO','EUROPA','GANYMEDE','CALLISTO'];for(const id of ids)assert(report.curves.some(c=>c.feature_id===id&&c.semantic==='PARENT_RELATIVE_REFERENCE_ORBIT'),`${id} reference curve must be governed product content`);
    const omissions=report.features.filter(f=>['PROTEUS','HYDRA','KERBEROS','NIX','STYX','DACTYL','SELAM'].includes(f.body_id)).map(f=>({body_id:f.body_id,geometry_status:f.geometry_status,reason:f.reason}));
    assert.equal(omissions.length,7);for(const row of omissions)assert.equal(row.geometry_status,'UNRESOLVED',`${row.body_id} omission must remain explicit`);
    assert.equal(requests.filter(url=>/authority|resolver|ephemeris|state-api/i.test(url)).length,0,'viewer must make no authority API calls');assert.deepEqual(errors,[],'browser must have no page errors');
    const result={schema:'loom.solar-basemap.generic-local-systems-touch-acceptance/0.1',product_build_id:final.build_id,viewport:{width:412,height:915,dpr:3},node_id:localNode,selected_body_id:final.selected_body_id,pinch_count:pinchTrace.length,pinch_trace:pinchTrace,io_drawn:final.lines.some(x=>x.feature_id==='IO'&&x.node_id===localNode&&x.clip_vertices>0),omissions,authority_calls:0,page_errors:errors};
    fs.writeFileSync(output,JSON.stringify(result,null,2));console.log(JSON.stringify({evidence:output,build_id:final.build_id,jupiter_node:localNode,pinches:pinchTrace.length,io_drawn:result.io_drawn,omission_count:omissions.length}));await page.close();
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1});
