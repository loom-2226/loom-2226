(() => {
'use strict';
const canvas = document.getElementById('gl');
const info = document.getElementById('info');
const statusEl = document.getElementById('status');
const epochEl = document.getElementById('epoch');
const frameEl = document.getElementById('frame');
const originButton = document.getElementById('origin');
const destinationButton = document.getElementById('destination');
const gl = canvas.getContext('webgl', {antialias:true, alpha:false});
if(!gl){statusEl.textContent='WebGL unavailable';return;}

const vs=`attribute vec3 aPos;attribute vec3 aColor;attribute float aSize;uniform mat4 uMVP;varying vec3 vColor;void main(){gl_Position=uMVP*vec4(aPos,1.0);gl_PointSize=aSize;vColor=aColor;}`;
const fs=`precision mediump float;varying vec3 vColor;uniform float uPointMode;void main(){if(uPointMode>0.5){vec2 p=gl_PointCoord*2.0-1.0;if(dot(p,p)>1.0)discard;}gl_FragColor=vec4(vColor,1.0);}`;
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const loc={pos:gl.getAttribLocation(program,'aPos'),color:gl.getAttribLocation(program,'aColor'),size:gl.getAttribLocation(program,'aSize'),mvp:gl.getUniformLocation(program,'uMVP'),pointMode:gl.getUniformLocation(program,'uPointMode')};
const buffers={pos:gl.createBuffer(),color:gl.createBuffer(),size:gl.createBuffer()};

let snapshot=null, states=[], center=[0,0,0], focusId='SOL', cameraMode='SYSTEM', yaw=.55, pitch=.38, zoom=2.7, pan=[0,0], scale=1, positions=[], colors=[], sizes=[];
let routeOverlay=null, routeStrips=[], routeId=null, routeAuthority=null;
const byId=new Map();

function resize(){const d=Math.min(devicePixelRatio||1,2);const w=Math.floor(canvas.clientWidth*d),h=Math.floor(canvas.clientHeight*d);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}}
function mul(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)o[c*4+r]=a[r]*b[c*4]+a[4+r]*b[c*4+1]+a[8+r]*b[c*4+2]+a[12+r]*b[c*4+3];return o;}
function perspective(fovy,aspect,n,f){const t=1/Math.tan(fovy/2),nf=1/(n-f);return new Float32Array([t/aspect,0,0,0,0,t,0,0,0,0,(f+n)*nf,-1,0,0,2*f*n*nf,0]);}
function translate3(x,y,z){return new Float32Array([1,0,0,0,0,1,0,0,0,1,0,x,y,z,1]);}
function rotX(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1]);}
function rotY(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]);}
function currentMVP(){const aspect=canvas.width/canvas.height;return mul(perspective(Math.PI/3,aspect,.05,100),mul(translate3(pan[0],pan[1],-zoom),mul(rotX(pitch),rotY(yaw))));}
function project(p,m){const x=p[0],y=p[1],z=p[2];const cx=m[0]*x+m[4]*y+m[8]*z+m[12],cy=m[1]*x+m[5]*y+m[9]*z+m[13],cw=m[3]*x+m[7]*y+m[11]*z+m[15];if(cw<=0)return null;return [(cx/cw*.5+.5)*canvas.clientWidth,(1-(cy/cw*.5+.5))*canvas.clientHeight];}
function distanceFromCenter(s){const p=s.position_km;return Math.hypot(p[0]-center[0],p[1]-center[1],p[2]-center[2]);}
function framingStates(){
 if(cameraMode==='SYSTEM'){
  const celestial=states.filter(s=>s.payload?.state_class==='CELESTIAL');
  return celestial.length?celestial:states;
 }
 const local=states.filter(s=>s.entity_id===focusId||s.payload?.center_entity_id===focusId);
 return local.length>1?local:[byId.get(focusId)].filter(Boolean);
}
function frameRadiusKm(){let radius=1;for(const s of framingStates())radius=Math.max(radius,distanceFromCenter(s));return radius;}
function rebuild(){if(!states.length)return;const rel=states.map(s=>[s.position_km[0]-center[0],s.position_km[1]-center[1],s.position_km[2]-center[2]]);const frameRadius=frameRadiusKm();scale=1/frameRadius;positions=[];colors=[];sizes=[];for(let i=0;i<states.length;i++){const s=states[i],p=rel[i];positions.push(p[0]*scale,p[1]*scale,p[2]*scale);const infra=s.payload?.state_class==='INFRASTRUCTURE';if(s.navigation_grade){colors.push(.70,.86,.77);}else if(infra){colors.push(.62,.72,.88);}else{colors.push(.85,.74,.45);}sizes.push(infra?5:9);}
 upload(buffers,new Float32Array(positions),new Float32Array(colors),new Float32Array(sizes));rebuildRoute();updateStatus(frameRadius);}
function totalRoutePoints(){return routeStrips.reduce((n,strip)=>n+strip.pointsKm.length,0);}
function updateStatus(frameRadius=frameRadiusKm()){
 const authority=routeAuthority?` · ${routeAuthority}`:'';
 const routeText=routeId?`\nroute ${routeId} · ${routeStrips.length} ordinary-space segment${routeStrips.length===1?'':'s'} · ${totalRoutePoints()} samples${authority}`:'\nno active trajectory';
 statusEl.textContent=`${states.length} states · ${snapshot?.counts?.navigation_grade||0} nav-grade\n${cameraMode} · ${frameRadius.toExponential(2)} km → 1 unit${routeText}`;
}
function finitePoint(p){return Array.isArray(p)&&p.length>=3&&p.slice(0,3).every(Number.isFinite);}
function routeOrdinaryStrips(active){
 const strips=[];
 for(const segment of active?.segments||[]){
  if(segment?.geometry_semantics?.ordinary_space_occupancy===false)continue;
  const pts=(segment?.geometry_points_j2000_ecliptic_km||[]).filter(finitePoint).map(p=>p.slice(0,3));
  if(pts.length>=2)strips.push(pts);
 }
 if(strips.length)return strips;
 const fallback=active?.trajectory?.ordinary_points_j2000_ecliptic_km;
 const pts=Array.isArray(fallback)?fallback.filter(finitePoint).map(p=>p.slice(0,3)):[];
 return pts.length>=2?[pts]:[];
}
function rebuildRoute(){for(const strip of routeStrips){const pos=[],color=[],size=[];for(const p of strip.pointsKm){pos.push((p[0]-center[0])*scale,(p[1]-center[1])*scale,(p[2]-center[2])*scale);color.push(.35,.88,1.0);size.push(1);}strip.positions=pos;upload(strip.buffers,new Float32Array(pos),new Float32Array(color),new Float32Array(size));}}
function bind(buf,attr,n){gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.enableVertexAttribArray(attr);gl.vertexAttribPointer(attr,n,gl.FLOAT,false,0,0);}
function upload(set,pos,color,size){gl.bindBuffer(gl.ARRAY_BUFFER,set.pos);gl.bufferData(gl.ARRAY_BUFFER,pos,gl.STATIC_DRAW);gl.bindBuffer(gl.ARRAY_BUFFER,set.color);gl.bufferData(gl.ARRAY_BUFFER,color,gl.STATIC_DRAW);gl.bindBuffer(gl.ARRAY_BUFFER,set.size);gl.bufferData(gl.ARRAY_BUFFER,size,gl.STATIC_DRAW);}
function useBuffers(set){bind(set.pos,loc.pos,3);bind(set.color,loc.color,3);bind(set.size,loc.size,1);}
function draw(){resize();gl.clearColor(.02,.03,.05,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.useProgram(program);gl.uniformMatrix4fv(loc.mvp,false,currentMVP());gl.uniform1f(loc.pointMode,0);for(const strip of routeStrips){if(strip.positions.length>=6){useBuffers(strip.buffers);gl.lineWidth(2);gl.drawArrays(gl.LINE_STRIP,0,strip.positions.length/3);}}gl.uniform1f(loc.pointMode,1);useBuffers(buffers);gl.drawArrays(gl.POINTS,0,states.length);requestAnimationFrame(draw);}
function resolveStateId(token){const wanted=String(token||'').trim().toUpperCase();if(!wanted)return null;if(byId.has(wanted))return wanted;for(const s of states){if(String(s.entity_id||'').toUpperCase()===wanted)return s.entity_id;if(String(s.payload?.name||'').trim().toUpperCase()===wanted)return s.entity_id;}return null;}
function setCenter(id,mode='FREE'){const s=byId.get(id);if(!s)return false;focusId=id;cameraMode=mode;center=s.position_km.slice();zoom=2.7;pan=[0,0];rebuild();return true;}
function setSystem(){focusId='SOL';cameraMode='SYSTEM';const sun=byId.get('SOL');center=sun?sun.position_km.slice():[0,0,0];zoom=2.7;pan=[0,0];rebuild();}
function focusRouteEndpoint(which){const active=routeOverlay?.active_route;const token=which==='ORIGIN'?active?.origin:active?.destination;const id=resolveStateId(token);if(!id){statusEl.textContent=`${which} camera unavailable · ${token||'no active route'}`;return;}setCenter(id,which);}
function inspect(index){const s=states[index];if(!s)return;const p=s.position_km,v=s.velocity_km_s,infra=s.payload?.state_class==='INFRASTRUCTURE';info.innerHTML=`<h2>${esc(s.payload?.name||s.entity_id)}</h2><div class="grid"><b>ID</b><span>${esc(s.entity_id)}</span><b>CLASS</b><span>${esc(s.payload?.state_class||'—')}</span><b>NAV</b><span class="${s.navigation_grade?'navgood':'navbad'}">${s.navigation_grade?'NAVIGATION GRADE':'PROVISIONAL / FALLBACK'}</span><b>POSITION km</b><span>${p.map(x=>x.toFixed(1)).join(', ')}</span><b>VELOCITY km/s</b><span>${v.map(x=>x.toFixed(4)).join(', ')}</span><b>SOURCE</b><span>${esc(s.provenance?.state_source||'—')}</span>${infra?`<b>CENTER</b><span>${esc(s.payload?.center_entity_id||'—')}</span><b>VALIDITY</b><span>${esc(s.payload?.validity_status||'—')}</span>`:''}</div>`;}
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

const pointers=new Map();let gesture=null;
function pointerPair(){return [...pointers.values()].slice(0,2);}
function pairMetrics(){const [a,b]=pointerPair();if(!a||!b)return null;return {distance:Math.hypot(a.x-b.x,a.y-b.y),midX:(a.x+b.x)/2,midY:(a.y+b.y)/2};}
canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,moved:false,panMode:e.shiftKey||e.button===2});if(pointers.size===2){const m=pairMetrics();gesture=m?{type:'pinch',...m}:null;}else{gesture={type:(e.shiftKey||e.button===2)?'pan':'orbit',id:e.pointerId,x:e.clientX,y:e.clientY};}});
canvas.addEventListener('pointermove',e=>{const p=pointers.get(e.pointerId);if(!p)return;const dx=e.clientX-p.x,dy=e.clientY-p.y;p.x=e.clientX;p.y=e.clientY;if(Math.hypot(e.clientX-p.startX,e.clientY-p.startY)>3)p.moved=true;if(pointers.size>=2){const m=pairMetrics();if(!m)return;if(!gesture||gesture.type!=='pinch'){gesture={type:'pinch',...m};return;}if(gesture.distance>0)zoom=Math.max(1.25,Math.min(8,zoom*(gesture.distance/m.distance)));pan[0]+=((m.midX-gesture.midX)/Math.max(canvas.clientWidth,1))*2;pan[1]-=((m.midY-gesture.midY)/Math.max(canvas.clientHeight,1))*2;cameraMode='FREE';gesture={type:'pinch',...m};return;}if(!gesture||gesture.id!==e.pointerId)gesture={type:p.panMode?'pan':'orbit',id:e.pointerId,x:e.clientX,y:e.clientY};if(gesture.type==='pan'){pan[0]+=(dx/Math.max(canvas.clientWidth,1))*2;pan[1]-=(dy/Math.max(canvas.clientHeight,1))*2;cameraMode='FREE';}else{yaw+=dx*.008;pitch=Math.max(-1.45,Math.min(1.45,pitch+dy*.008));cameraMode='FREE';}gesture.x=e.clientX;gesture.y=e.clientY;});
canvas.addEventListener('pointerup',e=>{const p=pointers.get(e.pointerId);const click=!!p&&!p.moved&&pointers.size===1;pointers.delete(e.pointerId);gesture=null;if(click)pick(e.clientX,e.clientY);});
canvas.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);gesture=null;});
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(1.25,Math.min(8,zoom*Math.exp(e.deltaY*.001)));cameraMode='FREE';},{passive:false});
function pick(x,y){const m=currentMVP();let best=-1,bd=26;for(let i=0;i<states.length;i++){const p=project([positions[i*3],positions[i*3+1],positions[i*3+2]],m);if(!p)continue;const d=Math.hypot(p[0]-x,p[1]-y);if(d<bd){bd=d;best=i;}}if(best>=0)inspect(best);}

document.getElementById('system').onclick=()=>setSystem();
originButton.onclick=()=>focusRouteEndpoint('ORIGIN');
destinationButton.onclick=()=>focusRouteEndpoint('DESTINATION');
document.getElementById('reset').onclick=()=>{yaw=.55;pitch=.38;zoom=2.7;pan=[0,0];};

function applyOverlay(data){routeOverlay=data;const active=data?.active_route||null;routeId=active?.route_id||null;routeAuthority=active?.trajectory?.authority||null;routeStrips=routeOrdinaryStrips(active).map(pointsKm=>({pointsKm,positions:[],buffers:{pos:gl.createBuffer(),color:gl.createBuffer(),size:gl.createBuffer()}}));originButton.disabled=!resolveStateId(active?.origin);destinationButton.disabled=!resolveStateId(active?.destination);rebuildRoute();updateStatus();}
function loadOverlay(){fetch('/navigation-overlay.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();}).then(applyOverlay).catch(()=>{});}
fetch('/spatial-state.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json();}).then(data=>{snapshot=data;states=data.states||[];for(const s of states)byId.set(s.entity_id,s);epochEl.textContent=data.epoch_utc;frameEl.textContent=data.reference_frame;setSystem();loadOverlay();setInterval(loadOverlay,1000);}).catch(err=>{statusEl.textContent='SPATIAL LOAD FAILED\n'+err;});
requestAnimationFrame(draw);
})();
