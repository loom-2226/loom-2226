(()=>{'use strict';
const button=document.getElementById('earthOrbit400');
if(!button||window.__loomOrbitalControlInstalled)return;
window.__loomOrbitalControlInstalled=true;
button.addEventListener('click',async()=>{
  if(button.disabled)return;
  button.disabled=true;
  const prior=button.textContent;
  button.textContent='SEEDING ORBIT…';
  try{
    const response=await fetch('/qualification-flight/control',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'INITIALIZE_EARTH_ORBIT',altitude_km:400,inclination_deg:0})
    });
    const payload=await response.json();
    if(!response.ok)throw new Error(payload.reason||'orbit initialization rejected');
    window.__loomLiveQualification=payload;
    window.dispatchEvent(new CustomEvent('loom-live-qualification',{detail:payload}));
    button.textContent='EARTH ORBIT 400 km ✓';
    setTimeout(()=>{button.textContent=prior;button.disabled=false},1200);
  }catch(err){
    button.textContent='ORBIT SEED FAILED';
    setTimeout(()=>{button.textContent=prior;button.disabled=false},1800);
    console.error(err);
  }
});
})();
