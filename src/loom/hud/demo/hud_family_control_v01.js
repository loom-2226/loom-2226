(()=>{'use strict';
const select=document.getElementById('hudFamily');
const state=document.getElementById('hudFamilyState');
if(!select||!state)return;
const ALLOWED=new Set(['AUTO','TACTICAL','NAV / FLIGHT PLAN','NAV / METRIC','SENSOR / WIDE','TACTICAL / TRACK']);
let automatic='TACTICAL';
let reason='DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM';
function effective(){return select.value==='AUTO'?automatic:select.value}
function render(){const f=effective();state.textContent=`HUD ${f} • ${select.value==='AUTO'?'AUTO '+reason:'MANUAL OVERRIDE / PRESENTATION ONLY'}`;document.documentElement.dataset.loomHudFamily=f;window.dispatchEvent(new CustomEvent('loom-hud-family-applied',{detail:{family:f,automatic_family:automatic,selection_mode:select.value==='AUTO'?'AUTO':'MANUAL_OVERRIDE_PRESENTATION_ONLY',reason}}));}
function consumeSelection(selection){if(!(selection&&ALLOWED.has(selection.family)&&selection.family!=='AUTO'))return;automatic=selection.family;reason=String(selection.reason||'SERVER_STAMPED_RUNTIME_STATE');render();}
function consumePayload(payload){consumeSelection(payload&&payload.hud_family_selection);}
window.addEventListener('loom-live-qualification',e=>consumePayload(e&&e.detail));
window.addEventListener('loom-rendezvous-quality',e=>consumePayload(e&&e.detail));
window.addEventListener('loom-hud-family',e=>{const d=e&&e.detail||{};if(ALLOWED.has(d.family)&&d.family!=='AUTO')automatic=d.family;if(d.reason)reason=String(d.reason);render()});
select.addEventListener('change',()=>{if(!ALLOWED.has(select.value))select.value='AUTO';render()});
if(window.__loomLiveQualification)consumePayload(window.__loomLiveQualification);
if(window.__loomRendezvousQuality)consumePayload(window.__loomRendezvousQuality);
render();
})();
