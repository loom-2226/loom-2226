"""Replace near-identical minor variations with five different floorplan concepts.

Use the same source-based WebGL renderer and base ship. Default interior
view removes canopy occlusion; all held canopy layers remain switchable.
"""
import json,re,math,html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
source=HERE/'out/wayfarer_l1_500_search_five_3d_finalists.html'
J=json.loads((ROOT/'command/l1_distinct_layout_families_20261029_results.json').read_text())
families=[f['chosen'] for f in J['families']]
assert len(families)==5 and all(families)
src=source.read_text()
m=re.search(r'const DATA=(\{.*?\});\nconst G=DATA\.geo;let C=DATA\.cmd;',src,re.S)
assert m
data=json.loads(m.group(1))
data['designs']=[{'id':f['id'],'name':f['layout']['family_name'],
 'idea':f['layout']['family_idea'],'stand_style':f['layout']['stand_style'],
 'layout':f['layout'],'screens':f['screens'],
 'path':f['metrics']['path'],'sightline':f['metrics']['sightline'],
 'captain_to_stand_m':f['metrics']['captain_stand_distance_m'],
 'support_visibility':f['metrics']['mean_support_forward_fraction'],
 'selected_sample':f['selected_sample']} for f in families]
src=src[:m.start()]+'const DATA='+json.dumps(data,separators=(',',':'))+';\nconst G=DATA.geo;let C=DATA.cmd;'+src[m.end():]

def floorplan(f):
 c=105;k=20.5;out=['<svg viewBox="0 0 210 210" xmlns="http://www.w3.org/2000/svg">']
 out.append('<rect width="210" height="210" rx="8" fill="#0b1e2b"/>')
 for r,color in [(4.15,'#436679'),(3.5,'#579c9e')]:
  out.append(f'<circle cx="105" cy="105" r="{r*k:.1f}" fill="none" stroke="{color}" stroke-width="1.3" stroke-dasharray="3 3"/>')
 for y in (1.4,-1.4):
  x=c+k*y;out.append(f'<rect x="{x-7:.1f}" y="98" width="14" height="14" fill="#263443" stroke="#86a8bc" stroke-width="1"/>')
  out.append(f'<text x="{x:.1f}" y="108" fill="#c5d7e0" font-size="9" text-anchor="middle">L</text>')
 for st in f['layout']['seats']:
  q=st['center'];u=st['u'];v=st['side'];coords=[]
  for a,b in ((-.79,-.35),(.79,-.35),(.79,.35),(-.79,.35)):
   y=q[0]+a*u[0]+b*v[0];z=q[1]+a*u[1]+b*v[1]
   coords.append(f'{c+k*y:.1f},{c-k*z:.1f}')
  color='#e4c78f' if st['id'] in ('PILOT','NAV') else '#62c9b8'
  out.append(f'<polygon points="{" ".join(coords)}" fill="{color}" fill-opacity=".48" stroke="{color}" stroke-width="1.6"/>')
  x=c+k*q[0];y=c-k*q[1]
  out.append(f'<text x="{x:.1f}" y="{y+3:.1f}" fill="white" font-size="10" text-anchor="middle">{st["id"]}</text>')
 a=f['layout']['stand']['anchor_yz'];x=c+k*a[0];y=c-k*a[1]
 out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#224865" stroke="#f9a46a" stroke-width="2"/>')
 out.append(f'<text x="{x:.1f}" y="{y+3:.1f}" fill="white" text-anchor="middle" font-size="9">C</text>')
 return ''.join(out)+'</svg>'

start='<h2>Five computational finalists · select one</h2>'
end='<h2>Camera / views</h2>'
assert start in src
a=src.index(start);b=src.index(end,a)
cards=['<h2>FIVE DISTINCT L1 FLOORPLANS · SAME SHIP</h2>',
'<p class="note">Choose a genuinely different arrangement. All five diagrams share the same scale. Teal: support chairs · gold: Pilot/NAV · C: standing command · L: ladder.</p>',
'<div class="families">']
for i,f in enumerate(data['designs']):
 cards.append(f'<button class="family" data-variant="{i}" aria-pressed="{"true" if i==0 else "false"}">'
 f'<span class="family-name"><b>{html.escape(f["id"])}</b> · {html.escape(f["name"])}</span>'
 f'{floorplan(f)}<span class="family-detail">{html.escape(f["idea"])}</span></button>')
cards+=['</div>','<p class="note" id="variantInfo">Five independently tested floorplan families.</p>']
src=src[:a]+'\n'.join(cards)+'\n'+src[b:]

src=src.replace("const opts={view:'CUT',light:'clear',mech:'gel',outer:true,seams:true,pressure:true,gel:true,crew:true,sensors:true,rim:true,labels:true};",
"const opts={view:'CUT',light:'clear',mech:'gel',outer:false,seams:false,pressure:false,gel:false,crew:true,sensors:false,rim:false,labels:true};")
for element in ['outer','seams','pressure','gel','sensors','rim']:
 src=src.replace('type="checkbox" id="'+element+'" checked','type="checkbox" id="'+element+'"')
src=src.replace("cam={az:-2.65,el:.28,dist:11.7,tx:1.35,ty:0,tz:0}",
                "cam={az:-2.65,el:1.10,dist:10.2,tx:2.25,ty:0,tz:0}")
assert 'el:1.10' in src
p0=src.index("  document.getElementById('variantInfo').textContent=k.id+")
p1=src.index('  rebuild();',p0)
src=src[:p0]+"""  document.getElementById('variantInfo').textContent=
   k.id+' · '+k.name+' | '+k.idea+
   ' | Captain to standing '+k.captain_to_stand_m.toFixed(2)+'m'+
   ' | ideal support forward view '+Math.round(k.support_visibility*100)+'%'+
   ' | combined ladder-route proxy '+k.path.route_cost_m.toFixed(2)+'m'+
   ' | research geometry only';
  document.getElementById('viewname').textContent='L1 '+k.id+' · '+k.name;
""" +src[p1:]
src=src.replace('stand:k.layout.stand};','stand:k.layout.stand,stand_style:k.stand_style};')
needle="meshOBox(mb('l1_shared'),[2.05,y,z+.45],[[0,1,0],[0,0,1],[-1,0,0]],[.55,.27,.035]);"
assert needle in src
src=src.replace(needle,"""const hw=sc.stand_style==='wide'?.80:sc.stand_style==='compact'?.37:sc.stand_style==='linear'?.64:.55;
  meshOBox(mb('l1_shared'),[2.05,y,z+.45],[[0,1,0],[0,0,1],[-1,0,0]],[hw,.27,.035]);""")
anchor='</style></head><body>'
src=src.replace(anchor,''' .families{display:flex;gap:10px;overflow-x:auto;padding:4px 0 12px;scroll-snap-type:x mandatory}
.family{scroll-snap-align:start;flex:0 0 185px;min-width:185px;border-radius:9px;border:1px solid #3d6677;background:#102438;color:#e5f1f5;padding:7px;cursor:pointer;text-align:left;font:12px system-ui;display:flex;flex-direction:column;gap:5px}
.family[aria-pressed="true"]{border:3px solid #83e9df;background:#1b4351;padding:5px}
.family svg{width:100%;aspect-ratio:1}
.family-name{font-size:11px;min-height:30px;display:block}
.family-detail{color:#afc8d8;font-size:10px;line-height:1.3}
.family:hover{background:#1a3b4c}
 '''+anchor)
src=src.replace('500→20→5 crew-function design search · five 3D finalists',
                'Five distinct L1 floorplan families · corrected comparison')
src=src.replace('crew positions from search; ship shell from source Rev 7',
                'five distinct floorplan concepts; ship shell from source Rev 7')
# Do not clip the whole floor in the default interior-only view.
src=src.replace("clip:opts.view==='CUT'?[0,-1,0,-.23]:null,",
 "clip:opts.view==='CUT'&&(opts.outer||opts.pressure||opts.rim)?[0,-1,0,-.23]:null,")
out=HERE/'out/wayfarer_l1_five_distinct_layouts_corrected.html'
out.write_text(src)
print('OUTPUT',out,'bytes',out.stat().st_size)
print('FAMILIES',[(k['id'],k['name'],k['path']['route_cost_m']) for k in data['designs']])