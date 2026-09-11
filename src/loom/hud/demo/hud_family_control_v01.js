(()=>{'use strict';
const select=document.getElementById('hudFamily');
const state=document.getElementById('hudFamilyState');
if(!select||!state)return;
const ALLOWED=new Set(['AUTO','TACTICAL','NAV / FLIGHT PLAN','NAV / METRIC','SENSOR / WIDE','TACTICAL / TRACK']);
let automatic='TACTICAL / TRACK';
let reason='LOCAL_GEOMETRY_TACTICAL_QUALITY';
function effective(){return select.value==='AUTO'?automatic:select.value}
function render(){const f=effective();state.textContent=`HUD ${f} • ${select.value==='AUTO'?'AUTO '+reason:'MANUAL OVERRIDE / PRESENTATION ONLY'}`;document.documentElement.dataset.loomHudFamily=f;}
window.addEventListener('loom-hud-family',e=>{const d=e&&e.detail||{};if(ALLOWED.has(d.family)&&d.family!=='AUTO')automatic=d.family;if(d.reason)reason=String(d.reason);render()});
select.addEventListener('change',()=>{if(!ALLOWED.has(select.value))select.value='AUTO';render()});
render();
})();
