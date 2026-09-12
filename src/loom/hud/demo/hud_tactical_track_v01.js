(()=>{'use strict';
const box=document.getElementById('tacticalTrack');
if(!box)return;
const mag=a=>Math.hypot(Number(a[0]),Number(a[1]),Number(a[2]));
function render(j){
  if(!(j&&j.moon&&j.wayfarer)){
    box.innerHTML='<b>TACTICAL / TRACK</b><br>LIVE RELATIVE STATE UNAVAILABLE';
    return;
  }
  const r=j.moon.relative_to_wayfarer_km;
  const vm=j.moon.velocity_earth_centered_km_s;
  const vs=j.wayfarer.velocity_earth_centered_km_s;
  if(!(Array.isArray(r)&&Array.isArray(vm)&&Array.isArray(vs))){
    box.innerHTML='<b>TACTICAL / TRACK</b><br>LIVE RELATIVE STATE UNAVAILABLE';
    return;
  }
  const range=mag(r);
  const rv=[vm[0]-vs[0],vm[1]-vs[1],vm[2]-vs[2]];
  const relSpeed=mag(rv);
  const radial=range>0?(r[0]*rv[0]+r[1]*rv[1]+r[2]*rv[2])/range:NaN;
  const radialText=Number.isFinite(radial)?`${radial>=0?'+':''}${radial.toFixed(3)} km/s`:'—';
  const state=!Number.isFinite(radial)?'UNKNOWN':Math.abs(radial)<0.005?'RADIAL HOLD':radial<0?'CLOSING':'RECEDING';
  const eph=j.ephemeris&&j.ephemeris.moon_source?String(j.ephemeris.moon_source):'NOT PROVIDED';
  const authority=j.authority?String(j.authority):'NOT PROVIDED';
  box.innerHTML=`<b>TACTICAL / TRACK • MOON</b><br>`+
    `RANGE ${Number.isFinite(range)?range.toFixed(1):'—'} km<br>`+
    `RANGE RATE ${radialText} • ${state}<br>`+
    `REL SPEED ${Number.isFinite(relSpeed)?relSpeed.toFixed(3):'—'} km/s<br>`+
    `TRACK SOURCE ${eph}<br>`+
    `AUTH ${authority} • NAV GRADE ${j.navigation_grade===true?'YES':'NO'}<br>`+
    `UNCERTAINTY NOT PROVIDED`;
}
window.addEventListener('loom-live-qualification',e=>render(e&&e.detail));
if(window.__loomLiveQualification)render(window.__loomLiveQualification);else render(null);
})();
