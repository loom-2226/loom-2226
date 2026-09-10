(()=>{'use strict';
const stage=document.getElementById('stage');
if(!stage||window.__loomWayfarerEngineeringPanelInstalled)return;
window.__loomWayfarerEngineeringPanelInstalled=true;
const panel=document.createElement('div');
panel.id='wayfarerEngineering';
panel.style.cssText='position:absolute;right:10px;bottom:34px;max-width:48%;background:rgba(2,8,10,.82);padding:6px 8px;font:8px/1.35 ui-monospace,monospace;color:#8ea2aa;border-right:2px solid #365e61;pointer-events:none;z-index:5;text-align:right';
panel.textContent='WAYFARER ENGINEERING —';stage.appendChild(panel);
const f=n=>Number(n).toFixed(0);
fetch('/wayfarer-engineering-state.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(s=>{
  const m=s.mass||{},t=s.torch||{},p=s.power_thermal||{},d=s.dispatch||{},fs=s.feedstock||{};
  const cards=t.mode_cards||{};const c=cards.CRUISE||{};
  const area=((p.radiator||{}).candidate_effective_area_m2)||[];
  const heat=((p.torch||{}).normal_ship_coupled_heat_ceiling_MW);
  const q5=p.qualification_status||p.status||'OPEN';
  const feed=fs.primary_candidate||'OPEN';
  const cert=(fs.certified_species||[]).length?fs.certified_species.join(','):'NONE';
  panel.innerHTML=`PR96 ${String((s.source||{}).commit||'').slice(0,7)} • NON-CANON<br>`+
    `MASS ${m.reference_wet_mass_t}t WET / ${m.dry_mass_t}t DRY • REMASS ${m.normal_remass_allowance_t}t<br>`+
    `PROTECTED WATER ${m.protected_water_reserve_t}t • OPTIMIZER ACCESS NO<br>`+
    `CRUISE ${c.acceleration_g}g / ${c.exhaust_velocity_km_s}km/s • ${c.status||t.status||'OPEN'}<br>`+
    `Q5 ${q5} • RAD ${area.length?f(Math.min(...area))+'–'+f(Math.max(...area))+'m²':'OPEN'} @ ${(p.radiator||{}).reject_temperature_K||'OPEN'}K • TORCH HEAT ≤${heat||'OPEN'}MW<br>`+
    `Q7 ${d.status||'OPEN'} • NORMAL ${d.normal_dispatch_remass_t}t • MIN ${d.minimum_dispatch_remass_t}t • OPT RES ${d.protected_optimizer_reserve_t}t<br>`+
    `FEED ${feed} PRIMARY CANDIDATE • CERTIFIED ${cert}`;
}).catch(e=>{panel.textContent='WAYFARER ENGINEERING UNAVAILABLE • '+e.message;panel.style.color='#ef8f8f'});
})();
