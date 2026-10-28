"""Offline rotatable visualization of two-tier rigid iris cam geometry.

The viewer is a visualization of the sampled point-cloud study, not a
manufactured iris. Both tiers are drawn as full rigid panel skins.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_iris_two_tier_cam_results.json').read_text())
opts=[]
for o in J['results']:
    opts.append({'R':o['iris_radius_m'],'frames':o['frames'],
       'path_clear':o['necessary_sampled_path_clear'],
       'visibility':o.get('visibility',{}),
       'end_margin':o['end_available_x_interval_m']})
D={'options':opts,'T':J['results'][0]['thickness_each_m'],
   'gap':J['results'][0]['intertier_axial_gap_m'],
   'source':'PR432 head 3485830a56df; research 50deg nose'}
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer 16-leaf two-tier iris cam</title><style>
*{box-sizing:border-box}body{margin:0;background:#0a1421;color:#e5eff9;font:14px system-ui,Arial,sans-serif}
header{padding:11px 15px;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:#16273c;border-bottom:1px solid #39536e}
h1{font-size:17px;margin:0}small,.muted{color:#b2c5d7}
select,button{color:#eaf4fe;background:#27445c;border:1px solid #6e889d;border-radius:6px;padding:7px;max-width:100%}
main{display:grid;grid-template-columns:minmax(0,1fr) 315px;height:calc(100dvh - 68px)}
canvas{touch-action:none;width:100%;height:100%;background:radial-gradient(ellipse at center,#233d51,#07111f 70%)}
aside{padding:14px;background:#132033;border-left:1px solid #375066;overflow:auto}
label{display:block;margin:10px 0 5px}input[type=range]{width:100%;accent-color:#eabd7c}
.stat{padding:8px 0;border-bottom:1px solid #364a60}.no{color:#ff9992}.yes{color:#a5dfb9}
@media(max-width:760px){main{display:block;height:auto}canvas{height:61dvh}aside{border-left:0;border-top:1px solid #375066}}
</style></head><body><header><div><h1>WAYFARER · INTERLEAVED IRIS CAM</h1>
<small>16 thick leaves · two x-levels · PR432 pressure envelope · NON-GOVERNING</small></div>
<select id="model"></select><button id="reset">Reset view</button></header>
<main><canvas id="view"></canvas><aside>
<label><b>Combined withdrawal and rotation</b> <span id="pct"></span></label><input id="stage" type="range" min="0" max="92" step="1" value="92">
<label><input id="leaves" type="checkbox" checked> 16 protective leaves</label>
<label><input id="outer" type="checkbox" checked> Fixed exterior armour</label>
<label><input id="pressure" type="checkbox" checked> Unchanged pressure head</label>
<label><input id="hub" type="checkbox" checked> 12 cm central armour boss</label>
<div id="stats"></div>
<h3>Mechanism assumptions</h3>
<p class="muted">Upper eight leaves <b style="color:#edbd77">gold</b>; lower eight <b style="color:#5dccbc">teal</b>. Each leaf is 0.1963 m thick, with 20 mm between levels. The leaves move aft first while inside the central aperture, then rotate together while an axial cam guides them beneath the fixed 20 cm-normal hypothetical shoulder armour.</p>
<p class="muted"><b>Not a qualified mechanism:</b> no real rim throat, bearings, drives, finite lap seal, structural load path or ballistic closure. When shut, the two tiers still have a 216 mm surface step. The rendering shows thin face skins; collision study used through-thickness intervals.</p>
<p class="muted">Drag to orbit, scroll to zoom. The 1.80 m design fails the two-tier pressure/shell allowance; 1.76 m and 1.75 m pass the selected necessary geometry checks. These do not imply mechanical certification or recovered panoramic side views.</p>
</aside></main><script>
const D=__DATA__,el=id=>document.getElementById(id);
const C=el('view'),ctx=C.getContext('2d');
D.options.forEach((o,i)=>{let n=document.createElement('option');n.value=i;n.textContent=o.R.toFixed(2)+' m iris radius'+(o.path_clear?'  ·  sampled path clear':'  ·  blocked');el('model').appendChild(n)});
el('model').value='1';
let yaw=-.8,pitch=.35,zoom=72,drag=false,last=null,W=1,H=1;
function hull(r){return -1.2+Math.max(0,r-2.0)*Math.tan(50*Math.PI/180)}
function pressure(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2))}
function polar(x,r,ang){return [x,r*Math.cos(ang),r*Math.sin(ang)]}
function project(P){let c=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
 let q=P[0]*c-P[1]*s, dep=P[0]*s+P[1]*c;
 return [W/2+(q-.3)*zoom,H/2-(P[2]*cp-dep*sp)*zoom,dep*cp+P[2]*sp]}
let tris=[];
function tri(a,b,c,color,opacity){let A=project(a),B=project(b),C=project(c);
 tris.push({p:[A,B,C],z:(A[2]+B[2]+C[2])/3,color,opacity})}
function surface(fn,rmin,rmax,color,opacity){
 const nr=22,na=48;
 for(let i=0;i<nr;i++)for(let j=0;j<na;j++){
  let r=rmin+(rmax-rmin)*i/nr,R=rmin+(rmax-rmin)*(i+1)/nr,
      a=j*2*Math.PI/na,b=(j+1)*2*Math.PI/na;
  let A=polar(fn(r),r,a),B=polar(fn(R),R,a),C=polar(fn(r),r,b),E=polar(fn(R),R,b);
  tri(A,B,C,color,opacity);tri(B,E,C,color,opacity);
 }
}
function blade(o,frame,k){
 const N=16,rot=frame.angle_deg*Math.PI/180,az=k*Math.PI/8;
 let R=o.R,angOffset=22*Math.PI/180,pivot=[(R+.07)*Math.cos(angOffset),(R+.07)*Math.sin(angOffset)];
 let ca=Math.cos(rot),sa=Math.sin(rot),cz=Math.cos(az),sz=Math.sin(az);
 let front=k%2===0?frame.upper_front_x_m:frame.lower_front_x_m;
 function pt(r,a){
  let y=r*Math.cos(a),z=r*Math.sin(a);
  let ry=pivot[0]+ca*(y-pivot[0])-sa*(z-pivot[1]);
  let rz=pivot[1]+sa*(y-pivot[0])+ca*(z-pivot[1]);
  return [front,cz*ry-sz*rz,sz*ry+cz*rz];
 }
 const nr=15,na=5,half=(11.25+1)*Math.PI/180,col=k%2===0?'#ebbd76':'#5dccbc';
 for(let i=0;i<nr;i++)for(let j=0;j<na;j++){
  let r=.12+(R-.12)*i/nr,R1=.12+(R-.12)*(i+1)/nr,
      a=-half+2*half*j/na,b=-half+2*half*(j+1)/na;
  let A=pt(r,a),B=pt(R1,a),C=pt(r,b),E=pt(R1,b);
  tri(A,B,C,col,.87);tri(B,E,C,col,.87);
 }
}
function hub(){
 let n=48,R=.12;
 for(let j=0;j<n;j++)tri([-1.201,0,0],polar(-1.201,R,j*2*Math.PI/n),polar(-1.201,R,(j+1)*2*Math.PI/n),'#e3e8f2',.94);
}
function render(){
 let pr=devicePixelRatio||1;W=C.clientWidth;H=C.clientHeight;C.width=W*pr;C.height=H*pr;ctx.setTransform(pr,0,0,pr,0,0);ctx.clearRect(0,0,W,H);
 let o=D.options[+el('model').value],s=o.frames[+el('stage').value];tris=[];
 if(el('pressure').checked)surface(pressure,0,4.3,'#5fb4e4',.14);
 if(el('outer').checked)surface(hull,o.R,4.5,'#7893a9',.44);
 if(el('leaves').checked)for(let k=0;k<16;k++)blade(o,s,k);
 if(el('hub').checked)hub();
 tris.sort((a,b)=>a.z-b.z);
 for(let f of tris){ctx.globalAlpha=f.opacity;ctx.fillStyle=f.color;ctx.beginPath();
 ctx.moveTo(f.p[0][0],f.p[0][1]);ctx.lineTo(f.p[1][0],f.p[1][1]);ctx.lineTo(f.p[2][0],f.p[2][1]);ctx.closePath();ctx.fill()}
 ctx.globalAlpha=1;ctx.fillStyle='#d8e8f7';ctx.fillText('Bow −x  /  x aft →  /  metres',16,24);
 el('pct').textContent=Math.round(s.stage_fraction*100)+'%';
 const pass=!s.fixed_armour_contacts&&!s.same_tier_collision&&s.min_pressure_gap_m>=.025;
 el('stats').innerHTML=
 '<div class="stat">Rotation <b>'+s.angle_deg+'°</b>; mode <b>'+s.stage+'</b></div>'+
 '<div class="stat">Upper leaf x <b>'+s.upper_front_x_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Lower leaf x <b>'+s.lower_front_x_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Pressure-head gap <b>'+s.min_pressure_gap_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Shell gap <b>'+(s.min_fixed_armour_gap_m===null?'N/A':s.min_fixed_armour_gap_m.toFixed(3)+' m')+'</b></div>'+
 '<div class="stat">All-tier fixed armour contacts <b>'+s.fixed_armour_contacts+'</b></div>'+
 '<div class="stat">Any same-tier collision <b>'+s.same_tier_collision+'</b></div>'+
 '<div class="stat">Minimum distance between tier faces <b>'+s.min_intertier_gap_m.toFixed(3)+' m</b></div>'+
 '<div class="stat">Sampled frame status <b class="'+(pass?'yes':'no')+'">'+(pass?'clear in model':'blocked')+'</b></div>'+
 '<div class="stat">Full path under this profile <b class="'+(o.path_clear?'yes':'no')+'">'+(o.path_clear?'all sampled stages clear':'not clear')+'</b></div>'+
 '<div class="stat">Pilot/NAV sampled 60° cone with outer windows <b>'+Math.round((o.visibility.worst_pilot_cone60||0)*100)+'%</b></div>';
}
for(let id of ['model','stage','leaves','outer','pressure','hub'])el(id).addEventListener('input',render);
C.addEventListener('pointerdown',e=>{drag=true;last=[e.clientX,e.clientY];C.setPointerCapture(e.pointerId)});
C.addEventListener('pointerup',()=>drag=false);C.addEventListener('pointercancel',()=>drag=false);
C.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-last[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];render()});
C.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(15,Math.min(180,zoom*Math.exp(-e.deltaY*.001)));render()},{passive:false});
el('reset').onclick=()=>{yaw=-.8;pitch=.35;zoom=72;render()};addEventListener('resize',render);render();
</script></body></html>'''
out=ROOT/'render/out/nose_two_tier_cam_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(D,separators=(',',':'))))
print('VIEWER',out,'bytes',out.stat().st_size)
