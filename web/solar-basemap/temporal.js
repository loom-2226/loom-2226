(function(){
  let manifest=null,chunks=new Map(),epoch=null;
  async function json(url){const r=await fetch(url,{cache:'no-cache'});if(!r.ok)throw Error(`temporal fetch ${r.status} ${url}`);return r.json()}
  async function load(){const ptr=await json('/temporal/current.json'),m=await json('/temporal/'+ptr.manifest_uri);manifest=m;epoch=m.start_et;return m}
  function descriptor(t){return manifest?.chunks.find(c=>t>=c.start_et&&t<=c.end_et)||null}
  async function chunk(t){const d=descriptor(t);if(!d)throw Error('epoch outside temporal publication');if(!chunks.has(d.sha256))chunks.set(d.sha256,await json('/temporal/'+d.uri));return chunks.get(d.sha256)}
  function hermite(a,b,t){const h=b.epoch_et-a.epoch_et,u=(t-a.epoch_et)/h,u2=u*u,u3=u2*u,h00=2*u3-3*u2+1,h10=u3-2*u2+u,h01=-2*u3+3*u2,h11=u3-u2;return a.position_km.map((p,i)=>h00*p+h10*h*a.velocity_km_s[i]+h01*b.position_km[i]+h11*h*b.velocity_km_s[i])}
  function relative(o,t){const s=o.samples;if(!s?.length)return null;let lo=0,hi=s.length-1;if(t<s[0].epoch_et||t>s[hi].epoch_et)return null;while(lo+1<hi){const m=(lo+hi)>>1;if(s[m].epoch_et<=t)lo=m;else hi=m}const a=s[lo],b=s[hi];if(a.epoch_et===t)return a.resolution==='RESOLVED'?a.position_km:null;if(b.epoch_et===t)return b.resolution==='RESOLVED'?b.position_km:null;if(a.resolution!=='RESOLVED'||b.resolution!=='RESOLVED')return null;if((a.source_ref!==b.source_ref)||(a.center_source_ref!==b.center_source_ref)||(a.authority_class!==b.authority_class))return null;return hermite(a,b,t)}
  async function evaluate(t){const c=await chunk(t),by=Object.fromEntries(c.objects.map(o=>[o.body_id,o])),memo={SUN:[0,0,0]};function world(id,stack=new Set()){if(memo[id])return memo[id];const o=by[id];if(!o||stack.has(id))return null;const rel=relative(o,t);if(!rel)return null;stack.add(id);const parent=o.center_id==='SUN'?[0,0,0]:world(o.center_id,stack);stack.delete(id);if(!parent)return null;return memo[id]=rel.map((v,i)=>v+parent[i])}for(const id of Object.keys(by))world(id);epoch=t;return memo}
  window.LoomTemporal={load,evaluate,get manifest(){return manifest},get epoch(){return epoch}};
})();
