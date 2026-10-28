"""Offline interactive 37-held outer, pressure-glazing-only viewshed comparisons."""
from pathlib import Path
import json,sys,math
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'command'))
import l1_inner_pressure_panorama_options as M
J=json.loads((ROOT/'command/l1_inner_pressure_panorama_results.json').read_text())
# Visual field samples only; display numeric stats from higher-res runs
M.N_MAIN=768
M.N_SUPPORT=768
vis={}
for i,station in enumerate(M.D.IDS):
    c=M.from_seat(i)
    ds=M.D.directions(c['n'])
    sky=[]
    for k,v in enumerate(ds):
        rho=math.acos(max(-1.,min(1.,-float(v[0]))))/(math.pi/2)
        theta=math.atan2(float(v[2]),float(v[1]))
        sky.append([round(rho*math.cos(theta),5),
            round(rho*math.sin(theta),5),
            round(float(c['r_inner'][k]),4),
            round(float(c['ang_inner'][k]),3),
            bool(c['base_clear'][k]),
            bool(c['outer_usable'][k]),
            bool(c['outer_37_seam'][k]),
            bool(c['sensor'][k]),
            bool(c['interior'][k]),
            bool(c['geometric'][k])])
    vis[station]=sky
data={'cases':{k:v for k,v in J['results'].items() if v['inner_radius_m']==3.5},
    'held_outer':J['held_37_layout'],'visuals':vis}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer L1 · Inner pressure-glazing viewsheds</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#091726;color:#e9f2fa;font:14px system-ui,Arial}
header{background:#15293c;border-bottom:1px solid #3f5b71;padding:14px 16px}h1{font-size:18px;margin:0 0 4px}
small,.note{color:#b3c6d7;line-height:1.45}main{display:grid;grid-template-columns:minmax(0,1fr) 330px}
article{padding:12px 16px}aside{padding:16px;background:#132437;border-left:1px solid #3c536c}
canvas{width:100%;display:block;background:#11283e;border:1px solid #3a5872;border-radius:9px;max-width:650px}
#sky{height:380px}#front{height:290px}
label{display:block;margin:12px 0 5px;color:#bcd0de}select{width:100%;padding:10px;border:1px solid #7390a8;background:#29435a;border-radius:7px;color:white}
.stat{display:flex;justify-content:space-between;border-bottom:1px solid #36526b;padding:9px 0;gap:8px}
.stat b{text-align:right;font-variant-numeric:tabular-nums}
.key{font-size:12px;display:inline-block;margin:6px 10px 6px 0}
.key:before{content:"";display:inline-block;background:var(--c);width:9px;height:9px;border-radius:50%;margin-right:4px}
h2{font-size:15px}
@media(max-width:760px){main{display:block}aside{border:0;border-top:1px solid #3c536c}#sky{height:330px}}
</style></head><body>
<header><h1>WAYFARER · INNER PRESSURE GLAZING</h1><small>Outer 37-panel design HELD and unchanged · source L1 eye/furniture/sensors retained · research only</small></header>
<main><article>
<h2>Actual seat viewshed</h2><canvas id="sky"></canvas>
<div>
<span class="key" style="--c:#66dbca">Visible through both</span>
<span class="key" style="--c:#e4788b">Inner frame</span>
<span class="key" style="--c:#e0b774">Opaque outer nose</span>
<span class="key" style="--c:#885fbc">Outer tile seams</span>
<span class="key" style="--c:#6d8dab">Cabin / sensors / geometry</span></div>
<p class="note">Each dot is one of 768 equal-solid-angle forward sightlines. The outer circle represents directions 90° off the bow axis. The statistic panel uses a denser 4096/1536-ray sample. No real glass refraction is modeled.</p>
<h2>Pressure glazing and held 37-piece outer panel pattern</h2>
<canvas id="front"></canvas>
<p class="note">Blue/teal outer rings represent the 37 independently replaceable protective panels. Red lines show the inner pressure-frame layout. These are projections, not a coincident physical support grid: the layers sit at different axial depths, and parallax matters.</p>
</article>
<aside>
<label for="seat">Station</label><select id="seat"><option>PILOT</option><option>NAV</option><option>S1</option><option>S2</option><option>S3</option><option>S4</option></select>
<label for="design">Inner pressure frame</label><select id="design">
<option value="current_8x80__innerR3.5">Held initial: 8 × 80 mm, r1.15 m ring</option>
<option value="slim_8x40__innerR3.5" selected>Simple improvement: 8 × 40 mm, r1.15 m</option>
<option value="slim_8x40_ring150__innerR3.5">8 × 40 mm, ring r1.5 m</option>
<option value="slim_8x40_ring200__innerR3.5">8 × 40 mm, ring r2.0 m</option>
<option value="current_width_8x80_ring200__innerR3.5">8 × 80 mm, ring r2.0 m</option>
<option value="slim_8x40_hub075__innerR3.5">8 × 40 mm, ring r0.75 m</option>
<option value="slim_12x40_hub075__innerR3.5">12 × 40 mm, ring r0.75 m</option>
<option value="slim_8x40_ring300_bound__innerR3.5">UNQUALIFIED upper-bound: 8 × 40 mm, ring r3 m</option>
<option value="rim_only_upper_bound__innerR3.5">UNREALISTIC upper-bound: rim only</option></select>
<div id="stats"></div>
<h2>What this does not certify</h2>
<p class="note">The <strong>inner pressure layer must remain load bearing</strong>. Narrowing or relocating its mullions changes pane spans, pressure loads, crack paths and redundancy. Here it is a geometric visibility test only. The outer 37 panels carry no cabin pressure.</p>
<p class="note">The view is a real geometric sampled sightline map, not a rendered photograph. Optical reflection, structural mounts, thickness and refraction are still missing.</p>
</aside></main>
<script>
const D=__DATA__,el=id=>document.getElementById(id);
const colors={visible:'#66dbca',inner:'#e4788b',outer:'#e0b774',seam:'#885fbc',other:'#6d8dab'};
function frame(r,phi,c){
 const v=c.configuration,w=v.width,step=360/v.spokes;
 if(Math.abs(r-3.5)<w/2)return true;
 if(v.ring!==null&&Math.abs(r-v.ring)<w/2)return true;
 if(v.spokes){
  let a=((phi-v.rotation_deg)%step+step)%step;
  if(r>(v.ring===null?0:v.ring)&&Math.min(a,step-a)*Math.PI/180*r<w/2)return true;
 }
 return false;
}
function drawSky(){
 const C=el('sky'),ratio=window.devicePixelRatio||1,W=C.clientWidth,H=C.clientHeight;
 C.width=W*ratio;C.height=H*ratio;let ctx=C.getContext('2d');ctx.setTransform(ratio,0,0,ratio,0,0);
 let cx=W/2,cy=H/2,R=Math.min(W-24,H-24)/2;ctx.clearRect(0,0,W,H);
 ctx.fillStyle='#182b40';ctx.beginPath();ctx.arc(cx,cy,R,0,2*Math.PI);ctx.fill();
 ctx.strokeStyle='#7493ad';ctx.lineWidth=1;
 for(let r of [1/3,2/3,1]){ctx.beginPath();ctx.arc(cx,cy,R*r,0,2*Math.PI);ctx.stroke()}
 let station=el('seat').value,design=D.cases[el('design').value];
 for(let q of D.visuals[station]){
  let [x,y,ri,phi,base,outer,seam,sensor,interior,geom]=q;
  let col=base?(ri>3.5?colors.other:frame(ri,phi,design)?colors.inner:colors.visible):
    (!geom||!outer?colors.outer:seam?colors.seam:colors.other);
  ctx.fillStyle=col;ctx.beginPath();ctx.arc(cx+x*R,cy-y*R,Math.max(2.3,R/75),0,Math.PI*2);ctx.fill();
 }
 ctx.fillStyle='#e8f0fc';ctx.font='12px system-ui';ctx.fillText('−X / FORWARD',12,18);
}
function front(){
 const C=el('front'),ratio=window.devicePixelRatio||1,W=C.clientWidth,H=C.clientHeight;
 C.width=W*ratio;C.height=H*ratio;let ctx=C.getContext('2d');ctx.setTransform(ratio,0,0,ratio,0,0);
 let cx=W/2,cy=H/2,R=Math.min(W-25,H-20)/2;
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#246c78';ctx.beginPath();ctx.arc(cx,cy,R,0,2*Math.PI);ctx.fill();
 function ring(r,color,th=1){ctx.strokeStyle=color;ctx.lineWidth=th;ctx.beginPath();ctx.arc(cx,cy,R*r/3.5,0,2*Math.PI);ctx.stroke()}
 for(let r of [.75,2,2.75,3.5])ring(r,'#122a3b',r===3.5?5:2);
 // outer 37 projected seams, 12 at 0..2.75, 12 shifted 15deg beyond 2.75
 for(let [r1,r2,rot] of [[.75,2,0],[2,2.75,0],[2.75,3.5,15]]){
  for(let k=0;k<12;k++){
   let t=(k*30+rot)*Math.PI/180;ctx.strokeStyle='#133447';ctx.lineWidth=2;ctx.beginPath();
   ctx.moveTo(cx+R*r1/3.5*Math.cos(t),cy-R*r1/3.5*Math.sin(t));
   ctx.lineTo(cx+R*r2/3.5*Math.cos(t),cy-R*r2/3.5*Math.sin(t));ctx.stroke();
  }
 }
 const v=D.cases[el('design').value].configuration;
 if(v.ring!==null)ring(v.ring,'#f58997',Math.max(2,v.width*150));
 ring(3.5,'#f58997',Math.max(2,v.width*100));
 for(let k=0;k<v.spokes;k++){
  const t=(k*360/v.spokes+v.rotation_deg)*Math.PI/180,a=v.ring===null?0:v.ring;
  ctx.strokeStyle='#f58997';ctx.lineWidth=Math.max(2,v.width*95);ctx.beginPath();
  ctx.moveTo(cx+R*a/3.5*Math.cos(t),cy-R*a/3.5*Math.sin(t));
  ctx.lineTo(cx+R*Math.cos(t),cy-R*Math.sin(t));ctx.stroke();
 }
 ctx.fillStyle='#f3f8fc';ctx.font='12px system-ui';ctx.fillText('Front projected',10,18);
}
function stats(){
 const s=D.cases[el('design').value].stations[el('seat').value],
 b=D.cases['current_8x80__innerR3.5'].stations[el('seat').value];
 const pp=(s.fraction-b.fraction)*100;
 const rows=[['Visible forward hemisphere',(s.fraction*100).toFixed(2)+'%'],
 ['Improvement from held inner frame',(pp>=0?'+':'')+pp.toFixed(2)+' percentage points'],
 ['Visible sampled rays',s.visible+' / '+s.sample_count],
 ['Blocked by inner frame',s.blockage_breakdown.inner_frame],
 ['Blocked by outer nose',s.blockage_breakdown.exterior_opaque],
 ['Blocked by outer 37 seams',s.blockage_breakdown.held_37_outer_seams],
 ['Blocked by furniture/other',s.blockage_breakdown.interior+s.blockage_breakdown.sensor+s.blockage_breakdown.geometry]];
 el('stats').innerHTML=rows.map(r=>'<div class="stat"><span>'+r[0]+'</span><b>'+r[1]+'</b></div>').join('');
}
function draw(){drawSky();front();stats()}
for(const key of ['seat','design'])el(key).addEventListener('change',draw);
window.addEventListener('resize',draw);draw();
</script></body></html>'''
out=ROOT/'render/out/nose_inner_pressure_panorama_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('VIEWER',out,'bytes',out.stat().st_size)
