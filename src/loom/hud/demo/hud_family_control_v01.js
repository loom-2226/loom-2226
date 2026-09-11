(()=>{'use strict';
const select=document.getElementById('hudFamily');
const state=document.getElementById('hudFamilyState');
if(!select||!state)return;
const ALLOWED=new Set(['AUTO','TACTICAL','NAV / FLIGHT PLAN','NAV / METRIC','SENSOR / WIDE','TACTICAL / TRACK']);
let automatic='TACTICAL';
let reason='DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM';
function effective(){return select.value==='AUTO'?automatic:select.value}
function render(){const f=effective();state.textContent=`HUD ${f} • ${select.value==='AUTO'?'AUTO '+reason:'MANUAL OVERRIDE / PRESENTATION ONLY'}`;document.documentElement.dataset.loomHudFamily=f;window.dispatchEvent(new CustomEvent('loom-hud-family-applied',{detail:{family:f,automatic_family:automatic,selection_mode:select.value==='AUTO'?'AUTO':'MANUAL_OVERRIDE_PRESENTATION_ONLY',reason}}));}
function setAutomatic(family,why){if(!ALLOWED.has(family)||family==='AUTO')return;automatic=family;reason=why;render()}
function hasLiveTrack(payload){const m=payload&&payload.moon,w=payload&&payload.wayfarer;if(!(m&&w))return false;return Array.isArray(m.relative_to_wayfarer_km)&&Array.isArray(m.velocity_earth_centered_km_s)&&Array.isArray(w.velocity_earth_centered_km_s);}
function consumeLive(payload){if(hasLiveTrack(payload))setAutomatic('TACTICAL / TRACK','LOCAL_GEOMETRY_TACTICAL_QUALITY');else setAutomatic('TACTICAL','DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM');}
function consumeRendezvous(payload){const status=payload&&payload.quality&&payload.quality.status;if(status==='SOLVED_TRANSLATIONAL_FEASIBILITY')setAutomatic('NAV / FLIGHT PLAN','STRATEGIC_PLANNING_SOLVED_TRANSLATIONAL_FEASIBILITY');}
window.addEventListener('loom-live-qualification',e=>consumeLive(e&&e.detail));
window.addEventListener('loom-rendezvous-quality',e=>consumeRendezvous(e&&e.detail));
window.addEventListener('loom-hud-family',e=>{const d=e&&e.detail||{};if(ALLOWED.has(d.family)&&d.family!=='AUTO')automatic=d.family;if(d.reason)reason=String(d.reason);render()});
select.addEventListener('change',()=>{if(!ALLOWED.has(select.value))select.value='AUTO';render()});
if(window.__loomLiveQualification)consumeLive(window.__loomLiveQualification);
if(window.__loomRendezvousQuality)consumeRendezvous(window.__loomRendezvousQuality);
render();
})();
