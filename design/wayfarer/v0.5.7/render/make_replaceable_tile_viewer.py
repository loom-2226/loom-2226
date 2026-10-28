"""Build standalone offline tile-layout tradeoff viewer; no external dependencies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
J=json.loads((ROOT/'command/l1_replaceable_outer_tiles_results.json').read_text())
data={'presets':J['tile_presets'],'areas':J['tile_areas_and_seams'],
      'scores':J['forward_hemisphere_sightline_scores']}
html=r'''<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfarer | Replaceable Transparent Nose Panels</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#091726;color:#e9f3fb;font:14px system-ui,Arial,sans-serif}
header{padding:13px 15px;border-bottom:1px solid #3b566c;background:#15283c}
h1{margin:0 0 5px;font-size:18px}small,.muted{color:#b1c8d8}
main{display:grid;grid-template-columns:minmax(0,1fr) 335px;min-height:calc(100dvh - 65px)}
article{padding:12px 16px}
canvas{width:100%;display:block;border-radius:9px;background:#0c1e30;touch-action:manipulation}
#tiles{max-width:630px;aspect-ratio:1/1;cursor:crosshair}
#section{max-width:630px;height:210px}
aside{padding:17px;background:#122337;border-left:1px solid #37546e}
h2{font-size:15px;margin:10px 0}
label{display:block;margin:14px 0 6px;color:#b8cbdc}
select{width:100%;padding:9px;background:#263f56;border:1px solid #7790a5;border-radius:6px;color:#f1f8ff}
.stat{padding:8px 0;border-bottom:1px solid #384d62;display:flex;gap:10px;justify-content:space-between}
.stat b{text-align:right;font-variant-numeric:tabular-nums}
.green{color:#9cdbce}.gold{color:#f0c182}
input{width:100%;accent-color:#70d5c5}
.note{margin:10px 0;color:#b8c9d8;font-size:13px;line-height:1.5}
@media(max-width:760px){main{display:block}aside{border-left:0;border-top:1px solid #37546e}#tiles{max-width:100%}}
</style></head><body>
<header><h1>WAYFARER · REPLACEABLE TRANSPARENT NOSE</h1>
<small>3.5m crown · exterior armour tiles only · unchanged inner pressure glazing · non-canon research</small></header>
<main><article>
<canvas id="tiles"></canvas>
<p class="note">Projected bow view. Teal patches are separately replaceable outer protective panels; dark lines represent the selected nominal opaque seam width. Tap a tile to inspect its mass and size. The faint circle marks the transition between the flat centre and sloped 50° outer facets.</p>
<h2>External replacement concept</h2><canvas id="section"></canvas>
<p class="note">Illustrative removal outward into space. The original pressure boundary remains sealed throughout. No cassette supports, robotic handling attachment or verified release motion is included.</p>
</article><aside>
<label for="layout">Tile shape and arrangement</label>
<select id="layout">
<option value="radial_trapezoids_12">25 large radial trapezoids</option>
<option value="staggered_trapezoids_12">37 staggered trapezoids</option>
<option value="staggered_trapezoids_compact_12" selected>37 compact staggered trapezoids</option>
<option value="large_hex_1p6">31 large hexagons</option>
<option value="large_hex_shifted_1p6">25 rim-aligned large hexagons</option>
<option value="medium_hex_1p2">43 medium hexagons</option>
<option value="medium_hex_shifted_1p2">42 rim-aligned medium hexagons</option>
</select>
<label for="seam">Opaque seam / retainer width</label>
<select id="seam"><option value="5">5 mm</option><option value="10" selected>10 mm</option><option value="20">20 mm</option></select>
<label for="seat">Visibility from source L1 station</label>
<select id="seat"><option>PILOT</option><option>NAV</option><option>S1</option><option>S2</option><option>S3</option><option>S4</option></select>
<div id="stats"></div>
<label for="lift">Illustrative outward replacement separation: <b id="liftval">0 cm</b></label>
<input type="range" id="lift" min="0" max="45" step="5" value="0"/>
<div id="picked"></div>
<p class="note">These panels have independent geometric footprints. <strong>Actual on-orbit removal is not certified</strong>: mount details, thermal constraints, impact resistance, service handling and peripheral stress remain open. Curved and sloped surfaces require shaped panes. Hexagons crossing the flat/facet transition are especially difficult.</p>
<p class="note">All masses shown are at the incumbent <b>270 kg/m² nominal armour material budget</b>, not verified equivalent transparent hypervelocity protection. Changes in shape do not make material scientifically qualified.</p>
</aside></main>
<script>
const D=__DATA__,E=id=>document.getElementById(id),c=E('tiles'),ctx=c.getContext('2d');
let chosen=null;
function mod(a,b){return ((a%b)+b)%b}
function classify(x,y,p){
 const r=Math.hypot(x,y),theta=mod(Math.atan2(y,x),2*Math.PI);
 if(p.type==='radial'){
   let group=0;while(group<p.ns.length-1&&r>=p.rings[group+1])group++;
   const n=p.ns[group],step=2*Math.PI/n,angle=mod(theta-p.offsets[group],2*Math.PI);
   const cell=Math.floor(angle/step);
   let gap=999;
   if(n>1){const da=Math.abs(mod(angle+step/2,step)-step/2);gap=r*da}
   for(let k=1;k<p.rings.length-1;k++)gap=Math.min(gap,Math.abs(r-p.rings[k]));
   return [String(group*1000+cell),gap];
 }
 const a=p.spacing,shift=p.origin_xy_m||[0,0],px=x-shift[0],py=y-shift[1];
 const jf=2*py/(Math.sqrt(3)*a),ifloat=px/a-jf/2,sf=-ifloat-jf;
 let qi=Math.round(ifloat),rj=Math.round(jf),sc=Math.round(sf);
 const di=Math.abs(qi-ifloat),dj=Math.abs(rj-jf),ds=Math.abs(sc-sf);
 if(di>dj&&di>ds)qi=-rj-sc;
 else if(dj>ds)rj=-qi-sc;
 else sc=-qi-rj;
 const cx=a*(qi+rj/2),cy=a*Math.sqrt(3)/2*rj;
 let gap=Infinity;
 for(let [u,v] of [[1,0],[-1,0],[0,1],[0,-1],[1,-1],[-1,1]]){
   let nx=cx+a*(u+v/2),ny=cy+a*Math.sqrt(3)/2*v;
   let distance=((px-nx)**2+(py-ny)**2-(px-cx)**2-(py-cy)**2)/(2*a);
   gap=Math.min(gap,Math.abs(distance));
 }
 return [String((qi+128)*1024+(rj+128)),gap];
}
function current(){return E('layout').value}
function renderTiles(){
 const id=current(),p=D.presets[id],w=+E('seam').value,sz=530;
 c.width=sz;c.height=sz;
 let out=ctx.createImageData(sz,sz),dst=out.data,m=3.5;
 for(let py=0;py<sz;py++)for(let px=0;px<sz;px++){
  let x=(px+.5-sz/2)*7/sz,y=(sz/2-py-.5)*7/sz,r=Math.hypot(x,y),i=(py*sz+px)*4;
  if(r>m){dst[i]=10;dst[i+1]=23;dst[i+2]=38;dst[i+3]=255;continue}
  let [panel,dist]=classify(x,y,p),num=+panel;
  let tone=((num*29)%37)-17;
  let dark=dist<w/2000;
  let chosenTile=chosen===panel;
  dst[i]=dark?22:chosenTile?192:63+tone;
  dst[i+1]=dark?43:chosenTile?160:147+tone;
  dst[i+2]=dark?63:chosenTile?89:165+tone;
  dst[i+3]=255;
 }
 ctx.putImageData(out,0,0);
 ctx.strokeStyle='rgba(226,240,249,.3)';ctx.lineWidth=1.2;ctx.setLineDash([4,7]);
 ctx.beginPath();ctx.arc(sz/2,sz/2,sz/2*2/3.5,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);
 ctx.fillStyle='#e8f3fa';ctx.font='14px system-ui';ctx.fillText('BOW / outward view',15,24);
}
function renderSection(){
 const el=E('section'),W=el.clientWidth,H=el.clientHeight,p=window.devicePixelRatio||1;
 el.width=W*p;el.height=H*p;const g=el.getContext('2d');g.setTransform(p,0,0,p,0,0);
 g.fillStyle='#0b2032';g.fillRect(0,0,W,H);
 const X=x=>20+(x+1.8)/5.25*(W-45),Y=r=>H/2-r/4.5*(H/2-15);
 function outer(r){return -1.2+Math.max(0,r-2)*Math.tan(50*Math.PI/180)}
 function press(r){return 2.35-2.15*Math.sqrt(Math.max(0,1-r*r/4.3**2))}
 function path(fn,lo,hi,fill,width,dash=[]){
  g.strokeStyle=fill;g.lineWidth=width;g.setLineDash(dash);
  for(let sign of [-1,1]){
   g.beginPath();
   for(let j=0;j<=150;j++){let r=lo+(hi-lo)*j/150,xx=X(fn(r)),yy=Y(sign*r);if(!j)g.moveTo(xx,yy);else g.lineTo(xx,yy)}
   g.stroke();
  }g.setLineDash([]);
 }
 path(press,0,3.5,'#a2c8e9',3);
 path(outer,0,3.5,'#6ed4ca',5);
 path(outer,3.5,4.3,'#d5b578',5);
 const lift=+E('lift').value/100;
 let r0=2.25,r1=3.05;
 path(r=>outer(r)-lift,r0,r1,lift>0?'#f4cb85':'#b4e9da',8);
 if(lift>0){g.strokeStyle='#f9cf84';g.lineWidth=2;
 let centerR=(r0+r1)/2,yy=Y(centerR),a=X(outer(centerR)),b=X(outer(centerR)-lift);
 g.beginPath();g.moveTo(a,yy-12);g.lineTo(b,yy-12);g.stroke();
 g.beginPath();g.moveTo(b,yy-12);g.lineTo(b+8,yy-17);g.lineTo(b+8,yy-7);g.closePath();g.fillStyle='#f9cf84';g.fill();}
 g.fillStyle='#f5f7fb';g.font='12px system-ui';g.fillText('SPACE ←',10,19);g.textAlign='right';g.fillText('Cabin →',W-10,19);g.textAlign='left';
 g.fillStyle='#9cc8df';g.fillText('Inner pressure glass remains installed',16,H-9);
}
function updateStats(){
 const id=current(),o=D.areas[id],seam=E('seam').value,seat=E('seat').value,score=D.scores[id][seat],
 z=score.seam_width_mm[seam];
 const pairs=[
 ['Replaceable panels',o.panel_count],
 ['Smallest panel',o.smallest_panel_area_m2.toFixed(3)+' m²'],
 ['Largest panel',o.largest_panel_area_m2.toFixed(2)+' m²'],
 ['Heaviest protective panel',o.largest_panel_armor_mass_kg.toFixed(0)+' kg'],
 ['Exterior protective material', (o.total_surface_area_m2*.27).toFixed(2)+' t'],
 [seam+' mm opaque seam area',o.width_sensitivity[seam].seam_band_area_m2.toFixed(2)+' m²'],
 [seat+' baseline visible sky',(score.base_fraction*100).toFixed(2)+'%'],
 [seat+' with opaque seams',(z.forward_visible_fraction*100).toFixed(2)+'%'],
 ['Visibility lost to seams',z.lost_forward_percentage_points.toFixed(2)+' percentage points']
 ];
 E('stats').innerHTML=pairs.map(v=>'<div class="stat"><span>'+v[0]+'</span><b>'+v[1]+'</b></div>').join('');
 let area=chosen===null?null:o.panel_area_m2[chosen];
 E('picked').innerHTML=area===undefined||area===null?'<p class="note">Tap any panel to see the individual replacement module.</p>':
 '<div class="stat"><span>Selected panel ID</span><b>'+chosen+'</b></div>'+
 '<div class="stat"><span>Panel area</span><b>'+area.toFixed(3)+' m²</b></div>'+
 '<div class="stat"><span>Protective material</span><b class="gold">'+Math.round(area*270)+' kg</b></div>';
 E('liftval').textContent=E('lift').value+' cm';
}
function render(){renderTiles();renderSection();updateStats()}
E('tiles').addEventListener('click',e=>{
 const rect=c.getBoundingClientRect(),x=(e.clientX-rect.left)/rect.width*7-3.5,y=3.5-(e.clientY-rect.top)/rect.height*7;
 if(x*x+y*y>3.5*3.5)return;
 chosen=classify(x,y,D.presets[current()])[0];render();
});
for(let name of ['layout','seam','seat'])E(name).addEventListener('change',()=>{if(name==='layout')chosen=null;render()});
E('lift').addEventListener('input',()=>{renderSection();updateStats()});
addEventListener('resize',render);render();
</script></body></html>'''
out=ROOT/'render/out/nose_replaceable_outer_tile_viewer.html'
out.write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print(out,out.stat().st_size)
