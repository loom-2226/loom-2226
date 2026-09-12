(()=>{'use strict';
const stage=document.getElementById('stage'),scrub=document.getElementById('scrub'),scrubState=document.getElementById('scrubState');
if(!stage||window.__loomRangeRateInstalled)return;
window.__loomRangeRateInstalled=true;
const box=document.createElement('div');
box.id='moonMotion';
box.style.cssText='position:absolute;left:10px;top:112px;background:rgba(2,8,10,.76);padding:5px 8px;font:9px/1.35 ui-monospace,monospace;color:#7fd7d0;border-left:2px solid #7fd7d0;pointer-events:none;z-index:5';
box.textContent='MOON MOTION —';
stage.appendChild(box);
let live=null,preview=null;
const realFetch=window.fetch.bind(window);
window.fetch=async function(...args){
  const response=await realFetch(...args);
  try{
    const u=String(args[0]&&args[0].url||args[0]||'');
    if(response.ok&&(u.includes('/qualification-flight.json')||u.includes('/trajectory-preview.json')||u.includes('/intercept-preview.json')||u.includes('/rendezvous-preview.json'))){
      response.clone().json().then(j=>{
        if(u.includes('/qualification-flight.json')){
          live=j;
          window.__loomLiveQualification=j;
          window.dispatchEvent(new CustomEvent('loom-live-qualification',{detail:j}));
        }else if(j&&Array.isArray(j.points))preview=j;
      }).catch(()=>{});
    }
  }catch(_e){}
  return response;
};
const mag=a=>Math.hypot(Number(a[0]),Number(a[1]),Number(a[2]));
function liveRate(){
  if(!(live&&live.moon&&live.wayfarer))return null;
  const r=live.moon.relative_to_wayfarer_km,vM=live.moon.velocity_earth_centered_km_s,vS=live.wayfarer.velocity_earth_centered_km_s;
  if(!(Array.isArray(r)&&Array.isArray(vM)&&Array.isArray(vS)))return null;
  const R=mag(r);if(!(R>0))return null;
  const rv=[vM[0]-vS[0],vM[1]-vS[1],vM[2]-vS[2]];
  return {rate:(r[0]*rv[0]+r[1]*rv[1]+r[2]*rv[2])/R,source:'VECTOR'};
}
function pointRange(p){
  if(!p)return NaN;
  if(Array.isArray(p.moon_relative_to_wayfarer_km))return mag(p.moon_relative_to_wayfarer_km);
  if(Array.isArray(p.moon_position_earth_centered_km)&&Array.isArray(p.wayfarer_position_earth_centered_km))return mag(p.moon_position_earth_centered_km.map((x,i)=>Number(x)-Number(p.wayfarer_position_earth_centered_km[i])));
  return NaN;
}
function previewRate(){
  const pts=preview&&preview.points;if(!(Array.isArray(pts)&&pts.length>=2&&scrub))return null;
  const i=Math.max(0,Math.min(pts.length-1,Math.round((Number(scrub.value)/100)*(pts.length-1))));
  const a=i===0?0:i-1,b=i===pts.length-1?pts.length-1:i+1;if(a===b)return null;
  const ra=pointRange(pts[a]),rb=pointRange(pts[b]),ta=Number(pts[a].elapsed_s),tb=Number(pts[b].elapsed_s);
  if(!(Number.isFinite(ra)&&Number.isFinite(rb)&&Number.isFinite(ta)&&Number.isFinite(tb)&&tb>ta))return null;
  return {rate:(rb-ra)/(tb-ta),source:'SAMPLED'};
}
function update(){
  const inPreview=!!(scrubState&&String(scrubState.textContent||'').startsWith('PREVIEW'));
  const q=inPreview?previewRate():liveRate();
  if(!q||!Number.isFinite(q.rate)){box.textContent='MOON MOTION —';return}
  const eps=.005,r=q.rate;
  const state=Math.abs(r)<eps?'RADIAL HOLD':r<0?'CLOSING':'RECEDING';
  const speed=Math.abs(r).toFixed(3),signed=(r>=0?'+':'')+r.toFixed(3);
  box.innerHTML=`MOON ${state} ${speed} km/s<br>dR/dt ${signed} km/s • ${q.source} DERIVED`;
}
setInterval(update,100);
})();
