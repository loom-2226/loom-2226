(()=>{'use strict';
const pro=document.getElementById('burnPrograde'),retro=document.getElementById('burnRetrograde'),dur=document.getElementById('orbitalBurnS'),state=document.getElementById('orbitalBurnState'),mode=document.getElementById('mode');
if(!pro||!retro||!dur||!state||window.__loomOrbitalBurnInstalled)return;
window.__loomOrbitalBurnInstalled=true;
const row=pro.closest('.row');
let vectorSelect=document.getElementById('orbitalBurnDirection'),vectorBurn=document.getElementById('burnOrbitalDirection');
if(row&&!vectorSelect&&!vectorBurn){
 vectorSelect=document.createElement('select');vectorSelect.id='orbitalBurnDirection';vectorSelect.setAttribute('aria-label','Orbital burn direction');
 [['PROGRADE','PROGRADE'],['RETROGRADE','RETROGRADE'],['RADIAL_OUT','RADIAL OUT'],['RADIAL_IN','RADIAL IN'],['NORMAL','NORMAL'],['ANTINORMAL','ANTINORMAL']].forEach(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;vectorSelect.appendChild(o);});
 vectorSelect.value='RADIAL_OUT';
 vectorBurn=document.createElement('button');vectorBurn.id='burnOrbitalDirection';vectorBurn.className='execute-burn';vectorBurn.textContent='BURN VECTOR';
 row.insertBefore(vectorSelect,state);row.insertBefore(vectorBurn,state);
}
let reviewButton=document.getElementById('reviewManeuverPlan'),reviewPanel=document.getElementById('maneuverPlanReview');
if(row&&!reviewButton){
 reviewButton=document.createElement('button');reviewButton.id='reviewManeuverPlan';reviewButton.textContent='REVIEW PLAN';
 row.insertBefore(reviewButton,state);
 reviewPanel=document.createElement('div');reviewPanel.id='maneuverPlanReview';reviewPanel.className='quality neutral';
 reviewPanel.innerHTML='<b>MANEUVER PLAN REVIEW</b><br>NO PLAN STAGED';
 row.parentNode.insertBefore(reviewPanel,row.nextSibling);
}
let busy=false;
const controls=()=>[pro,retro,vectorSelect,vectorBurn].filter(Boolean);
const fmt=(n,d=2)=>Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
function stagedPlan(){
 const direction=vectorSelect?vectorSelect.value:'PROGRADE';
 const duration=Number(dur.value);
 const torchMode=mode?mode.value:'CRUISE';
 return {
  contract:'LOOM_MANEUVER_PLAN_V1',
  objective:`Review ${direction} qualification burn`,
  planner:'HUD_MANUAL_REVIEW',
  execution_policy:'REVIEW_REQUIRED',
  commands:[{
   contract:'LOOM_FLIGHT_COMMAND_V1',
   kind:'TORCH_BURN',
   origin:'MANUAL',
   duration_s:duration,
   torch_mode:torchMode,
   target_direction_inertial:null,
   requested_by:'HUD_MANUAL_REVIEW',
   execution_authority:'NONE_UNTIL_DETERMINISTIC_EXECUTOR_ACCEPTS'
  }],
  review_context:{direction_reference:direction,direction_basis:'CURRENT_LIVE_EARTH_CENTERED_ORBITAL_FRAME_AT_EXECUTION'},
  execution_authority:'NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY'
 };
}
function renderReview(){
 if(!reviewPanel)return;
 const p=stagedPlan(),c=p.commands[0],ctx=p.review_context;
 reviewPanel.className='quality neutral';
 reviewPanel.innerHTML=`<b>MANEUVER PLAN REVIEW / BROWSER STAGED</b><br>${p.objective}<br>POLICY ${p.execution_policy} • AUTHORITY NONE<br>${ctx.direction_reference} • ${fmt(c.duration_s,1)} s • ${c.torch_mode}<br><span class="scale">${p.contract} • ${c.contract} • NON-EXECUTING • TARGET VECTOR NOT RESOLVED UNTIL DETERMINISTIC BOUNDARY</span>`;
 window.__loomStagedManeuverPlan=p;
}
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
if(reviewButton)reviewButton.addEventListener('click',renderReview);
})();
