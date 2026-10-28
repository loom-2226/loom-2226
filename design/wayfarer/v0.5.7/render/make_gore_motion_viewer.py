"""Build portable offline canvas visualisation of 16 hinged armour sectors.
Self-contained HTML: no CDNs or JS dependencies.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
G=json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())
SW=json.loads((ROOT/'command/l1_single_gore_sweep_results.json').read_text())
OC=json.loads((ROOT/'command/l1_gore_occlusion_results.json').read_text())
options=[]
for i,(name,shape,c) in enumerate([('Rev7 ellipsoid',None,2.8),('Compact angular +0.8m 35°',(.8,1.2,35),3.2),('Panoramic angular +1.2m 50°',(1.2,2.,50),3.5)]):
    tests=SW['mechanisms'][i]['tests']
    states={str(x['angle_deg']):x for test in tests for x in test['angles'] if abs(x['angle_deg'])<=90}
    options.append({'name':name,'shape':shape,'crown':c,'states':states,
                    'occlusion':OC['cases'][i]['results'],
                    'sample_count':tests[0]['sample_count_per_angle']})
data={'options':options,'nodes':[f['pos'] for f in G['features'] if f.get('kind')=='node_face' and f.get('ring')==0],
      'sensor':next(p['shape'] for p in G['parts'] if p['id']=='bow_sensors'),
      'armor_thickness_m':SW['assumptions']['normal_layer_equivalent_m'],
      'source':'PR #432 source head 3485830a56df; isolated research branch'}
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer: moving crown gore</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0a111e;color:#e7edf6;font:14px system-ui,Arial}
header{display:flex;align-items:center;gap:16px;flex-wrap:wrap;background:#101e30;padding:11px 14px;border-bottom:1px solid #2e4258}
h1{font-size:18px;margin:0}small,.muted{color:#afc0d4}select,button,input{accent-color:#e5b76a}
select,button{padding:7px;color:#edf4fc;background:#263c55;border:1px solid #617d99;border-radius:6px}
main{display:grid;grid-template-columns:minmax(300px,1fr) minmax(260px,320px);height:calc(100dvh - 65px)}
canvas{width:100%;height:100%;touch-action:none;background:radial-gradient(ellipse at center,#20364b,#08101e 70%)}
aside{border-left:1px solid #3a5065;background:#111c2b;overflow:auto;padding:15px}
input[type=range]{width:100%;margin:14px 0}
label{display:block;margin:10px 0}
.detail{padding:8px 0;border-bottom:1px solid #34485c}.error{color:#f49e9e}.ok{color:#8cdfbe}
.key{display:inline-block;width:12px;height:12px;margin-right:6px;vertical-align:middle}
strong{font-weight:700}h3{font-size:14px;margin:17px 0 7px}
@media(max-width:800px){main{grid-template-columns:1fr;grid-template-rows:61dvh auto;height:auto}aside{max-height:none;border-left:0;border-top:1px solid #3a5065}}
</style></head><body>
<header><div><h1>WAYFARER · A MOVING ARMOUR PETAL</h1><small>Actual Rev 7 source coordinates · conceptual hinged mechanism · NON-GOVERNING</small></div>
<select id="model"></select><button id="camera">Reset camera</button></header>
<main><canvas id="v"></canvas><aside>
<div><strong>Hinge rotation</strong><div id="angleLabel"></div><input id="angle" type="range" min="-90" max="90" step="5" value="-60"><small>Negative = opens forward. Positive = folds aft. At zero the crown is closed.</small></div>
<div id="status"></div>
<h3>Layers</h3>
<label><input type="checkbox" id="petals" checked> All 16 protective gores</label>
<label><input type="checkbox" id="shell" checked> Existing pressure head</label>
<label><input type="checkbox" id="fixed" checked> Fixed outer armour shoulder</label>
<label><input type="checkbox" id="sensors" checked> Bow sensor ring and Metric nodes</label>
<h3>Legend</h3>
<p><span class="key" style="background:#f0bb65"></span> Hinged protective gores <span class="key" style="background:#78bdec"></span> Pressure hull</p>
<p><span class="key" style="background:#7d91a4"></span> Fixed exterior <span class="key" style="background:#a991ed"></span> Sensor and Metric hardware</p>
<h3>Read this before deciding</h3>
<p class="muted">This is a real-coordinate, constant-thickness <b>rigid-panel swept-motion screen</b>, not an engineered hinge. A zero collision count means none of the sampled panel material points intersects the modelled pressure hull, bow sensor solid or node-face spheres; the sample is not a proof of clearance. Adjacent petal self-collision, hinge bracket, seals, stops and actuation are not yet qualified.</p>
<p class="muted">The petal surface is shown as a thin 3D sheet. Collision testing uses 0.196 m effective armour thickness at three depth samples. The original crown's zero-angle test registers a small nominal pressure overlap because the simplified normal-layer construction differs from the source shell thickness geometry. The angular designs do not register this at zero.</p>
<p class="muted">Rotate with one finger; mouse wheel zooms. Figures are metrically positioned, but transparent surfaces use painter's-order rendering, not engineering CAD.</p>
</aside></main><script>
const D=__DATA__;
const cvs=document.getElementById('v'),ctx=cvs.getContext('2d');
const model=document.getElementById('model'),angle=document.getElementById('angle');
for(let i=0;i<D.options.length;i++){const el=document.createElement('option');el.value=i;el.textContent=D.options[i].name;model.appendChild(el)}
model.value='1';
let yaw=-.9,pitch=.40,scale=57,drag=false,old=null,W=0,H=0,center=0;
const rad=Math.PI/180;
const pol=(x,r,a)=>[x,r*Math.cos(a),r*Math.sin(a)];
const outX=r=>2.35*(1-Math.sqrt(Math.max(0,1-(r/4.5)**2)));
const pressX=r=>2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2));
function xprof(r,o){if(o.shape===null)return outX(r);let [e,f,a]=o.shape;return -e+Math.max(0,r-f)*Math.tan(a*rad)}
function localRot(p,h,a){let c=Math.cos(a),s=Math.sin(a);let dx=p[0]-h[0],dy=p[1]-h[1];return [h[0]+c*dx-s*dy,h[1]+s*dx+c*dy,p[2]]}
function spinX(p,a){let c=Math.cos(a),s=Math.sin(a);return [p[0],c*p[1]-s*p[2],s*p[1]+c*p[2]]}
function project3(p){let c=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);let xx=p[0]*c-p[1]*s,dep=p[0]*s+p[1]*c;return [xx, p[2]*cp-dep*sp,dep*cp+p[2]*sp]}
function point(p){let q=project3(p);return [W/2+(q[0]-center)*scale,H/2-q[1]*scale,q[2]]}
function tri(A,B,C,color,alpha,list){let a=point(A),b=point(B),c=point(C);list.push({p:[a,b,c],z:(a[2]+b[2]+c[2])/3,color,alpha})}
function nose(o,items){
  if(document.getElementById('shell').checked){
    for(let i=0;i<19;i++)for(let j=0;j<48;j++){
      let ra=4.3*i/19,rb=4.3*(i+1)/19;let a=j*Math.PI/24,b=(j+1)*Math.PI/24;
      let A=pol(pressX(ra),ra,a),B=pol(pressX(rb),rb,a),C=pol(pressX(ra),ra,b),E=pol(pressX(rb),rb,b);
      tri(A,B,C,'#60a5d6',.14,items);tri(B,E,C,'#60a5d6',.14,items);
    }
  }
  if(document.getElementById('fixed').checked){
    for(let i=0;i<9;i++)for(let j=0;j<64;j++){
      let ra=o.crown+(4.5-o.crown)*i/9,rb=o.crown+(4.5-o.crown)*(i+1)/9;
      let a=j*Math.PI/32,b=(j+1)*Math.PI/32;
      let A=pol(xprof(ra,o),ra,a),B=pol(xprof(rb,o),rb,a),C=pol(xprof(ra,o),ra,b),E=pol(xprof(rb,o),rb,b);
      tri(A,B,C,'#7d91a4',.44,items);tri(B,E,C,'#7d91a4',.44,items);
    }
  }
}
function addPetals(o,items){
  let a=+angle.value*rad, c=o.crown,h=[xprof(c,o),c,0];
  let count=document.getElementById('petals').checked?16:1;
  for(let k=0;k<count;k++){
    let az=k*2*Math.PI/16;
    function v(r,t){let p=pol(xprof(r,o),r,t);return spinX(localRot(p,h,a),az)}
    for(let i=0;i<13;i++)for(let j=0;j<6;j++){
      let r1=Math.max(.01,c*i/13),r2=c*(i+1)/13;
      let p1=-Math.PI/16+j*Math.PI/48,p2=-Math.PI/16+(j+1)*Math.PI/48;
      let A=v(r1,p1),B=v(r2,p1),C=v(r1,p2),E=v(r2,p2);
      let col=(k%2===0)?'#f0bb65':'#dc954e';
      tri(A,B,C,col,.87,items);tri(B,E,C,col,.87,items);
    }
  }
}
function drawLines(lines){
  ctx.lineWidth=1.4;
  for(let l of lines){let a=point(l[0]),b=point(l[1]);ctx.strokeStyle=l[2];ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke()}
}
function render(){
  let o=D.options[+model.value],v=cvs,pr=window.devicePixelRatio||1;
  W=v.clientWidth;H=v.clientHeight;v.width=W*pr;v.height=H*pr;ctx.setTransform(pr,0,0,pr,0,0);ctx.clearRect(0,0,W,H);
  center=0.5;
  let parts=[];nose(o,parts);addPetals(o,parts);
  parts.sort((a,b)=>a.z-b.z);
  for(let f of parts){ctx.globalAlpha=f.alpha;ctx.fillStyle=f.color;ctx.beginPath();ctx.moveTo(f.p[0][0],f.p[0][1]);ctx.lineTo(f.p[1][0],f.p[1][1]);ctx.lineTo(f.p[2][0],f.p[2][1]);ctx.closePath();ctx.fill()}
  ctx.globalAlpha=1;
  if(document.getElementById('sensors').checked){
    // Sensor ring actual x span .2..2, annular radial occupancy 2.9..4.15; gaps at 45,135,225,315.
    let lines=[];
    for(let k=0;k<48;k++){
      let a=2*Math.PI*k/48,b=2*Math.PI*(k+1)/48,mid=(a+b)/2/rad;
      if([45,135,225,315].some(t=>Math.abs(((mid-t+540)%360)-180)<14))continue;
      let x=1.8,inner=2.9,outer=4.0;
      lines.push([pol(x,inner,a),pol(x,outer,a),'#a991ed']);
      lines.push([pol(x,outer,a),pol(x,outer,b),'#a991ed']);
    }
    drawLines(lines);
    for(let p of D.nodes){let q=point(p);ctx.fillStyle='#e8a5ff';ctx.beginPath();ctx.arc(q[0],q[1],3.7,0,2*Math.PI);ctx.fill()}
  }
  let l=[[[o.shape===null?0:-o.shape[0],0,0],[2.35,0,0],'#e8f4ff'],[[0,0,0],[0,1,0],'#fff']];
  drawLines(l);
  const st=o.states[angle.value], vals=st.counts;
  const hasCol=Object.values(vals).some(n=>n>0);
  const oc=o.occlusion.find(q=>q.angle_deg===+angle.value);
  const shellOuter=o.shape===null?0:-o.shape[0];
  document.getElementById('angleLabel').textContent=(angle.value>0?'+':'')+angle.value+'°  '+(angle.value<0?'forward-opening':angle.value>0?'aft-folding':'closed');
  document.getElementById('status').innerHTML=
    '<div class="detail"><strong>Sampled collision: <span class="'+(hasCol?'error':'ok')+'">'+(hasCol?'DETECTED':'NONE DETECTED')+'</span></strong></div>'+
    Object.entries(vals).map(([k,v])=>'<div class="detail">'+k.replaceAll('_',' ')+': <strong>'+v+'</strong> / '+o.sample_count+'</div>').join('')+
    '<div class="detail">Maximum deployed radius: <strong>'+st.max_radial_m.toFixed(2)+' m</strong> '+(st.max_radial_m>4.5?'<span class="error">(over 4.5 m shell radius)</span>':'<span class="ok">(within 4.5 m)</span>')+'</div>'+
    '<div class="detail">Forward tip: <strong>x = '+st.min_x_m.toFixed(2)+' m</strong>; additional over closed bow '+Math.max(0,shellOuter-st.min_x_m).toFixed(2)+' m</div>'+
    (oc?'<div class="detail">Pilot / NAV cone directly blocked by petals: <strong>'+(oc.pilot_cone_occluded_fraction*100).toFixed(1)+'% / '+(oc.nav_cone_occluded_fraction*100).toFixed(1)+'%</strong></div>':'')+
    '<div class="detail muted">'+o.sample_count+' collision material samples (48×9×3 per sector). Only one sector tested for obstructions; visual repeats it 16×.</div>';
}
for(let id of ['model','angle','petals','shell','fixed','sensors'])document.getElementById(id).addEventListener('input',render);
cvs.addEventListener('pointerdown',e=>{drag=true;old=[e.clientX,e.clientY];cvs.setPointerCapture(e.pointerId)});
cvs.addEventListener('pointerup',()=>drag=false);cvs.addEventListener('pointercancel',()=>drag=false);
cvs.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-old[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-old[1])*.008));old=[e.clientX,e.clientY];render()});
cvs.addEventListener('wheel',e=>{e.preventDefault();scale=Math.max(20,Math.min(140,scale*Math.exp(-e.deltaY*.001)));render()},{passive:false});
document.getElementById('camera').addEventListener('click',()=>{yaw=-.9;pitch=.40;scale=57;render()});
window.addEventListener('resize',render);
render();
</script></body></html>'''
(ROOT/'render/out/nose_gore_motion_viewer.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('WROTE',ROOT/'render/out/nose_gore_motion_viewer.html', 'bytes', (ROOT/'render/out/nose_gore_motion_viewer.html').stat().st_size)
