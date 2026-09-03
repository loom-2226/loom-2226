(() => {
'use strict';
const PLANNING_SCHEMA='LOOM_GIS_FLIGHT_PLANNING_V1';
const ENTITY_TO_TOKEN={ME:'MERCURY',VE:'VENUS',EA:'EARTH',LU:'LUNA',MA:'MARS',CER:'CERES',JU:'JUPITER_SYSTEM',SA:'SATURN_SYSTEM',UR:'URANUS_SYSTEM',NE:'NEPTUNE_SYSTEM',PL:'PLUTO_SYSTEM'};
let planning=null,busy=false;

function escP(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
function destinationFromSelection(){
  if(!scene||!selectedEntityId)return null;
  const e=(scene.entities||[]).find(x=>x.entity_id===selectedEntityId);if(!e)return null;
  if(ENTITY_TO_TOKEN[e.entity_id])return ENTITY_TO_TOKEN[e.entity_id];
  if(e.entity_class==='MOON')return String(e.entity_id||'').toUpperCase();
  if(e.entity_class==='INFRASTRUCTURE')return String(e.parent_entity_id||e.entity_id||'').toUpperCase();
  return String(e.entity_id||'').toUpperCase();
}
function fmt(v,d=2){const n=Number(v);return Number.isFinite(n)?n.toFixed(d):'—'}
function mins(v){const n=Number(v);if(!Number.isFinite(n))return '—';if(n>=1440)return (n/1440).toFixed(2)+' d';if(n>=60)return (n/60).toFixed(2)+' h';return n.toFixed(1)+' min'}
async function postPlanning(action,body={}){
  if(busy)return null;busy=true;renderPlanning();
  try{
    const r=await fetch('/flight-planning/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),cache:'no-store'});
    const x=await r.json();if(!r.ok)throw new Error(x.error||`HTTP ${r.status}`);planning=x;
    if(planning.preview_overlay)window.dispatchEvent(new CustomEvent('loom-navigation-overlay',{detail:planning.preview_overlay}));
    renderPlanning();return x;
  }catch(err){console.warn('LOOM flight planning',err);const s=document.querySelector('#flightPlanningPanel .fpStatus');if(s)s.textContent='ERROR · '+err.message;return null}
  finally{busy=false;renderPlanning()}
}
function candidateCard(c){
  const s=c.summary||{},selected=planning?.preview_route_id===c.route_id,committed=planning?.committed_route_id===c.route_id;
  const disabled=s.selectable===false?'disabled':'';
  return `<div class="fpCandidate ${selected?'selected':''} ${committed?'committed':''}"><div class="fpCandHead"><b>${escP(s.strategy||c.route_id)}</b><span>${committed?'COMMITTED':selected?'PREVIEW':''}</span></div><div class="fpGrid"><div>TIME</div><b>${escP(mins(s.duration_minutes))}</b><div>REMASS</div><b>${escP(fmt(s.remass_t,3))} t</b><div>HOLONOMY</div><b>${escP(fmt(s.holonomy,3))}</b><div>CONFIDENCE</div><b>${escP(fmt(s.confidence,3))}</b></div><div class="fpActions"><button data-preview="${escP(c.route_id)}" ${disabled}>PLAN DETAILS</button><button data-commit="${escP(c.route_id)}" ${disabled}>COMMIT</button></div></div>`;
}
function renderPlanning(){
  const p=document.getElementById('flightPlanningPanel');if(!p||!planning)return;
  const dest=destinationFromSelection();
  p.querySelector('.fpOrigin').textContent=planning.origin||'—';
  p.querySelector('.fpDestination').textContent=planning.destination||dest||'SELECT ON MAP';
  p.querySelector('.fpStatus').textContent=busy?'NAVIGATOR WORKING…':planning.committed_route_id?'PLAN COMMITTED · EXECUTION WAITS FOR PHASE 6':planning.preview_route_id?'PREVIEW · CAMPAIGN STATE UNCHANGED':planning.candidates?.length?`${planning.candidates.length} CANDIDATE(S)`:'SELECT DESTINATION';
  const list=p.querySelector('.fpCandidates');list.innerHTML=(planning.candidates||[]).map(candidateCard).join('');
  list.querySelectorAll('[data-preview]').forEach(b=>b.onclick=()=>postPlanning('preview',{route_id:b.dataset.preview}));
  list.querySelectorAll('[data-commit]').forEach(b=>b.onclick=()=>postPlanning('commit',{route_id:b.dataset.commit}));
  const discover=p.querySelector('.fpDiscover');discover.disabled=busy||!dest||dest===planning.origin;discover.textContent=dest?`DISCOVER ROUTES · ${dest}`:'SELECT DESTINATION ON MAP';
}
function installPlanningPanel(){
  if(document.getElementById('flightPlanningPanel'))return;
  const style=document.createElement('style');style.textContent=`#flightPlanningPanel{position:fixed;left:max(10px,env(safe-area-inset-left));top:86px;z-index:14;width:min(310px,82vw);max-height:58vh;overflow:auto;background:rgba(10,14,20,.94);border:1px solid rgba(150,165,185,.30);border-radius:11px;padding:8px;backdrop-filter:blur(9px);font:9px ui-monospace,SFMono-Regular,Menlo,monospace;color:#aeb9c8}#flightPlanningPanel .fpTitle{font-weight:850;letter-spacing:.09em;color:#d9e4f2;margin-bottom:6px}.fpRoute{display:grid;grid-template-columns:68px 1fr;gap:4px 7px;padding:6px;border:1px solid rgba(130,145,165,.16);border-radius:8px}.fpRoute b{color:#e1e9f3;overflow-wrap:anywhere}.fpStatus{margin:6px 2px;color:#8897aa;line-height:1.35}.fpDiscover{width:100%;font:800 9px ui-monospace,SFMono-Regular,Menlo,monospace}.fpCandidate{margin-top:6px;padding:7px;border:1px solid rgba(130,145,165,.18);border-radius:8px;background:rgba(255,255,255,.018)}.fpCandidate.selected{border-color:rgba(189,165,255,.58)}.fpCandidate.committed{border-color:rgba(99,214,229,.65)}.fpCandHead{display:flex;justify-content:space-between;gap:6px;color:#d8e2ef}.fpCandHead span{color:#63d6e5}.fpGrid{display:grid;grid-template-columns:1fr 1fr;gap:3px 8px;margin-top:6px}.fpGrid div{color:#7f8b9c}.fpActions{display:flex;gap:5px;margin-top:7px}.fpActions button{flex:1;min-width:0;padding:5px;font-size:8px}.fpBottom{display:flex;gap:5px;margin-top:6px}.fpBottom button{flex:1;min-width:0;padding:5px;font-size:8px}`;document.head.appendChild(style);
  const p=document.createElement('div');p.id='flightPlanningPanel';p.innerHTML='<div class="fpTitle">PLAN FLIGHT</div><div class="fpRoute"><div>ORIGIN</div><b class="fpOrigin">—</b><div>DEST</div><b class="fpDestination">SELECT ON MAP</b><div>PRIORITY</div><b>BALANCED</b></div><div class="fpStatus">LOADING…</div><button class="fpDiscover">SELECT DESTINATION ON MAP</button><div class="fpCandidates"></div><div class="fpBottom"><button class="fpCancel">CANCEL</button></div>';document.body.appendChild(p);
  p.querySelector('.fpDiscover').onclick=()=>{const d=destinationFromSelection();if(d)postPlanning('discover',{destination:d,priority:'BALANCED'})};
  p.querySelector('.fpCancel').onclick=()=>postPlanning('cancel',{});
  canvas.addEventListener('pointerup',()=>setTimeout(renderPlanning,0));
}
fetch('/flight-planning.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(x=>{if(x.contract!==PLANNING_SCHEMA)throw new Error(`unsupported planning schema ${x.contract}`);planning=x;installPlanningPanel();renderPlanning()}).catch(err=>console.warn('LOOM flight planning unavailable',err));
})();
