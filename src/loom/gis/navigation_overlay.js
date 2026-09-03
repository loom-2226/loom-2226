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
function navEntityScreen(token){const e=navEntity(token);return e?project(entityVec(e)):null}
function navKmScreen(km){if(viewMode!=='SOLAR'||scaleMode!=='TRUE')return null;const v=navAbsoluteVectorKm(km);return v?project(v):null}
function navStroke(style,alpha=1){
  ctx.strokeStyle=style?.stroke||`rgba(190,205,224,${alpha})`;
  ctx.lineWidth=Number(style?.width)||1.5;
  ctx.setLineDash(Array.isArray(style?.dash)?style.dash:[]);
}
function navPoint(p,r,stroke,fill='rgba(8,12,18,.92)'){
  if(!p)return;ctx.save();ctx.setLineDash([]);ctx.lineWidth=1.5;ctx.strokeStyle=stroke;ctx.fillStyle=fill;
  ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.restore();
}
function navDiamond(p,r,stroke){
  if(!p)return;ctx.save();ctx.setLineDash([]);ctx.lineWidth=1.4;ctx.strokeStyle=stroke;ctx.fillStyle='rgba(8,12,18,.92)';
  ctx.beginPath();ctx.moveTo(p.x,p.y-r);ctx.lineTo(p.x+r,p.y);ctx.lineTo(p.x,p.y+r);ctx.lineTo(p.x-r,p.y);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
}
function navDrawPolyline(points,style,alpha=1){
  if(!Array.isArray(points)||points.length<2||viewMode!=='SOLAR'||scaleMode!=='TRUE')return;
  const screen=points.map(navKmScreen).filter(Boolean);if(screen.length<2)return;
  ctx.save();ctx.globalAlpha=alpha;navStroke(style,alpha);ctx.beginPath();
  screen.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.stroke();ctx.restore();
}
function navDrawRoute(route,alpha=1){
  if(!route)return;
  const op=navEntityScreen(route.origin),dp=navEntityScreen(route.destination);
  navPoint(op,5,'rgba(226,168,95,.95)');navPoint(dp,5,'rgba(99,214,229,.95)');
  if(navVisible.phases){
    for(const seg of route.segments||[]){
      const pts=seg.geometry_points_j2000_ecliptic_km||[];
      if(pts.length>=2)navDrawPolyline(pts,seg.style,alpha);
      // Phase anchors are rendered as points only. We deliberately do not connect
      // unsampled anchors because RC6.1 does not provide authoritative interpolation.
      const sp=navKmScreen(seg.start_position_j2000_ecliptic_km),ep=navKmScreen(seg.end_position_j2000_ecliptic_km);
      if(sp)navDiamond(sp,4,seg.style?.stroke||'#bda5ff');
      if(ep)navDiamond(ep,4,seg.style?.stroke||'#bda5ff');
    }
  }
  if(navVisible.maneuvers){
    for(const a of route.anchors||[]){
      if(a.anchor_type==='DEPARTURE'||a.anchor_type==='ARRIVAL')continue;
      const p=a.position_j2000_ecliptic_km?navKmScreen(a.position_j2000_ecliptic_km):navEntityScreen(a.body_id);
      navDiamond(p,6,a.anchor_type==='METRIC_COLLAPSE'?'#bda5ff':'#63d6e5');
    }
  }
  const state=route.current_vehicle_state||{},shipToken=state.location_token||state.location;
  if(shipToken){const sp=navEntityScreen(shipToken);if(sp){ctx.save();ctx.strokeStyle='#ffffff';ctx.lineWidth=1.5;ctx.setLineDash([]);ctx.beginPath();ctx.arc(sp.x,sp.y,9,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(sp.x-12,sp.y);ctx.lineTo(sp.x+12,sp.y);ctx.moveTo(sp.x,sp.y-12);ctx.lineTo(sp.x,sp.y+12);ctx.stroke();ctx.restore()}}
}
function drawNavigationOverlay(){
  if(!navOverlay||!scene)return;
  if(navVisible.history)for(const r of navOverlay.historical_routes||[])navDrawRoute(r,.28);
  if(navVisible.alternates)for(const r of navOverlay.alternate_routes||[])navDrawRoute(r,.42);
  if(navVisible.active&&navOverlay.active_route)navDrawRoute(navOverlay.active_route,1);
}

function escNav(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
function navGeometryLabel(route){
  const segs=route?.segments||[];
  const sampled=segs.filter(s=>(s.geometry_points_j2000_ecliptic_km||[]).length>=2).length;
  return sampled?`${sampled}/${segs.length} sampled phases`:'AUTHORITATIVE PHASE ANCHORS ONLY';
}
function showNavigationIntel(route){
  if(!route)return;
  const drawer=document.getElementById('atlasDrawer'),label=document.getElementById('atlasHandleLabel'),content=document.getElementById('atlasContent');
  if(!drawer||!label||!content)return;
  label.textContent='NAVIGATION · '+route.origin+' → '+route.destination;
  const phases=(route.segments||[]).map(s=>`<div class="atlasCard"><h3>${escNav(s.type)}</h3><div class="atlasKV"><div><b>PHASE</b></div><div>${escNav(s.phase||'—')}</div><div><b>START</b></div><div>${escNav(s.start_epoch||'—')}</div><div><b>END</b></div><div>${escNav(s.end_epoch||'—')}</div><div><b>GEOMETRY</b></div><div>${escNav(s.geometry_authority)}</div></div></div>`).join('');
  content.innerHTML=`<div class="ahead"><div><h2>${escNav(route.origin)} → ${escNav(route.destination)}</h2><div class="status">${escNav(route.status)} · ${escNav(route.strategy||'—')}</div></div></div>
    <div class="soWhat"><div class="soWhatLabel">NAVIGATOR AUTHORITY</div><div class="soWhatText">GIS is rendering LOOM_ROUTE_LAYER_V1. It does not calculate or interpolate flight physics.</div></div>
    <div class="atlasCard"><h3>FLIGHT</h3><div class="atlasKV"><div><b>FLIGHT ID</b></div><div>${escNav(route.flight_id)}</div><div><b>DEPARTURE</b></div><div>${escNav(route.departure_epoch||'—')}</div><div><b>ARRIVAL</b></div><div>${escNav(route.arrival_epoch||'—')}</div><div><b>GEOMETRY</b></div><div>${escNav(navGeometryLabel(route))}</div><div><b>SOURCE SHA</b></div><div>${escNav(String(route.source_sha256||'').slice(0,16))}…</div></div></div>${phases}`;
  drawer.classList.add('open');
}
function navButton(label,key){
  const b=document.createElement('button');b.type='button';b.textContent=label;b.className='navPhaseBtn active';
  b.addEventListener('click',()=>{navVisible[key]=!navVisible[key];b.classList.toggle('active',navVisible[key]);scheduleDraw()});return b;
}
function installNavPanel(){
  if(document.getElementById('navOverlayPanel'))return;
  const style=document.createElement('style');style.textContent=`#navOverlayPanel{position:fixed;right:max(10px,env(safe-area-inset-right));top:86px;z-index:13;width:min(270px,72vw);background:rgba(10,14,20,.90);border:1px solid rgba(150,165,185,.28);border-radius:11px;padding:7px;backdrop-filter:blur(8px);font:9px ui-monospace,SFMono-Regular,Menlo,monospace;color:#aeb9c8}#navOverlayPanel .navTitle{font-weight:850;letter-spacing:.09em;color:#d9e4f2;margin:1px 2px 6px}#navOverlayPanel .navRoute{width:100%;text-align:left;min-width:0;padding:7px;font:800 9px ui-monospace,SFMono-Regular,Menlo,monospace}#navOverlayPanel .navMeta{color:#7f8b9c;margin:5px 2px;line-height:1.35}#navOverlayPanel .navBtns{display:flex;gap:4px;flex-wrap:wrap}.navPhaseBtn{min-width:0;padding:5px 6px;font-size:8px}`;document.head.appendChild(style);
  const p=document.createElement('div');p.id='navOverlayPanel';p.innerHTML='<div class="navTitle">NAVIGATION</div><div class="navRouteSlot"></div><div class="navMeta"></div><div class="navBtns"></div>';document.body.appendChild(p);
  const slot=p.querySelector('.navRouteSlot'),meta=p.querySelector('.navMeta'),btns=p.querySelector('.navBtns');
  if(navOverlay?.active_route){const r=navOverlay.active_route,b=document.createElement('button');b.className='navRoute';b.textContent=`ACTIVE · ${r.origin} → ${r.destination}`;b.addEventListener('click',()=>showNavigationIntel(r));slot.appendChild(b);meta.textContent=navGeometryLabel(r)}else{slot.textContent='NO ACTIVE ROUTE';meta.textContent='Navigator route layer available; no route supplied.'}
  btns.append(navButton('ACTIVE','active'),navButton('ALTS','alternates'),navButton('PHASES','phases'),navButton('MANEUVERS','maneuvers'),navButton('HISTORY','history'));
  const traffic=document.createElement('button');traffic.type='button';traffic.textContent='TRAFFIC';traffic.className='navPhaseBtn '+(trafficLayerActive?'active':'');traffic.addEventListener('click',()=>{trafficLayerActive=!trafficLayerActive;traffic.classList.toggle('active',trafficLayerActive);rebuildTrafficRollups();scheduleDraw()});btns.appendChild(traffic);
}

const baseDrawNow=drawNow;
drawNow=function(){baseDrawNow();drawNavigationOverlay()};
fetch('/navigation-overlay.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(x=>{
  if(x.contract!==OVERLAY_SCHEMA)throw new Error(`unsupported navigation overlay ${x.contract}`);
  navOverlay=x;installNavPanel();scheduleDraw();
}).catch(err=>{console.warn('LOOM navigation overlay unavailable',err);});
})();
