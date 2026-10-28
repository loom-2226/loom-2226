"""Offline interactive view of both glass boundaries from six actual Rev7 L1 eyes."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'command'))
import l1_refine as REF
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_two_transparent_layers_results.json').read_text())
data={
 'crowns':[{'r':c['crown_radius_m'],'fit':c['fit'],'stations':c['stations']} for c in J['results']],
 'eyes':{name:[round(float(x),4) for x in REF.D.EYES[i]] for i,name in enumerate(REF.D.IDS)},
 'Touter':J['outer_protection_kg_m2']/3670.,
 'Tinner':J['inner_press_panes_combined_kg_m2']/2210.,
 'baseline':.6914,
 'geometry':[1.2,2.,50],
}
html=r'''<!doctype html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer L1 2-Layer Panoramic Window Walkthrough</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a1523;color:#e5f0fa;font:14px system-ui,Arial,sans-serif}
header{padding:12px 16px;background:#17293b;border-bottom:1px solid #37536a;display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
h1{font-size:18px;margin:0}small,.muted{color:#b1c4d6}
select{color:#f4f8fc;background:#233b55;border:1px solid #7892a8;border-radius:6px;padding:8px}
main{display:grid;grid-template-columns:minmax(0,1fr) 340px;min-height:calc(100dvh - 67px)}
article{padding:14px}
aside{background:#132235;border-left:1px solid #37526a;padding:15px}
canvas{touch-action:manipulation;display:block;width:100%;border:1px solid #3d5a71;border-radius:9px;background:#0d1e31}
#sky{height:390px;max-width:800px}#section{height:275px;max-width:800px}
h2{font-size:16px;margin:14px 0 8px}
p{margin:8px 0;color:#bbcada;line-height:1.45}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 12px}
.key{font-size:11px;white-space:nowrap}
.key:before{content:'';display:inline-block;width:8px;height:8px;margin-right:5px;border-radius:50%;background:var(--c)}
.stat{padding:9px 0;border-bottom:1px solid #384b62}
.stat b{float:right}
#ray{line-height:1.55;margin-top:12px;padding:10px;border:1px solid #4a6075;border-radius:7px}
label{color:#b9cbdb}
@media(max-width:780px){main{display:block}aside{border-left:0;border-top:1px solid #37526a}#sky{height:340px}#section{height:250px}}
</style></head><body>
<header><div><h1>WAYFARER · L1 TWO-LAYER PANORAMA</h1>
<small>Actual Rev 7 eye locations and interior occlusion · research geometry, not qualified glazing</small></div>
<div class="row"><label for="seat">Station</label><select id="seat">
<option>PILOT</option><option>NAV</option><option>S1</option><option>S2</option><option>S3</option><option>S4</option></select>
<label for="crown">Crown</label><select id="crown">
<option value="2.8">2.8 m</option><option value="3.2">3.2 m</option><option value="3.5" selected>3.5 m</option></select></div></header>
<main><article>
<h2>View forward from selected seat</h2>
<canvas id="sky"></canvas>
<div class="legend">
<span class="key" style="--c:#5ad3bc">Visible through both panes</span>
<span class="key" style="--c:#e0b678">Opaque exterior</span>
<span class="key" style="--c:#aa85da">Opaque pressure hull</span>
<span class="key" style="--c:#e17a83">Frame</span>
<span class="key" style="--c:#e58f50">Bow sensor</span>
<span class="key" style="--c:#6283a0">Furniture/interior</span></div>
<p>Each dot is one equal-solid-angle ray over the forward hemisphere. The circle is 90° off the bow axis at its rim, not a photographed scene. Tap any dot to trace its actual path through the two window layers.</p>
<h2>Axial cutaway: outer shield and pressure glazing</h2>
<canvas id="section"></canvas>
<p><span style="color:#74d9bf">Teal</span> is transparent material, <span style="color:#e8b971">gold</span> is opaque exterior, and <span style="color:#9bc7ed">pale blue</span> is the original pressure-envelope line. The white line shows one selected ray from the crew eye. Radial height is projected, so angled rays are schematic in this cross-section.</p>
</article>
<aside>
<h2>Station visibility</h2><div id="stats"></div>
<h2>Selected sightline</h2><div id="ray"></div>
<h2>Scientific boundaries</h2>
<p>These are straight geometric rays through both assumed transparent layers. Glass does refract and reflect; the model does not account for that. The original sensor ring and source L1 furniture are included.</p>
<p>At 3.5 m the illustrative outside protective layer is ~7.36 cm ALON-density solid and the inside pressure assembly is ~3.86 cm fused-silica-density solid. These are mass/density illustrations only, <b>not validated thicknesses</b> for impact resistance or airtight strength.</p>
<p>The 35 cm minimum inter-layer gap is a gross 1D shell envelope clearance. There is no certified ring/frame installation, structural pressure glazing, ballistic law, scattering or optical throughput model.</p>
</aside></main>
<script>
const D=__DATA__,el=id=>document.getElementById(id);
const colors={visible:'#5ad3bc',outer_opaque:'#e0b678',inner_opaque:'#aa85da',pressure_frame:'#e17a83',sensor:'#e58f50',interior:'#6283a0',geometry:'#4d5563'};
let selected=0,hitpos=[];
function dataset(){return D.crowns.find(c=>c.r===+el('crown').value)}
function station(){return dataset().stations[el('seat').value]}
function scaleCanvas(canvas){
 let W=canvas.clientWidth,H=canvas.clientHeight,p=devicePixelRatio||1;
 canvas.width=W*p;canvas.height=H*p;let ctx=canvas.getContext('2d');ctx.setTransform(p,0,0,p,0,0);
 return [ctx,W,H];
}
function sky(){
 const C=el('sky'),[ctx,W,H]=scaleCanvas(C),cx=W/2,cy=H/2,R=Math.min(W-28,H-26)/2;
 ctx.clearRect(0,0,W,H);
 ctx.fillStyle='#162b40';ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#7694b1';ctx.lineWidth=1;ctx.beginPath();ctx.arc(cx,cy,R,0,Math.PI*2);ctx.stroke();
 ctx.setLineDash([4,6]);for(let r of [.33,.666]){ctx.beginPath();ctx.arc(cx,cy,R*r,0,Math.PI*2);ctx.stroke()}
 ctx.setLineDash([]);
 const rays=station().rays;hitpos=[];
 rays.forEach((a,i)=>{
  let x=cx+a.u*R,y=cy-a.v*R;hitpos.push([x,y]);
  ctx.beginPath();ctx.arc(x,y,i===selected?6:Math.max(2.8,R/55),0,Math.PI*2);
  ctx.fillStyle=colors[a.stage]||'#ffffff';ctx.fill();
  if(i===selected){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke()}
 });
 ctx.fillStyle='#dcebf8';ctx.font='12px system-ui';
 ctx.textAlign='left';ctx.fillText('FORWARD (−x)',12,20);
 ctx.textAlign='right';ctx.fillText('90° off-axis at ring',W-14,H-13);
}
function cross(){
 const C=el('section'),[ctx,W,H]=scaleCanvas(C);
 ctx.clearRect(0,0,W,H);
 const xmin=-1.8,xmax=2.9,rmax=4.65,margin=18;
 const X=x=>margin+(x-xmin)/(xmax-xmin)*(W-2*margin);
 const Y=r=>H/2-r/rmax*(H/2-margin);
 const shape=(r)=>-1.2+Math.max(0,r-2)*Math.tan(50*Math.PI/180);
 const hull=(r)=>2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2));
 function trace(fn,r0,r1,col,lw,dash=[]){
  ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.setLineDash(dash);
  for(let s of [-1,1]){
   ctx.beginPath();
   for(let k=0;k<=220;k++){
    const r=r0+(r1-r0)*k/220,x=X(fn(r)),y=Y(s*r);
    if(k===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
   }ctx.stroke();
  }ctx.setLineDash([]);
 }
 trace(hull,0,4.3,'#93bcdf',1.5,[6,5]);
 const crown=dataset().r;
 trace(hull,0,crown,'#66d0bb',5);
 trace(shape,0,crown,'#72d5cb',6);
 trace(shape,crown,4.5,'#dfb77b',5);
 // approximate rear face of protective outer layer, drawn to scale
 const off=r=>r<=2?D.Touter:D.Touter/Math.cos(50*Math.PI/180);
 trace(r=>shape(r)+off(r),0,crown,'#7ca5a0',1.5,[2,4]);
 const id=el('seat').value,eye=D.eyes[id],a=station().rays[selected];
 let end=a.outer_hit_xyz;
 // actual selected ray is linear in XYZ, radial projection is nonlinear
 ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();
 for(let j=0;j<=48;j++){
  let t=j/48,p=eye.map((v,i)=>v*(1-t)+end[i]*t);
  let x=X(p[0]),y=Y(Math.hypot(p[1],p[2]));
  if(!j)ctx.moveTo(x,y);else ctx.lineTo(x,y)
 }ctx.stroke();
 for(let p of [eye,a.pressure_hit_xyz,a.outer_hit_xyz]){
  ctx.beginPath();ctx.arc(X(p[0]),Y(Math.hypot(p[1],p[2])),4,0,Math.PI*2);
  ctx.fillStyle=p===eye?'#ffda80':'white';ctx.fill();
 }
 ctx.fillStyle='#e3edf7';ctx.font='12px system-ui';ctx.textAlign='left';ctx.fillText('SPACE / BOW ←',12,18);
 ctx.textAlign='right';ctx.fillText('L1 cabin →',W-12,18);
}
function info(){
 const s=station(),f=dataset().fit,r=s.rays[selected],inc=s.visible_either_surface_over_60deg_count;
 const stats=[
 ['Visible forward sky',(s.fraction_visible*100).toFixed(2)+'%'],
 ['Visible sampled rays',s.visible_ray_count+' / '+s.count],
 ['Median inner pane incidence',s.visible_inner_incidence_median_deg+'°'],
 ['Median outer pane incidence',s.visible_outer_incidence_median_deg+'°'],
 ['Visible rays incident ≥60° on either pane',inc],
 ['Minimum inter-layer material clearance',f.min_clearance_between_solid_materials_m.toFixed(3)+' m'],
 ['Rev 7 Pilot/NAV reference','69.14%']
 ];
 el('stats').innerHTML=stats.map(v=>'<div class="stat">'+v[0]+'<b>'+v[1]+'</b></div>').join('');
 el('ray').innerHTML='<b>Ray '+(selected+1)+'</b><br>Status: <b style="color:'+colors[r.stage]+'">'+r.stage.replaceAll('_',' ')+'</b><br>Inner pressure intersection: r = '+r.inner_radius_m.toFixed(2)+' m<br>Exterior intersection: r = '+r.outer_radius_m.toFixed(2)+' m<br>Inner pane angle: '+r.inner_inc_deg.toFixed(1)+'°<br>Outer pane angle: '+r.outer_inc_deg.toFixed(1)+'°';
}
function render(){if(selected>=station().rays.length)selected=0;sky();cross();info()}
el('sky').addEventListener('click',ev=>{
 const rect=el('sky').getBoundingClientRect(),x=ev.clientX-rect.left,y=ev.clientY-rect.top;
 let best=0,d=1e99;hitpos.forEach((p,i)=>{let dd=(p[0]-x)**2+(p[1]-y)**2;if(dd<d){d=dd;best=i}});
 selected=best;render();
});
el('crown').addEventListener('change',render);el('seat').addEventListener('change',render);
addEventListener('resize',render);
render();
</script></body></html>'''
out=ROOT/'render/out/nose_two_transparent_layers_seat_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print(out,'bytes',out.stat().st_size)
