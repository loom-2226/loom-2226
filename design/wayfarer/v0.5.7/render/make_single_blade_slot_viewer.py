"""Build a small, offline, touch-rotatable *single* iris-blade motion viewer."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_iris_one_blade_slot_results.json').read_text())
D={'paths':{'cam':J['cam_path'],'naive':J['naive_path']},
   'R':J['iris_R_m'],'T':J['blade_thickness_m'],
   'shell_normal_m':J['armor_normal_depth_m'],
   'angle':50,'source':'Rev7 PR432, research angular +1.2m / 50deg'}
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer Iris: One Blade Under Armour</title><style>
*{box-sizing:border-box}body{margin:0;background:#08131f;color:#e6eff8;font:14px system-ui,Arial,sans-serif}
header{background:#14253a;border-bottom:1px solid #34495e;display:flex;gap:12px;align-items:center;flex-wrap:wrap;justify-content:space-between;padding:10px 14px}
h1{font-size:17px;margin:0}small,.muted{color:#acc1d5}select,button{background:#2b4157;color:#eaf4ff;border:1px solid #718ca2;border-radius:6px;padding:8px}
main{display:grid;grid-template-columns:minmax(0,1fr) 315px;height:calc(100dvh - 70px)}
canvas{touch-action:none;width:100%;height:100%;background:radial-gradient(circle at center,#233c53,#08121f 70%)}
aside{border-left:1px solid #395169;padding:15px;overflow:auto;background:#122034}
label{display:block;margin:12px 0 6px}input[type=range]{width:100%;accent-color:#eaba76}
.stat{padding:8px 0;border-bottom:1px solid #374a62}.pass{color:#99e2ba}.fail{color:#ff9c98}
@media(max-width:740px){main{display:block;height:auto}canvas{height:60dvh}aside{border-left:0;border-top:1px solid #395169}}
</style></head><body>
<header><div><h1>WAYFARER · SINGLE IRIS BLADE</h1><small>Rigid 196 mm-thick leaf · metric source shell / pressure head · research only</small></div>
<select id="mechanism"><option value="cam">Retract first, then cam under armour</option><option value="naive">Rotate first, then push through armour</option></select>
<button id="reset">Reset camera</button></header>
<main><canvas id="v"></canvas><aside>
<label>Travel <b id="stepLabel"></b></label><input id="stage" type="range" min="0" max="92" step="1" value="92">
<label><input type="checkbox" id="skin" checked> Original angular nose + shoulder armour</label>
<label><input type="checkbox" id="pressure" checked> Original pressure head</label>
<label><input type="checkbox" id="leaf" checked> One solid armoured leaf</label>
<div id="results"></div>
<p><span style="color:#edbd74">■</span> Gold leaf: sampled collision-free in the selected path.<br><span style="color:#fa7777">■</span> Red leaf: intersects original fixed shoulder armour.</p>
<p class="muted"><b>Why the motion works:</b> pulling the blade backward while still over the empty central aperture lets it pass *under* the neighbouring solid armour as it begins rotating. The old path crossed the armour afterward.</p>
<p class="muted">The 20 cm normal angular shell, slit geometry and free axial cam travel are assumptions. No bearing, rim load path, tip seal, 16-blade coordination or actuator has been validated. This viewer is a useful physical thought experiment, not a finished shutter.</p>
<p class="muted">Drag to rotate. Mouse wheel zoom. Coordinates in metres; colour denotes sampled intersections, not certified clearance.</p>
</aside></main><script>
const DATA=__DATA__;const E=id=>document.getElementById(id);
const cvs=E('v'),ctx=cvs.getContext('2d');
const steps={'cam':DATA.paths.cam,'naive':DATA.paths.naive};
E('stage').max=steps.cam.length-1;E('stage').value=steps.cam.length-1;
let yaw=-.85,pitch=.36,zoom=72,drag=false,prev=null,W=0,H=0;
function outx(r){return -1.2+Math.max(0,r-2)*Math.tan(50*Math.PI/180)}
function pressx(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2))}
function v3(x,r,a){return [x,r*Math.cos(a),r*Math.sin(a)]}
function projection(p){let c=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
const u=p[0]*c-p[1]*s,dep=p[0]*s+p[1]*c;return [W/2+(u-.4)*zoom,H/2-(p[2]*cp-dep*sp)*zoom,dep*cp+p[2]*sp]}
let tris=[];
function tri(a,b,c,color,alpha){let x=projection(a),y=projection(b),z=projection(c);
tris.push({p:[x,y,z],depth:(x[2]+y[2]+z[2])/3,color,alpha})}
function cone(type){let a=type==='skin'?1.8:0, b=type==='skin'?4.5:4.3,radial=29,azimuth=64;
for(let i=0;i<radial;i++)for(let j=0;j<azimuth;j++){
let r0=a+(b-a)*i/radial,r1=a+(b-a)*(i+1)/radial,aa=j*2*Math.PI/azimuth,bb=(j+1)*2*Math.PI/azimuth;
let fn=type==='skin'?outx:pressx;
let A=v3(fn(r0),r0,aa),B=v3(fn(r1),r1,aa),C=v3(fn(r0),r0,bb),D=v3(fn(r1),r1,bb);
tri(A,B,C,type==='skin'?'#8799aa':'#5ac3f3',type==='skin'?.51:.13);
tri(B,D,C,type==='skin'?'#8799aa':'#5ac3f3',type==='skin'?.51:.13);
}}
function panel(s){const R=DATA.R,piv=R+.07,ph=22*Math.PI/180;let pivot=[piv*Math.cos(ph),piv*Math.sin(ph)];
let ang=s.angle_deg*Math.PI/180,co=Math.cos(ang),si=Math.sin(ang);
let nr=18,na=12;
function v(r,a,depth){let y=r*Math.cos(a),z=r*Math.sin(a);
let yy=pivot[0]+co*(y-pivot[0])-si*(z-pivot[1]);
let zz=pivot[1]+si*(y-pivot[0])+co*(z-pivot[1]);
return [s.x_front_m+depth,yy,zz]}
let col=s.fixed_armour_intersections?'#ff686b':'#edba71';
for(let i=0;i<nr;i++)for(let j=0;j<na;j++){
let r0=.12+(R-.12)*i/nr,r1=.12+(R-.12)*(i+1)/nr,half=12.25*Math.PI/180;
let a=-half+2*half*j/na,b=-half+2*half*(j+1)/na;
for(let depth of [0,DATA.T]){
let A=v(r0,a,depth),B=v(r1,a,depth),C=v(r0,b,depth),D=v(r1,b,depth);
tri(A,B,C,col,.97);tri(B,D,C,col,.97);
}
}}
function draw(){let pr=devicePixelRatio||1;W=cvs.clientWidth;H=cvs.clientHeight;
cvs.width=Math.round(W*pr);cvs.height=Math.round(H*pr);ctx.setTransform(pr,0,0,pr,0,0);
ctx.clearRect(0,0,W,H);
const path=steps[E('mechanism').value],index=Math.min(path.length-1,+E('stage').value),s=path[index];
tris=[];
if(E('pressure').checked)cone('pressure');
if(E('skin').checked)cone('skin');
if(E('leaf').checked)panel(s);
tris.sort((a,b)=>a.depth-b.depth);
for(let z of tris){ctx.globalAlpha=z.alpha;ctx.fillStyle=z.color;
ctx.beginPath();ctx.moveTo(z.p[0][0],z.p[0][1]);ctx.lineTo(z.p[1][0],z.p[1][1]);ctx.lineTo(z.p[2][0],z.p[2][1]);ctx.closePath();ctx.fill()}
ctx.globalAlpha=1;ctx.fillStyle='#d2e2f0';ctx.font='13px system-ui';ctx.fillText('Bow −x   |   x aft →   |   metres',15,25);
E('stepLabel').textContent=Math.round(s.stage_t*100)+'%';
E('results').innerHTML=
'<div class="stat">Blade rotation <b>'+s.angle_deg.toFixed(1)+'°</b></div>'+
'<div class="stat">Axial front x <b>'+s.x_front_m.toFixed(3)+' m</b></div>'+
'<div class="stat">Leaf outermost radius <b>'+s.max_r_m.toFixed(3)+' m</b></div>'+
'<div class="stat">Points inside existing armour <b class="'+(s.fixed_armour_intersections?'fail':'pass')+'">'+s.fixed_armour_intersections+'</b></div>'+
'<div class="stat">Minimum pressure gap <b>'+s.min_pressure_gap_m.toFixed(3)+' m</b></div>'+
'<div class="stat">Minimum clearance from inner armour face <b>'+(s.min_fixed_shell_sep_m===null?'N/A':s.min_fixed_shell_sep_m.toFixed(3)+' m')+'</b></div>'+
'<div class="stat muted">Current source: 16 leaves have NOT been physically integrated. This is exactly one solid leaf, not the full iris.</div>';
}
for(let id of ['stage','skin','pressure','leaf'])E(id).addEventListener('input',draw);
E('mechanism').addEventListener('change',()=>{E('stage').max=steps[E('mechanism').value].length-1;E('stage').value=E('stage').max;draw()});
cvs.addEventListener('pointerdown',e=>{drag=true;prev=[e.clientX,e.clientY];cvs.setPointerCapture(e.pointerId)});
cvs.addEventListener('pointerup',()=>drag=false);cvs.addEventListener('pointercancel',()=>drag=false);
cvs.addEventListener('pointermove',e=>{if(!drag)return;
yaw+=(e.clientX-prev[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-prev[1])*.008));
prev=[e.clientX,e.clientY];draw()});
cvs.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.min(180,Math.max(15,zoom*Math.exp(-e.deltaY*.001)));draw()},{passive:false});
E('reset').onclick=()=>{yaw=-.85;pitch=.36;zoom=72;draw()};addEventListener('resize',draw);draw();
</script></body></html>'''
path=ROOT/'render/out/nose_iris_single_blade_slot_viewer.html'
path.write_text(html.replace('__DATA__',json.dumps(D,separators=(',',':'))))
print('VIEWER',path.name,'size',path.stat().st_size)
