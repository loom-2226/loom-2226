"""Self-contained HTML of the *failed* compact lateral shutter sweep.
Uses actual source geometry, six moving panel surface meshes, and sampled
clearance data. The mechanism is deliberately NOT presented as qualified.
"""
import json
from pathlib import Path
import numpy as np
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'command'))
import l1_lateral_slide_sweep as W
ROOT=Path(__file__).resolve().parent.parent
RESULT=json.loads((ROOT/'command/l1_lateral_slide_sweep_results.json').read_text())
ns,na=14,14
nr,nw=12,7
base=[W.central(1),W.central(-1)]+[W.ring(i) for i in range(4)]
sizes=[(ns,na)]*2+[(nr,nw)]*4
frames={}
for sequence in RESULT['sequences']:
    steps=[]
    for line in sequence['frames']:
        tc,tr=line['central_t'],line['ring_t']
        verts=[W.cap_pose(base[0],1,tc),W.cap_pose(base[1],-1,tc)]
        verts += [W.ring_pose(q,tr) for q in base[2:]]
        steps.append({
            'panels':[v[::2].round(4).tolist() for v in verts],
            'stats':line,
            'sequence':sequence['sequence']
        })
    frames[sequence['sequence']]=steps
data={'frames':frames,'shape':W.SHAPE,'noses':{'pressure_xa':.2,'pressure_xb':2.35},
      'panel_dims':[list(k) for k in sizes],
      'nodes':W.NODES.tolist(),'source':'Rev7 PR432, angular +0.8m /35° / r=3.2m'}
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer: lateral shutters, swept-motion screen</title>
<style>
body{margin:0;background:#07121e;color:#e9f1f9;font:14px system-ui}
header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;padding:12px 14px;gap:12px;background:#15283b;border-bottom:1px solid #39536b}
h1{font-size:18px;margin:0}small,.muted{color:#b0c1d3}button,select{color:#e9f1f9;background:#203a54;border:1px solid #6e8a9e;border-radius:7px;padding:7px}
main{display:grid;grid-template-columns:minmax(0,1fr) 295px;height:calc(100dvh - 67px)}
canvas{background:radial-gradient(ellipse at center,#25384b,#07121e 70%);width:100%;height:100%;touch-action:none}
aside{padding:14px;overflow:auto;background:#111d2e;border-left:1px solid #375069}input[type=range]{width:100%;accent-color:#efb86f}
label{display:block;margin:10px 0}.stat{border-bottom:1px solid #35465c;padding:8px 0}.bad{color:#ffa09c}.good{color:#a9e1c1}
@media(max-width:750px){main{display:block;height:auto}canvas{height:61dvh}aside{border-left:0;border-top:1px solid #375069}}
</style></head><body>
<header><div><h1>WAYFARER · LATERAL SHUTTER EXPERIMENT</h1><small>Actual metre geometry · concept failed physical closure · research only</small></div>
<select id="seq"><option value="central_first">Central covers first</option><option value="ring_first">Side windows first</option><option value="simultaneous">All six together</option></select>
<button id="reset">Reset view</button></header>
<main><canvas id="c"></canvas><aside>
<label><b>Shutter motion</b> <span id="stepLabel"></span></label>
<input id="stage" type="range" min="0" max="10" step="1" value="10">
<label><input type="checkbox" id="outer" checked> Outer armoured nose</label>
<label><input type="checkbox" id="pressure" checked> Original pressure head</label>
<label><input type="checkbox" id="metrics" checked> Metric-node front ring</label>
<label><input type="checkbox" id="panels" checked> Six moving cover panels</label>
<div id="stats"></div>
<p class="muted"><b>Orange/yellow:</b> the two sliding central half-discs. <b>Teal:</b> four rotating side-window shutters. Every mesh is built from Rev 7's metric coordinates with the +0.8 m angular exterior.</p>
<p class="muted"><b>No false PASS:</b> These are sampled paths, not physical rails. The central panels are automatically shifted forward enough to avoid the hull during travel, which is an optimistic kinematic assumption. Stowed they can stand 0.56 m clear of the armour. Pairwise sampled distances under 0.1 m are possible interference warnings, not exact interpenetration proof.</p>
<p class="muted">Drag to orbit. Mouse wheel zoom. Sectors are thin rendered surfaces; collision checks include 0.196 m effective thickness and use more geometry than these visible faces. Mechanical mounts, seals, drives and ring geometry are unresolved.</p>
</aside></main>
<script>
const D=__DATA__,el=id=>document.getElementById(id);
const cvs=el('c'),cx=cvs.getContext('2d');
let yaw=-.65,pitch=.39,zoom=60,W=1,H=1,drag=false,last=null;
function profile(r){return -.8+Math.max(0,r-1.2)*Math.tan(35*Math.PI/180)}
function pX(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2))}
function projection(p){
let c=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
let u=p[0]*c-p[1]*s,v=p[0]*s+p[1]*c;
return [W/2+(u-.4)*zoom,H/2-(p[2]*cp-v*sp)*zoom,v*cp+p[2]*sp]
}
function V(x,r,a){return [x,r*Math.cos(a),r*Math.sin(a)]}
let triangles=[];
function tri(a,b,c,color,alpha){let A=projection(a),B=projection(b),C=projection(c);triangles.push({p:[A,B,C],depth:(A[2]+B[2]+C[2])/3,color,alpha})}
function shell(type){
if(type==='outer'){
 for(let i=0;i<23;i++)for(let j=0;j<40;j++){
 let r=i*4.5/23,rr=(i+1)*4.5/23,a=j*Math.PI/20,b=(j+1)*Math.PI/20;
 let A=V(profile(r),r,a),B=V(profile(rr),rr,a),C=V(profile(r),r,b),E=V(profile(rr),rr,b);
 tri(A,B,C,'#748a9e',.33);tri(B,E,C,'#748a9e',.33);
 }
} else {
 for(let i=0;i<21;i++)for(let j=0;j<40;j++){
 let r=i*4.3/21,rr=(i+1)*4.3/21,a=j*Math.PI/20,b=(j+1)*Math.PI/20;
 let A=V(pX(r),r,a),B=V(pX(rr),rr,a),C=V(pX(r),r,b),E=V(pX(rr),rr,b);
 tri(A,B,C,'#4aa4e1',.13);tri(B,E,C,'#4aa4e1',.13);
 }
}
}
function panel(mesh,dim,color){
 let [nr,na]=dim;
 for(let i=0;i<nr-1;i++)for(let j=0;j<na-1;j++){
  let a=mesh[i*na+j],b=mesh[(i+1)*na+j],c=mesh[i*na+j+1],d=mesh[(i+1)*na+j+1];
  tri(a,b,c,color,.94);tri(b,d,c,color,.94);
 }
}
function render(){
 let pr=devicePixelRatio||1;W=cvs.clientWidth;H=cvs.clientHeight;cvs.width=W*pr;cvs.height=H*pr;cx.setTransform(pr,0,0,pr,0,0);
 cx.clearRect(0,0,W,H);triangles=[];
 const q=D.frames[el('seq').value][+el('stage').value];
 if(el('outer').checked)shell('outer');
 if(el('pressure').checked)shell('pressure');
 if(el('panels').checked)q.panels.forEach((v,i)=>panel(v,D.panel_dims[i],i===0?'#f3c36e':i===1?'#dc9652':'#57d4c1'));
 triangles.sort((a,b)=>a.depth-b.depth);
 for(let t of triangles){cx.globalAlpha=t.alpha;cx.fillStyle=t.color;cx.beginPath();cx.moveTo(t.p[0][0],t.p[0][1]);cx.lineTo(t.p[1][0],t.p[1][1]);cx.lineTo(t.p[2][0],t.p[2][1]);cx.closePath();cx.fill()}
 cx.globalAlpha=1;
 if(el('metrics').checked)for(let p of D.nodes){const k=projection(p);cx.fillStyle='#c3aaff';cx.beginPath();cx.arc(k[0],k[1],4,0,Math.PI*2);cx.fill()}
 cx.fillStyle='#e9f1fa';cx.fillText('Bow −x   /   x aft →   /   metres',17,24);
 let s=q.stats;el('stepLabel').textContent=Math.round(s.t*100)+'%';
 el('stats').innerHTML=
 '<div class="stat">Central slide: <b>'+Math.round(s.central_t*100)+'%</b>; ring rotation: <b>'+Math.round(s.ring_t*100)+'%</b></div>'+
 '<div class="stat">Closest sampled central-to-ring points: <b class="'+(s.minimum_central_to_ring_sample_distance_m<.1?'bad':'good')+'">'+s.minimum_central_to_ring_sample_distance_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Maximum radial extent: <b>'+s.max_radius_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Largest outward central-panel gap from hull: <b>'+s.max_central_gap_outward_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Minimum node-face marker separation: <b>'+s.minimum_node_face_surface_clearance_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Minimum signed exterior gap (positive = completely outside): <b>'+s.minimum_external_skin_gap_m.toFixed(3)+' m</b></div>';
}
for(let id of ['seq','stage','outer','pressure','metrics','panels'])el(id).addEventListener('input',render);
cvs.addEventListener('pointerdown',e=>{drag=true;last=[e.clientX,e.clientY];cvs.setPointerCapture(e.pointerId)});
cvs.addEventListener('pointerup',()=>drag=false);cvs.addEventListener('pointercancel',()=>drag=false);
cvs.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-last[0])*.008;pitch=Math.max(-1.52,Math.min(1.52,pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];render()});
cvs.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.min(200,Math.max(15,zoom*Math.exp(-e.deltaY*.0009)));render()},{passive:false});
el('reset').onclick=()=>{yaw=-.65;pitch=.39;zoom=60;render()};addEventListener('resize',render);render();
</script></body></html>'''
out=ROOT/'render/out/nose_lateral_shutter_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('BUILT',out,'bytes',out.stat().st_size)
