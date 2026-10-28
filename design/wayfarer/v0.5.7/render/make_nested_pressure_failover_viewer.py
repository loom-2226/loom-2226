"""Offline 37-held + two seamless pressure domes failover cross-section viewer."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
D=json.loads((ROOT/'command/l1_nested_pressure_dome_failover_results.json').read_text())
data={'spaces':D['separation_sensitivity'],
      'states':D['nominal_static_failover_states'],
      'properties':D['fixed_assumptions'],
      'forces_MN':D['per_individual_pressure_shell_axial_pressure_resultant_MN'],
      'mass_t':D['two_pressure_panes_total_material_mass_t'],
      'outer_allocation_t':D['outer_protective_37_material_allocation_t']}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer dual seamless domes · failure and separation</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0a1827;color:#ebf2f8;font:14px system-ui,Arial}
header{padding:14px 16px;background:#162a3e;border-bottom:1px solid #415970}
h1{font-size:18px;margin:0 0 4px}
small,.note{color:#b5c8d7;line-height:1.5}main{display:grid;grid-template-columns:minmax(0,1fr) 350px}
article{padding:14px}aside{padding:16px;background:#142638;border-left:1px solid #3e5971}
canvas{width:100%;height:430px;max-width:780px;background:#102539;border:1px solid #3c5469;border-radius:8px}
label{display:block;margin:14px 0 6px;color:#bbd1df}
select{color:#f2f8ff;background:#263e54;border:1px solid #7692a7;padding:10px;width:100%;border-radius:7px}
.stat{padding:10px 0;border-bottom:1px solid #385269;display:flex;justify-content:space-between;gap:12px}
.stat b{text-align:right;font-variant-numeric:tabular-nums}
.good{color:#7ee3ce}.warn{color:#f0c187}
h2{font-size:16px}
.key{display:inline-block;padding-right:14px;font-size:12px}
.key:before{content:'';display:inline-block;background:var(--color);width:10px;height:10px;border-radius:50%;margin-right:5px}
@media(max-width:780px){main{display:block}aside{border:0;border-top:1px solid #3e5971}canvas{height:310px}}
</style></head><body>
<header><h1>WAYFARER · TWO SEAMLESS PRESSURE DOMES</h1>
<small>37 separately replaceable outer protective panels remain HELD · static redundancy experiment · non-canon</small>
</header><main><article><h2>Cross-section through the existing nose</h2>
<canvas id="section"></canvas><div>
<span class="key" style="--color:#64d5d9">37-panel protective skin (projected)</span>
<span class="key" style="--color:#a7e2c5">Outer backup pressure dome</span>
<span class="key" style="--color:#f6cd81">Inner primary pressure dome</span></div>
<p class="note">The two pressure domes use identical curved ellipsoid profiles, with separate axial mounting positions. The 37 protective tiles are shown as one outline in axial section, not as one monolithic piece. The heavy dots at both rims represent hypothetical separate pressure load-bearing attachments.</p>
<h2>Static failover logic</h2>
<p class="note">During normal operation the inter-pane gap is evacuated and isolated. If the inner primary fails, cavity air pressure rises and the intact outer pressure dome becomes the backup. This graphic shows stable end states only. Actual rupture, shock loading and glass debris are not simulated.</p>
</article><aside>
<label for="space">Axial offset between pressure-shell centre surfaces</label>
<select id="space">
<option value="0.06">6 cm, tight</option>
<option value="0.08">8 cm</option>
<option value="0.10">10 cm</option>
<option value="0.12" selected>12 cm, reference</option>
<option value="0.15">15 cm</option>
<option value="0.20">20 cm</option>
<option value="0.25">25 cm, largest tested</option>
</select>
<label for="failure">Pressure state</label><select id="failure">
<option value="normal">Normal: inner holds pressure</option>
<option value="inner_primary_fails_stable">Inner fails: outer backup holds</option>
<option value="outer_backup_fails_stable">Outer fails: inner still holds</option>
<option value="both_fail">Both fail: no containment</option></select>
<div id="stats"></div>
<h2>Real engineering unknowns</h2>
<p class="note">Each pressure shell's own rim must accept the entire ~3.90 MN axial pressure resultant upon failure of the other. The unloaded backup in normal operations is **not** an unused decorative pane; its flange and seal are critical.</p>
<p class="note">This model assumes full-pressure-capable shells based on a previous *ideal membrane* analysis, not actual failure-tested glass. The transient after primary fracture could impact or fracture the backup; the seal response, shock and crack fragmentation are not modeled.</p>
<p class="note">The interspace must stay isolated from an open-to-vacuum vent. Otherwise inner-pane failure could leak cabin air through that vent rather than pressurising the backup cavity. Periodic evacuation with a closed isolation path is one possible operating concept, but no valve is designed here.</p>
<p class="note">Outer protective tiles and inner pressure shells use independent attachment systems and the baseline material density allocations. No change to source PR432, crew stations, shielding, or canon.</p>
</aside></main>
<script>
const D=__DATA__,E=id=>document.getElementById(id);
function cfg(){return D.spaces.find(x=>Math.abs(x.axial_center_separation_m-Number(E('space').value))<1e-8)}
function mode(){return D.states.find(x=>x.event===E('failure').value)}
function sketch(){
 let can=E('section'),w=can.clientWidth,h=can.clientHeight,d=window.devicePixelRatio||1;
 can.width=w*d;can.height=h*d;let ctx=can.getContext('2d');ctx.setTransform(d,0,0,d,0,0);
 const X=x=>22+(x+1.75)/5.4*(w-44),Y=r=>h/2-r/4.55*(h/2-18);
 const slope=r=>2.35-2.15*Math.sqrt(Math.max(0,1-r*r/(4.3*4.3)));
 const shield=r=>-1.2+Math.max(0,r-2)*Math.tan(50*Math.PI/180);
 function trace(fn,a,b,col,stroke,broken=false){
  ctx.lineWidth=stroke;ctx.strokeStyle=col;ctx.setLineDash(broken?[7,7]:[]);
  for(let sg of [-1,1]){
   ctx.beginPath();for(let i=0;i<=200;i++){
    let r=a+(b-a)*i/200,x=X(fn(r)),y=Y(sg*r);
    if(!i)ctx.moveTo(x,y);else ctx.lineTo(x,y);
   }ctx.stroke();
  }ctx.setLineDash([]);
 }
 let space=cfg(),sta=mode(),dx=space.axial_center_separation_m;
 ctx.clearRect(0,0,w,h);
 trace(slope,0,4.3,'#44647c',2,true);
 trace(shield,0,3.5,'#64d5d9',5);
 trace(shield,3.5,4.3,'#cfae7c',5);
 let isBroken=sta.event==='inner_primary_fails_stable'||sta.event==='both_fail';
 let osBroken=sta.event==='outer_backup_fails_stable'||sta.event==='both_fail';
 trace(r=>slope(r)-dx,0,3.5,'#a7e2c5',5,osBroken);
 trace(slope,0,3.5,'#f6cd81',5,isBroken);
 for(let r of [-3.5,3.5]){
   for(let x of [slope(3.5),slope(3.5)-dx]){
    ctx.fillStyle='#ecb6a0';ctx.beginPath();ctx.arc(X(x),Y(r),5,0,2*Math.PI);ctx.fill();
   }
 }
 let center=sta.cavity_kPa===null?'#e8a9a9':sta.cavity_kPa>1?'#67778a':'#23435c';
 ctx.fillStyle=center;ctx.font='12px system-ui';ctx.fillText('CAVITY: '+(sta.cavity_kPa===null?'FAILED':sta.cavity_kPa.toFixed(1)+' kPa'),12,h-20);
 ctx.fillStyle='#ecf7fe';ctx.font='12px system-ui';ctx.fillText('SPACE ←',12,20);ctx.textAlign='right';ctx.fillText('CABIN →',w-12,20);
}
function stats(){
 const s=cfg(),st=mode(),n=D.mass_t;
 const pairs=[
 ['Inner load, axial',st.inner_axial_force_MN===null?'unknown':st.inner_axial_force_MN.toFixed(2)+' MN'],
 ['Outer backup load, axial',st.outer_axial_force_MN===null?'unknown':st.outer_axial_force_MN.toFixed(2)+' MN'],
 ['Approx. free normal gap', (100*s.min_free_gap_between_pressure_shells_normal_approx_m).toFixed(1)+' cm'],
 ['Gross outer-shield clearance', (100*s.min_shield_to_outer_pressure_shell_gap_axial_m).toFixed(1)+' cm'],
 ['Evacuated cavity volume',s.inter_pressure_void_volume_m3.toFixed(2)+' m³'],
 ['Gas in cavity when filled at 101.3kPa',s.gas_to_fill_cavity_at_cabin_p_and_293K_kg.toFixed(2)+' kg'],
 ['Pressure glass material, both shells',D.mass_t.toFixed(2)+' t'],
 ['Outer 37-panel shield material allocation',D.outer_allocation_t.toFixed(2)+' t']
 ];
 E('stats').innerHTML=pairs.map(([a,b])=>'<div class="stat"><span>'+a+'</span><b>'+b+'</b></div>').join('')+
 '<p class="note">'+st.narrative+'</p>';
}
function run(){sketch();stats()}E('space').addEventListener('change',run);
E('failure').addEventListener('change',run);window.addEventListener('resize',run);run();
</script></body></html>'''
out=ROOT/'render/out/nose_nested_pressure_failover_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print('VIEWER',out,'bytes',out.stat().st_size)
