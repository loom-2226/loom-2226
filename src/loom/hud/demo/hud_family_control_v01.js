(()=>{'use strict';
const select=document.getElementById('hudFamily');
const state=document.getElementById('hudFamilyState');
const liveView=document.getElementById('liveView');
if(!select||!state)return;
const ALLOWED=new Set(['AUTO','TACTICAL','NAV / FLIGHT PLAN','NAV / METRIC','SENSOR / WIDE','TACTICAL / TRACK']);
let automatic='TACTICAL';
let reason='DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM';
let planningHold=false;
let lastLiveSelection=null;
function effective(){return select.value==='AUTO'?automatic:select.value}
function render(){const f=effective();state.textContent=`HUD ${f} • ${select.value==='AUTO'?'AUTO '+reason:'MANUAL OVERRIDE / PRESENTATION ONLY'}`;document.documentElement.dataset.loomHudFamily=f;window.dispatchEvent(new CustomEvent('loom-hud-family-applied',{detail:{family:f,automatic_family:automatic,selection_mode:select.value==='AUTO'?'AUTO':'MANUAL_OVERRIDE_PRESENTATION_ONLY',reason,planning_hold:planningHold}}));}
function validSelection(selection){return !!(selection&&ALLOWED.has(selection.family)&&selection.family!=='AUTO')}
function applySelection(selection){if(!validSelection(selection))return;automatic=selection.family;reason=String(selection.reason||'SERVER_STAMPED_RUNTIME_STATE');render();}
function consumeLive(payload){const selection=payload&&payload.hud_family_selection;if(!validSelection(selection))return;lastLiveSelection=selection;if(planningHold)return;applySelection(selection);}
function consumeRendezvous(payload){const selection=payload&&payload.hud_family_selection;if(!validSelection(selection))return;if(selection.family==='NAV / FLIGHT PLAN')planningHold=true;applySelection(selection);}
function releasePlanningHold(){if(!planningHold)return;planningHold=false;if(validSelection(lastLiveSelection)){automatic=lastLiveSelection.family;reason=`RETURN_LIVE_RELEASE / ${String(lastLiveSelection.reason||'SERVER_STAMPED_RUNTIME_STATE')}`;}else{automatic='TACTICAL';reason='RETURN_LIVE_RELEASE / DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM';}render();}
window.addEventListener('loom-live-qualification',e=>consumeLive(e&&e.detail));
window.addEventListener('loom-rendezvous-quality',e=>consumeRendezvous(e&&e.detail));
window.addEventListener('loom-hud-family',e=>{const d=e&&e.detail||{};if(ALLOWED.has(d.family)&&d.family!=='AUTO')automatic=d.family;if(d.reason)reason=String(d.reason);render()});
if(liveView)liveView.addEventListener('click',releasePlanningHold);
select.addEventListener('change',()=>{if(!ALLOWED.has(select.value))select.value='AUTO';render()});
if(window.__loomLiveQualification)consumeLive(window.__loomLiveQualification);
if(window.__loomRendezvousQuality)consumeRendezvous(window.__loomRendezvousQuality);
render();
})();
