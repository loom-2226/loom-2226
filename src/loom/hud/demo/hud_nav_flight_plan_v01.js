(()=>{'use strict';
const panel=document.getElementById('navFlightPlan');
if(!panel)return;
const fmt=n=>Number.isFinite(Number(n))?Number(n).toFixed(2):'—';
const speed=v=>Array.isArray(v)&&v.length===3?Math.hypot(Number(v[0])||0,Number(v[1])||0,Number(v[2])||0):null;
const lastPoint=(points,phase)=>{let hit=null;for(const p of (points||[]))if(p&&p.phase===phase)hit=p;return hit;};
function navQuality(payload,point){
  const source=point&&point.state_source?String(point.state_source):'SOURCE UNAVAILABLE';
  return `${payload.status||'QUALIFICATION_ONLY'} / ${payload.navigation_grade?'NAV-GRADE':'NON-NAV-GRADE'} / ${source}`;
}
function render(payload){
  const status=payload&&payload.quality&&payload.quality.status||'NOT_SOLVED';
  if(status!=='SOLVED_TRANSLATIONAL_FEASIBILITY'){
    panel.innerHTML='<b>NAV / FLIGHT PLAN</b><br>NO SOLVED FLIGHT PLAN TABLE • TERMINAL-STATE SOLVE NOT CLOSED';
    panel.className='navplan neutral';
    return;
  }
  const att=payload.attitude_transitions||{};
  const mode=String(payload.mode||'UNKNOWN');
  const frame=`EARTH-CENTERED ${payload.frame||'FRAME UNKNOWN'}`;
  const rows=[
    ['ROTATE_DEPARTURE',Number(att.initial_transition_s)||0,'RCS / Q4 FINITE ATTITUDE'],
    ['BURN',Number(payload.burn1_s)||0,`TORCH ${mode}`],
    ['COAST',Number(payload.coast_s)||0,'TORCH OFF / BALLISTIC'],
    ['ROTATE_BRAKE',Number(att.flip_transition_s)||0,'RCS / Q4 FINITE ATTITUDE'],
    ['BRAKE',Number(payload.burn2_s)||0,`TORCH ${mode}`]
  ];
  let cumulative=0;
  const points=payload.points||[];
  let html='<b>NAV / FLIGHT PLAN • SOLVED QUALIFICATION PREVIEW</b><div class="navplan-grid navplan-head"><span>PHASE</span><span>DURATION</span><span>CUM ETA</span><span>SPEED</span><span>VEL REF</span><span>PROPULSION</span><span>NAV/EPH</span></div>';
  for(const [phase,duration,propulsion] of rows){
    cumulative+=duration;
    const point=lastPoint(points,phase);
    const v=point&&point.wayfarer_velocity_earth_centered_km_s;
    const s=speed(v);
    html+=`<div class="navplan-grid"><span>${phase}</span><span>${fmt(duration)} s</span><span>${fmt(cumulative)} s</span><span>${s===null?'—':fmt(s)+' km/s'}</span><span>${frame}</span><span>${propulsion}</span><span>${navQuality(payload,point)}</span></div>`;
  }
  html+='<div class="navplan-foot">DISPLAY ADAPTER ONLY • EXISTING RENDEZVOUS PAYLOAD • NOT NAVIGATOR TARGETING AUTHORITY</div>';
  panel.innerHTML=html;
  panel.className='navplan good';
}
window.addEventListener('loom-rendezvous-quality',e=>render(e&&e.detail||{}));
if(window.__loomRendezvousQuality)render(window.__loomRendezvousQuality);
else render({quality:{status:'NOT_SOLVED'}});
})();
