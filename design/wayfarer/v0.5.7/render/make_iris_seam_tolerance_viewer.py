"""Self-contained interactive near-boss iris scarf seam sensitivity viewer.
Shows one seam cross section, NOT a ballistic prediction.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_iris_seam_tolerance_results.json').read_text())
data={'R':1.76,'hub':.12,'T':J['nominal_full_leaf_depth_m'],
      'nominal_protection_g_cm2':J['nominal_protection_g_cm2'],
      'variants':J['variants']}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer Iris: Finite Scarf Seam Tolerance</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0a1421;color:#e9f1f9;font:14px system-ui,Arial,sans-serif}
header{padding:12px 15px;background:#15283a;border-bottom:1px solid #3b5668}
h1{font-size:18px;margin:0 0 5px}small,.muted{color:#b2c7d7}
main{display:grid;grid-template-columns:minmax(0,1fr) 300px;min-height:calc(100dvh - 73px)}
canvas{width:100%;height:430px;background:#101d30}
aside{padding:16px;border-left:1px solid #364d63;background:#142236}
select,input{accent-color:#eab871}select{background:#2c4054;border:1px solid #698398;border-radius:6px;color:#eff6fc;padding:8px}
label{display:block;margin:13px 0 5px}input[type=range]{width:100%}
.stat{padding:9px 0;border-bottom:1px solid #374d63}.warn{color:#ffad9d}.ok{color:#a1e3c2}
@media(max-width:780px){main{display:block}canvas{height:350px}aside{border-top:1px solid #364d63;border-left:0}}
</style></head><body><header><h1>WAYFARER · ARMOUR IRIS EDGE-TOLERANCE TEST</h1><small>Closed joint near the centre boss · axial cross-section · ideal geometry, NOT an impact simulation</small></header>
<main><div><canvas id="cross"></canvas><div style="padding:15px;color:#afc7da">Gold = forward upper-blade armour (first ~98 mm depth). Teal = aft lower-blade armour (next ~98 mm). The two edge lips share one full nominal shield thickness only where both are present. White dashed lines mark the original geometric seam ends.</div></div>
<aside>
<label>Nominal angular scarf lap</label><select id="lap"><option value="2">2° (original)</option><option value="3">3° (narrowly opens)</option><option value="4">4° (does not fully clear)</option></select>
<label>Radius along radial seam</label><select id="r"><option value="0.12">0.12 m, central boss edge</option><option value="0.30">0.30 m</option><option value="1.00">1.00 m</option><option value="1.76">1.76 m, outer tip</option></select>
<label>Adverse retreat of EACH mating lip <b id="errorVal">0.5 mm</b></label>
<input id="err" type="range" min="0" max="3" step=".25" value=".5">
<div id="metrics"></div>
<p class="muted">The retreat is a deliberate adverse geometric error, not a claim that a real machine has this tolerance. The colour blocks show nominal material occupancy. Even when the joint has no complete hole, thin bands with only half the nominal material can remain. That cannot be treated as full hypervelocity protection.</p>
<p class="muted">A finite axial face gap or structural load path makes the joint harder, not easier. The code does not compute dynamic strength, fragmentation, spall, leakage or projectile survival.</p>
</aside></main><script>
const D=__DATA__,el=id=>document.getElementById(id),ctx=el('cross').getContext('2d');
function draw(){
let w=el('cross').clientWidth,h=el('cross').clientHeight,p=devicePixelRatio||1;el('cross').width=w*p;el('cross').height=h*p;
ctx.setTransform(p,0,0,p,0,0);ctx.clearRect(0,0,w,h);
let deg=+el('lap').value,r=+el('r').value,e=+el('err').value;
let seam=r*1000*deg*Math.PI/180;
let both=Math.max(0,seam-2*e),hole=Math.max(0,2*e-seam);
let span=Math.max(seam*1.8,13),xv=x=>w/2+(x/span)*Math.min(w-50,620),top=85,depth=185;
const a=-seam/2,b=seam/2,ul=b-e,ll=a+e,aa=xv(-span/2),bb=xv(span/2);
function fillSection(x0,x1,y0,y1,c){ctx.fillStyle=c;ctx.fillRect(xv(x0),y0,Math.max(0,xv(x1)-xv(x0)),y1-y0)}
// upper blade full main to the left and half lip to the right
fillSection(-span/2,a,top,top+depth,'#ddb878');
fillSection(a,ul,top,top+depth/2,'#eab76b');
// lower blade full main to the right and half lip from left
fillSection(b,span/2,top,top+depth,'#4abfb1');
fillSection(ll,b,top+depth/2,top+depth,'#62cfc0');
// in middle of overlap both half-depth lips:
fillSection(Math.max(a,ll),Math.min(b,ul),top,top+depth/2,'#eab76b');
fillSection(Math.max(a,ll),Math.min(b,ul),top+depth/2,top+depth,'#62cfc0');
ctx.lineWidth=1;
for(let x of [a,b]){ctx.strokeStyle='#e4f4ff';ctx.setLineDash([4,5]);ctx.beginPath();ctx.moveTo(xv(x),top-18);ctx.lineTo(xv(x),top+depth+12);ctx.stroke()}
ctx.setLineDash([]);ctx.fillStyle='#e3effa';ctx.textAlign='center';
ctx.font='13px system-ui';ctx.fillText('OUTSIDE / FORWARD',w/2,34);
ctx.fillText('PRESSURE HULL (further aft)',w/2,top+depth+47);
ctx.fillText('Nominal 196 mm total material depth',w/2,top+depth+73);
ctx.fillStyle='#aebfd3';ctx.font='11px system-ui';ctx.fillText('Schematic; lateral seam distances to scale, radial thickness not to scale',w/2,h-16);
ctx.textAlign='left';
el('errorVal').textContent=e.toFixed(2)+' mm';
let min=e===0?27:(hole>0?0:13.5);
let current=D.variants.find(x=>x.overlap_deg===deg);
el('metrics').innerHTML=
'<div class="stat">Nominal lap width here <b>'+seam.toFixed(2)+' mm</b></div>'+
'<div class="stat">Both half-lips overlapping <b>'+both.toFixed(2)+' mm</b></div>'+
'<div class="stat">Exposed direct empty slit (projected) <b class="'+(hole?'warn':'ok')+'">'+hole.toFixed(2)+' mm</b></div>'+
'<div class="stat">Least local nominal protection <b class="'+(min<27?'warn':'ok')+'">'+min.toFixed(1)+' / 27 g/cm²</b></div>'+
'<div class="stat">Entire 16-blade cam at 62° <b class="'+(current.pressure_and_armor_path_clear?'ok':'warn')+'">'+(current.pressure_and_armor_path_clear?'geometry clear':'collision')+'</b></div>'+
'<div class="stat">Full 1.76 m aperture at 62° <b class="'+(current.radial_aperture_goal_R_minus_1cm_met?'ok':'warn')+'">'+(current.radial_aperture_goal_R_minus_1cm_met?'within 1 cm':'insufficient clear radius')+'</b></div>'+
'<div class="stat">Remaining x-packing allowance <b>'+Math.round(current.remaining_x_positioning_interval_m*1000)+' mm</b></div>';
}
for(let id of ['lap','r','err'])el(id).addEventListener('input',draw);
addEventListener('resize',draw);draw();
</script></body></html>'''
out=ROOT/'render/out/nose_iris_seam_tolerance_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print(out,'bytes',out.stat().st_size)
