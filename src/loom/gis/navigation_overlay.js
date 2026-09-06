(() => {
'use strict';
const OVERLAY_SCHEMA='LOOM_GIS_NAVIGATION_OVERLAY_V1';
const TOKEN_TO_ENTITY={
  MERCURY:'ME',VENUS:'VE',EARTH:'EA',LUNA:'LU',MOON:'LU',MARS:'MA',CERES:'CER',
  JUPITER:'JU',JUPITER_SYSTEM:'JU',SATURN:'SA',SATURN_SYSTEM:'SA',URANUS:'UR',URANUS_SYSTEM:'UR',
  NEPTUNE:'NE',NEPTUNE_SYSTEM:'NE',PLUTO:'PL',PLUTO_SYSTEM:'PL'
};
let navOverlay=null;
const navVisible={active:true,alternates:true,phases:true,maneuvers:true,history:true};
let hudMode=(localStorage.getItem('loomHudMode')||'NAV').toUpperCase()==='ATLAS'?'ATLAS':'NAV';
let navPlaybackRouteId=null,navPlaybackIndex=null,navPlaybackTimer=null;

function navEntity(token){
  if(!scene||!scene.entities)return null;
  const raw=String(token||'').toUpperCase();
  const id=TOKEN_TO_ENTITY[raw]||raw;
  return scene.entities.find(e=>e.entity_id===id)||scene.entities.find(e=>String(e.name||'').toUpperCase()===raw)||null;
}
function navAbsoluteVectorKm(km){
  if(!Array.isArray(km)||km.length<3||!scene)return null;
  const r=Number(scene.max_reference_radius_au)||50;
  return [Number(km[0])/AU_KM/r,Number(km[1])/AU_KM/r,Number(km[2])/AU_KM/r];
}
function navEntityVector(token){const e=navEntity(token);return e?entityVec(e):null}
function navEntityScreen(token){const v=navEntityVector(token);return v?project(v):null}
function navKmScreen(km){if(viewMode!=='SOLAR'||scaleMode!=='TRUE')return null;const v=navAbsoluteVectorKm(km);return v?project(v):null}
function navStroke(style,alpha=1){ctx.strokeStyle=style?.stroke||`rgba(190,205,224,${alpha})`;ctx.lineWidth=Number(style?.width)||1.5;ctx.setLineDash(Array.isArray(style?.dash)?style.dash:[])}
function navPoint(p,r,stroke,fill='rgba(8,12,18,.92)'){if(!p)return;ctx.save();ctx.setLineDash([]);ctx.lineWidth=1.5;ctx.strokeStyle=stroke;ctx.fillStyle=fill;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.restore()}
function navDiamond(p,r,stroke){if(!p)return;ctx.save();ctx.setLineDash([]);ctx.lineWidth=1.4;ctx.strokeStyle=stroke;ctx.fillStyle='rgba(8,12,18,.92)';ctx.beginPath();ctx.moveTo(p.x,p.y-r);ctx.lineTo(p.x+r,p.y);ctx.lineTo(p.x,p.y+r);ctx.lineTo(p.x-r,p.y);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore()}
function navDrawPolyline(points,style,alpha=1){
  if(!Array.isArray(points)||points.length<2||viewMode!=='SOLAR'||scaleMode!=='TRUE')return;
  const screen=points.map(navKmScreen).filter(Boolean);if(screen.length<2)return;
  ctx.save();ctx.globalAlpha=alpha;
  if(alpha>=.75){ctx.strokeStyle='rgba(3,8,13,.82)';ctx.lineWidth=Math.max(5.5,(Number(style?.width)||1.5)+4);ctx.setLineDash([]);ctx.beginPath();screen.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.stroke()}
  navStroke(style,alpha);ctx.beginPath();screen.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.stroke();ctx.restore();
}
function navShip(p,{relational=false,alpha=1}={}){
  if(!p)return;
  ctx.save();ctx.globalAlpha=alpha;ctx.translate(p.x,p.y);ctx.setLineDash(relational?[3,3]:[]);ctx.strokeStyle=relational?'#bda5ff':'#ffffff';ctx.fillStyle=relational?'rgba(189,165,255,.18)':'rgba(255,255,255,.16)';ctx.lineWidth=1.8;
  ctx.beginPath();ctx.moveTo(0,-10);ctx.lineTo(7,8);ctx.lineTo(0,5);ctx.lineTo(-7,8);ctx.closePath();ctx.fill();ctx.stroke();
  if(relational){ctx.beginPath();ctx.arc(0,0,14,0,Math.PI*2);ctx.stroke()}
  ctx.restore();
}
function navDrawVehicle(state){const shipToken=state?.location_token||state?.location;if(!shipToken)return;navShip(navEntityScreen(shipToken))}
function navMetricEnd(route){const seg=(route?.segments||[]).find(s=>s.type==='METRIC');return seg?.end_position_j2000_ecliptic_km?navKmScreen(seg.end_position_j2000_ecliptic_km):null}
function navDrawRelationalMetric(route,seg,alpha=1){
  if(!route||!seg||seg.geometry_semantics?.ordinary_space_occupancy!==false)return;
  const a=navEntityScreen(route.origin),b=seg.end_position_j2000_ecliptic_km?navKmScreen(seg.end_position_j2000_ecliptic_km):null;if(!a||!b)return;
  ctx.save();ctx.globalAlpha=Math.min(.9,alpha);
  if(alpha>=.75){ctx.strokeStyle='rgba(3,8,13,.82)';ctx.lineWidth=6;ctx.setLineDash([]);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}
  ctx.strokeStyle=seg.style?.stroke||'#bda5ff';ctx.lineWidth=2.4;ctx.setLineDash([7,6]);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
  const mx=(a.x+b.x)/2,my=(a.y+b.y)/2;ctx.setLineDash([]);ctx.fillStyle='rgba(189,165,255,.92)';ctx.font='700 8px ui-monospace,SFMono-Regular,Menlo,monospace';ctx.textAlign='center';ctx.fillText('METRIC · RELATIONAL',mx,my-6);ctx.restore();
}

function navRouteWorldVectors(route){
  if(!route||!scene)return [];
  const out=[];const add=v=>{if(Array.isArray(v)&&v.length>=3&&v.every(x=>Number.isFinite(Number(x))))out.push(v.map(Number))};
  add(navEntityVector(route.origin));add(navEntityVector(route.destination));
  for(const seg of route.segments||[]){
    add(navAbsoluteVectorKm(seg.start_position_j2000_ecliptic_km));add(navAbsoluteVectorKm(seg.end_position_j2000_ecliptic_km));
    if(seg.geometry_semantics?.ordinary_space_occupancy!==false){for(const p of seg.geometry_points_j2000_ecliptic_km||[])add(navAbsoluteVectorKm(p))}
  }
  for(const a of route.anchors||[]){if(a.position_j2000_ecliptic_km)add(navAbsoluteVectorKm(a.position_j2000_ecliptic_km))}
  return out;
}
function navCameraSafeRect(){
  let safe=null;try{if(typeof cameraSafeRect==='function')safe=cameraSafeRect()}catch(_err){}
  if(!safe)safe={left:12,right:innerWidth-12,top:82,bottom:innerHeight-90};
  const panel=document.getElementById('flightPlanningPanel');
  if(panel&&getComputedStyle(panel).display!=='none'){const r=panel.getBoundingClientRect();if(r.width>20&&r.height>20){const mid=(safe.top+safe.bottom)/2;if(r.top<=mid&&r.bottom>safe.top)safe={...safe,top:Math.min(safe.bottom-80,r.bottom+10)};else if(r.bottom>=mid&&r.top<safe.bottom)safe={...safe,bottom:Math.max(safe.top+80,r.top-10)}}}
  return safe;
}
function navRouteNeedsFit(route){
  const pts=navRouteWorldVectors(route);if(pts.length<2||viewMode!=='SOLAR'||scaleMode!=='TRUE')return true;
  const safe=navCameraSafeRect(),margin=18;let inside=0;
  for(const v of pts){const p=project(v);if(p.x>=safe.left+margin&&p.x<=safe.right-margin&&p.y>=safe.top+margin&&p.y<=safe.bottom-margin)inside++}
  const ends=[navEntityScreen(route.origin),navEntityScreen(route.destination)].filter(Boolean);const endsInside=ends.length===2&&ends.every(p=>p.x>=safe.left+margin&&p.x<=safe.right-margin&&p.y>=safe.top+margin&&p.y<=safe.bottom-margin);
  return !endsInside||inside/pts.length<.75;
}
function fitNavigationRoute(route){
  const pts=navRouteWorldVectors(route);if(pts.length<2)return false;
  orbitInspectEntityId=null;cameraBand=CAMERA_BANDS.SOLAR;viewMode='SOLAR';focusEntityId=null;focusRadiusKm=0;scaleMode='TRUE';
  const focusBadge=document.getElementById('focusBadge');if(focusBadge)focusBadge.style.display='none';
  const mapScale=document.getElementById('mapScale'),trueScale=document.getElementById('trueScale');if(mapScale){mapScale.disabled=false;mapScale.classList.remove('active')}if(trueScale){trueScale.disabled=false;trueScale.classList.add('active')}
  const safe=navCameraSafeRect(),unit=Math.min(innerWidth,innerHeight)*.385;let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const v of pts){const q=rot(v),x=Number(q[0]),y=Number(q[1]);if(!Number.isFinite(x)||!Number.isFinite(y))continue;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y)}
  if(!Number.isFinite(minX))return false;
  const spanX=Math.max(.002,maxX-minX),spanY=Math.max(.002,maxY-minY),pad=26,availW=Math.max(90,safe.right-safe.left-pad*2),availH=Math.max(90,safe.bottom-safe.top-pad*2);
  const zx=availW/(spanX*unit),zy=availH/(spanY*unit);zoom=Math.max(MIN_ZOOM,Math.min(MAX_ZOOM,Math.min(zx,zy)*.92));
  const cx=(minX+maxX)/2,cy=(minY+maxY)/2,rad=unit*zoom,sx=(safe.left+safe.right)/2,sy=(safe.top+safe.bottom)/2;panX=sx-innerWidth/2-cx*rad;panY=sy-innerHeight/2+cy*rad;
  try{updateScaleLadder()}catch(_err){}scheduleDraw();return true;
}
function maybeAutoFitNavigationRoute(){
  const route=navOverlay?.active_route;if(!route)return;
  const key=`${route.route_id}:${route.source_sha256||''}`;if(sessionStorage.getItem('loomNavAutoFitRoute')===key)return;
  sessionStorage.setItem('loomNavAutoFitRoute',key);requestAnimationFrame(()=>{if(navRouteNeedsFit(route))fitNavigationRoute(route)});
}

function navPlaybackRoute(){if(!navPlaybackRouteId)return null;const routes=[navOverlay?.active_route,...(navOverlay?.alternate_routes||[]),...(navOverlay?.historical_routes||[])].filter(Boolean);return routes.find(r=>r.route_id===navPlaybackRouteId)||null}
function navPlaybackScreen(route,index){
  const samples=route?.trajectory?.samples||[];if(!samples.length)return null;
  const i=Math.max(0,Math.min(samples.length-1,Number(index)||0)),s=samples[i];const xyz=[s.ordinary_pos_x_km,s.ordinary_pos_y_km,s.ordinary_pos_z_km];
  if(xyz.every(v=>v!==null&&v!==undefined))return {p:navKmScreen(xyz.map(Number)),relational:false,sample:s};
  if(Number(s.position_semantics_code)===0){const a=navEntityScreen(route.origin),b=navMetricEnd(route);if(!a||!b)return null;const q=Math.max(0,Math.min(1,Number(s.relational_progress)||0));return {p:{x:a.x+(b.x-a.x)*q,y:a.y+(b.y-a.y)*q},relational:true,sample:s}}
  return null;
}
function navDrawPlayback(){const route=navPlaybackRoute();if(!route||navPlaybackIndex===null)return false;const hit=navPlaybackScreen(route,navPlaybackIndex);if(!hit||!hit.p)return false;navShip(hit.p,{relational:hit.relational});return true}
function stopNavPlayback(){if(navPlaybackTimer){clearInterval(navPlaybackTimer);navPlaybackTimer=null}navPlaybackIndex=null;navPlaybackRouteId=null;scheduleDraw();refreshNavPanel()}
function startNavPlayback(route){
  if(!route?.trajectory?.samples?.length)return;if(navPlaybackTimer)clearInterval(navPlaybackTimer);navPlaybackRouteId=route.route_id;navPlaybackIndex=0;
  navPlaybackTimer=setInterval(()=>{const r=navPlaybackRoute(),n=r?.trajectory?.samples?.length||0;if(!n||navPlaybackIndex>=n-1){clearInterval(navPlaybackTimer);navPlaybackTimer=null;refreshNavPanel();return}navPlaybackIndex++;scheduleDraw();refreshNavPanel()},90);scheduleDraw();refreshNavPanel();
}
function navDrawRoute(route,alpha=1){
  if(!route)return;const op=navEntityScreen(route.origin),dp=navEntityScreen(route.destination);navPoint(op,alpha>=.75?6:4,'rgba(226,168,95,.95)');navPoint(dp,alpha>=.75?6:4,'rgba(99,214,229,.95)');
  if(navVisible.phases){for(const seg of route.segments||[]){const pts=seg.geometry_points_j2000_ecliptic_km||[];if(pts.length>=2)navDrawPolyline(pts,seg.style,alpha);if(seg.type==='METRIC')navDrawRelationalMetric(route,seg,alpha);const sp=navKmScreen(seg.start_position_j2000_ecliptic_km),ep=navKmScreen(seg.end_position_j2000_ecliptic_km);if(sp)navDiamond(sp,4,seg.style?.stroke||'#bda5ff');if(ep)navDiamond(ep,4,seg.style?.stroke||'#bda5ff')}}
  if(navVisible.maneuvers){for(const a of route.anchors||[]){if(a.anchor_type==='DEPARTURE'||a.anchor_type==='ARRIVAL')continue;const p=a.position_j2000_ecliptic_km?navKmScreen(a.position_j2000_ecliptic_km):navEntityScreen(a.body_id);navDiamond(p,6,a.anchor_type==='METRIC_COLLAPSE'?'#bda5ff':'#63d6e5')}}
}
function drawNavigationOverlay(){if(!navOverlay||!scene)return;if(navVisible.history)for(const r of navOverlay.historical_routes||[])navDrawRoute(r,.25);if(navVisible.alternates)for(const r of navOverlay.alternate_routes||[])navDrawRoute(r,.38);if(navVisible.active&&navOverlay.active_route)navDrawRoute(navOverlay.active_route,1);if(!navDrawPlayback())navDrawVehicle(navOverlay.current_vehicle_state||{})}

function escNav(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
function navGeometryLabel(route){const segs=route?.segments||[],sampled=segs.filter(s=>(s.geometry_points_j2000_ecliptic_km||[]).length>=2).length,timeline=route?.trajectory?.samples?.length||0;if(timeline)return `${timeline} NAVIGATOR SAMPLES · ${sampled} ORDINARY 3D PHASE${sampled===1?'':'S'}`;return sampled?`${sampled}/${segs.length} SAMPLED PHASES`:'AUTHORITATIVE PHASE ANCHORS ONLY'}
function ensureNavIntel(){let sheet=document.getElementById('navIntelSheet');if(sheet)return sheet;sheet=document.createElement('div');sheet.id='navIntelSheet';sheet.hidden=true;sheet.innerHTML='<div class="navIntelHead"><b>NAVIGATION DETAILS</b><button type="button" class="navIntelClose">CLOSE</button></div><div class="navIntelContent"></div>';document.body.appendChild(sheet);sheet.querySelector('.navIntelClose').onclick=()=>{sheet.hidden=true};return sheet}
function showNavigationIntel(route){if(!route)return;setHudMode('NAV');const sheet=ensureNavIntel(),content=sheet.querySelector('.navIntelContent');const phases=(route.segments||[]).map(s=>`<div class="navIntelCard"><b>${escNav(s.type)}</b><span>${escNav(s.phase||'—')}</span><span>${escNav(s.geometry_authority)}</span><span>${escNav(s.geometry_semantics?.semantics||'')}</span></div>`).join('');content.innerHTML=`<div class="navIntelRoute"><strong>${escNav(route.origin)} → ${escNav(route.destination)}</strong><span>${escNav(route.status)} · ${escNav(route.strategy||'—')}</span><span>${escNav(navGeometryLabel(route))}</span></div><div class="navIntelNote">METRIC = relational displacement, not ordinary-space occupancy. Solid phase tracks = Navigator-authored ordinary 3D trajectory.</div>${phases}`;sheet.hidden=false}
function navButton(label,key){const b=document.createElement('button');b.type='button';b.textContent=label;b.className='navPhaseBtn active';b.addEventListener('click',()=>{navVisible[key]=!navVisible[key];b.classList.toggle('active',navVisible[key]);scheduleDraw()});return b}
function primaryRoute(){return navOverlay?.active_route||(navOverlay?.historical_routes||[]).slice(-1)[0]||null}
function refreshNavPanel(){
  const p=document.getElementById('navOverlayPanel');if(!p)return;const route=primaryRoute(),slot=p.querySelector('.navRouteSlot'),meta=p.querySelector('.navMeta'),play=p.querySelector('.navPlay'),fit=p.querySelector('.navFit');
  if(slot){slot.innerHTML='';if(route){const b=document.createElement('button');b.className='navRoute';b.textContent=`${route.origin} → ${route.destination}`;b.onclick=()=>showNavigationIntel(route);slot.appendChild(b)}else slot.textContent='NO ROUTE'}
  if(meta)meta.textContent=route?navGeometryLabel(route):'Navigator ready';
  if(fit){fit.hidden=!route;fit.onclick=()=>fitNavigationRoute(route)}
  if(play){play.hidden=!route?.trajectory?.samples?.length;play.textContent=navPlaybackTimer?'STOP':'PLAY ROUTE';play.onclick=()=>navPlaybackTimer?stopNavPlayback():startNavPlayback(route)}
}
function installNavPanel(){
  if(document.getElementById('navOverlayPanel'))return;const p=document.createElement('div');p.id='navOverlayPanel';p.innerHTML='<div class="navTitle">NAV</div><div class="navRouteSlot"></div><div class="navMeta"></div><div class="navBtns"></div><div class="navActions"><button type="button" class="navFit">FIT ROUTE</button><button type="button" class="navPlay">PLAY ROUTE</button></div>';document.body.appendChild(p);
  const btns=p.querySelector('.navBtns');btns.append(navButton('ACTIVE','active'),navButton('PHASES','phases'),navButton('HISTORY','history'));refreshNavPanel();
}
function installHudStyles(){
  if(document.getElementById('loomNavAtlasStyles'))return;const style=document.createElement('style');style.id='loomNavAtlasStyles';style.textContent=`
#loomModeTabs{position:fixed;z-index:31;left:max(8px,env(safe-area-inset-left));top:78px;display:flex;padding:3px;border:1px solid rgba(150,165,185,.35);border-radius:10px;background:rgba(7,11,17,.94);backdrop-filter:blur(10px);box-shadow:0 6px 20px rgba(0,0,0,.28)}
#loomModeTabs button{min-width:58px;padding:7px 10px;font:850 9px ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;opacity:.58}#loomModeTabs button.active{opacity:1;border-color:rgba(99,214,229,.65);color:#e7f4ff}
#navOverlayPanel{position:fixed;right:max(8px,env(safe-area-inset-right));top:78px;z-index:13;width:min(205px,48vw);background:rgba(10,14,20,.90);border:1px solid rgba(150,165,185,.28);border-radius:10px;padding:6px;backdrop-filter:blur(8px);font:8px ui-monospace,SFMono-Regular,Menlo,monospace;color:#aeb9c8}
#navOverlayPanel .navTitle{display:none}#navOverlayPanel .navRoute{width:100%;text-align:left;padding:6px;font:800 8px ui-monospace,SFMono-Regular,Menlo,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#navOverlayPanel .navMeta{color:#7f8b9c;margin:4px 2px;line-height:1.25}#navOverlayPanel .navBtns,#navOverlayPanel .navActions{display:flex;gap:3px}.navPhaseBtn,#navOverlayPanel .navPlay,#navOverlayPanel .navFit{min-width:0;padding:4px 5px;font-size:7px}#navOverlayPanel .navActions{margin-top:4px}#navOverlayPanel .navPlay,#navOverlayPanel .navFit{flex:1}
#navIntelSheet{position:fixed;z-index:29;left:8px;right:8px;bottom:max(64px,env(safe-area-inset-bottom));max-height:42vh;overflow:auto;background:rgba(8,12,18,.97);border:1px solid rgba(99,214,229,.38);border-radius:12px;padding:8px;font:8px ui-monospace,SFMono-Regular,Menlo,monospace;color:#acbacb;backdrop-filter:blur(10px)}.navIntelHead{display:flex;align-items:center;justify-content:space-between}.navIntelHead button{font-size:7px;padding:4px 6px}.navIntelRoute{display:grid;gap:3px;margin:7px 0;color:#dbe7f4}.navIntelNote{padding:6px;border-left:2px solid #bda5ff;color:#9caac0}.navIntelCard{display:grid;grid-template-columns:90px 1fr;gap:3px 7px;padding:6px 0;border-top:1px solid rgba(150,165,185,.12)}
#atlasDrawer{position:relative}#atlasDrawer .loomAtlasClose{position:absolute;z-index:5;right:8px;top:8px;padding:4px 7px;font:850 8px ui-monospace,SFMono-Regular,Menlo,monospace}#atlasDrawer.loom-atlas-closed{display:none!important}
body.loom-nav-mode #atlasDrawer{display:none!important}body.loom-atlas-mode #flightPlanningPanel,body.loom-atlas-mode #flightPlanningRestore,body.loom-atlas-mode #navOverlayPanel,body.loom-atlas-mode #navIntelSheet{display:none!important}
@media(max-width:700px){
  #flightPlanningPanel{left:8px!important;right:8px!important;top:auto!important;bottom:max(62px,env(safe-area-inset-bottom))!important;width:auto!important;max-height:40vh!important;padding:7px!important;border-radius:12px!important}
  #flightPlanningPanel .fpCandidates{max-height:18vh!important}
  #flightPlanningRestore{left:8px!important;top:auto!important;bottom:max(68px,env(safe-area-inset-bottom))!important}
  #navOverlayPanel{top:118px;width:min(190px,48vw)}
  #atlasDrawer{left:8px!important;right:8px!important;bottom:max(58px,env(safe-area-inset-bottom))!important;max-height:52vh!important}
}
`;document.head.appendChild(style);
}
function installAtlasClose(){const drawer=document.getElementById('atlasDrawer');if(!drawer||drawer.querySelector('.loomAtlasClose'))return;const b=document.createElement('button');b.type='button';b.className='loomAtlasClose';b.textContent='×';b.title='Close Atlas';b.onclick=e=>{e.stopPropagation();drawer.classList.add('loom-atlas-closed');try{if(typeof setAtlasExpanded==='function')setAtlasExpanded(false);if(typeof setAtlasOpen==='function')setAtlasOpen(false)}catch(_err){drawer.classList.remove('open','expanded')}};drawer.appendChild(b)}
function installModeTabs(){if(document.getElementById('loomModeTabs'))return;const tabs=document.createElement('div');tabs.id='loomModeTabs';tabs.innerHTML='<button type="button" data-mode="NAV">NAV</button><button type="button" data-mode="ATLAS">ATLAS</button>';document.body.appendChild(tabs);tabs.querySelectorAll('button').forEach(b=>b.onclick=()=>setHudMode(b.dataset.mode))}
function setHudMode(mode){hudMode=String(mode||'NAV').toUpperCase()==='ATLAS'?'ATLAS':'NAV';localStorage.setItem('loomHudMode',hudMode);document.body.classList.toggle('loom-nav-mode',hudMode==='NAV');document.body.classList.toggle('loom-atlas-mode',hudMode==='ATLAS');document.querySelectorAll('#loomModeTabs button').forEach(b=>b.classList.toggle('active',b.dataset.mode===hudMode));const drawer=document.getElementById('atlasDrawer');if(hudMode==='ATLAS'&&drawer){drawer.classList.remove('loom-atlas-closed');try{if(typeof setAtlasOpen==='function')setAtlasOpen(true)}catch(_err){drawer.classList.add('open')}}if(hudMode==='NAV'&&drawer){try{if(typeof setAtlasExpanded==='function')setAtlasExpanded(false)}catch(_err){}}}
function installHudModes(){installHudStyles();installModeTabs();installAtlasClose();setHudMode(hudMode);document.addEventListener('click',e=>{if(e.target?.closest?.('.fpAtlasPlanHere'))localStorage.setItem('loomHudMode','NAV')},true)}

const baseDrawNow=drawNow;drawNow=function(){baseDrawNow();drawNavigationOverlay()};
fetch('/navigation-overlay.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(x=>{if(x.contract!==OVERLAY_SCHEMA)throw new Error(`unsupported navigation overlay ${x.contract}`);navOverlay=x;installHudModes();installNavPanel();maybeAutoFitNavigationRoute();scheduleDraw()}).catch(err=>{console.warn('LOOM navigation overlay unavailable',err);installHudModes()});
})();
