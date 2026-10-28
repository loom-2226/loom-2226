"""Portable self-contained rotatable Wayfarer protected central iris model.

The displayed blades are the actual 16 rigid wedge surfaces from the saved
parametric motion test, using modelled pressure/outer source coordinates.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_armoured_iris_results.json').read_text())
G=json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
options=[]
for x in J['results']:
    options.append({
        'name':x['design']+' / R '+str(x['requested_clear_radius_m']),
        'shape':x['shape'],'R':x['requested_clear_radius_m'],
        'best':x['first_usable_angle'],'stow':x['stow_annulus'],
        'frames':[{k:v for k,v in q.items() if k in
          ('angle_deg','center_clear_radius_m','max_leaf_radial_m','same_tier_overlap','low_x_shift_m','high_x_shift_m','axial_shift_slot_m','two_tier_press_clear_possible')}
           for q in x['frames']],
        'visibility':{k:v for k,v in x.get('associated_window_layout_visibility',{}).items() if k!='stations'}
    })
data={'options':options,'nodes':[f['pos'] for f in G['features'] if f.get('kind')=='node_face' and f.get('ring')==0],
      'thickness_m':J['single_blade_thickness_m'],'two_tier_depth_m':J['two_level_stack_depth_m'],
      'count':16,'overlap_deg':J['blade_edge_angular_overlap_deg'],
      'pivot_dr':.07,'pivot_phi_deg':22,'source':'PR432 geometry, separate research branch'}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer Central Armoured Iris</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#07111f;color:#e7eef8;font:14px system-ui,sans-serif}
header{display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:wrap;padding:12px;background:#132338;border-bottom:1px solid #344a60}
h1{font-size:17px;margin:0}small,.muted{color:#aebfd2}
select,button{background:#29425b;color:#e8f2fb;border-radius:6px;border:1px solid #718da5;padding:7px;max-width:100%}
main{display:grid;grid-template-columns:minmax(0,1fr) 315px;height:calc(100dvh - 68px)}
canvas{width:100%;height:100%;touch-action:none;background:radial-gradient(ellipse at center,#1a2c41,#07111f 70%);cursor:grab}
aside{border-left:1px solid #35516a;background:#101d2f;padding:15px;overflow:auto}
label{display:block;margin:8px 0}input[type=range]{width:100%;accent-color:#e6b981}
.stat{padding:8px 0;border-bottom:1px solid #2d435b}.no{color:#ff9795}.yes{color:#a4e0bd}
h3{font-size:14px;margin:18px 0 7px}.key{display:inline-block;width:12px;height:12px;vertical-align:middle;margin-right:6px}
@media(max-width:750px){main{display:block;height:auto}canvas{height:62dvh}aside{max-height:none;border-left:none;border-top:1px solid #35516a}}
</style></head><body>
<header><div><h1>WAYFARER · CENTRAL ARMOURED IRIS</h1><small>16 moving metre-scale leaves · real source envelope · research, NOT QUALIFIED</small></div>
<select id="model"></select><button id="reset">Reset camera</button></header>
<main><canvas id="view"></canvas><aside>
<strong>Iris motion</strong><label>Opening angle <span id="angleLabel">0°</span></label>
<input id="stage" type="range" min="0" max="90" value="62" step="1">
<label><input type="checkbox" id="blades" checked> 16 overlapping armour leaves</label>
<label><input type="checkbox" id="shell" checked> Outer armoured nose</label>
<label><input type="checkbox" id="pressure" checked> Existing pressure head</label>
<label><input type="checkbox" id="sensors"> Sensor ring and Metric nodes</label>
<div id="stats"></div>
<h3>Key</h3>
<p><span class="key" style="background:#e7b576"></span> Outer-tier leaves
<span class="key" style="background:#65c6b9"></span> Inner-tier leaves</p>
<p><span class="key" style="background:#6a94ae"></span> Fixed armour
<span class="key" style="background:#62b7ee"></span> Pressure head</p>
<h3>Limits of this test</h3>
<p class="muted">The 16 polygonal blades mathematically cover the closed disk. <b>That is not a physically sealed zero-radius closure.</b> The central tips need a real overlap/seal, likely a tiny cap or articulated tip. Outer and inner tiers are staggered ~0.413 m; flush closure across their seams has not been achieved.</p>
<p class="muted">The open-state blades turn into an opaque annulus. The pressure-head slot is an idealised axial interval, not a manufactured bearing, track, slot or actuating mechanism. An apparent collision-free state does not demonstrate ballistic protection, thermal, pressure or hardware qualification.</p>
<p class="muted">Drag to rotate the ship. Mouse wheel zooms. Colours, scale and triangle positions are illustrative but the vertices use metres and computed 16-blade motion.</p>
</aside></main>
<script>
const D=__DATA__,elem=id=>document.getElementById(id),selector=elem('model'),bar=elem('stage'),canvas=elem('view'),ctx=canvas.getContext('2d');
D.options.forEach((o,i)=>{const q=document.createElement('option');q.value=i;q.textContent=o.name;selector.appendChild(q)});
selector.value=3;bar.value=62;
let yaw=-.73,pitch=.35,zoom=70,W=0,H=0,drag=false,last=null;
const deg=Math.PI/180;
function profile(r,o){if(!o.shape)return 2.35*(1-Math.sqrt(Math.max(0,1-r*r/(4.5*4.5))));let [e,f,a]=o.shape;return -e+Math.max(0,r-f)*Math.tan(a*deg)}
function pressure(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-r*r/(4.3*4.3)))}
function xyz(x,r,a){return [x,r*Math.cos(a),r*Math.sin(a)]}
function transform(p){const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);const a=p[0]*cy-p[1]*sy,depth=p[0]*sy+p[1]*cy;return [a,p[2]*cp-depth*sp,depth*cp+p[2]*sp]}
function project(p){let q=transform(p);return [W/2+q[0]*zoom,H/2-q[1]*zoom,q[2]]}
let triangles=[];
function tri(a,b,c,color,alpha){let pa=project(a),pb=project(b),pc=project(c);triangles.push({v:[pa,pb,pc],depth:(pa[2]+pb[2]+pc[2])/3,color,alpha})}
function surface(o,typ){
 const R=typ==='pressure'?4.3:4.5,nr=25,nt=64,firstR=typ==='pressure'?0:o.R;
 for(let i=0;i<nr;i++)for(let j=0;j<nt;j++){
  let r0=firstR+(R-firstR)*i/nr,r1=firstR+(R-firstR)*(i+1)/nr,a=j*2*Math.PI/nt,b=(j+1)*2*Math.PI/nt;
  let fn=typ==='pressure'?pressure:r=>profile(r,o);
  let A=xyz(fn(r0),r0,a),B=xyz(fn(r1),r1,a),C=xyz(fn(r0),r0,b),E=xyz(fn(r1),r1,b);
  let color=typ==='pressure'?'#62b7ee':(r0 < (o.stow?.r_outer_m||o.R)?'#657e97':'#51677c');
  let opacity=typ==='pressure'?.13:.38;
  tri(A,B,C,color,opacity);tri(B,E,C,color,opacity);
 }
}
function addBlades(o,a,s){
 const N=D.count,half=Math.PI/N+D.overlap_deg*deg,R=o.R;
 const pivotR=R+D.pivot_dr,pivotTheta=D.pivot_phi_deg*deg;
 let dr=Math.max(0,s.low_x_shift_m||0)+0.0001;
 for(let k=0;k<N;k++){
  let az=k*2*Math.PI/N,ca=Math.cos(az),sa=Math.sin(az);
  let pa=[pivotR*Math.cos(pivotTheta),pivotR*Math.sin(pivotTheta)],co=Math.cos(a*deg),si=Math.sin(a*deg);
  function mk(r,phi){
   let y=r*Math.cos(phi),z=r*Math.sin(phi);
   let yy=pa[0]+co*(y-pa[0])-si*(z-pa[1]);
   let zz=pa[1]+si*(y-pa[0])+co*(z-pa[1]);
   let x=profile(r,o)+dr+(k%2)*(D.thickness_m+.02);
   return [x,ca*yy-sa*zz,sa*yy+ca*zz];
  }
  const steps=24;
  const center=mk(0,0),edge=[];
  for(let j=0;j<=steps;j++)edge.push(mk(R,-half+(2*half*j/steps)));
  let color=(k%2===0)?'#e7b576':'#65c6b9';
  for(let j=0;j<steps;j++)tri(center,edge[j],edge[j+1],color,.92);
 }
}
function dots(){for(let p of D.nodes){const q=project(p);ctx.beginPath();ctx.fillStyle='#c6a6ff';ctx.arc(q[0],q[1],3,0,Math.PI*2);ctx.fill()}}
function draw(){
 let pr=devicePixelRatio||1;W=canvas.clientWidth;H=canvas.clientHeight;
 canvas.width=Math.round(W*pr);canvas.height=Math.round(H*pr);
 ctx.setTransform(pr,0,0,pr,0,0);ctx.clearRect(0,0,W,H);
 const o=D.options[+selector.value],s=o.frames[+bar.value];triangles=[];
 if(elem('shell').checked)surface(o,'outer');
 if(elem('pressure').checked)surface(o,'pressure');
 if(elem('blades').checked)addBlades(o,+bar.value,s);
 triangles.sort((a,b)=>a.depth-b.depth);
 for(let t of triangles){ctx.globalAlpha=t.alpha;ctx.fillStyle=t.color;ctx.beginPath();ctx.moveTo(t.v[0][0],t.v[0][1]);ctx.lineTo(t.v[1][0],t.v[1][1]);ctx.lineTo(t.v[2][0],t.v[2][1]);ctx.closePath();ctx.fill()}
 ctx.globalAlpha=1;
 if(elem('sensors').checked)dots();
 ctx.fillStyle='#d7e5f6';ctx.font='12px system-ui';ctx.fillText('Bow −x   /   x aft →   / metres',14,24);
 elem('angleLabel').textContent=bar.value+'°';
 const clear=(s.center_clear_radius_m>=o.R-.01);
 const good=clear && !s.same_tier_overlap && s.two_tier_press_clear_possible;
 const allPrior=o.frames.slice(0,+bar.value+1).every(q=>!q.same_tier_overlap&&q.two_tier_press_clear_possible);
 const v=o.visibility;
 elem('stats').innerHTML=
  '<div class="stat">Central aperture nominal radius <b>'+o.R.toFixed(2)+' m</b></div>'+
  '<div class="stat">Centre currently clear to <b>'+s.center_clear_radius_m.toFixed(3)+' m</b></div>'+
  '<div class="stat">Blade motion since closed: <b>'+bar.value+'°</b> / possible all-stage route: <b class="'+(allPrior?'yes':'no')+'">'+(allPrior?'CLEAR IN SCREEN':'BLOCKED')+'</b></div>'+
  '<div class="stat">Same-tier leaf collision <b class="'+(s.same_tier_overlap?'no':'yes')+'">'+(s.same_tier_overlap?'YES':'NO')+'</b></div>'+
  '<div class="stat">Outer reach <b>'+s.max_leaf_radial_m.toFixed(3)+' m</b></div>'+
  '<div class="stat">Two-tier axial depth <b>'+D.two_tier_depth_m.toFixed(3)+' m</b></div>'+
  '<div class="stat">Calculated available x-travel slot <b class="'+((s.axial_shift_slot_m||0)<0?'no':'yes')+'">'+(s.axial_shift_slot_m===null?'N/A':s.axial_shift_slot_m.toFixed(3)+' m')+'</b></div>'+
  '<div class="stat">Selected design first fully open &amp; collision-screen clear <b class="'+(o.best?'yes':'no')+'">'+(o.best?o.best.angle_deg+'°':'NOT FOUND')+'</b></div>'+
  (v.worst_pilot_cone60===undefined?'':'<div class="stat">Pilot/NAV forward 60° sampling with outer views <b>'+Math.round(v.worst_pilot_cone60*100)+'%</b></div>')+
  '<div class="stat muted">Geometry only. Full closed zero-radius seal <b class="no">NOT PROVEN</b>.</div>';
}
for(let id of ['model','stage','shell','pressure','blades','sensors'])elem(id).addEventListener('input',draw);
canvas.addEventListener('pointerdown',e=>{drag=true;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointerup',()=>drag=false);canvas.addEventListener('pointercancel',()=>drag=false);
canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-last[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];draw()});
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(20,Math.min(180,zoom*Math.exp(-e.deltaY*.001)));draw()},{passive:false});
elem('reset').onclick=()=>{yaw=-.73;pitch=.35;zoom=70;draw()};addEventListener('resize',draw);draw();
</script></body></html>'''
out=ROOT/'render/out/nose_armoured_iris_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('IRIS VIEWER',out, 'options',len(options),'bytes',out.stat().st_size)
