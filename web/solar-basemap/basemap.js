/* Shared deterministic selection, verified loader and reconciliation contract. */
(function(root,factory){const api=factory(); if(typeof module==="object"&&module.exports) module.exports=api; root.LoomBasemap=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
  const cache=new Map();
  function selectLevel(levels,sse,state={}){
    if(!levels||!levels.length)return null;
    const sorted=[...levels].sort((a,b)=>a.level-b.level);
    let chosen=sorted.at(-1);
    for(const l of sorted){if(l.measured_error_km*sse<=0.75){chosen=l;break;}}
    const current=sorted.find(l=>l.level===state.current_level);
    if(current&&chosen.level<current.level){
      if(chosen.measured_error_km*sse>=0.35){state.below_since=null;return current;}
      if(!state.below_since)state.below_since=Date.now();
      if(Date.now()-state.below_since<250)return current;
    }else state.below_since=null;
    state.sse=sse;
    return chosen;
  }
  function nodeSelection(root,view){
    const result=[];const levelState=view.levelState||{};
    for(const n of root.nodes){
      if(n.node_id==="solar"||view.visibleNodes?.has(n.node_id)){
        const sorted=[...(n.levels||[])].sort((a,b)=>a.level-b.level);
        const screenError=view.errorScaleByNode?.[n.node_id]||0;
        const state=levelState[n.node_id]||(levelState[n.node_id]={});if(view.activeLevels&&view.activeLevels[n.node_id]!==undefined)state.current_level=view.activeLevels[n.node_id];
        const d=selectLevel(n.levels,screenError,state);
        const current=state.current_level;const ci=sorted.findIndex(x=>x.level===current),next=ci>=0?sorted[ci+1]:null;
        const active=ci>=0?sorted[ci]:null;const prefetch=active&&next&&active.measured_error_km*screenError>0.5&&active.measured_error_km*screenError<=0.75?next:null;
        result.push({node_id:n.node_id,level:d?.level??null,resource:d?.resource||null,prefetch:prefetch||null});
      }
    }
    return result;
  }
  async function bytes(url,key){if(cache.has(key))return cache.get(key);const p=fetch(url,{cache:"force-cache"}).then(async r=>{if(!r.ok)throw Error(`HTTP ${r.status} ${url}`);return new Uint8Array(await r.arrayBuffer());});cache.set(key,p);try{return await p}catch(e){cache.delete(key);throw e;}}
  async function jsonVerified(base,desc,monolithic,buildId){const key=`${buildId}:${desc.uri}:${desc.sha256}`;let b;if(monolithic&&monolithic[desc.uri]){const bin=atob(monolithic[desc.uri]);b=Uint8Array.from(bin,c=>c.charCodeAt(0));}else{const u=new URL("product/"+desc.uri,base);b=await bytes(u,key);}try{const hash=hex(new Uint8Array(await crypto.subtle.digest("SHA-256",b)));if(hash!==desc.sha256||b.byteLength!==desc.bytes)throw Error(`integrity mismatch ${desc.uri}`);return JSON.parse(new TextDecoder().decode(b));}finally{cache.delete(key);}}
  function hex(bytes){return [...bytes].map(x=>x.toString(16).padStart(2,"0")).join("");}
  async function loadBasemap(manifestURL){
    let manifest,monolithic=null;
    if(new URL(manifestURL).searchParams.get('delivery')==='monolithic'){const response=await fetch(manifestURL,{cache:'no-store'});if(!response.ok)throw Error('monolithic product fetch failed');monolithic=await response.json();manifest=monolithic.manifest;}
    else{const manifestResponse=await fetch(manifestURL,{cache:"no-cache"});if(!manifestResponse.ok)throw Error("manifest fetch failed");manifest=await manifestResponse.json();}
    if(manifest.schema!=="loom.solar-basemap.manifest/0.1"||manifest.frame!=="ECLIPJ2000"||manifest.center!=="SUN")throw Error("unsupported manifest contract");
    const base=new URL("/",manifestURL);const root=await jsonVerified(base,manifest.root,monolithic?.resources,manifest.build_id);if(root.schema!=="loom.solar-basemap.root/0.1")throw Error("unsupported root schema");
    if(root.features.length!==manifest.counts.catalog||new Set(root.features.map(f=>f.body_id)).size!==root.features.length)throw Error("catalog identity mismatch");
    const nodeIds=new Set(root.nodes.map(n=>n.node_id));if(!nodeIds.has("solar")||root.nodes.some(n=>n.parent_node_id&&!nodeIds.has(n.parent_node_id)))throw Error("hierarchy mismatch");
    const parents=new Map(root.nodes.map(n=>[n.node_id,n.parent_node_id]));for(const id of nodeIds){const seen=new Set();let at=id;while(at!=null){if(seen.has(at))throw Error("cyclic hierarchy");seen.add(at);at=parents.get(at);}}
    if(root.curves.some(c=>!['HELIOCENTRIC_REFERENCE_ORBIT','PARENT_RELATIVE_REFERENCE_ORBIT','PHYSICAL_TRAJECTORY'].includes(c.semantic)||c.closed))throw Error("unsupported curve semantics");
    let lastSelection=[];const loaded=new Map(),listeners=new Set(),active=new Map(),levelState={},inflight=new Map(),queue=[],priorities=new Map(),lastUsed=new Map();let running=0,maxRunning=0;
    const clientExtension=root.extensions?.['org.loom.solar-basemap.client/0.1']||{};
    const solarEmbedded=clientExtension.solar_embedded_level??0;
    const solarEmbeddedCurves=clientExtension.solar_embedded_curves||{};active.set('solar',solarEmbedded);
    const frontierCost=root.nodes.map(n=>Math.max(0,...n.levels.map(l=>l.resource.bytes+l.vertices*36))).sort((a,b)=>b-a);
    const cacheBudgetBytes=manifest.root.bytes+frontierCost.slice(0,3).reduce((a,b)=>a+b,0);
    function touch(key){if(loaded.has(key)){const v=loaded.get(key);lastUsed.delete(key);lastUsed.set(key,Date.now());return v;}return null;}
    function pinnedKeys(){const out=new Set();for(const [nodeId,level] of active){const node=root.nodes.find(n=>n.node_id===nodeId),desc=node?.levels.find(l=>l.level===level);if(desc)out.add(`${manifest.build_id}:${desc.resource.uri}:${desc.resource.sha256}`);}return out;}
    function trimCache(){const pinned=pinnedKeys();let used=[...loaded.values()].reduce((n,x)=>n+(x.cache_bytes||0),0);let evicted=0;
      for(const key of [...lastUsed.keys()].sort((a,b)=>{const aa=loaded.get(a)?.level??-1,bb=loaded.get(b)?.level??-1;return bb-aa||lastUsed.get(a)-lastUsed.get(b);})){if(used<=cacheBudgetBytes)break;if(pinned.has(key))continue;const x=loaded.get(key);if(!x)continue;used-=x.cache_bytes||0;loaded.delete(key);lastUsed.delete(key);evicted++;}
      return {used_bytes:used,budget_bytes:cacheBudgetBytes,evicted,memory_limit:used>cacheBudgetBytes};}
    function setActive(selection){const visible=new Set(selection.map(d=>d.node_id));for(const key of [...active.keys()])if(key!=='solar'&&!visible.has(key))active.delete(key);
      for(const d of selection){if(!d.resource)continue;const key=`${manifest.build_id}:${d.resource.uri}:${d.resource.sha256}`;if(d.node_id==='solar'&&d.level<=solarEmbedded)active.set('solar',solarEmbedded);else if(loaded.get(key)?.curves)active.set(d.node_id,d.level);}trimCache();}
    function pump(){while(running<(monolithic?1:2)&&queue.length){queue.sort((a,b)=>(priorities.get(a.key)??1e6)-(priorities.get(b.key)??1e6));const task=queue.shift();running++;maxRunning=Math.max(maxRunning,running);const started=performance.now();
      (async()=>{try{const chunk=await jsonVerified(base,task.descriptor,monolithic?.resources,manifest.build_id);if(chunk.build_spec_id!==root.build_spec_id||chunk.node_id!==task.nodeId||chunk.level!==task.level)throw Error('stale or mismatched chunk');const node=root.nodes.find(n=>n.node_id===task.nodeId),desc=node.levels.find(l=>l.level===task.level);loaded.set(task.key,{...chunk,status:'VERIFIED',request_ms:performance.now()-started,cache_bytes:desc.resource.bytes+desc.vertices*36,level:task.level});lastUsed.set(task.key,Date.now());if(lastSelection.some(x=>x.node_id===task.nodeId&&x.level===task.level))active.set(task.nodeId,task.level);task.resolve(chunk);trimCache();}catch(error){const failed={error:String(error),status:'DETAIL_FAILED',request_ms:performance.now()-started,cache_bytes:0};loaded.set(task.key,failed);task.resolve(failed);}finally{running--;inflight.delete(task.key);for(const fn of listeners)fn();pump();}})();}}
    function requestChunk(d){const key=`${manifest.build_id}:${d.resource.uri}:${d.resource.sha256}`;if(loaded.has(key)){touch(key);return Promise.resolve(loaded.get(key));}if(inflight.has(key))return inflight.get(key);let resolve;const promise=new Promise(r=>resolve=r);inflight.set(key,promise);queue.push({key,descriptor:d.resource,nodeId:d.node_id,level:d.level,resolve});pump();return promise;}
    async function loadSelected(selection){setActive(selection);const requests=[];for(const d of selection){if(d.resource)requests.push(d);if(d.prefetch)requests.push({...d,...d.prefetch,prefetch_only:true});}
      const pending=requests.filter(d=>!(d.node_id==='solar'&&d.level<=solarEmbedded)&&!loaded.has(`${manifest.build_id}:${d.resource.uri}:${d.resource.sha256}`));
      pending.forEach((d,i)=>priorities.set(`${manifest.build_id}:${d.resource.uri}:${d.resource.sha256}`,i));await Promise.all(pending.map(requestChunk));setActive(lastSelection);}
    return {manifest,root,catalog:()=>root.features,updateView:view=>{view={...view,levelState,activeLevels:Object.fromEntries(active)};lastSelection=nodeSelection(root,view);loadSelected(lastSelection).then(()=>{for(const fn of listeners)fn();});return Promise.resolve(lastSelection);},onChange:fn=>{listeners.add(fn);return ()=>listeners.delete(fn);},
      drawList:()=>{const out=[];const selected=lastSelection;const solarLevel=active.get('solar')??solarEmbedded;const solarDesc=root.nodes.find(n=>n.node_id==='solar')?.levels.find(l=>l.level===solarLevel);const solarChunk=solarDesc&&solarLevel>solarEmbedded?loaded.get(`${manifest.build_id}:${solarDesc.resource.uri}:${solarDesc.resource.sha256}`):null;
        if(solarLevel<=solarEmbedded||!solarChunk?.curves)for(const c of root.curves)for(const s of c.segments||[])out.push({node_id:c.anchor_id==='SUN'?'solar':`system:${c.anchor_id}`,level:solarEmbeddedCurves[c.feature_id]?.level??solarEmbedded,curve:c,segment:s,verified:true});
        for(const nodeId of new Set(selected.map(x=>x.node_id).filter(x=>x!=='solar'))){const level=active.get(nodeId);if(level===undefined)continue;const d=root.nodes.find(n=>n.node_id===nodeId)?.levels.find(l=>l.level===level);const key=d&&`${manifest.build_id}:${d.resource.uri}:${d.resource.sha256}`,chunk=key&&touch(key);if(chunk?.curves)for(const c of chunk.curves)for(const s of c.segments||[])out.push({node_id:nodeId,level,curve:c,segment:s,verified:true});}return out;},
      inspect:id=>{const f=root.features.find(x=>x.body_id===id);if(!f)return {body_id:id,status:"UNKNOWN"};return {...f,visibility_reason:f.resolution==="UNRESOLVED"?"AUTHORITY_UNRESOLVED":"CAMERA_OR_LAYER_POLICY"};},
      selection:()=>lastSelection.map(d=>{const result=loaded.get(`${manifest.build_id}:${d.resource?.uri}:${d.resource?.sha256}`);return {...d,status:result?.status||'DETAIL_PENDING',error:result?.error||null,request_ms:result?.request_ms??null};}),cacheStats:()=>({entries:cache.size,loaded:loaded.size,active:Object.fromEntries(active),max_concurrent:maxRunning,queued:queue.length,...trimCache()}),dispose:()=>{loaded.clear();queue.length=0;}};
  }
  return {selectLevel,nodeSelection,loadBasemap,_cache:cache};
});
