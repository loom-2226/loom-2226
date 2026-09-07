(() => {
'use strict';
const STAGE_F_CONTRACT='LOOM_STAGE_F_INTEGRATED_GIS_3D_V2';
const ROUTE_OVERLAY_URL='/navigation-overlay.json';
let inspectorRoute=null;
let inspectorYaw=.55;
let inspectorPitch=.45;
let inspectorDragging=false;
let inspectorPointer=null;

function finitePoint(v){return Array.isArray(v)&&v.length>=3&&v.every(x=>Number.isFinite(Number(x)))}
function ordinaryRouteSegments(route){
  const out=[];
  for(const seg of route?.segments||[]){
    if(seg?.geometry_semantics?.ordinary_space_occupancy===false)continue;
    const points=(seg?.geometry_points_j2000_ecliptic_km||[]).filter(finitePoint).map(p=>p.map(Number));
    if(points.length>=2)out.push({segment:seg,points});
  }
  return out;
}
function ordinaryRoutePoints(route){return ordinaryRouteSegments(route).flatMap(x=>x.points)}
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

function inspectorProject(p,center,scale,w,h){
  let x=p[0]-center[0],y=p[1]-center[1],z=p[2]-center[2];
  const cy=Math.cos(inspectorYaw),sy=Math.sin(inspectorYaw);
  const x1=cy*x-sy*y,y1=sy*x+cy*y;
  const cp=Math.cos(inspectorPitch),sp=Math.sin(inspectorPitch);
  const y2=cp*y1-sp*z,z2=sp*y1+cp*z;
  const perspective=1/(1+Math.max(-.8,Math.min(.8,z2/Math.max(scale,1)))*.18);
  return {x:w/2+x1*perspective/scale*w*.42,y:h/2-y2*perspective/scale*h*.42,z:z2};
}
function inspectorSpan(points){
  let min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(const p of points)for(let i=0;i<3;i++){min[i]=Math.min(min[i],p[i]);max[i]=Math.max(max[i],p[i])}
  const span=[max[0]-min[0],max[1]-min[1],max[2]-min[2]];
  return {center:[(min[0]+max[0])/2,(min[1]+max[1])/2,(min[2]+max[2])/2],scale:Math.max(1,...span),spanKm:Math.hypot(...span)};
}
function drawOrdinaryInspector(){
  const box=document.getElementById('loomStageFOrdinary3d');
  const canvas=box?.querySelector('canvas');
  if(!box||box.hidden||!canvas||!inspectorRoute)return;
  const segments=ordinaryRouteSegments(inspectorRoute),points=segments.flatMap(x=>x.points);
  if(points.length<2)return;
  const rect=canvas.getBoundingClientRect(),d=Math.min(window.devicePixelRatio||1,2),w=Math.max(1,rect.width),h=Math.max(1,rect.height);
  canvas.width=Math.floor(w*d);canvas.height=Math.floor(h*d);
  const c=canvas.getContext('2d');c.setTransform(d,0,0,d,0,0);c.clearRect(0,0,w,h);
  const fit=inspectorSpan(points);
  c.fillStyle='rgba(8,12,18,.96)';c.fillRect(0,0,w,h);
  c.strokeStyle='rgba(150,165,185,.14)';c.lineWidth=1;c.beginPath();c.moveTo(w/2,10);c.lineTo(w/2,h-10);c.moveTo(10,h/2);c.lineTo(w-10,h/2);c.stroke();
  for(const item of segments){
    const projected=item.points.map(p=>inspectorProject(p,fit.center,fit.scale,w,h));
    c.strokeStyle=item.segment?.style?.stroke||'#e2a85f';c.lineWidth=2.2;c.setLineDash([]);c.beginPath();projected.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));c.stroke();
    const a=projected[0],b=projected[projected.length-1];
    c.fillStyle='#e2a85f';c.beginPath();c.arc(a.x,a.y,4,0,Math.PI*2);c.fill();
    c.fillStyle='#63d6e5';c.beginPath();c.arc(b.x,b.y,4,0,Math.PI*2);c.fill();
  }
  const meta=box.querySelector('.stageFOrdinaryMeta');
  if(meta){const span=fit.spanKm>=1e6?`${(fit.spanKm/1e6).toFixed(2)}M km`:fit.spanKm>=1e3?`${(fit.spanKm/1e3).toFixed(1)}k km`:`${fit.spanKm.toFixed(0)} km`;meta.textContent=`${points.length} AUTHORITATIVE XYZ SAMPLES · LOCAL DISPLAY FIT · SPAN ${span}`}
}
function ensureOrdinaryInspector(){
  let box=document.getElementById('loomStageFOrdinary3d');if(box)return box;
  box=document.createElement('div');box.id='loomStageFOrdinary3d';box.hidden=true;
  box.innerHTML='<div class="stageFOrdinaryHead"><b>ORDINARY 3D · J2000 ECLIPTIC</b><button type="button">CLOSE</button></div><div class="stageFOrdinaryMeta"></div><canvas aria-label="Authoritative ordinary-space Navigator trajectory"></canvas><div class="stageFOrdinaryHint">DRAG TO ROTATE · METRIC PHASE EXCLUDED</div>';
  document.body.appendChild(box);
  box.querySelector('button').onclick=()=>{box.hidden=true};
  const canvas=box.querySelector('canvas');
  canvas.addEventListener('pointerdown',e=>{inspectorDragging=true;inspectorPointer={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture?.(e.pointerId)});
  canvas.addEventListener('pointermove',e=>{if(!inspectorDragging||!inspectorPointer||e.pointerId!==inspectorPointer.id)return;const dx=e.clientX-inspectorPointer.x,dy=e.clientY-inspectorPointer.y;inspectorPointer.x=e.clientX;inspectorPointer.y=e.clientY;inspectorYaw+=dx*.012;inspectorPitch=Math.max(-1.45,Math.min(1.45,inspectorPitch+dy*.012));drawOrdinaryInspector()});
  const stop=e=>{if(inspectorPointer&&e.pointerId!==inspectorPointer.id)return;inspectorDragging=false;inspectorPointer=null};canvas.addEventListener('pointerup',stop);canvas.addEventListener('pointercancel',stop);
  window.addEventListener('resize',()=>{if(!box.hidden)drawOrdinaryInspector()});
  return box;
}
async function showOrdinary3D(button){
  const route=await activeRoute();
  if(ordinaryRoutePoints(route).length<2)return;
  inspectorRoute=route;const box=ensureOrdinaryInspector();box.hidden=false;button.classList.add('active');drawOrdinaryInspector();
}

function installStageFRoute3D(){
  const panel=document.getElementById('navOverlayPanel');
  if(!panel||panel.dataset.stageF3d===STAGE_F_CONTRACT)return false;
  const actions=panel.querySelector('.navActions');
  const fit=panel.querySelector('.navFit');
  if(!actions||!fit)return false;

  const button=document.createElement('button');button.type='button';button.className='nav3d';button.textContent='3D ROUTE';button.title='Route-focused J2000 ecliptic 3D camera using authoritative ordinary-space Navigator geometry';button.onclick=()=>activateRoute3D(panel,button);
  const ordinary=document.createElement('button');ordinary.type='button';ordinary.className='navOrdinary3d';ordinary.textContent='ORDINARY';ordinary.title='Inspect only authoritative ordinary-space XYZ trajectory samples; metric transit is excluded';ordinary.onclick=()=>showOrdinary3D(ordinary);
  actions.insertBefore(button,actions.querySelector('.navPlay'));actions.insertBefore(ordinary,actions.querySelector('.navPlay'));

  const style=document.createElement('style');style.id='loomStageFIntegrated3DStyles';style.textContent=`
#navOverlayPanel .nav3d,#navOverlayPanel .navOrdinary3d{flex:1;min-width:0;padding:4px 5px;font-size:7px}#navOverlayPanel .nav3d.active,#navOverlayPanel .navOrdinary3d.active{outline:1px solid rgba(99,214,229,.75)}
#loomStageFOrdinary3d{position:fixed;z-index:28;left:10px;right:10px;bottom:max(66px,env(safe-area-inset-bottom));background:rgba(8,12,18,.97);border:1px solid rgba(99,214,229,.38);border-radius:12px;padding:8px;backdrop-filter:blur(10px);font:8px ui-monospace,SFMono-Regular,Menlo,monospace;color:#aeb9c8}#loomStageFOrdinary3d[hidden]{display:none}#loomStageFOrdinary3d .stageFOrdinaryHead{display:flex;align-items:center;justify-content:space-between;color:#dbe7f4}#loomStageFOrdinary3d .stageFOrdinaryHead button{padding:4px 7px;font-size:7px}#loomStageFOrdinary3d .stageFOrdinaryMeta{margin:5px 0;color:#7f8b9c}#loomStageFOrdinary3d canvas{display:block;width:100%;height:210px;border:1px solid rgba(150,165,185,.16);border-radius:8px;touch-action:none}#loomStageFOrdinary3d .stageFOrdinaryHint{margin-top:5px;color:#7f8b9c}
`;document.head.appendChild(style);

  const clearActive=()=>button.classList.remove('active');for(const id of ['top','edge']){const b=document.getElementById(id);if(b)b.addEventListener('click',clearActive)}
  const sync=async()=>{button.hidden=!!fit.hidden;if(button.hidden)clearActive();const route=button.hidden?null:await activeRoute();ordinary.hidden=ordinaryRoutePoints(route).length<2;if(ordinary.hidden)ordinary.classList.remove('active')};sync();new MutationObserver(sync).observe(fit,{attributes:true,attributeFilter:['hidden']});
  panel.dataset.stageF3d=STAGE_F_CONTRACT;return true;
}

if(!installStageFRoute3D()){
  const observer=new MutationObserver(()=>{if(installStageFRoute3D())observer.disconnect()});observer.observe(document.documentElement,{childList:true,subtree:true});
}
})();
