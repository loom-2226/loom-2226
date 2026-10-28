"""Self-contained actual-source L1 command-deck 3D plus clearly speculative new canopy.

Reuses existing LOOM v0.5.7 WebGL2 renderer and authoritative source geometry
for six couches, occupants, displays, deck, ladders, flight deck support.
Only the 37 outer panes, two seamless inner domes and optogel are non-canon
research overlays. No network resources, no production/runtime mutation.
"""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
gp=ROOT/'out/wayfarer_v05_geometry.json'
G=json.loads(gp.read_text()); C=json.loads((HERE/'out/l1_scene.json').read_text())
assert hashlib.sha256(gp.read_bytes()).hexdigest()==C['geometry_sha256']
T=json.loads((ROOT/'command/l1_replaceable_outer_tiles_results.json').read_text())
N=json.loads((ROOT/'command/l1_nested_pressure_dome_failover_results.json').read_text())
assert T['tile_areas_and_seams']['staggered_trapezoids_compact_12']['panel_count']==37
P=T['tile_presets']['staggered_trapezoids_compact_12']
assert P['rings']==[0,.75,2,2.75,3.5] and P['ns']==[1,12,12,12]
assert abs(N['reference_separation_m']-.12)<1e-8
parts=[p for p in G['parts'] if p['id'] in ('floor_L1','flight_deck','bow_sensors')
       or p['id'].startswith('flight_deck_column_')]
# The old hull, frames and shutter crown are OMITTED; the pressure shell
# above r3.5 and outer opaque bow are built explicitly below.
data={'geo':{'version':G['version'],'length_m':G['length_m'],
       'parts':parts,'features':[],'skin':False,'window_bore':None},
      'cmd':C, 'panels':P,'geometry_sha256':C['geometry_sha256'],
      'shell_offset':N['reference_separation_m']}
engine=(HERE/'loomgl.js').read_text()
engine=re.sub(r'^export\s+','',engine,flags=re.M)
# Adapt renderer copy IN OUTPUT HTML ONLY, keeping source loomgl.js intact.
engine=engine.replace('  frame:        {c: [0.30, 0.31, 0.33], m: 0.6, r: 0.4, nosec: 1},',
'''  frame:        {c: [0.30, 0.31, 0.33], m: 0.6, r: 0.4, nosec: 1},
  l1_outer_glass: {c:[0.30,0.70,0.79],m:0.05,r:0.1,em:[0.016,0.03,0.038],nosec:1},
  l1_inner_glass: {c:[0.47,0.78,0.77],m:0.07,r:0.1,em:[0.015,0.031,0.03],nosec:1},
  l1_backup_glass: {c:[0.60,0.76,0.92],m:0.04,r:0.1,em:[0.018,0.025,0.04],nosec:1},
  l1_optogel: {c:[0.25,0.75,0.72],m:0.02,r:0.2,em:[0.004,0.01,0.009],nosec:1},
  l1_seam: {c:[0.025,0.10,0.145],m:0.6,r:0.2,nosec:1},
  l1_rim: {c:[0.28,0.34,0.40],m:0.4,r:0.4,nosec:1},''')
engine=engine.replace('if (crown) {\n      const G = crownMeshes(crown, this.xc);', 'if (crown && !cfg.customCanopy) {\n      const G = crownMeshes(crown, this.xc);')
assert 'crown && !cfg.customCanopy' in engine
assert 'l1_backup_glass' in engine
engine=engine.replace('if(!gl_FrontFacing){ if(uClipOn>0.5', 'if(!gl_FrontFacing && uAlpha>=0.999){ if(uClipOn>0.5')
engine=engine.replace('vec3 n=normalize(vN); vec3 v=normalize(uEye-vW);','vec3 n=normalize(gl_FrontFacing?vN:-vN); vec3 v=normalize(uEye-vW);')
engine=engine.replace('o=vec4(pow(aces(col*uExp),vec3(1.0/2.2)),1.0);','o=vec4(pow(aces(col*uExp),vec3(1.0/2.2)),uAlpha);')
assert 'uAlpha);' in engine
engine=engine.replace('if (m.mat === "plume") continue; gl.uniform1f(this.shp.U.uClipOn', 'if (m.mat === "plume" || (m.alpha !== undefined && m.alpha < 1)) continue; gl.uniform1f(this.shp.U.uClipOn')
engine=engine.replace('    for (const m of this.meshes) {\n      if (m.mat === "plume") continue;\n      const mt = MATS[m.mat] || MATS.equipment;',
'''    const orderedMeshes = [...this.meshes.filter(m => (m.alpha ?? 1) >= 0.999),...this.meshes.filter(m => (m.alpha ?? 1) < 0.999)];
    for (const m of orderedMeshes) {
      if (m.mat === "plume") continue;
      const alpha=m.alpha ?? 1;
      if(alpha<0.999){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);}
      else{gl.depthMask(true);gl.disable(gl.BLEND);}
      const mt = MATS[m.mat] || MATS.equipment;''')
engine=engine.replace('gl.uniform1f(U.uAlpha, 1); gl.uniform1f(U.uSec', 'gl.uniform1f(U.uAlpha, alpha); gl.uniform1f(U.uSec')
engine=engine.replace('    const pl = this.meshes.find(m => m.mat === "plume");','    gl.depthMask(true);gl.disable(gl.BLEND);\n    const pl = this.meshes.find(m => m.mat === "plume");')
assert 'const orderedMeshes' in engine

html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LOOM 2226 · Wayfarer L1 full 3D</title>
<style>
:root{color-scheme:dark;--bg:#070e18;--pane:#111f2f;--line:#2a465b;--ice:#d5e8f2;--cyan:#79e6de;--muted:#91afc4;--gold:#edbd88}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ice);font:14px system-ui,Arial,sans-serif}
header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;padding:10px 15px;background:#112234;border-bottom:1px solid var(--line)}
h1{font-size:18px;margin:0 0 4px;font-weight:650;letter-spacing:.03em}small{color:var(--muted);font-size:11px}
main{max-width:1500px;margin:0 auto}
#stage{height:min(68dvh,790px);min-height:340px;position:relative;background:#040910;border-bottom:1px solid var(--line)}
#cv{width:100%;height:100%;display:block;touch-action:none}
.hud{position:absolute;left:12px;top:10px;padding:8px 11px;border:1px solid #2d556a;background:#091826dd;border-radius:8px;pointer-events:none;max-width:300px}
.hud b{color:#c0f7ee}.hud small{line-height:1.6;display:block}
.legend{position:absolute;bottom:10px;left:11px;right:11px;pointer-events:none;color:#a8c2d0;font-size:11px;background:#071321b5;padding:6px 10px;border-radius:6px}
section.controls{padding:14px;display:grid;grid-template-columns:minmax(0,1.5fr) minmax(250px,1fr);gap:15px}
.panel{border:1px solid #274358;background:#102034;border-radius:11px;padding:12px;min-width:0}
.panel h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#8adcd8;margin:0 0 12px}
.line{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin-bottom:11px}
.chip{background:#233d51;border:1px solid #496a7f;color:#d5e8f2;border-radius:6px;padding:8px 10px;font:12px system-ui;cursor:pointer}
.chip[aria-pressed=true]{background:#1b716f;color:#f7fffe;border-color:#86e9da}
.chip:focus-visible{outline:2px solid white;outline-offset:2px}
.checks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px 14px;margin:10px 0 0}
.checks label{display:flex;align-items:center;gap:7px;font-size:12px;color:#c8dbe5}
.checks input{accent-color:#65d9d0}
.stat{padding:7px 0;border-bottom:1px solid #284253;display:flex;justify-content:space-between;gap:10px;font-size:12px}
.stat strong{text-align:right;color:#b8eadd;font-variant-numeric:tabular-nums}
p.note{font-size:12px;line-height:1.5;color:#a6c2d1;margin:8px 0}
a{color:#98e6e1}
@media(max-width:750px){section.controls{grid-template-columns:1fr;padding:9px}#stage{height:58dvh;min-height:380px}.hud{max-width:72%}.chip{padding:9px}}
</style></head><body>
<header><div><h1>WAYFARER · L1 COMMAND DECK / FULL 3D</h1>
<small>Source-based six-station interior · held 37 protective tiles · optogel seamless-canopy research overlay · NON-CANON</small></div>
<div><small>LOOM 2226 / INTERACTIVE GEOMETRY EXPERIMENT</small></div></header>
<main>
<div id="stage">
<canvas id="cv" aria-label="Interactively rendered 3D model of Wayfarer L1 command deck"></canvas>
<div class="hud"><b id="viewname">3D cutaway</b><small id="vsubtitle">One finger to rotate · pinch to zoom · two fingers to pan</small></div>
<div class="legend">Spacecraft bow points toward −X · all dimensions in metres · Crew/furniture from source Rev 7 · glazed canopy is speculative research</div>
</div>
<section class="controls">
<div class="panel"><h2>Camera / views</h2>
<div class="line" id="viewBtns">
<button class="chip" data-view="CUT" aria-pressed="true">Deck cutaway</button>
<button class="chip" data-view="EXT" aria-pressed="false">Exterior bow</button>
<button class="chip" data-view="PILOT" aria-pressed="false">Pilot eye</button>
<button class="chip" data-view="NAV" aria-pressed="false">Navigator</button>
<button class="chip" data-view="S1" aria-pressed="false">Support 1</button>
<button class="chip" data-view="S2" aria-pressed="false">Support 2</button>
<button class="chip" data-view="S3" aria-pressed="false">Support 3</button>
<button class="chip" data-view="S4" aria-pressed="false">Support 4</button>
<button class="chip" data-view="STAND" aria-pressed="false">Standing</button>
</div>
<h2>Canopy optical state (proposed 2226 material)</h2>
<div class="line" id="lightBtns">
<button class="chip" data-light="clear" aria-pressed="true">Clear</button>
<button class="chip" data-light="glare" aria-pressed="false">Glare control</button>
<button class="chip" data-light="dark" aria-pressed="false">Dark / blackout</button>
</div>
<h2>Mechanical gel state (independent of light control)</h2>
<div class="line" id="mechanicalBtns">
<button class="chip" data-mech="gel" aria-pressed="true">Compliant gel</button>
<button class="chip" data-mech="locked" aria-pressed="false">Locked / solid-like</button>
</div>
<p class="note">Modes illustrate the research concept visually. No claimed switching speed, blast resistance or structural safety is implied.</p>
</div>
<div class="panel"><h2>Explore actual L1 components</h2>
<div class="checks">
<label><input type="checkbox" id="outer" checked>37 outer replaceable tiles</label>
<label><input type="checkbox" id="seams" checked>Panel seam outlines</label>
<label><input type="checkbox" id="pressure" checked>Two seamless pressure domes</label>
<label><input type="checkbox" id="gel" checked>Adaptive optogel volume</label>
<label><input type="checkbox" id="crew" checked>Occupants</label>
<label><input type="checkbox" id="sensors" checked>Original bow sensor ring</label>
<label><input type="checkbox" id="rim" checked>Opaque pressure/armor rim</label>
<label><input type="checkbox" id="labels" checked>Station labels</label>
</div>
<div class="stat"><span>Command stations</span><strong>6 (2 flight + 4 support)</strong></div>
<div class="stat"><span>External protective modules</span><strong>37</strong></div>
<div class="stat"><span>Transparent crown diameter</span><strong>7.00 m</strong></div>
<div class="stat"><span>Unframed pressure domes</span><strong>2 · rim retained</strong></div>
<div class="stat"><span>Nominal inter-dome axial offset</span><strong>0.12 m</strong></div>
<div class="stat"><span>Adaptive gel inventory</span><strong>~3.02 m³ (hypothetical)</strong></div>
<p class="note">The cockpit, consoles, occupants, flight deck, floor and ladders come from the L1 model. The outer 37 panels and seamless double pressure dome/gel are explicitly held non-canon concept geometry. Glass thickness, refraction, material stress, actual hydraulic controls and tile mounting are NOT verified.</p>
</div>
</section></main>
<script>
__ENGINE__
const DATA=__DATA__;
const G=DATA.geo,C=DATA.cmd;
const canvas=document.getElementById('cv'),stage=document.getElementById('stage');
let ship=null,error=null;
try{ship=new Ship(canvas,G,{shadowSize:1024});}catch(e){error=String(e);stage.insertAdjacentHTML('beforeend','<p style="padding:18px;color:orange">WebGL2 unavailable: '+String(e)+'</p>');}
const D2=Math.PI/180,cos=Math.cos,sin=Math.sin;
function face3(x,r,t){return [x,r*cos(t),r*sin(t)]}
function Xpress(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2))}
function Xext(r){return -1.2+Math.max(0,r-2)*Math.tan(50*D2)}
const opts={view:'CUT',light:'clear',mech:'gel',outer:true,seams:true,pressure:true,gel:true,crew:true,sensors:true,rim:true,labels:true};
const COLOR={outer:'#7ce1e4',inner:'#e6cea0',backup:'#a7c9fc'};
function group(mat,mb,alpha=1){
 if(mb.i.length===0) return;
 const gl=ship.gl,m={mat,system:'l1research',n:mb.i.length,ids:[mat],alpha,noclip:true};
 m.pb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,m.pb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(mb.p),gl.STATIC_DRAW);
 m.nb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,m.nb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(mb.n),gl.STATIC_DRAW);
 m.ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,m.ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(mb.i),gl.STATIC_DRAW);
 ship.meshes.push(m);
}
function surface(mb,xf,r0,r1,a0,a1,nr=14,nt=12,outside=true){
 for(let j=0;j<nr;j++){
  const rA=r0+(r1-r0)*j/nr,rB=r0+(r1-r0)*(j+1)/nr,
        A=[],B=[],NA=[],NB=[];
  for(let k=0;k<=nt;k++){
    const theta=a0+(a1-a0)*k/nt,c=cos(theta),s=sin(theta);
    const norm=(r)=> {
      const d=.0001,dX=(xf(Math.min(r+.0001,3.8))-xf(Math.max(0,r-.0001)))/(.0002);
      const sign=outside?1:-1,den=Math.hypot(1,dX);
      return [sign*(-1/den),sign*dX*c/den,sign*dX*s/den];
    };
    A.push(face3(xf(rA),rA,theta));B.push(face3(xf(rB),rB,theta));
    NA.push(norm(rA));NB.push(norm(rB));
  }
  mb.strip(A,B,NA,NB,k=>NA[k]);
 }
}
function arc(mb,xf,r,a0,a1,tube=.008,step=128){
 for(let k=0;k<step;k++){
  const th=a0+(a1-a0)*k/step,th2=a0+(a1-a0)*(k+1)/step;
  meshTube(mb,{p0:face3(xf(r)-.008,r,th),p1:face3(xf(r)-.008,r,th2),r:tube},7);
 }
}
function spoke(mb,xf,r0,r1,th){
 const n=28;
 for(let i=0;i<n;i++){
  const ra=r0+(r1-r0)*i/n,rb=r0+(r1-r0)*(i+1)/n;
  meshTube(mb,{p0:face3(xf(ra)-.009,ra,th),p1:face3(xf(rb)-.009,rb,th),r:.006},7);
 }
}
function makeCanopy(){
 const p=DATA.panels;
 if(opts.outer){
   const mb=new MB(ship.xc);
   // Each independently removable pane has its own angular/radial boundary.
   for(let j=0;j<p.ns.length;j++){
     const n=p.ns[j],r0=p.rings[j],r1=p.rings[j+1],off=p.offsets[j];
     for(let k=0;k<n;k++){
       let a0=off+k*2*Math.PI/n,a1=off+(k+1)*2*Math.PI/n;
       const inset=j===0?0:.005/Math.max(r0,.2);
       const ra=r0+(j===0?0:.005),rb=r1-.005;
       if(j===0)surface(mb,Xext,0,rb,0,2*Math.PI,18,120);
       else surface(mb,Xext,ra,rb,a0+inset,a1-inset,18,9);
     }
   }
   group('l1_outer_glass',mb,.20);
 }
 if(opts.pressure){
   // NOTE: all layers optically uninterrupted, no intermediate metal bars.
   const inner=new MB(ship.xc),backup=new MB(ship.xc);
   surface(inner,Xpress,0,3.5,0,2*Math.PI,60,120,false);
   surface(backup,r=>Xpress(r)-DATA.shell_offset,0,3.5,0,2*Math.PI,60,120,false);
   group('l1_inner_glass',inner,.22);
   group('l1_backup_glass',backup,.18);
 }
 if(opts.gel){
   const mb=new MB(ship.xc);
   // A volume can't be shown by a single opaque hull; depict its continuous
   // intermediate isosurface plus physical closing side boundary at r=3.5.
   surface(mb,r=>Xpress(r)-DATA.shell_offset/2,0,3.5,0,2*Math.PI,40,100,false);
   let alpha=opts.light==='clear'?.065:opts.light==='glare'?.30:.84;
   if(opts.mech==='locked')alpha+=.025;
   MATS.l1_optogel.c=opts.light==='dark'?[.025,.055,.088]:opts.light==='glare'?[.10,.32,.34]:[.25,.75,.72];
   group('l1_optogel',mb,alpha);
 }
 if(opts.rim){
   const rim=new MB(ship.xc);
   surface(rim,Xpress,3.5,4.15,0,2*Math.PI,20,120,false);
   // opacity is opaque structural region, NOT an extra glazing frame.
   group('l1_rim',rim,1);
 }
 if(opts.seams){
   const m=new MB(ship.xc);
   for(let r of [.75,2,2.75,3.5])arc(m,Xext,r,0,2*Math.PI,r===3.5?.015:.007);
   for(let j=1;j<DATA.panels.ns.length;j++){
     const n=DATA.panels.ns[j],off=DATA.panels.offsets[j];
     for(let k=0;k<n;k++)spoke(m,Xext,DATA.panels.rings[j],DATA.panels.rings[j+1],off+2*Math.PI*k/n);
   }
   group('l1_seam',m);
 }
}
function rebuild(){
 if(!ship)return;
 ship.build({show:p=>p.id!=='bow_sensors'||opts.sensors,
   cmd:C,cmdHideCrew:(opts.crew?(opts.view==='CUT'||opts.view==='EXT'?[]:[opts.view]):C.couches.map(c=>c.id)),
   crown:{r:3.5},customCanopy:true,features:false,windowFrames:false,shuttersClosed:false,bands:false,shuttleDetail:false});
 makeCanopy();dirty=true;
}
let cam={az:-2.65,el:.28,dist:11.7,tx:1.35,ty:0,tz:0},look={yaw:0,pitch:0,fov:102};
let dirty=true,first=true;
function camEye(){
 return [cam.tx-cam.dist*sin(cam.el),cam.ty+cam.dist*cos(cam.el)*cos(cam.az),cam.tz+cam.dist*cos(cam.el)*sin(cam.az)];
}
function basis(){
 if(opts.view==='STAND')return [[2.05,0,1.4],[-1,0,0],[0,0,1]];
 const c=C.couches.find(x=>x.id===opts.view);
 if(!c)return null;
 const up=[0,c.head[0]-c.feet[0],c.head[1]-c.feet[1]],mag=Math.hypot(...up);
 return [c.eye,[-1,0,0],up.map(v=>v/mag)];
}
function redraw(){
 if(!ship || !dirty)return;
 dirty=false;const isEye=!['CUT','EXT'].includes(opts.view);
 if(isEye){
  const [eye,fw,up]=basis();const right=[fw[1]*up[2]-fw[2]*up[1],fw[2]*up[0]-fw[0]*up[2],fw[0]*up[1]-fw[1]*up[0]];
  const cp=cos(look.pitch),dir=[0,1,2].map(i=>fw[i]*cp*cos(look.yaw)+right[i]*cp*sin(look.yaw)+up[i]*sin(look.pitch));
  ship.draw({eye,target:eye.map((v,i)=>v+dir[i]),up,fov:look.fov,near:.03,sun:[-.6,.3,.6],
    planet:true,planetC:[-2100,1200,720],planetR:900,shadows:false,holes:false,
    lights:[{at:[1.1,0.7,.5],c:[3.0,3.3,3.2]},{at:[2.9,-1.8,-.8],c:[1.8,2.1,2.6]}],exposure:1.25});
 }else{
  ship.draw({eye:camEye(),target:[cam.tx,cam.ty,cam.tz],up:[-1,0,0],fov:42,near:.05,
  clip:opts.view==='CUT'?[0,-1,0,-.23]:null,
  shadows:false,planet:false,holes:false,sun:[-.35,.45,.70],exposure:1.3,
  lights:[{at:[1,.5,1],c:[2.5,2.7,3.0]},{at:[2,-1,-1],c:[2.5,2.2,2.1]}]});
 }
 drawLabels();
}
function drawLabels(){
 stage.querySelectorAll('.label3d').forEach(x=>x.remove());
 if(!opts.labels||!['CUT','EXT'].includes(opts.view))return;
 for(let c of C.couches){
  const a=ship.project(c.eye[0],c.eye[1],c.eye[2]),rect=canvas.getBoundingClientRect();
  if(!a[2]||a[0]<25||a[1]<25||a[0]>rect.width-25||a[1]>rect.height-20)continue;
  const b=document.createElement('span');b.className='label3d';b.textContent=c.id;
  b.style.cssText='position:absolute;pointer-events:none;left:'+a[0]+'px;top:'+a[1]+'px;transform:translate(-50%,-150%);font-size:10px;letter-spacing:.05em;color:#e6fdf9;background:#09202bdc;border:1px solid #528b9a;border-radius:4px;padding:2px 5px';
  stage.appendChild(b);
 }
}
function resize(){
 const rect=canvas.getBoundingClientRect(),pixel=Math.min(devicePixelRatio||1,1.5);
 canvas.width=Math.max(2,Math.round(rect.width*pixel));canvas.height=Math.max(2,Math.round(rect.height*pixel));
 if(first){cam.dist=Math.max(10,Math.min(17,4.1/Math.tan(20*D2)/Math.max(.5,rect.width/rect.height)));first=false;}
 dirty=true;redraw();
}
function selectView(v){
 opts.view=v;look={yaw:0,pitch:0,fov:100};
 if(v==='CUT'){cam={az:-2.65,el:.28,dist:11.7,tx:1.35,ty:0,tz:0};}
 else if(v==='EXT'){cam={az:-.18,el:.32,dist:12,tx:.3,ty:0,tz:0};}
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.view===v?'true':'false'));
 document.getElementById('viewname').textContent=({'CUT':'L1 deck cutaway','EXT':'Exterior bow'}[v]||v+' eye position');
 document.getElementById('vsubtitle').textContent=['CUT','EXT'].includes(v)?
 'Drag to orbit · pinch to zoom · two fingers pan':'Drag to turn head · pinch for field of view';
 rebuild();
}
const activePointers=new Map();let pinch=null;
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);activePointers.set(e.pointerId,[e.clientX,e.clientY]);pinch=null;});
for(let type of ['pointerup','pointercancel'])canvas.addEventListener(type,e=>{activePointers.delete(e.pointerId);pinch=null;});
canvas.addEventListener('pointermove',e=>{
 if(!activePointers.has(e.pointerId))return;
 const old=activePointers.get(e.pointerId);activePointers.set(e.pointerId,[e.clientX,e.clientY]);
 const eye=!['CUT','EXT'].includes(opts.view);
 if(activePointers.size===1){
  if(eye){look.yaw-=(e.clientX-old[0])*.005;look.pitch=Math.max(-1.42,Math.min(1.42,look.pitch-(e.clientY-old[1])*.005))}
  else{cam.az-=(e.clientX-old[0])*.007;cam.el=Math.max(-1.4,Math.min(1.4,cam.el+(e.clientY-old[1])*.006))}
  dirty=true;redraw();
 }else if(activePointers.size===2){
  const q=[...activePointers.values()],dist=Math.hypot(q[0][0]-q[1][0],q[0][1]-q[1][1]),mid=[(q[0][0]+q[1][0])/2,(q[0][1]+q[1][1])/2];
  if(pinch){if(eye)look.fov=Math.max(40,Math.min(125,look.fov*pinch.dist/dist));
   else{cam.dist=Math.max(2.8,Math.min(35,cam.dist*pinch.dist/dist));
     cam.ty-=(mid[0]-pinch.mid[0])*cam.dist*.0013;cam.tz+=(mid[1]-pinch.mid[1])*cam.dist*.0013;}}
  pinch={dist,mid};dirty=true;redraw();
 }
});
canvas.addEventListener('wheel',e=>{e.preventDefault();if(['CUT','EXT'].includes(opts.view))cam.dist=Math.max(2.8,Math.min(35,cam.dist*Math.exp(e.deltaY*.001)));
 else look.fov=Math.max(40,Math.min(125,look.fov*Math.exp(e.deltaY*.001)));dirty=true;redraw();},{passive:false});
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>selectView(b.dataset.view)));
document.querySelectorAll('[data-light]').forEach(b=>b.addEventListener('click',()=>{opts.light=b.dataset.light;document.querySelectorAll('[data-light]').forEach(z=>z.setAttribute('aria-pressed',z===b?'true':'false'));rebuild();}));
document.querySelectorAll('[data-mech]').forEach(b=>b.addEventListener('click',()=>{opts.mech=b.dataset.mech;document.querySelectorAll('[data-mech]').forEach(z=>z.setAttribute('aria-pressed',z===b?'true':'false'));rebuild();}));
for(let k of ['outer','pressure','seams','gel','crew','sensors','rim','labels'])document.getElementById(k).addEventListener('change',e=>{opts[k]=e.target.checked;rebuild();});
window.addEventListener('resize',resize);
rebuild();resize();redraw();
</script></body></html>'''
out=HERE/'out/wayfarer_l1_full_3d_37panel_optogel.html'
out.write_text(html.replace('__ENGINE__',engine).replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('OUTPUT',out,'bytes',out.stat().st_size,'parts',len(parts),'couches',len(C['couches']),'panels',T['tile_areas_and_seams']['staggered_trapezoids_compact_12']['panel_count'])