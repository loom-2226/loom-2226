"""Build standalone offline geometry and mechanics sensitivity for seamless dome."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_seamless_pressure_dome_screen_results.json').read_text())
D={'geometry':J['geometry'],'material':J['material_sensitivity'],
   'held_outer':J['held_outer_37_panels'],
   'pressure_Pa':101300,'default_areal_kgm2':85.2}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Wayfarer · Seamless pressure dome research</title>
<style>
*{box-sizing:border-box}body{background:#091727;color:#e6f0fa;margin:0;font:14px system-ui,Arial}
header{padding:15px 18px;background:#182d40;border-bottom:1px solid #4b6171}
h1{font-size:19px;margin:0 0 5px}small,.note{color:#b7cad8;line-height:1.5}
main{display:grid;grid-template-columns:minmax(0,1fr) 340px}
article{padding:16px}aside{padding:16px;background:#142437;border-left:1px solid #455e75}
canvas{width:100%;display:block;background:#10283c;border-radius:8px}
#section{height:315px;max-width:720px}#stress{height:245px;max-width:720px}
h2{font-size:16px;margin:18px 0 8px}
select{color:#f0f7fb;background:#26445c;padding:9px;border:1px solid #7591a6;width:100%;border-radius:6px}
label{display:block;margin:13px 0 6px}
input{width:100%;accent-color:#69cabb}
.stat{display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #40576a;padding:9px 0}
.stat b{text-align:right;font-variant-numeric:tabular-nums}
.bad{color:#e9b58e}.good{color:#82dbcd}
@media(max-width:800px){main{display:block}aside{border:0;border-top:1px solid #40576a}#section{height:265px}}
</style></head><body>
<header><h1>WAYFARER · SEAMLESS INNER PRESSURE DOME</h1>
<small>37 replaceable transparent outer panels HELD · inner pressure ellipsoid without internal frame · non-canon engineering sensitivity</small>
</header><main><article>
<h2>True source pressure-head profile and protected outer glazing</h2>
<canvas id="section"></canvas>
<p class="note">Blue-green curve: continuous visually frameless structural dome to radius 3.5m, matching original pressure ellipsoid. Pale cyan: independent outer fixed protective panels, flat until r2m then 50° angled, with 37 replaceable tiles around circumference (individual seam topology not represented in this section). Orange: attachment/perimeter ring. Cross-section shows actual shape, not strength or optical refraction.</p>
<h2>Ideal membrane tension across dome radius</h2>
<canvas id="stress"></canvas>
<p class="note">Solid: meridional tensile stress. Dashed: hoop tensile stress. This is the thin curved-shell equilibrium solution under 101.3 kPa, scaled by selected normal thickness. Edge bending, stress concentrations, thermal gradients, fracture dynamics, fasteners, optical refraction and impact loads are NOT modeled.</p>
</article>
<aside>
<label for="mat">Transparent material benchmark (real measured properties)</label>
<select id="mat"><option value="fused_silica">Fused silica (low thermal expansion)</option><option value="transparent_spinel">Transparent spinel</option><option value="ALON">ALON optical ceramic</option></select>
<label for="layers">Pressure-dome configuration</label>
<select id="layers"><option value="1">One continuous pressure shell</option><option value="2">Two independently thick shells (mass doubled)</option></select>
<label for="thick">Per-shell thickness factor vs original window mass allocation: <b id="factor">1.00 ×</b></label>
<input type="range" id="thick" min="0.50" max="2.5" step="0.05" value="1">
<label for="temp">Hypothetical fully restrained temperature change: <b id="tempval">20 K</b></label>
<input type="range" id="temp" min="0" max="40" step="5" value="20">
<div id="numbers"></div>
<h2>Read the limitations</h2>
<p class="note">A physically shared laminate is not necessarily redundant. The two-dome switch doubles full-capable material layers but does NOT prove independent failure survival: sealing, venting, gap pressurization and dynamic load transfer are absent.</p>
<p class="note">The thermal value is a purposely conservative full-restraint <b>stress scale</b>. It is not a prediction of actual Wayfarer temperatures or stresses, and cannot be freely added to pressure stress as a certified worst-case.</p>
<p class="note">Fracture threshold uses ideal surface flaw K = 1.12 × stress × √(πa), not an acceptance criterion. The full 7m material object and boundary ring have not been qualified. This demonstration cannot conclude that a seamless pressure dome is safe.</p>
</aside></main>
<script>
const D=__DATA__, E=id=>document.getElementById(id);
function size(id){const c=E(id),f=devicePixelRatio||1,W=c.clientWidth,H=c.clientHeight;
c.width=W*f;c.height=H*f;const ctx=c.getContext('2d');ctx.setTransform(f,0,0,f,0,0);return [ctx,W,H]}
function g(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-r*r/(4.3*4.3)))}
function o(r){return -1.2+Math.max(0,r-2)*Math.tan(50*Math.PI/180)}
function section(){
 const [ctx,W,H]=size('section'),X=x=>22+(x+1.65)/5.2*(W-42),Y=r=>H/2-r/4.5*(H/2-16);
 function trace(fn,a,b,color,w,dash=[]){
  ctx.strokeStyle=color;ctx.lineWidth=w;ctx.setLineDash(dash);
  for(let sg of [-1,1]){ctx.beginPath();for(let i=0;i<=180;i++){
    let r=a+(b-a)*i/180,x=X(fn(r)),y=Y(sg*r);
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
   }ctx.stroke();}ctx.setLineDash([]);
 }
 ctx.clearRect(0,0,W,H);trace(g,0,4.3,'#577992',2,[6,7]);
 let count=+E('layers').value,thick=D.material[E('mat').value].normal_thickness_m_at_source_areal_mass*(+E('thick').value);
 trace(o,0,3.5,'#75cbd0',5);trace(o,3.5,4.4,'#d8ae75',5);
 trace(g,0,3.5,'#75e0c9',Math.max(3,thick*65));
 if(count===2){trace(r=>g(r)-.075,0,3.5,'#46af9e',Math.max(3,thick*65));}
 for(let s of [-1,1]){ctx.fillStyle='#efa983';ctx.beginPath();ctx.arc(X(g(3.5)),Y(s*3.5),6,0,Math.PI*2);ctx.fill();}
 ctx.fillStyle='#eff7fa';ctx.font='12px system-ui';ctx.fillText('SPACE / BOW ←',10,20);ctx.textAlign='right';ctx.fillText('CABIN →',W-10,20);
 ctx.textAlign='left';ctx.fillStyle='#b5d4e2';ctx.fillText('Uninterrupted inner transparent pressure boundary (ellipse)',12,H-9);
}
function stress(){
 let [ctx,W,H]=size('stress'),m=D.material[E('mat').value],
 fac=+E('thick').value,th=m.normal_thickness_m_at_source_areal_mass*fac;
 let samples=Object.values(D.geometry.station_membrane).sort((a,b)=>a.r_m-b.r_m),
 max=Math.max(...samples.flatMap(s=>[s.meridional_membrane_N_per_m,s.hoop_membrane_N_per_m]))/th/1e6;
 let X=r=>40+r/3.5*(W-60),Y=s=>H-35-s/(max*1.1)*(H-60);
 ctx.clearRect(0,0,W,H);ctx.strokeStyle='#7594aa';ctx.beginPath();ctx.moveTo(X(0),Y(0));ctx.lineTo(X(3.5),Y(0));ctx.stroke();
 function line(field,color,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=2.5;ctx.setLineDash(dash);ctx.beginPath();
 for(let i=0;i<samples.length;i++){let q=samples[i],v=q[field]/th/1e6;if(!i)ctx.moveTo(X(q.r_m),Y(v));else ctx.lineTo(X(q.r_m),Y(v))}
 ctx.stroke();ctx.setLineDash([]);}
 line('meridional_membrane_N_per_m','#72dbca');line('hoop_membrane_N_per_m','#e4bd84',[6,5]);
 ctx.fillStyle='#f1f6fb';ctx.font='12px system-ui';ctx.fillText(max.toFixed(1)+' MPa',8,15);
 ctx.fillText('0',20,H-17);ctx.textAlign='right';ctx.fillText('r=3.5 m',W-10,H-17);ctx.textAlign='left';
 ctx.fillStyle='#72dbca';ctx.fillText('Meridional',14,35);ctx.fillStyle='#e4bd84';ctx.fillText('Hoop (dashed)',110,35);
}
function stats(){
 const mat=D.material[E('mat').value],p=mat.source_properties,fac=+E('thick').value,
  t=mat.normal_thickness_m_at_source_areal_mass*fac,n=+E('layers').value,temp=+E('temp').value;
 const stress=mat.ideal_pressure_max_membrane_stress_MPa/fac;
 const th=p.elastic_modulus_GPa*1000*p.cte_micro_per_K*1e-6*temp/(1-p.poisson);
 const a=(p.KIC_MPa_sqrt_m/(1.12*stress*Math.sqrt(Math.PI)))**2*1000;
 const ab=(p.KIC_MPa_sqrt_m/(1.12*(stress+th)*Math.sqrt(Math.PI)))**2*1000;
 const pairs=[
 ['Individual pane thickness',(t*1000).toFixed(1)+' mm'],
 ['Total transparent pressure material',(mat.full_single_dome_mass_t*n*fac).toFixed(2)+' t'],
 ['Ideal peak pressure stress',stress.toFixed(2)+' MPa'],
 ['Full-restraint thermal proxy',th.toFixed(1)+' MPa'],
 ['Pressure-only theoretical critical flaw',a.toFixed(3)+' mm'],
 ['Pressure + thermal proxy flaw',ab.toFixed(3)+' mm'],
 ['Total axial cabin pressure resultant',D.geometry.axial_pressure_resultant_MN.toFixed(2)+' MN'],
 ['Reference 4g normal inertia load',(mat.acceleration_4g_normal_inertial_pressure_proxy_kPa*fac).toFixed(2)+' kPa']
 ];
 E('factor').textContent=fac.toFixed(2)+' ×';E('tempval').textContent=temp+' K';
 E('numbers').innerHTML=pairs.map(x=>'<div class="stat"><span>'+x[0]+'</span><b>'+x[1]+'</b></div>').join('');
}
function draw(){section();stress();stats()}
for(let id of ['mat','layers','thick','temp'])E(id).addEventListener('input',draw);
window.addEventListener('resize',draw);draw();
</script></body></html>'''
out=ROOT/'render/out/nose_seamless_inner_pressure_dome_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(D,separators=(',',':'))))
print(out,out.stat().st_size)
