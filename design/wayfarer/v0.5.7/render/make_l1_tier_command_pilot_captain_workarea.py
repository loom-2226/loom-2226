"""LOOM L1 F1 revision: raised Pilot + Captain pair, lower Navigator, former S4 spot -> standalone task bench.

Single deliberately authored concept. Original F1 retained as second button.
No source geometry/hull fit imposed; six seats preserved, no canon mutation.
"""
import json,copy,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
base=HERE/'out/wayfarer_l1_eight_unconstrained_3d.html'
data_src=json.loads((ROOT/'command/L1_EIGHT_FREEFORM_2226_CONCEPTS_20261029.json').read_text())
old=copy.deepcopy(data_src['designs'][0])
L=1.58
def station(s,y,z,x,a):
 rad=math.radians(a);u=[math.sin(rad),-math.cos(rad)]
 h=[y-.5*L*u[0],z-.5*L*u[1]]
 f=[y+.5*L*u[0],z+.5*L*u[1]]
 s.update(center_yz=[y,z],base_x=x,heading_deg=a,
          head=[round(v,3) for v in h],feet=[round(v,3) for v in f],
          eye=[round(x-.45,3),round(h[0]+.2*u[0],3),round(h[1]+.2*u[1],3)])
def display(s):
 ang=math.radians(38 if s['id'] in ('PILOT','NAV') else 35)
 hd=math.radians(s['heading_deg'])
 u=[math.sin(hd),-math.cos(hd)]
 dr=[-math.cos(ang),u[0]*math.sin(ang),u[1]*math.sin(ang)]
 e=s['eye'];p=[round(e[i]+.60*dr[i],4) for i in range(3)]
 return dict(for_station=s['id'],center_xyz=p,half_width_m=.22,
             half_height_m=.14,angle_deg=math.degrees(ang))
new=copy.deepcopy(old)
new['id']='F1-R2';new['name']='Pilot + Commander raised together'
new['idea']='Raised Pilot and Captain share one compact command tier; Navigator works forward and lower. Former S4 site is a separate standing mission workbench.'
new['advantage']='Pilot/Commander side-by-side supervision plus a real specialist work area'
new['tradeoff']='Navigator separated from Pilot; requires verified crew communications and transitions between tiers'
# Ship X increasing toward stern (down), so lower X is forward/raised in this
# conceptual -X view. Relative "elevation" remains tied to illustrative axial
# tiers, not a claim about arbitrary acceleration/gravity.
pos={
 'PILOT':(-.87,-.40,1.89,0),
 'NAV':(0,2.10,2.76,0),
 'S1':(.87,-.40,1.89,0),
 'S2':(-2.55,-1.30,3.29,-38),
 'S3':(2.55,-1.30,3.29,38),
 'S4':(2.60,-3.55,3.32,25)
}
for s in new['layout']['seats']:station(s,*pos[s['id']])
new['screens']=[display(s) for s in new['layout']['seats']]
new['layout']['stand']={
 'eye_xyz':[2.12,0,-1.36],'floor_x':2.75,'anchor_yz':[0,-1.36],
 'foot_restraints':True,'handholds':True,'low_g_only':True}
new['layout']['platforms']=[
 {'x':2.91,'y':0,'z':2.05,'wy':2.25,'wz':2.70}, # Navigator low forward
 {'x':2.02,'y':0,'z':-.48,'wy':2.75,'wz':2.42}, # two-person command raised
 {'x':3.39,'y':-2.30,'z':-1.45,'wy':2.55,'wz':4.30}, # engineering
 {'x':3.39,'y':2.55,'z':-2.00,'wy':2.85,'wz':5.05}, # sensors & MOPS
 {'x':3.39,'y':0,'z':-3.15,'wy':2.45,'wz':1.90}, # dedicated old-S4 workspace
]
new['layout']['work_area']={
 'label':'Independent mission operations workbench',
 'floor_x':3.39,'anchor_yz':[0,-3.0],
 'purpose':'Crew standing/anchored console, robotics/EVA/survey planning or equipment work; NOT seventh 4g seat',
 'foot_restraints':True,'handholds':True,'local_display':True,'surface_width_m':1.35}
new['levels']=len({s['base_x'] for s in new['layout']['seats']})
new['role_centres']={s['role']:s['center_yz'] for s in new['layout']['seats']}
old['id']='F1-ORIGINAL'
old['name']='Previous tiered command'
old['advantage']='Pilot and NAV together with Captain separate and raised'
old['tradeoff']='Mission seat occupies the location now proposed as a separate workbench'
old['idea']='Earlier tiered layout retained for direct before/after comparison.'
# All roles and seating remain, mission seat moved away from former S4 site.
assert len(new['layout']['seats'])==6
assert {s['id'] for s in new['layout']['seats']}=={'PILOT','NAV','S1','S2','S3','S4'}
assert new['layout']['seats'][0]['base_x']==new['layout']['seats'][2]['base_x']<new['layout']['seats'][1]['base_x']
assert new['layout']['seats'][5]['center_yz']!=old['layout']['seats'][5]['center_yz']
# Keep narrative separate from authoritative data.
result={'classification':'RESEARCH NON-CANON NON-RUNTIME; NO HULL/THRUST/SEAT QUALIFICATION',
        'change':'F1 Pilot and Captain paired on raised tier, NAV lower/forward; former S4 site becomes a real anchored mission workbench; S4 retains a separate acceleration seat.',
        'concepts':[new,old],
        'unresolved':['4g body loads and load paths','actual raised/lower relative ship thrust orientation','Navigator/Pilot handoff','pressure vessel fit','safe transfer paths and ladder access','screen/crew sightlines'],
        'selected_by_user':'F1 revised paired Pilot and Captain raised; former S4 standalone work area'}
data_path=ROOT/'command/L1_PAIRED_PILOT_CAPTAIN_STANDALONE_WORKAREA_20261029.json'
data_path.write_text(json.dumps(result,indent=2))
# Existing fully self-contained WebGL file contains all renderer logic. Replace
# only authored data, two layout buttons and add one separate physical workbench.
src=base.read_text()
m=re.search(r'const DATA=(\{.*?\});\nconst G=DATA\.geo;let C=DATA\.cmd;',src,re.S)
assert m
data=json.loads(m.group(1));data['designs']=[new,old]
src=src[:m.start()]+'const DATA='+json.dumps(data,separators=(',',':'))+';\nconst G=DATA.geo;let C=DATA.cmd;'+src[m.end():]
# Header labels and concept cards.
src=src.replace('EIGHT UNCONSTRAINED COMMAND-DECK CONCEPTS','TIERED COMMAND · PILOT + COMMANDER PAIRED')
# Frame the whole new tiered concept instead of clipping the specialist wing.
src=src.replace('let dirty=true,first=true;','let dirty=true,first=false;')
src=src.replace('el:1.10,dist:10.2,tx:2.25,ty:0,tz:0','el:1.12,dist:14.3,tx:2.30,ty:0,tz:-.50')
src=src.replace('EIGHT FREEFORM COMMAND-DECK CONCEPTS','PAIRED COMMAND · TWO 3D VERSIONS')
src=src.replace('Eight different L1 command architectures · no fixed interior',
                'F1 · paired Pilot + Captain elevated, separate mission work area')
src=src.replace('Only the six functions and proper acceleration work seats are retained. NO hull, existing ladder, deck or crown fit constraints. All floorplans use the same scale; small numbers in chairs are their X-tier levels. C is a proposed anchored command workpoint.',
'''Revised concept keeps all six acceleration seats. Pilot and Commander are paired on the raised tier;
Navigator stays forward/lower. The former S4 position becomes a standalone anchored workbench
(marked W). S4 Mission Operations' acceleration seat is relocated. Compare new and old 3D layouts.''')
s=src.index('<div class="families">');e=src.index('</div><p class="note" id="variantInfo">',s)
# Use compact two comparative cards, separate clear role labels.
def plan(k):
 scale=21.;c=110;arr=['<svg viewBox="0 0 224 224" xmlns="http://www.w3.org/2000/svg"><rect width="224" height="224" rx="8" fill="#0b1d2b"/>']
 for st in k['layout']['seats']:
  y,z=st['center_yz'];ang=math.radians(st['heading_deg'])
  u=[math.sin(ang),-math.cos(ang)];v=[-u[1],u[0]]
  co=[]
  for a,b in [(-.79,-.35),(.79,-.35),(.79,.35),(-.79,.35)]:
   yy=y+u[0]*a+v[0]*b;zz=z+u[1]*a+v[1]*b;co.append(f'{c+scale*yy:.1f},{c-scale*zz:.1f}')
  fill='#f0c27c' if st['id'] in ('PILOT','S1') else '#85d5e9' if st['id']=='NAV' else '#91baab'
  text='CAPT' if st['id']=='S1' else ('MOPS' if st['id']=='S4' else st['id'])
  arr.append(f'<polygon points="{" ".join(co)}" fill="{fill}" fill-opacity=".52" stroke="{fill}" stroke-width="2"/>')
  arr.append(f'<text x="{c+scale*y:.1f}" y="{c-scale*z+3:.1f}" text-anchor="middle" fill="#f6fffd" font-size="9">{text}</text>')
 if k['layout'].get('work_area'):
  w=k['layout']['work_area'];y,z=w['anchor_yz']
  arr.append(f'<rect x="{c+scale*y-13:.1f}" y="{c-scale*z-9:.1f}" width="26" height="18" rx="2" fill="#6a3765" stroke="#ffb9ea" stroke-width="2"/>')
  arr.append(f'<text x="{c+scale*y:.1f}" y="{c-scale*z+3:.1f}" text-anchor="middle" fill="white" font-size="12">W</text>')
 arr.append('</svg>');return ''.join(arr)
cards=['<div class="families">']
for i,k in enumerate((new,old)):
 cards.append(f'<button class="family" data-variant="{i}" aria-pressed="{"true" if i==0 else "false"}">'
  f'<span class="family-name"><b>{k["id"]}</b> · {k["name"]}</span>{plan(k)}'
  f'<span class="family-detail">{k["idea"]}</span></button>')
cards.append('')
src=src[:s]+'\n'.join(cards)+src[e:]
# Need role labels in top-down 3D, not S1.
src=src.replace("b.textContent=c.id;", "b.textContent=({S1:'CAPTAIN',S4:'MISSION OPS'}[c.id]||c.id);")
# Add standalone mission work area distinct from the command standing console.
pos=src.index(' if(sc.stand){',src.index('function commandMeshes(sc,opt={})'))
work_js=r'''
 if(sc.work_area){
   const wa=sc.work_area,[y,z]=wa.anchor_yz,floor=wa.floor_x;
   // Non-seat specialist workstation. A physical work surface, independent
   // display, two handgrips, equipment lockers and anchored foot positions.
   const A=[[1,0,0],[0,1,0],[0,0,1]];
   meshOBox(mb('l1_seat_shell'),[floor-.43,y,z],A,[.070,.72,.35]);
   meshOBox(mb('l1_control'),[floor-.53,y,z+.23],A,[.025,.62,.21]);
   meshOBox(mb('l1_shared'),[floor-.85,y,z+.35],[[0,1,0],[0,0,1],[-1,0,0]],[.64,.27,.029]);
   for(const dy of [-.75,.75]){
     meshOBox(mb('equipment'),[floor-.18,y+dy,z-.20],A,[.11,.12,.25]);
     meshTube(mb('rail'),{p0:[floor-.52,y+dy,z+.03],p1:[floor-.89,y+dy,z+.22],r:.027},9);
   }
   for(const dy of [-.21,.21])
     meshOBox(mb('l1_harness'),[floor+.014,y+dy,z],A,[.028,.11,.13]);
 }
'''
src=src[:pos]+work_js+src[pos:]
src=src.replace('stand:k.layout.stand,stand_style:"wide",platforms:k.layout.platforms,',
                'stand:k.layout.stand,work_area:k.layout.work_area||null,stand_style:"wide",platforms:k.layout.platforms,')
# Distinguish the workbench with overlay label.
needle=" for(let c of C.couches){\n  const a=ship.project("
idx=src.find(needle)
assert idx>=0
work_label=""" if(C.work_area){
   const w=C.work_area,xyz=[w.floor_x-.8,...w.anchor_yz],
    a=ship.project(...xyz),rect=canvas.getBoundingClientRect();
   if(a[2]&&a[0]>10&&a[1]>10&&a[0]<rect.width-10&&a[1]<rect.height-10){
     const b=document.createElement('span');b.className='label3d';
     b.textContent='INDEPENDENT WORK AREA';
     b.style.cssText='position:absolute;pointer-events:none;left:'+a[0]+'px;top:'+a[1]+'px;transform:translate(-50%,-150%);font-size:10px;color:#ffd2ee;background:#3d2343dd;border:1px solid #d98bd0;border-radius:5px;padding:4px 6px';
     stage.appendChild(b);
   }
 }
"""
src=src[:idx]+work_label+src[idx:]
src=src.replace('The prior L1 structure is intentionally omitted.','The prior L1 structure is intentionally omitted.')
src=src.replace('eight unrestricted floorplan concepts','two tier-command variants')
src=src.replace('eight different floorplan concepts','paired-command and prior-command variants')
src=src.replace('EIGHT FREEFORM COMMAND-DECK CONCEPTS','TIERED COMMAND · TWO VERSIONS')
src=src.replace('Research reference only','Reference only')
src=src.replace('All seats, decks and standing workpoints are newly authored freeform concepts;','All seats, decks and standing workpoints are newly authored research concepts;')
# Inform user there is no actual mass/hull acceptance.
src=src.replace('View actual L1 components','View concept components')
assert "work_area:k.layout.work_area" in src
assert "INDEPENDENT WORK AREA" in src
assert "redraw();\n  requestAnimationFrame" in src
out=HERE/'out/wayfarer_l1_pilot_captain_raised_mission_workarea.html'
out.write_text(src)
print('VIEWER',out,out.stat().st_size,'bytes')
print('DATA',data_path,data_path.stat().st_size,'bytes')