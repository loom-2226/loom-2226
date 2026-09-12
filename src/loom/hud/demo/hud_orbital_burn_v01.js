(()=>{'use strict';
const pro=document.getElementById('burnPrograde'),retro=document.getElementById('burnRetrograde'),dur=document.getElementById('orbitalBurnS'),state=document.getElementById('orbitalBurnState'),mode=document.getElementById('mode');
if(!pro||!retro||!dur||!state||window.__loomOrbitalBurnInstalled)return;
window.__loomOrbitalBurnInstalled=true;
const row=pro.closest('.row');
let vectorSelect=document.getElementById('orbitalBurnDirection'),vectorBurn=document.getElementById('burnOrbitalDirection');
if(row&&!vectorSelect&&!vectorBurn){
 vectorSelect=document.createElement('select');vectorSelect.id='orbitalBurnDirection';vectorSelect.setAttribute('aria-label','Orbital burn direction');
 [['RADIAL_OUT','RADIAL OUT'],['RADIAL_IN','RADIAL IN'],['NORMAL','NORMAL'],['ANTINORMAL','ANTINORMAL']].forEach(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;vectorSelect.appendChild(o);});
 vectorBurn=document.createElement('button');vectorBurn.id='burnOrbitalDirection';vectorBurn.className='execute-burn';vectorBurn.textContent='BURN VECTOR';
 row.insertBefore(vectorSelect,state);row.insertBefore(vectorBurn,state);
}
let busy=false;
const controls=()=>[pro,retro,vectorSelect,vectorBurn].filter(Boolean);
const fmt=(n,d=2)=>Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
async function execute(direction){
 if(busy)return;busy=true;controls().forEach(x=>x.disabled=true);state.textContent=`EXECUTING ${direction}…`;
 try{
  const body={action:'EXECUTE_VELOCITY_BURN',direction,duration_s:Number(dur.value),mode:mode?mode.value:'CRUISE'};
  const r=await fetch('/qualification-flight/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),d=await r.json();
  if(!r.ok||d.contract!=='LOOM_HUD_EXECUTION_RESPONSE_V1')throw new Error(d.reason||`HTTP ${r.status}`);
  const x=d.receipt||{},a=x.attitude_transition||{},e=x.execution||{},end=x.end||{};
  state.textContent=`${direction} EXECUTED • BURN ${fmt(e.burn_elapsed_s,1)}s • SLEW ${fmt(a.transition_time_s,1)}s • V ${fmt(end.speed_km_s,3)} km/s • REMASS ${fmt(end.remass_t,2)} t`;
  if(d.live)window.dispatchEvent(new CustomEvent('loom-live-qualification',{detail:d.live}));
 }catch(err){state.textContent=`BURN REJECTED • ${String(err&&err.message||err)}`;}
 finally{busy=false;controls().forEach(x=>x.disabled=false);}
}
pro.addEventListener('click',()=>execute('PROGRADE'));
retro.addEventListener('click',()=>execute('RETROGRADE'));
if(vectorBurn&&vectorSelect)vectorBurn.addEventListener('click',()=>execute(vectorSelect.value));
})();
