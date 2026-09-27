#!/usr/bin/env node
const assert=require('node:assert/strict'),crypto=require('node:crypto');
global.crypto=crypto.webcrypto;
const {loadBasemap}=require('../web/solar-basemap/basemap.js');
function bytes(value){return Buffer.from(JSON.stringify(value));}
function fixture({cycle=false,semantic='HELIOCENTRIC_REFERENCE_ORBIT',badHash=false,badChunk=false}={}){
 const root={schema:'loom.solar-basemap.root/0.1',build_spec_id:'spec',epoch_et:7131844800,
  features:[{body_id:'EARTH',resolution:'RESOLVED'}],
  nodes:[{node_id:'solar',parent_node_id:cycle?'system:x':null,levels:[]},
         {node_id:'system:MARS',parent_node_id:'solar',levels:[{level:0,resource:{uri:'objects/chunk.json',sha256:'0'.repeat(64),bytes:10},measured_error_km:0,vertices:1}]},
         ...(cycle?[{node_id:'system:x',parent_node_id:'solar',levels:[]}]:[])],
  curves:[{feature_id:'EARTH',semantic:'HELIOCENTRIC_REFERENCE_ORBIT',anchor_id:'SUN',closed:false,segments:[{points:[[1,1,0,0],[2,2,0,0]]}]},
          {feature_id:'PHOBOS',semantic:semantic==='HELIOCENTRIC_REFERENCE_ORBIT'?'PARENT_RELATIVE_REFERENCE_ORBIT':semantic,anchor_id:'MARS',closed:false,segments:[]}],extensions:{'org.loom.solar-basemap.client/0.1':{solar_embedded_level:0}}};
 const rootBytes=bytes(root),rootHash=crypto.createHash('sha256').update(rootBytes).digest('hex');
 const rootDesc={uri:'objects/root.json',sha256:badHash?'f'.repeat(64):rootHash,bytes:rootBytes.length};
 const manifest={schema:'loom.solar-basemap.manifest/0.1',frame:'ECLIPJ2000',center:'SUN',counts:{catalog:1},build_id:'build',root:rootDesc};
 const manifestBytes=bytes(manifest);
 const chunk={schema:'loom.solar-basemap.chunk/0.1',build_spec_id:badChunk?'stale':'spec',node_id:'system:MARS',level:0,curves:[]};
 const chunkBytes=bytes(chunk);const chunkDesc={uri:'objects/chunk.json',sha256:crypto.createHash('sha256').update(chunkBytes).digest('hex'),bytes:chunkBytes.length};
 root.nodes.find(n=>n.node_id==='system:MARS').levels[0].resource=chunkDesc;
 // Re-encode the now complete root and update its manifest descriptor.
 const completeRootBytes=bytes(root);manifest.root={uri:'objects/root.json',sha256:badHash?'f'.repeat(64):crypto.createHash('sha256').update(completeRootBytes).digest('hex'),bytes:completeRootBytes.length};
 const resources={'objects/root.json':completeRootBytes.toString('base64'),'objects/chunk.json':chunkBytes.toString('base64')};
 return {manifest,resources,root,rootBytes:completeRootBytes,chunkBytes};
}
function response(value){return {ok:true,json:async()=>value};}
async function run(){
 let authorityCalls=0;
 for(const scenario of ['ok','cycle','unknown','bad_hash','stale_chunk','abort','progressive','dedupe']){
  const f=fixture({cycle:scenario==='cycle',semantic:scenario==='unknown'?'MADE_UP':undefined,badHash:scenario==='bad_hash',badChunk:scenario==='stale_chunk'});
  const requested=[];let releaseChunk=null,chunkRequests=0;global.fetch=async url=>{const u=String(url);requested.push(u);if(u.includes('/authority')||u.includes('/resolve'))authorityCalls++;if(['abort','progressive','dedupe'].includes(scenario)){if(u.endsWith('/product/current.json'))return response(f.manifest);if(u.endsWith('/objects/root.json'))return {ok:true,arrayBuffer:async()=>f.rootBytes};if(u.endsWith('/objects/chunk.json')){chunkRequests++;if(scenario==='progressive')return {ok:true,arrayBuffer:async()=>f.chunkBytes};if(scenario==='dedupe')return new Promise(resolve=>{releaseChunk=()=>resolve({ok:true,arrayBuffer:async()=>f.chunkBytes});});}throw Error('AbortError: request aborted');}return response({manifest:f.manifest,resources:f.resources});};
  if(scenario==='ok'){const handle=await loadBasemap('http://qa/product/current.json?delivery=monolithic');assert.equal(handle.catalog().length,1);}
  else if(scenario==='cycle')await assert.rejects(loadBasemap('http://qa/product/current.json?delivery=monolithic'),/cyclic hierarchy/);
  else if(scenario==='unknown')await assert.rejects(loadBasemap('http://qa/product/current.json?delivery=monolithic'),/unsupported curve semantics/);
  else if(scenario==='bad_hash')await assert.rejects(loadBasemap('http://qa/product/current.json?delivery=monolithic'),/integrity mismatch/);
  else if(scenario==='dedupe'){const h=await loadBasemap('http://qa/product/current.json');const v={errorScaleByNode:{'system:MARS':1},visibleNodes:new Set(['system:MARS'])};h.updateView(v);for(let i=0;i<50&&!releaseChunk;i++)await new Promise(r=>setTimeout(r,2));assert.equal(chunkRequests,1);h.updateView({errorScaleByNode:{},visibleNodes:new Set()});h.updateView(v);assert.equal(chunkRequests,1,'returning to an in-flight node must reuse its pending request');releaseChunk();for(let i=0;i<50&&h.selection().find(x=>x.node_id==='system:MARS')?.status!=='VERIFIED';i++)await new Promise(r=>setTimeout(r,2));assert.equal(h.selection().find(x=>x.node_id==='system:MARS').status,'VERIFIED');assert(h.cacheStats().max_concurrent<=2);}
  else {const mono=!['abort','progressive'].includes(scenario);const handle=await loadBasemap(`http://qa/product/current.json${mono?'?delivery=monolithic':''}`);await handle.updateView({errorScaleByNode:{'system:MARS':1},visibleNodes:new Set(['system:MARS'])});for(let i=0;i<50&&handle.selection().every(x=>x.node_id!=='system:MARS'||x.status==='DETAIL_PENDING');i++)await new Promise(r=>setTimeout(r,2));const detail=handle.selection().find(x=>x.node_id==='system:MARS');if(scenario==='progressive'){assert.equal(detail.status,'VERIFIED');assert(requested.some(u=>new URL(u).pathname==='/product/objects/root.json'),'progressive root URL must not duplicate /product');}else{assert.equal(detail.status,'DETAIL_FAILED');assert.match(detail.error,scenario==='abort'?/AbortError/:/mismatched chunk/);assert.equal(handle.drawList().length,1,'verified coarse root curve must persist after detail failure');}}
 }
 assert.equal(authorityCalls,0);console.log(JSON.stringify({loader_cases:8,authority_calls:authorityCalls,pass:true}));
}
run().catch(e=>{console.error(e);process.exitCode=1;});
