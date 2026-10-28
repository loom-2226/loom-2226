"""Build standalone, local, no-CDN interactive 3D Wayfarer nose viewer.
Actual PR #432 coordinates and candidate parameter mesh; NOT CAD/qualified.
"""
import json,math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(ROOT/'command')]
import l1_study as L
R=json.loads((ROOT/'command/l1_design_refined.json').read_text())
scene=L.scene_export()
import hashlib
R['geometry_sha256']=hashlib.sha256((ROOT/'out/wayfarer_v05_geometry.json').read_bytes()).hexdigest()
allrows=R['candidates']
# Diverse examples, only documented original sensor ring and proven baseline access.
good=[a for a in allrows if a['sensors']=='ring' and a['shift']==[0,0,0]]
# Prefer actual measured through both glazing sheets + room obstructions.
good.sort(key=lambda r:(-min(r['stations'][k]['forward_integrated'] for k in ('S1','S2','S3','S4')),-min(r['stations'][k]['forward_integrated'] for k in ('PILOT','NAV'))))
examples=[]; used=set()
for q in good:
    key=(q['windows'],q['crown'])
    if key not in used:
        examples.append(q);used.add(key)
    if len(examples)==7:break
if len(examples)<4:
    for q in allrows:
        key=(tuple(q['shape']),q['windows'],q['crown'],tuple(q['shift']))
        if key not in used:
            examples.append(q);used.add(key)
        if len(examples)==7:break
options=[{'name':'Rev 7 reference | 53.3 m', 'baseline':True,'extension':0,
          'shape':None,'crown':2.8,'windows':'current','sensors':'ring','metrics':{
             k:{'integrated':v['forward_integrated']}
             for k,v in R['consistent_baseline'].items()}}]
for n,q in enumerate(examples,1):
    sh=q['shape']
    options.append({'name':('%s | crown %.1f m | +%.1f m | %.0f°'%(q['windows'],q['crown'],sh[0],sh[2])),
                    'shape':sh,'extension':sh[0],'crown':q['crown'],'windows':q['windows'],
                    'sensors':q['sensors'],'metrics':q['stations'],
                    'area':q['area_m2'],'outer_area':q['exterior_shutter_area_m2'],'shutter':q['shutter_equiv_t'],'paths':True,
                    'qual':q['shutter_swept_volume']})
DATA={'options':options,'scene':scene,'source':R['source_sha'],'geometry_sha':R['geometry_sha256']}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer Rev 7 | L1 nose experimental 3D viewer</title>
<style>body{margin:0;font:14px system-ui,Segoe UI,sans-serif;background:#0b1320;color:#e8edf6}
header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;padding:12px 18px;border-bottom:1px solid #334155;background:#121f32;gap:10px}
main{display:grid;grid-template-columns:minmax(0,1fr) 285px;height:calc(100dvh - 76px)}
canvas{width:100%;height:100%;touch-action:none;cursor:grab;background:radial-gradient(circle at center,#1b2f46,#0b1320 65%)}
aside{padding:16px;background:#121d2c;overflow:auto;border-left:1px solid #334155}
select,button{background:#24374d;color:#eef5ff;border:1px solid #718096;border-radius:6px;padding:6px;font:inherit}
label{display:block;margin:12px 0 6px}.muted{color:#98aabe}h3{font-size:14px;margin:20px 0 8px}
.key{display:flex;align-items:center;gap:9px;margin:9px 0}.sw{display:inline-block;width:16px;height:12px;border:1px solid #7689a5}
.stat{padding:9px;border-bottom:1px solid #2c3a4d}
footer{color:#93a4b9;font-size:12px} @media(max-width:750px){main{grid-template-columns:1fr;grid-template-rows:minmax(340px,68dvh) 1fr;height:auto}aside{border-left:none;border-top:1px solid #334155;max-height:42dvh}}
</style></head><body>
<header><div><b>WAYFARER / L1 + NOSE</b><div class="muted">Scaled 3D geometry experiment · 28 Oct 2026 · NON-GOVERNING</div></div><div><label for="model">Candidate <select id="model"></select></label></div></header>
<main><canvas id="c"></canvas><aside><div id="meta"></div>
<h3>Display</h3>
<label><input id="outer" type="checkbox" checked> Exterior faceted armour / windows</label>
<label><input id="pressure" type="checkbox" checked> Existing pressure-head location</label>
<label><input id="crew" type="checkbox" checked> Six real Rev 7 crew stations</label>
<label><input id="sensor" type="checkbox" checked> Existing sensor ring extent</label>
<label><input id="axes" type="checkbox" checked> Coordinate axes / scale</label>
<button id="reset">Reset camera</button>
<h3>Geometry legend</h3>
<div class="key"><span class="sw" style="background:#67c0f5"></span>Glazed patch, pressure head</div>
<div class="key"><span class="sw" style="background:#2d718d"></span>Glazed exterior panel</div>
<div class="key"><span class="sw" style="background:#5e788c"></span>Armoured exterior</div>
<div class="key"><span class="sw" style="background:#a88dd7"></span>Sensor-ring placeholder</div>
<div class="key"><span class="sw" style="background:#f5b963"></span>Couch / station eye</div>
<h3>Important limitations</h3>
<p class="muted">Vertices use metric metres and Rev 7 source positions. The faceted exterior is a triangulated concept mesh, not CAD manufacturing geometry; tessellation is visual only. Transparent patches are proposed pressure-bearing openings, not a qualified pane design. Shutter storage, interlayer support and sensor relocation remain unverified.</p>
<footer id="prov"></footer>
</aside></main>
<script>const DATA=__DATA__;
const canvas=document.getElementById('c'),cx=canvas.getContext('2d'),selector=document.getElementById('model');
DATA.options.forEach((o,i)=>{const opt=document.createElement('option');opt.value=i;opt.textContent=o.name;selector.appendChild(opt)});
let yaw=-.62,pitch=.34,zoom=50,panX=0,panY=0,drag=false,last=null;
function reset(){yaw=-.62;pitch=.34;zoom=50;panX=0;panY=0;draw()}
document.getElementById('reset').onclick=reset;
for(const id of ['model','outer','pressure','crew','sensor','axes'])document.getElementById(id).onchange=()=>draw();
canvas.addEventListener('pointerdown',e=>{drag=true;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointerup',()=>drag=false);canvas.addEventListener('pointercancel',()=>drag=false);
canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-last[0])*.008;pitch=Math.max(-1.52,Math.min(1.52,pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];draw()});
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom*=Math.exp(-e.deltaY*.0008);zoom=Math.max(10,Math.min(180,zoom));draw()},{passive:false});
function vec(x,r,a){return [x,r*Math.cos(a),r*Math.sin(a)]}
function oldX(r){return 2.35*(1-Math.sqrt(Math.max(0,1-(r/4.5)**2)))}
function pressureX(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2))}
function facetX(r,o){let [ext,face,ang]=o.shape;return -ext+Math.max(0,r-face)*Math.tan(ang*Math.PI/180)}
function isGlass(r,a,o){if(r>o.crown&&o.windows!=='current')return false;
if(o.windows==='current')return r<=2.8;
if(o.windows==='radial')return r<=o.crown;
const ph=(a*180/Math.PI+360)%360;
const nearest=(centers)=>Math.min(...centers.map(v=>Math.abs(((ph-v+540)%360)-180)));
if(o.windows==='segmented')return r<=1.15||r<=o.crown&&nearest([0,45,90,135,180,225,270,315])<=14;
return r<=2||r<=o.crown&&nearest([45,135,225,315])<=24}
function faces(o){
const out=[];
function tri(a,b,c,col,alpha){out.push({v:[a,b,c],col,alpha})}
const N=48;function surf(radial,fn,type){
for(let i=0;i<radial.length-1;i++)for(let j=0;j<N;j++){
const a=j*2*Math.PI/N,b=(j+1)*2*Math.PI/N;
const r0=radial[i],r1=radial[i+1],rc=(r0+r1)/2,ac=(a+b)/2;
const glass=isGlass(rc,ac,o);
const col=type==='pressure'?(glass?'#67c0f5':'#3b5066'):(glass?'#2d718d':'#5e788c');
const al=type==='pressure'?(glass?.55:.12):(glass?.40:.66);
const A=vec(fn(r0),r0,a),B=vec(fn(r0),r0,b),C=vec(fn(r1),r1,a),D=vec(fn(r1),r1,b);
tri(A,B,C,col,al);tri(B,C,D,col,al);
}}
if(document.getElementById('outer').checked){
const grid=o.baseline?Array.from({length:27},(_,i)=>4.5*i/26):
 Array.from(new Set([0,.4,.8,1.2,o.shape[1],2,2.8,o.crown,3.5,4,4.5].filter(r=>r>=0&&r<=4.5))).sort((a,b)=>a-b);
surf(grid,r=>o.baseline?oldX(r):facetX(r,o),'outer');
if(!o.baseline){
for(let i=0;i<N;i++){const a=i*2*Math.PI/N,b=(i+1)*2*Math.PI/N;let x=facetX(4.5,o);
tri(vec(x,4.5,a),vec(x,4.5,b),vec(2.35,4.5,a),'#667484',.78);
tri(vec(x,4.5,b),vec(2.35,4.5,a),vec(2.35,4.5,b),'#667484',.78);
}}
}
if(document.getElementById('pressure').checked){const rr=Array.from({length:33},(_,i)=>4.3*i/32);surf(rr,pressureX,'pressure')}
if(document.getElementById('sensor').checked){
for(let j=0;j<48;j++){let a=j*2*Math.PI/48,b=(j+1)*2*Math.PI/48;
let mid=(a+b)/2*180/Math.PI,ok=[45,135,225,315].every(t=>Math.abs(((mid-t+540)%360)-180)>14);
if(!ok)continue;
tri(vec(1.8,2.9,a),vec(1.8,4.15,a),vec(1.8,2.9,b),'#9c83d8',.4);
tri(vec(1.8,4.15,a),vec(1.8,4.15,b),vec(1.8,2.9,b),'#9c83d8',.4);
}}
return out
}
function transform(p){let [x,y,z]=p;const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);let u=x*cy-y*sy,depth=x*sy+y*cy;return [u, z*cp-depth*sp,depth*cp+z*sp]}
function canvasDims(){let w=canvas.clientWidth,h=canvas.clientHeight;if(canvas.width!==Math.round(w*devicePixelRatio)||canvas.height!==Math.round(h*devicePixelRatio)){canvas.width=w*devicePixelRatio;canvas.height=h*devicePixelRatio}cx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);return [w,h]}
function drawLine(P,Q,col,width=1){const a=project(P),b=project(Q);cx.strokeStyle=col;cx.lineWidth=width;cx.beginPath();cx.moveTo(...a);cx.lineTo(...b);cx.stroke()}
let W,H,CENTRE=2;
function project(p){const [x,y]=transform(p);return [W/2+(x-CENTRE)*zoom+panX,H/2-y*zoom+panY]}
function dot(p,color,size=4){const q=project(p);cx.fillStyle=color;cx.beginPath();cx.arc(...q,size,0,2*Math.PI);cx.fill()}
function draw(){
[W,H]=canvasDims();cx.clearRect(0,0,W,H);const o=DATA.options[+selector.value||0];CENTRE=1.5-o.extension*.30;
const sorted=faces(o).map(f=>({...f,depth:f.v.map(v=>transform(v)[2]).reduce((a,b)=>a+b,0)/3})).sort((a,b)=>a.depth-b.depth);
for(const f of sorted){const v=f.v.map(project);cx.globalAlpha=f.alpha;cx.fillStyle=f.col;cx.beginPath();cx.moveTo(...v[0]);cx.lineTo(...v[1]);cx.lineTo(...v[2]);cx.closePath();cx.fill()}
cx.globalAlpha=1;
if(document.getElementById('crew').checked){
const sc=DATA.scene;
for(const st of sc.couches){let head=st.head,feet=st.feet,x=st.base_x-.25;
drawLine([x,...head],[x,...feet],'#f1b86a',4);dot(st.eye,'#ffe7a5',4);
const q=project(st.eye);cx.font='11px system-ui';cx.fillStyle='#f6daab';cx.fillText(st.id,q[0]+5,q[1]-7)}
const fd=sc.flight_deck;
for(const y of fd.y)for(const z of fd.z)drawLine([fd.x[0],y,z],[fd.x[1],y,z],'#8d9ca9',1);
for(const y of fd.y)drawLine([fd.x[0],y,fd.z[0]],[fd.x[0],y,fd.z[1]],'#8d9ca9',2);
}
if(document.getElementById('axes').checked){
drawLine([-o.extension,0,0],[2.35,0,0],'#fff',1);
for(let i=0;i<=5;i++){drawLine([i,0,0],[i,0,.10],'#b2c3d7',1)}
drawLine([3.2,0,0],[4.2,0,0],'#fff',3);
const [sx,sy]=project([3.2,0,0]);cx.fillStyle='#fff';cx.font='12px system-ui';cx.fillText('1 m',sx,sy+19);
}
cx.fillStyle='#d5e3f4';cx.font='13px system-ui';cx.fillText('Bow (−x)    |    +x aft   |   all coordinates metres',16,25);
const pilot=(Math.min(...['PILOT','NAV'].map(k=>o.metrics[k].forward_integrated))||0).toFixed(3);
const sup=(Math.min(...['S1','S2','S3','S4'].map(k=>o.metrics[k].forward_integrated))||0).toFixed(3);
document.getElementById('meta').innerHTML='<div class="stat"><b>Length envelope:</b> '+(53.3+o.extension).toFixed(1)+' m</div>'+
'<div class="stat"><b>Pressure shell:</b> Rev 7 original, r 4.30 m</div>'+
'<div class="stat"><b>Crown:</b> '+o.crown.toFixed(1)+' m · '+o.windows+'</div>'+
'<div class="stat"><b>Pilot score:</b> '+pilot+'</div>'+
'<div class="stat"><b>Worst support score:</b> '+sup+'</div>'+
'<div class="stat"><b>Pane area (estimate):</b> '+(o.area===undefined?'Rev 7 declared 25 m²':o.area+' m²')+'</div>'+
'<div class="stat"><b>Outer shutter area:</b> '+(o.outer_area===undefined?'Unresolved':o.outer_area+' m²')+'</div>'+
'<div class="stat"><b>Shutter material (27 g/cm²):</b> '+(o.shutter===undefined?'Unresolved':o.shutter+' t · storage UNVERIFIED')+'</div>';
}
document.getElementById('prov').textContent='PR #432: '+DATA.source.slice(0,12)+' · source geometry SHA-256: '+DATA.geometry_sha.slice(0,16);
addEventListener('resize',draw);draw();
</script></body></html>'''
(ROOT/'render/out/nose_search_viewer.html').write_text(html.replace('__DATA__',json.dumps(DATA,separators=(',',':'))))
print('VIEWER',ROOT/'render/out/nose_search_viewer.html','examples',len(options))
