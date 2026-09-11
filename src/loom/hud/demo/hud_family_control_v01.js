(()=>{'use strict';
const select=document.getElementById('hudFamily');
const state=document.getElementById('hudFamilyState');
if(!select||!state)return;
const ALLOWED=new Set(['AUTO','TACTICAL','NAV / FLIGHT PLAN','NAV / METRIC','SENSOR / WIDE','TACTICAL / TRACK']);
let automatic='TACTICAL / TRACK';
let reason='LOCAL_GEOMETRY_TACTICAL_QUALITY';
function effective(){return select.value==='AUTO'?automatic:select.value}
function render(){const f=effective();state.textContent=`HUD ${f} • ${select.value==='AUTO'?'AUTO '+reason:'MANUAL OVERRIDE / PRESENTATION ONLY'}`;document.documentElement.dataset.loomHudFamily=f;}
function setAutomatic(family,why){if(!ALLOWED.has(family)||family==='AUTO')return;automatic=family;reason=why;render()}
window.addEventListener('loom-hud-family',e=>{const d=e&&e.detail||{};if(ALLOWED.has(d.family)&&d.family!=='AUTO')automatic=d.family;if(d.reason)reason=String(d.reason);render()});
select.addEventListener('change',()=>{if(!ALLOWED.has(select.value))select.value='AUTO';render()});
for(const id of ['preview','solve','rendezvous'])document.getElementById(id)?.addEventListener('click',()=>setAutomatic('NAV / FLIGHT PLAN','STRATEGIC_PLANNING_PRESENTATION'));
document.getElementById('liveView')?.addEventListener('click',()=>setAutomatic('TACTICAL / TRACK','LOCAL_GEOMETRY_TACTICAL_QUALITY'));
document.getElementById('reset')?.addEventListener('click',()=>setAutomatic('TACTICAL / TRACK','LOCAL_GEOMETRY_TACTICAL_QUALITY'));
render();
})();
