(()=>{'use strict';
const stage=document.getElementById('stage');
if(!stage||window.__loomWayfarerEngineeringPanelInstalled)return;
window.__loomWayfarerEngineeringPanelInstalled=true;
const panel=document.createElement('div');
panel.id='wayfarerEngineering';
panel.style.cssText='position:absolute;right:10px;bottom:34px;max-width:48%;background:rgba(2,8,10,.82);padding:6px 8px;font:8px/1.35 ui-monospace,monospace;color:#8ea2aa;border-right:2px solid #365e61;pointer-events:none;z-index:5;text-align:right';
panel.textContent='WAYFARER ENGINEERING —';stage.appendChild(panel);
const val=d=>d&&Object.prototype.hasOwnProperty.call(d,'value')?d.value:null;
const q=d=>d&&d.quality?d.quality:'OPEN';
const fmt=n=>Number.isFinite(Number(n))?Number(n).toFixed(0):'OPEN';
fetch('/wayfarer-engineering-state.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(s=>{
  if(s.contract!=='LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1')throw new Error('unexpected engineering contract');
  const m=s.mass||{},d=s.dispatch||{},p=s.power_thermal||{},fs=s.feedstock||{},a=s.attitude||{},cards=s.torch_modes||{};
  const energy=a.energy_screen||{};const c=cards.CRUISE||{};const area=val(p.radiator_effective_area_range)||[];
  const cert=val(fs.certified_species)||[];
  const optimizerWater=val(d.routine_optimizer_may_consume_protected_water);
  const heatPass=val(energy.gross_conversion_heat_within_50GJ_buffer);
  const detailAvailable=val(energy.per_maneuver_detail_available);
  const combinedEnergy=val(energy.combined_maneuver_energy_available);
  const translationEnergy=val(energy.translation_maneuver_energy_available);
  panel.innerHTML=`PR96 ${String(s.source_commit||'').slice(0,7)} • NON-CANON • TYPED<br>`+
    `MASS ${val(m.reference_wet_mass)}t WET / ${val(m.dry_mass)}t DRY • REMASS ${val(m.normal_remass)}t<br>`+
    `PROTECTED WATER ${val(m.protected_water_reserve)}t • OPTIMIZER ACCESS ${optimizerWater===false?'NO':'OPEN'}<br>`+
    `CRUISE ${val(c.acceleration_g)}g / ${val(c.exhaust_velocity)}km/s • ${q(c.status)}<br>`+
    `Q4 ${val(a.status)||'OPEN'}<br>`+
    `Q5 ${val(p.status)||'OPEN'} • RAD ${Array.isArray(area)&&area.length===2?fmt(area[0])+'–'+fmt(area[1])+'m²':'OPEN'} • BUFFER ${Array.isArray(val(p.thermal_buffer_range))?val(p.thermal_buffer_range).join('–')+'GJ':'OPEN'} • TORCH HEAT ≤${val(p.torch_coupled_heat_ceiling)??'OPEN'}MW<br>`+
    `Q5 ATT ENERGY ${val(energy.status)||'OPEN'} • 50GJ SCREEN ${heatPass===true?'PASS':'OPEN'} • DETAIL ${detailAvailable===true?'AVAILABLE':'PENDING MACHINE HANDOFF'}<br>`+
    `Q5 TRANS/COMBINED ENERGY ${translationEnergy===true||combinedEnergy===true?'AVAILABLE':'UNAVAILABLE — TIMING OPEN'}<br>`+
    `Q7 ${val(d.status)||'OPEN'} • NORMAL ${val(d.normal_dispatch_remass)}t • FLOOR ${val(d.operational_remass_floor)}t • OPT RES ${val(d.protected_optimizer_reserve)}t<br>`+
    `FEED ${val(fs.primary)||'OPEN'} • ${q(fs.primary)} • CERTIFIED ${cert.length?cert.join(','):'NONE'}`;
}).catch(e=>{panel.textContent='WAYFARER ENGINEERING UNAVAILABLE • '+e.message;panel.style.color='#ef8f8f'});
})();
