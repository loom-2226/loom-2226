"""Offline Android-safe 3D L1 viewer; no WebGL, libraries or remote assets.

Use existing F1-R2 and F1 original geometry, six acceleration seats, command
standing station and dedicated independent S4-site work area. Canvas2D software
projection and depth sorting. Purely visual, still non-canon/unqualified.
"""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parent.parent
j=json.loads((R/"command/L1_PAIRED_PILOT_CAPTAIN_STANDALONE_WORKAREA_20261029.json").read_text())
assert len(j["concepts"])==2
assert all(len(x["layout"]["seats"])==6 for x in j["concepts"])
data=json.dumps(j["concepts"],separators=(",",":"))
page=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>Wayfarer L1 · Android-safe interactive 3D</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;background:#07121f;color:#e3f1f8;font:14px system-ui,-apple-system,Arial,sans-serif}
header{padding:12px 16px;background:#10243a;border-bottom:1px solid #2d4963}
h1{margin:0 0 4px;font-size:19px;line-height:1.25}
small,p{color:#a9c5d7;line-height:1.5}small{font-size:12px}
main{max-width:1400px;margin:auto}
#stage{height:min(67dvh,700px);min-height:390px;position:relative;border-bottom:1px solid #28435b}
#view{display:block;width:100%;height:100%;touch-action:none;user-select:none}
#static{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#081321;pointer-events:none}
#floating{position:absolute;top:12px;left:12px;max-width:calc(100% - 24px);padding:8px 11px;
 background:#0d2236ed;border:1px solid #3d687e;border-radius:8px;pointer-events:none}
#floating strong{color:#9df7db}#floating span{display:block;color:#b8cede;font-size:11px;margin-top:3px}
#status{position:absolute;bottom:10px;left:12px;right:12px;color:#c2d5df;background:#081c2ddc;
 padding:7px 10px;border-radius:7px;font-size:11px;pointer-events:none}
.controls{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.card{background:#12263b;border:1px solid #284760;border-radius:10px;padding:12px}
h2{font-size:12px;letter-spacing:.07em;text-transform:uppercase;color:#8ee4dc;margin:0 0 9px}
button{border:1px solid #42677d;background:#1d3850;border-radius:7px;color:#e5f5fa;
 font:12px system-ui;padding:10px 11px;cursor:pointer;touch-action:manipulation}
button[aria-pressed=true]{background:#236561;border:2px solid #80e6dc;padding:9px 10px}
button:focus-visible{outline:2px solid white;outline-offset:2px}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
details{margin-top:10px;border-top:1px solid #2d4963;padding-top:10px}
summary{color:#bad9e7;cursor:pointer}
#description{color:#bed6df;font-size:12px;line-height:1.5}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;color:#b8cfde;font-size:11px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px}
@media(max-width:750px){#stage{height:54dvh;min-height:380px}.controls{grid-template-columns:1fr;padding:9px}
header h1{font-size:18px}}
</style></head><body>
<header><h1>WAYFARER · L1 COMMAND DECK</h1>
<small>Interactive 3D · Android-friendly Canvas renderer · no WebGL required · non-canon research</small></header>
<main>
<div id="stage">
<canvas id="view" aria-label="Rotatable three-dimensional schematic of Wayfarer L1 crew positions"></canvas>
<img id="static" alt="Static fallback rendering of the paired Pilot-Captain command deck" src="__FALLBACK__"/>
<div id="floating"><strong id="viewTitle">F1-R2 · Paired command</strong><span>Drag to rotate · pinch to zoom · two fingers to pan</span></div>
<div id="status">Loading 3D view. If interactive graphics cannot start, the static image remains visible.</div>
</div>
<div class="controls">
<div class="card"><h2>Compare the two designs</h2>
<div class="actions">
<button data-design="0" aria-pressed="true">NEW · Pilot + Captain raised</button>
<button data-design="1" aria-pressed="false">OLD · Original F1</button>
</div><p id="description">Pilot and Captain together on the elevated command tier, Navigator forward and lower. The former S4 position becomes a separate workbench.</p>
<h2>Camera</h2><div class="actions">
<button data-view="orbit" aria-pressed="true">3D orbit</button>
<button data-view="top" aria-pressed="false">Deck plan</button>
<button data-view="side" aria-pressed="false">Side / tier view</button>
<button id="reset">Reset view</button>
</div>
</div>
<div class="card"><h2>Layer visibility</h2>
<div class="actions">
<button data-layer="crew" aria-pressed="true">Crew figures</button>
<button data-layer="screens" aria-pressed="true">Screens</button>
<button data-layer="floors" aria-pressed="true">Decks</button>
<button data-layer="labels" aria-pressed="true">Station names</button>
</div><div class="legend">
<span><span class="dot" style="background:#e8c88a"></span>Pilot/Captain</span>
<span><span class="dot" style="background:#8ddafa"></span>Navigator</span>
<span><span class="dot" style="background:#82bdad"></span>Specialists</span>
<span><span class="dot" style="background:#cd98e2"></span>Standalone workbench</span>
</div>
<details><summary>Research boundaries</summary>
<p>This is a software-rendered, freely arranged concept. It does not certify pressure-hull fit, acceleration tolerance, safe egress, screen ergonomics or crew performance. All six functions retain separate acceleration work seats. The independent work area is not a seventh high-g seat.</p>
</details></div></div></main>
<noscript><p>JavaScript is needed for interaction. The static layout illustration should still appear above.</p></noscript>
<script>
"use strict";
const designs=__DATA__,cv=document.getElementById("view"),ctx=cv.getContext("2d");
const state={variant:0,yaw:-0.70,pitch:0.60,zoom:.79,panx:0,pany:0,
 crew:true,screens:true,floors:true,labels:true};
let lastDown=new Map(),lastPinch=null,drawn=false;
const roleName={PILOT:"PILOT",NAV:"NAVIGATOR",S1:"CAPTAIN",S2:"ENGINEERING",S3:"SENSORS / EW",S4:"MISSION OPS"};
const colors={PILOT:"#e3b86e",NAV:"#81d5ec",S1:"#e3b86e",S2:"#7bc3b6",S3:"#73b7ac",S4:"#8fbd9b"};
let rect={w:400,h:400,scale:32};
const HEX=(c,f=1)=>{const x=c.replace("#","");return "#"+[0,2,4].map(i=>Math.max(0,Math.min(255,Math.round(parseInt(x.slice(i,i+2),16)*f))).toString(16).padStart(2,"0")).join("")};
function toWorld(y,z,axial){return [y,z,4-axial]}
function projection(p){
 const dx=p[0],dy=p[1],h=p[2]-1.15;
 const cr=Math.cos(state.yaw),sr=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
 const side=cr*dx+sr*dy,dist=-sr*dx+cr*dy,vert=cp*h+sp*dist,dep=cp*dist-sp*h;
 return {x:rect.w/2+(side*rect.scale*state.zoom)+state.panx,
         y:rect.h*.53-(vert*rect.scale*state.zoom)+state.pany,dep};
}
let faces=[],markers=[];
function polygon(vertices,color,alpha=1){
 const pts=vertices.map(projection);
 const depth=pts.reduce((a,v)=>a+v.dep,0)/pts.length;
 faces.push({type:"poly",pts,color,alpha,depth});
}
function prism(vertices,color,alpha=1){
 // 0..3 lower; 4..7 upper, each quad projects separately for shaded 3D
 for(const [ids,f] of [[[0,1,2,3],.60],[[4,5,6,7],1.10],[[0,1,5,4],.70],
                        [[1,2,6,5],.84],[[2,3,7,6],.72],[[3,0,4,7],.93]]){
  polygon(ids.map(i=>vertices[i]),HEX(color,f),alpha);
 }
}
function box(x,y,z,wx,wy,wz,color,alpha=1){
 const a=x-wx/2,b=x+wx/2,c=y-wy/2,d=y+wy/2,e=z-wz/2,f=z+wz/2;
 prism([[a,c,e],[b,c,e],[b,d,e],[a,d,e],[a,c,f],[b,c,f],[b,d,f],[a,d,f]],color,alpha);
}
function oriented(seat,along,width,ht,boxL,boxW,boxH,color){
 const ang=seat.heading_deg*Math.PI/180,u=[Math.sin(ang),-Math.cos(ang)],v=[-u[1],u[0]];
 const cy=seat.center_yz[0]+along*u[0],cz=seat.center_yz[1]+along*u[1],floor=4-seat.base_x;
 const V=[];
 for(const h of [ht,ht+boxH])for(const [a,b] of [[-boxL/2,-boxW/2],[boxL/2,-boxW/2],[boxL/2,boxW/2],[-boxL/2,boxW/2]]){
  V.push([cy+a*u[0]+b*v[0]+width*v[0],cz+a*u[1]+b*v[1]+width*v[1],floor+h]);
 }
 prism(V,color);
}
function segment(a,b,r,color){
 const A=projection(a),B=projection(b);
 faces.push({type:"line",a:A,b:B,r,color,depth:(A.dep+B.dep)/2});
}
function sphere(p,r,color){
 const q=projection(p);faces.push({type:"sphere",p:q,r,color,depth:q.dep});
}
function label(p,text,color="#eaf4fc"){
 const q=projection(p);markers.push({...q,text,color});
}
function build(){
 faces=[];markers=[];
 const design=designs[state.variant],layout=design.layout;
 if(state.floors){
  for(const f of layout.platforms||[]){
   const w=4-f.x;
   box(f.y,f.z,w-.04,f.wy,f.wz,.10,"#344c63");
   // small illuminated guide stripes just inside slab perimeter
   const ztop=w+.01;
   polygon([[f.y-f.wy/2+.11,f.z-f.wz/2+.11,ztop],[f.y+f.wy/2-.11,f.z-f.wz/2+.11,ztop],
     [f.y+f.wy/2-.11,f.z-f.wz/2+.14,ztop],[f.y-f.wy/2+.11,f.z-f.wz/2+.14,ztop]],"#517e8e",.55);
  }
 }
 for(const seat of layout.seats){
  const upper=4-seat.base_x;
  const mat=colors[seat.id]||"#72bfb3";
  // Realistic-ish contoured acceleration WORK chair; articulated, not a slab bed
  oriented(seat,0,0,.13,1.62,.79,.15,"#344c62"); // structural tub
  oriented(seat,-.59,0,.26,.37,.64,.22,"#4b758c"); // head/body
  oriented(seat,-.23,0,.23,.51,.66,.15,mat); // torso pad
  oriented(seat,.18,0,.23,.40,.65,.12,mat); // pelvis
  oriented(seat,.48,0,.32,.38,.57,.13,"#537c94"); // bent thigh
  oriented(seat,.73,0,.19,.25,.53,.16,"#537c94"); // foot
  for(const q of [-.37,.37])oriented(seat,-.16,q,.35,.74,.065,.16,"#263f55");
  if(state.crew){
   // explicit head/torso/legs for occupied seats
   const ang=seat.heading_deg*Math.PI/180,u=[Math.sin(ang),-Math.cos(ang)];
   function at(t,h,lat=0){return [seat.center_yz[0]+t*u[0]+lat*Math.cos(ang),
      seat.center_yz[1]+t*u[1]+lat*Math.sin(ang),upper+h]}
   sphere(at(-.63,.61),.14,"#e6bb88");
   oriented(seat,-.25,0,.45,.48,.39,.14,"#d9c18c");
   for(const sign of [-1,1]){
    segment(at(-.36,.48,sign*.18),at(.0,.40,sign*.31),.065,"#d7b888");
    segment(at(.18,.40,sign*.16),at(.53,.52,sign*.15),.09,"#c9ad80");
    segment(at(.53,.52,sign*.15),at(.75,.34,sign*.15),.08,"#c9ad80");
   }
  }
  if(state.screens){
   const d=design.screens.find(v=>v.for_station===seat.id);
   if(d){
    const w=toWorld(d.center_xyz[1],d.center_xyz[2],d.center_xyz[0]);
    // slim upright rectangular screen near seat's existing display position
    box(w[0],w[1],w[2]+.20,.39,.06,.31,"#1b6074");
    box(w[0],w[1],w[2]+.23,.31,.025,.23,"#5cb9cb",.78);
   }
  }
  label(toWorld(seat.eye[1],seat.eye[2],seat.base_x-.75),roleName[seat.id],seat.id==='S1'?"#f6daa0":"#def4f5");
 }
 if(layout.stand){
  const s=layout.stand,y=s.anchor_yz[0],z=s.anchor_yz[1],up=4-s.floor_x;
  box(y,z,up+.46,.76,.39,.08,"#4e879a");
  box(y,z-.12,up+.77,.69,.07,.44,"#3b99ae",.88);
  for(let yy of [y-.31,y+.31])segment([yy,z-.25,up+.05],[yy,z-.18,up+.52],.025,"#9aadb8");
  label([y,z,up+.97],"COMMAND WORKPOINT","#9becdf");
 }
 if(layout.work_area){
  const w=layout.work_area,y=w.anchor_yz[0],z=w.anchor_yz[1],up=4-w.floor_x;
  box(y,z,up+.40,1.45,.61,.10,"#76507d");
  box(y,z-.22,up+.86,1.22,.08,.64,"#743e7d");
  box(y,z-.26,up+.90,1.08,.045,.50,"#c877d1",.87);
  for(const off of [-.58,.58])box(y+off,z+.2,up+.11,.18,.18,.24,"#596883");
  label([y,z,up+1.27],"INDEPENDENT MISSION WORK AREA","#f7bbf5");
 }
}
function starBackground(){
 const {w,h}=rect;ctx.fillStyle="#071421";ctx.fillRect(0,0,w,h);
 for(let i=0;i<100;i++){
  // deterministic distribution; no external image
  const xx=((i*173+39)%997)/997*w,yy=((i*431+131)%997)/997*h;
  const r=(i%13===0?1.25:.55);ctx.globalAlpha=i%4===0?.53:.23;
  ctx.fillStyle="#d3e6f5";ctx.beginPath();ctx.arc(xx,yy,r,0,Math.PI*2);ctx.fill();
 }
 ctx.globalAlpha=1;
}
function paint(){
 if(!ctx){document.getElementById("status").textContent="Canvas unsupported. Static view remains available.";return;}
 build();starBackground();
 faces.sort((a,b)=>b.depth-a.depth);
 for(const f of faces){
  ctx.globalAlpha=f.alpha===undefined?1:f.alpha;
  if(f.type==="poly"){
   ctx.beginPath();ctx.moveTo(f.pts[0].x,f.pts[0].y);
   for(const v of f.pts.slice(1))ctx.lineTo(v.x,v.y);
   ctx.closePath();ctx.fillStyle=f.color;ctx.fill();
   ctx.strokeStyle="rgba(10,23,36,.23)";ctx.lineWidth=.5;ctx.stroke();
  }else if(f.type==="sphere"){
   ctx.beginPath();ctx.arc(f.p.x,f.p.y,Math.max(2,f.r*rect.scale*state.zoom),0,Math.PI*2);
   ctx.fillStyle=f.color;ctx.fill();
  }else if(f.type==="line"){
   ctx.beginPath();ctx.moveTo(f.a.x,f.a.y);ctx.lineTo(f.b.x,f.b.y);
   ctx.lineWidth=Math.max(2,f.r*rect.scale*state.zoom*1.7);
   ctx.strokeStyle=f.color;ctx.lineCap="round";ctx.stroke();
  }
 }
 ctx.globalAlpha=1;
 if(state.labels){
  ctx.textAlign="center";ctx.font="600 10px system-ui";
  for(const m of markers){
   const text=m.text,tw=ctx.measureText(text).width;
   let x=Math.max(6+tw/2,Math.min(rect.w-6-tw/2,m.x));
   let y=Math.max(16,Math.min(rect.h-12,m.y-15));
   ctx.fillStyle="#10273eea";ctx.fillRect(x-tw/2-6,y-13,tw+12,18);
   ctx.strokeStyle="#46718a";ctx.lineWidth=.75;ctx.strokeRect(x-tw/2-6,y-13,tw+12,18);
   ctx.fillStyle=m.color;ctx.fillText(text,x,y);
  }
 }
 if(!drawn){drawn=true;document.getElementById("static").style.display="none";}
 document.getElementById("status").textContent=
  "RENDERED · "+designs[state.variant].id+" · 6 acceleration seats"+
   (designs[state.variant].layout.work_area?" + independent mission workbench":"")+
  " · non-canon geometry";
}
function resize(){
 const a=cv.getBoundingClientRect();if(a.width<2||a.height<2)return;
 const d=Math.min(window.devicePixelRatio||1,1.6);
 cv.width=Math.round(a.width*d);cv.height=Math.round(a.height*d);
 ctx.setTransform(d,0,0,d,0,0);
 rect={w:a.width,h:a.height,scale:Math.min(a.width/9.8,a.height/8.5)};
 paint();
}
function choose(n){
 state.variant=n;for(const b of document.querySelectorAll("[data-design]"))
 b.setAttribute("aria-pressed",+b.dataset.design===n?"true":"false");
 const v=designs[n];document.getElementById("viewTitle").textContent=v.id+" · "+v.name;
 document.getElementById("description").textContent=v.idea;
 paint();
}
function view(mode){
 if(mode==="orbit"){state.yaw=-.70;state.pitch=.60}
 if(mode==="top"){state.yaw=0;state.pitch=1.48}
 if(mode==="side"){state.yaw=-Math.PI/2;state.pitch=.16}
 state.zoom=.79;state.panx=state.pany=0;
 document.querySelectorAll("[data-view]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.view===mode?"true":"false"));
 paint();
}
document.querySelectorAll("[data-design]").forEach(b=>b.addEventListener("click",()=>choose(+b.dataset.design)));
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>view(b.dataset.view)));
document.querySelectorAll("[data-layer]").forEach(b=>b.addEventListener("click",()=>{
 const k=b.dataset.layer;state[k]=!state[k];b.setAttribute("aria-pressed",state[k]?"true":"false");paint();
}));
document.getElementById("reset").addEventListener("click",()=>view("orbit"));
cv.addEventListener("pointerdown",e=>{cv.setPointerCapture(e.pointerId);lastDown.set(e.pointerId,[e.clientX,e.clientY]);lastPinch=null;});
for(const ev of ["pointerup","pointercancel","lostpointercapture"])cv.addEventListener(ev,e=>{lastDown.delete(e.pointerId);lastPinch=null;});
cv.addEventListener("pointermove",e=>{
 if(!lastDown.has(e.pointerId))return;
 const prev=lastDown.get(e.pointerId);lastDown.set(e.pointerId,[e.clientX,e.clientY]);
 if(lastDown.size===1){
  state.yaw+=(e.clientX-prev[0])*.008;
  state.pitch=Math.max(.05,Math.min(1.56,state.pitch-(e.clientY-prev[1])*.006));
 }else if(lastDown.size===2){
  const p=[...lastDown.values()],dst=Math.hypot(p[0][0]-p[1][0],p[0][1]-p[1][1]);
  const mx=(p[0][0]+p[1][0])/2,my=(p[0][1]+p[1][1])/2;
  if(lastPinch){
   state.zoom=Math.max(.45,Math.min(2.7,state.zoom*(dst/lastPinch.dst)));
   state.panx+=mx-lastPinch.mx;state.pany+=my-lastPinch.my;
  }
  lastPinch={dst,mx,my};
 }
 paint();
});
cv.addEventListener("wheel",e=>{e.preventDefault();state.zoom=Math.max(.45,Math.min(2.7,state.zoom*Math.exp(-e.deltaY*.001)));paint()},{passive:false});
window.addEventListener("resize",resize);
try{resize()}catch(e){document.getElementById("status").textContent="Interactive renderer error: "+e.message;console.error(e)}
</script></body></html>'''
out=R/"render/out/wayfarer_l1_android_safe_3d.html"
from base64 import b64encode
preview=R/"render/out/l1_android_preview.png"
fallback=("data:image/png;base64,"+b64encode(preview.read_bytes()).decode("ascii")) if preview.exists() else (
 "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20400%20400%22%3E%3Crect%20width%3D%22400%22%20height%3D%22400%22%20fill%3D%22%230b2336%22/%3E%3Ctext%20x%3D%22200%22%20y%3D%22200%22%20fill%3D%22white%22%20text-anchor%3D%22middle%22%3EStatic%20preview%20unavailable%3C/text%3E%3C/svg%3E")
out.write_text(page.replace("__DATA__",data).replace("__FALLBACK__",fallback),encoding="utf-8")
print("VIEWER",out,"bytes",out.stat().st_size)