(() => {
'use strict';
const STAGE_F_CONTRACT='LOOM_STAGE_F_INTEGRATED_GIS_3D_V1';
const ROUTE_OVERLAY_URL='/navigation-overlay.json';

function finitePoint(v){return Array.isArray(v)&&v.length>=3&&v.every(x=>Number.isFinite(Number(x)))}
function ordinaryRoutePoints(route){
  const out=[];
  for(const seg of route?.segments||[]){
    if(seg?.geometry_semantics?.ordinary_space_occupancy===false)continue;
    for(const p of seg?.geometry_points_j2000_ecliptic_km||[])if(finitePoint(p))out.push(p.map(Number));
  }
  return out;
}
function routeAxis(points){
  if(!Array.isArray(points)||points.length<2)return null;
  const a=points[0],b=points[points.length-1],d=[b[0]-a[0],b[1]-a[1],b[2]-a[2]];
  return Math.hypot(d[0],d[1],d[2])>0?d:null;
}
async function activeRoute(){
  try{
    const response=await fetch(ROUTE_OVERLAY_URL,{cache:'no-store'});
    if(!response.ok)return null;
    const payload=await response.json();
    return payload?.active_route||null;
  }catch(_err){return null}
}
function applyRouteCamera(route){
  const axis=routeAxis(ordinaryRoutePoints(route));
  if(axis&&typeof yaw!=='undefined'){
    const az=Math.atan2(axis[1],axis[0]);
    yaw=-az+Math.PI/4;
  }
  if(typeof pitch!=='undefined')pitch=.96;
  if(typeof scheduleDraw==='function')scheduleDraw();
}
async function activateRoute3D(panel,button){
  const oblique=document.getElementById('obl');
  if(oblique)oblique.click();
  const route=await activeRoute();
  applyRouteCamera(route);
  const currentFit=panel.querySelector('.navFit');
  if(currentFit&&!currentFit.hidden)currentFit.click();
  button.classList.add('active');
}

function installStageFRoute3D(){
  const panel=document.getElementById('navOverlayPanel');
  if(!panel||panel.dataset.stageF3d===STAGE_F_CONTRACT)return false;
  const actions=panel.querySelector('.navActions');
  const fit=panel.querySelector('.navFit');
  if(!actions||!fit)return false;

  const button=document.createElement('button');
  button.type='button';
  button.className='nav3d';
  button.textContent='3D ROUTE';
  button.title='Route-focused J2000 ecliptic 3D camera using authoritative ordinary-space Navigator geometry';
  button.onclick=()=>activateRoute3D(panel,button);
  actions.insertBefore(button,actions.querySelector('.navPlay'));

  const style=document.createElement('style');
  style.id='loomStageFIntegrated3DStyles';
  style.textContent='#navOverlayPanel .nav3d{flex:1;min-width:0;padding:4px 5px;font-size:7px}#navOverlayPanel .nav3d.active{outline:1px solid rgba(99,214,229,.75)}';
  document.head.appendChild(style);

  const clearActive=()=>button.classList.remove('active');
  for(const id of ['top','edge']){const b=document.getElementById(id);if(b)b.addEventListener('click',clearActive)}
  const sync=()=>{button.hidden=!!fit.hidden;if(button.hidden)clearActive()};
  sync();
  new MutationObserver(sync).observe(fit,{attributes:true,attributeFilter:['hidden']});
  panel.dataset.stageF3d=STAGE_F_CONTRACT;
  return true;
}

if(!installStageFRoute3D()){
  const observer=new MutationObserver(()=>{
    if(installStageFRoute3D())observer.disconnect();
  });
  observer.observe(document.documentElement,{childList:true,subtree:true});
}
})();
