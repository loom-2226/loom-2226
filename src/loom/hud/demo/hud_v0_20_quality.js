(()=>{'use strict';
const panel=document.getElementById('qualityPanel');
if(!panel)return;
const fmt=(n,d=2)=>Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
function render(payload){
  const q=payload&&payload.quality||null,f=payload&&payload.final||{},s=payload&&payload.search||{},a=payload&&payload.attitude_transitions||null;
  if(!q){panel.innerHTML='<b>TRAJECTORY QUALITY</b><br>NO CORRECTED RENDEZVOUS SOLUTION LOADED';panel.className='quality neutral';return;}
  const solved=q.status==='SOLVED_TRANSLATIONAL_FEASIBILITY';
  const flags=[
    ['POS',q.position_ok],['VEL',q.velocity_ok],['CLEAR',q.surface_clearance_ok],['REMASS',q.remass_ok]
  ].map(([k,v])=>`${k}:${v?'PASS':'FAIL'}`).join(' • ');
  const attitude=a?`Q4 ATT ${a.control_case||'—'} • INIT ${fmt(a.initial_angle_deg,1)}°/${fmt(a.initial_transition_s,2)}s • FLIP ${fmt(a.flip_angle_deg,1)}°/${fmt(a.flip_transition_s,2)}s`:'Q4 ATTITUDE DATA UNAVAILABLE';
  panel.className='quality '+(solved?'good':'badq');
  panel.innerHTML=`<b>${solved?'SOLVED — TRANSLATIONAL FEASIBILITY':'NOT SOLVED'}</b><br>`+
    `TARGET ERR ${fmt(f.target_position_error_km,1)} km • REL V ${fmt(f.relative_speed_km_s,3)} km/s<br>`+
    `MIN CLEAR ${fmt(f.min_surface_clearance_km,1)} km • REMASS ${fmt(f.remass_t,1)} t<br>`+
    `${flags}<br>`+
    `ITER ${fmt(s.selected_iteration,0)} / ${fmt(s.corrector_iterations_max,0)} • CANDIDATES ${fmt(s.candidate_count,0)}<br>`+
    `<span>${attitude} • TORCH OFF DURING SLEW • NOT NAVIGATOR AUTHORITY</span>`;
}
window.addEventListener('loom-rendezvous-quality',e=>render(e.detail));
if(window.__loomRendezvousQuality)render(window.__loomRendezvousQuality);
})();
