(()=>{'use strict';
const pro=document.getElementById('burnPrograde'),retro=document.getElementById('burnRetrograde'),dur=document.getElementById('orbitalBurnS'),state=document.getElementById('orbitalBurnState'),mode=document.getElementById('mode');
if(!pro||!retro||!dur||!state||window.__loomOrbitalBurnInstalled)return;
window.__loomOrbitalBurnInstalled=true;
let busy=false;
const fmt=(n,d=2)=>Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
async function execute(direction){
 if(busy)return;busy=true;pro.disabled=true;retro.disabled=true;state.textContent=`EXECUTING ${direction}…`;
 try{
  const body={action:'EXECUTE_VELOCITY_BURN',direction,duration_s:Number(dur.value),mode:mode?mode.value:'CRUISE'};
  const r=await fetch('/qualification-flight/control',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),d=await r.json();
  if(!r.ok||d.contract!=='LOOM_HUD_EXECUTION_RESPONSE_V1')throw new Error(d.reason||`HTTP ${r.status}`);
  const x=d.receipt||{},a=x.attitude_transition||{},e=x.execution||{},end=x.end||{};
  state.textContent=`${direction} EXECUTED • BURN ${fmt(e.burn_elapsed_s,1)}s • SLEW ${fmt(a.transition_time_s,1)}s • V ${fmt(end.speed_km_s,3)} km/s • REMASS ${fmt(end.remass_t,2)} t`;
  if(d.live)window.dispatchEvent(new CustomEvent('loom-live-qualification',{detail:d.live}));
 }catch(err){state.textContent=`BURN REJECTED • ${String(err&&err.message||err)}`;}
 finally{busy=false;pro.disabled=false;retro.disabled=false;}
}
pro.addEventListener('click',()=>execute('PROGRADE'));
retro.addEventListener('click',()=>execute('RETROGRADE'));
})();
