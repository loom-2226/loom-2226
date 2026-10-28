"""Offline 2D comparison of candidate flush iris joint edge kinematics."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
src=json.loads((ROOT/'command/l1_iris_joint_kinematics_results.json').read_text())
data={'T':src['normal_equivalent_material_reference_m'],'R':src['radius_m'],'hub':src['hub_radius_m'],
 'rows':src['seam_cross_section_checks'],
 'shapes':{'straight_scarf':[[0,.5],[1,-.5]],'releasable_dogleg':[[0,.5],[1/3,.35],[2/3,-.35],[1,-.5]],'reverse_lap_labyrinth':[[0,-.5],[1/3,.5],[2/3,-.5],[1,.5]]}}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer: iris seam geometry and withdrawal</title><style>
*{box-sizing:border-box}body{margin:0;background:#081421;color:#e9f2fa;font:14px system-ui}
header{padding:12px 15px;border-bottom:1px solid #375066;background:#15283a}h1{font-size:18px;margin:0}small,.muted{color:#aec2d4}
main{display:grid;grid-template-columns:minmax(0,1fr) 320px;min-height:calc(100dvh - 63px)}
canvas{width:100%;height:490px;background:radial-gradient(ellipse at center,#1b3148,#091526 80%)}
aside{padding:15px;border-left:1px solid #375066;background:#142236;overflow:auto}
label{display:block;margin-top:12px;margin-bottom:4px}
select{background:#2a445c;color:#ecf6fe;border:1px solid #6b8ba5;border-radius:6px;padding:8px;width:100%}
input[type=range]{width:100%;accent-color:#e5b270}
.stat{border-bottom:1px solid #3a4d62;padding:7px 0}.red{color:#ffa297}.green{color:#a7e1c0}
@media(max-width:760px){main{display:block}canvas{height:370px}aside{border-left:0;border-top:1px solid #375066}}
</style></head><body><header><h1>WAYFARER · IRIS INTERLOCK / RELEASE TEST</h1><small>Two adjoining thick armour leaves · local seam cross-section · NON-CANON research</small></header>
<main><div><canvas id="c"></canvas><div style="padding:14px;color:#acc5db">Gold = fixed upper leaf, teal = retracting lower leaf, red = geometric interference. Left is space-facing; right leads inward toward the pressure hull. This is a magnified cut through one seam, not the entire iris.</div></div>
<aside>
<label>Joint shape</label><select id="shape"><option value="straight_scarf">Straight diagonal scarf</option><option value="releasable_dogleg">Monotone dogleg</option><option value="reverse_lap_labyrinth">Reversing labyrinth</option></select>
<label>Angular lap</label><select id="lap"><option>2</option><option selected>3</option><option>4</option></select>
<label>Where the seam is measured</label><select id="radius"><option value="0.12">Near central boss (r=0.12 m)</option><option value="0.30">r=0.30 m</option><option value="1.00">r=1.00 m</option><option value="1.76">Outer viewport rim (r=1.76 m)</option></select>
<label>Adverse edge retreat on each side: <b id="errlabel">0.5 mm</b></label><input id="err" type="range" min="0.25" max="2" step=".25" value=".5">
<label>Lower-blade axial withdrawal: <b id="withdrawlabel">0 mm</b></label><input id="pull" type="range" min="0" max="196.28" step="1" value="0">
<div id="stats"></div>
<p class="muted">Every cross-section is illustrative. The diagonal and monotone dogleg release axially; the reversing labyrinth catches on an undercut. These views do not establish manufacturable tolerances, strength, dust sealing or hypervelocity shielding performance.</p>
</aside></main><script>
const D=__DATA__,e=id=>document.getElementById(id),C=e('c'),ctx=C.getContext('2d');
function geom(name,r,lap){
 const q=D.shapes[name],w=r*1000*lap*Math.PI/180;
 return q.map(v=>[v[0]*D.T*1000,v[1]*w]);
}
function f(path,x){if(x<=path[0][0])return path[0][1];for(let i=1;i<path.length;i++){if(x<=path[i][0]){let a=path[i-1],b=path[i],t=(x-a[0])/(b[0]-a[0]);return a[1]*(1-t)+b[1]*t}}return path.at(-1)[1]}
function draw(){
 const pr=devicePixelRatio||1,W=C.clientWidth,H=C.clientHeight;C.width=W*pr;C.height=H*pr;ctx.setTransform(pr,0,0,pr,0,0);ctx.clearRect(0,0,W,H);
 const name=e('shape').value,lap=+e('lap').value,r=+e('radius').value,err=+e('err').value,shift=+e('pull').value,points=geom(name,r,lap);
 const full=D.T*1000,w=r*1000*lap*Math.PI/180,g=2*err,halfSpan=Math.max(w*1.7,10);
 let xToPx=x=>52+(x/Math.max(full+shift,230))*(W-95),yToPx=y=>H/2-(y/halfSpan)*(H*.37);
 let topY=halfSpan,bottomY=-halfSpan,coll=0;
 for(let i=0;i<450;i++){
  let xa=i/450*(full+shift),xb=(i+1)/450*(full+shift),xm=(xa+xb)/2;
  let fy=f(points,Math.min(full,Math.max(0,xm)));
  if(xm<=full){
   ctx.fillStyle='#e4b775';ctx.fillRect(xToPx(xa),yToPx(fy-g/2),Math.max(1,xToPx(xb)-xToPx(xa)),yToPx(bottomY)-yToPx(fy-g/2));
  }
  if(xm>=shift && xm<=shift+full){
   let by=f(points,xm-shift)+g/2;
   ctx.fillStyle='#63cabb';ctx.fillRect(xToPx(xa),yToPx(topY),Math.max(1,xToPx(xb)-xToPx(xa)),yToPx(by)-yToPx(topY));
   if(xm<=full && fy-g/2>by){
    coll=Math.max(coll,fy-g/2-by);
    ctx.fillStyle='#f56864';ctx.fillRect(xToPx(xa),yToPx(fy-g/2),Math.max(1,xToPx(xb)-xToPx(xa)),yToPx(by)-yToPx(fy-g/2));
   }
  }
 }
 ctx.strokeStyle='#a6bbd1';ctx.setLineDash([4,4]);for(let ax of [0,full]){let px=xToPx(ax);ctx.beginPath();ctx.moveTo(px,40);ctx.lineTo(px,H-40);ctx.stroke()}ctx.setLineDash([]);
 ctx.fillStyle='#c9dbeb';ctx.font='12px system-ui';ctx.fillText('SPACE',18,24);ctx.fillText('pressure hull is farther inward →',Math.max(20,W-245),24);
 ctx.fillText('Original 196.3 mm leaf depth',54,H-20);
 e('errlabel').textContent=err.toFixed(2)+' mm';e('withdrawlabel').textContent=shift.toFixed(0)+' mm';
 let saved=D.rows.find(x=>x.type===name&&x.lap_deg===lap&&x.edge_recession_mm===err);
 e('stats').innerHTML='<div class="stat">Lap width at this radius <b>'+w.toFixed(2)+' mm</b></div>'+
 '<div class="stat">Instantaneous 2D interference <b class="'+(coll>.01?'red':'green')+'">'+coll.toFixed(2)+' mm</b></div>'+
 '<div class="stat">Axial release across full 196mm stroke <b class="'+(saved.axially_releasable?'green':'red')+'">'+(saved.axially_releasable?'Geometry clear at boss':'JAMS at boss')+'</b></div>'+
 '<div class="stat">Minimum nominal material depth at r=0.12m <b>'+saved.nominal_material_depth_remaining_at_weakest_cross_section_mm.toFixed(1)+' / 196.3 mm</b></div>'+
 '<div class="stat muted">Nominal areal mass, seam fracture and HVI performance are NOT qualified.</div>';
}
for(let id of ['shape','lap','radius','err','pull'])e(id).addEventListener('input',draw);
addEventListener('resize',draw);draw();
</script></body></html>'''
out=ROOT/'render/out/nose_iris_interlocking_joint_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('created',out,'bytes',out.stat().st_size)
