"""One-off interactive offline bounded primary pressure pane fracture timeline."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_primary_fracture_one_case_results.json').read_text())
DATA={'case':J,'timeseries':J['uniform_cavity_fill_with_fragment']['sampled_time_series']}
html=r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer · Primary pressure pane fracture challenge</title>
<style>
*{box-sizing:border-box}body{font:14px system-ui,Arial,sans-serif;background:#0a1929;color:#e8f2fc;margin:0}
header{padding:15px 17px;background:#152c42;border-bottom:1px solid #466078}
h1{margin:0 0 5px;font-size:18px}small,p{color:#b7cbd9;line-height:1.5}
main{display:grid;grid-template-columns:minmax(0,1fr) 340px}
article{padding:16px}aside{background:#14283a;border-left:1px solid #425a70;padding:15px}
canvas{display:block;width:100%;background:#10273a;border-radius:8px;max-width:720px}
#gap{height:220px}#graph{height:250px}h2{font-size:15px;margin:15px 0 8px}
label{display:block;margin-top:8px;color:#c1d7e6}input{width:100%;accent-color:#7cd8c7}
.stat{display:flex;justify-content:space-between;gap:10px;padding:9px 0;border-bottom:1px solid #3d566b}
.stat b{text-align:right;font-variant-numeric:tabular-nums}
.caption{font-size:12px}
@media(max-width:770px){main{display:block}aside{border:0;border-top:1px solid #405970}}
</style></head><body><header><h1>WAYFARER · PRIMARY-PANE FRACTURE CHALLENGE</h1>
<small>Held 37 replaceable exterior tiles · two seamless pressure shells · one assumed 0.25m² breach and detached fragment · non-canon research</small></header>
<main><article>
<h2>Fragment travel versus backup pressure</h2>
<canvas id="gap"></canvas>
<label for="timeline">Time since inner pressure dome fracture: <b id="clock">0 ms</b></label>
<input id="timeline" type="range" min="0" max="100" value="0" step="1"/>
<p class="caption">Fragment follows the schematic normal direction. The backup is 5.97 cm away at the smallest clearance location; the graphic expands this gap for readability. Fragment stops in the drawing at contact, but its real collision and any subsequent motion are unmodeled.</p>
<h2>Uniform-cavity pressure history</h2>
<canvas id="graph"></canvas>
<p class="caption">Model is choked-to-subcritical ideal gas flow through an assumed 0.25m² constant opening into a 3.02m³ cavity, with constant cabin pressure and temperature. The gap begins evacuated: sound cannot propagate through the vacuum. The 0.174ms distance/sound-speed comparison is NOT an arrival-time calculation; the real fracture creates a compressible jet and expansion front.</p>
</article><aside>
<div id="stats"></div>
<h2>What this does NOT show</h2>
<p>There is no verified impact failure threshold for the backup dome. One 21.3kg piece is an invented diagnostic fragment, not a predicted fragmentation pattern. The model excludes released shell strain energy, pane flexure, shard breakup and gas-jet forces.</p>
<p>Both pressure domes are independently sealed in the static concept. The external 37 protective tiles are unchanged and do not bear cabin pressure.</p>
<p>The decisive issue is whether primary-pane fragments or pressure shocks initiate backup-pane failure. A static pressure design cannot answer that, and neither can this deliberately simple one-piece motion test.</p>
</aside></main>
<script>
const D=__DATA__,J=D.case,E=id=>document.getElementById(id);
const st=J.uniform_cavity_fill_with_fragment,impact=st.contact,times=st.pressure_transition_times_s;
function context(id){const C=E(id),p=devicePixelRatio||1,W=C.clientWidth,H=C.clientHeight;
C.width=W*p;C.height=H*p;const g=C.getContext('2d');g.setTransform(p,0,0,p,0,0);return[g,W,H]}
function frame(){
 const t=+E('timeline').value,v=D.timeseries[t],p=v.cavity_pressure_kPa;
 E('clock').textContent=t+' ms';
 let[g,w,h]=context('gap');
 g.fillStyle='#234257';g.fillRect(0,0,w,h);
 let gapStart=Math.max(70,w*.27),gapEnd=Math.min(w-50,w*.78),top=30,bot=h-38;
 g.fillStyle='#e1b980';g.fillRect(gapStart-12,top,10,bot-top);
 g.fillStyle='#88dfd1';g.fillRect(gapEnd,top,10,bot-top);
 g.fillStyle='#b5cce1';g.font='12px system-ui';
 g.textAlign='center';g.fillText('FAILED INNER',gapStart,20);g.fillText('BACKUP',gapEnd,20);
 g.fillStyle='#65c6d2';g.fillRect(gapStart,top+16,(gapEnd-gapStart)*(p/101.3),bot-top-32);
 let fx=gapStart+Math.min(1,v.fragment_distance_m/J.min_normal_gap_m)*(gapEnd-gapStart);
 g.fillStyle='#ffdb91';g.fillRect(fx-5,top+45,12,bot-top-90);
 g.fillStyle='#e9f4f9';g.fillText((p).toFixed(1)+' kPa in cavity',w/2,h-16);
 let[c,W,H]=context('graph'),pad=35;
 c.clearRect(0,0,W,H);c.strokeStyle='#7593a6';
 c.beginPath();c.moveTo(pad,14);c.lineTo(pad,H-pad);c.lineTo(W-10,H-pad);c.stroke();
 function X(i){return pad+i/100*(W-pad-17)}
 function Y(kPa){return H-pad-kPa/101.3*(H-pad-25)}
 c.beginPath();for(let i=0;i<D.timeseries.length;i++){
  const r=D.timeseries[i];i?c.lineTo(X(i),Y(r.cavity_pressure_kPa)):c.moveTo(X(i),Y(r.cavity_pressure_kPa));
 }c.strokeStyle='#76d6c7';c.lineWidth=2.3;c.stroke();
 c.strokeStyle='#ffcd84';c.setLineDash([4,4]);c.beginPath();
 c.moveTo(X(impact.time_s*1000),14);c.lineTo(X(impact.time_s*1000),H-pad);c.stroke();c.setLineDash([]);
 c.strokeStyle='#f1f8ff';c.beginPath();c.moveTo(X(t),14);c.lineTo(X(t),H-pad);c.stroke();
 c.fillStyle='#e9f2fa';c.font='12px system-ui';c.textAlign='right';c.fillText('101 kPa',pad-5,22);
 c.fillText('0',pad-5,H-pad+4);c.textAlign='left';c.fillText('0',pad,H-12);
 c.textAlign='right';c.fillText('100 ms',W-10,H-12);
 const stats=[
 ['Current model cavity pressure',p.toFixed(1)+' kPa'],
 ['Gap/air sound-speed distance scale','0.174 ms (not measured arrival)'],
 ['Estimated fragment arrival',(impact.time_s*1000).toFixed(2)+' ms'],
 ['Fragment impact speed',impact.speed_m_s.toFixed(2)+' m/s'],
 ['Ideal contact kinetic energy',impact.kinetic_energy_J.toFixed(0)+' J'],
 ['Cavity reaches 50% cabin pressure',(times.pressure_50pct_time_s*1000).toFixed(1)+' ms'],
 ['Cavity reaches 90% cabin pressure',(times.pressure_90pct_time_s*1000).toFixed(1)+' ms']
 ];
 E('stats').innerHTML=stats.map(([a,b])=>'<div class="stat"><span>'+a+'</span><b>'+b+'</b></div>').join('');
}
E('timeline').addEventListener('input',frame);window.addEventListener('resize',frame);frame();
</script></body></html>'''
out=ROOT/'render/out/nose_primary_fracture_timeline_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(DATA,separators=(',',':'))))
print(out,out.stat().st_size)
