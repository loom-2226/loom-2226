(()=>{'use strict';
const stage=document.getElementById('stage');
if(!stage||window.__loomOrbitalStateInstalled)return;
window.__loomOrbitalStateInstalled=true;
const panel=document.createElement('div');
panel.id='orbitalState';
panel.style.cssText='position:absolute;left:10px;bottom:10px;max-width:min(48%,330px);background:rgba(2,8,10,.80);padding:6px 8px;font:8px/1.35 ui-monospace,monospace;color:#8ea2aa;border-left:2px solid #365e61;pointer-events:none;z-index:5';
panel.innerHTML='<b>ORBIT / EARTH</b><br>STATE UNAVAILABLE';
stage.appendChild(panel);
const fmt=(n,d=1)=>Number.isFinite(Number(n))?Number(n).toFixed(d):'—';
function render(payload){
  const o=payload&&payload.orbital_state;
  if(!o){panel.innerHTML='<b>ORBIT / EARTH</b><br>STATE UNAVAILABLE';return;}
  const bound=o.classification==='BOUND_ELLIPTIC';
  const period=Number(o.period_s);
  const periodText=Number.isFinite(period)?`${fmt(period/60,1)} min`:'—';
  const ap=bound?fmt(o.apoapsis_altitude_km,1):'—';
  const pe=bound?fmt(o.periapsis_altitude_km,1):'—';
  panel.innerHTML=`<b>ORBIT / EARTH • ${String(o.classification||'UNKNOWN')}</b><br>`+
    `ALT ${fmt(o.altitude_km,1)} km • V ${fmt(o.speed_km_s,3)} km/s<br>`+
    `AP ${ap} km • PE ${pe} km<br>`+
    `INC ${fmt(o.inclination_deg,2)}° • ECC ${fmt(o.eccentricity,5)}<br>`+
    `PERIOD ${periodText}<br>`+
    `${String(o.sandbox_state||'FREE_FLIGHT_QUALIFICATION')} • NAV GRADE ${o.navigation_grade===true?'YES':'NO'}`;
}
window.addEventListener('loom-live-qualification',e=>render(e&&e.detail));
if(window.__loomLiveQualification)render(window.__loomLiveQualification);
})();
