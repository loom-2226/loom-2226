"""Three visibly different fully-furnished Wayfarer L1 concept interiors.

Builds on Android-safe Canvas2D (no WebGL) and actual six-role F1-R2
source positions. Floors, connected tier paths, lighting, storage, 
workstations, wall/canopy context are rendered as lightweight meshes.
No hull/4g/egress certification or canon changes.
"""
import re,copy,json,math,html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
old=json.loads((ROOT/"command/L1_PAIRED_PILOT_CAPTAIN_STANDALONE_WORKAREA_20261029.json").read_text())['concepts'][0]
base=(HERE/'make_l1_canvas2d_android_viewer.py').read_text()
t=re.search(r"page=r'''(.*?)'''",base,re.S)
assert t,"Original viewer template missing"
page=t.group(1)
def box(y,z,height,wy,wz,th=.10,color="#364f61",opacity=1):
 return dict(y=y,z=z,height=height,wy=wy,wz=wz,th=th,color=color,opacity=opacity)
def line(a,b,color="#7bc5c8",radius=.018):
 return dict(a=a,b=b,color=color,radius=radius)
def seat_move(v,id,y,z,base_x,heading=0):
 s=next(s for s in v['layout']['seats'] if s['id']==id)
 a=math.radians(heading);u=(math.sin(a),-math.cos(a));L=1.58
 h=(y-L/2*u[0],z-L/2*u[1]);feet=(y+L/2*u[0],z+L/2*u[1])
 s.update(center_yz=[y,z],heading_deg=heading,base_x=base_x,
    head=[round(x,4) for x in h],feet=[round(x,4) for x in feet],
    eye=[base_x-.45,h[0]+.2*u[0],h[1]+.2*u[1]])
def rebuild_displays(v):
 screens=[]
 for s in v['layout']['seats']:
  a=math.radians(35)
  if s['id'] in ('PILOT','NAV','S1'):a=math.radians(38)
  u=(math.sin(math.radians(s['heading_deg'])),-math.cos(math.radians(s['heading_deg'])))
  dr=(-math.cos(a),u[0]*math.sin(a),u[1]*math.sin(a))
  e=s['eye'];screens.append(dict(for_station=s['id'],
    center_xyz=[round(e[k]+.60*dr[k],4) for k in range(3)],
    half_width_m=.22,half_height_m=.14,angle_deg=math.degrees(a)))
 v['screens']=screens
def decorate(v,id,name,idea,benefit,risk,blocks,rails,consoles,lights,connectors):
 v['id']=id;v['name']=name;v['idea']=idea;v['advantage']=benefit;v['tradeoff']=risk
 v['interior']={'blocks':blocks,'rails':rails,'consoles':consoles,'lights':lights,
               'connectors':connectors}
 v['layout']['platforms']=[]
 rebuild_displays(v)
 return v
# Height = 4 - seat.base_x, base deck ~0.65m. All dimensions illustrative.
A=copy.deepcopy(old)
# Big connected working deck with two distinct elevated flight terraces.
aB=[
 box(0,-.70,.66,8.15,8.2,.16,"#344c63"),
 box(0,2.20,1.22,2.65,2.70,.16,"#42596e"),
 box(0,-.38,2.09,2.95,2.85,.17,"#4c6074"),
 # more usable side and aft built-in cabinetry
 box(-3.83,-1.30,1.02,.37,3.60,.69,"#455969"),
 box(3.83,-.80,1.02,.37,3.35,.69,"#455969"),
 box(-1.0,-4.32,1.06,1.42,.38,.77,"#455969"),
 # team status wall and compact central briefing table on rear operation floor
 box(0,-2.05,1.07,1.28,.58,.13,"#37758a"),
 box(0,-2.47,1.40,1.24,.09,.55,"#2d8492"),
]
aRail=[
 line([-1.52,-1.77,2.18],[-1.52,.72,2.18],"#83d9d2"),
 line([1.52,-1.77,2.18],[1.52,.72,2.18],"#83d9d2"),
 line([-1.44,1.10,1.33],[-1.44,3.03,1.33],"#82d4dc"),
 line([1.44,1.10,1.33],[1.44,3.03,1.33],"#82d4dc"),
 line([-3.54,-4.25,.79],[3.54,-4.25,.79],"#61a6bc")
]
aLight=[
 line([-3.73,-3.85,.84],[-3.73,2.62,.84],"#68a8aa",.023),
 line([3.73,-3.85,.84],[3.73,2.62,.84],"#68a8aa",.023),
 line([-1.25,.68,2.27],[1.25,.68,2.27],"#f0bf78",.027),
 line([-1.1,3.28,1.41],[1.1,3.28,1.41],"#86d3de",.026)
]
aConnect=[
 dict(start=[-.72,-1.95,.78],end=[-.72,-1.64,2.04],width=.44),
 dict(start=[.72,-1.95,.78],end=[.72,-1.64,2.04],width=.44),
 dict(start=[-.75,3.16,.78],end=[-.75,3.00,1.18],width=.44)
]
A=decorate(A,"L1-I1","Unified Terraced Commons",
 "One continuous lower operating deck connects specialist stations and a separate mission workshop; a compact two-person raised command tier faces the forward Navigator.",
 "Clear circulation and a command pair who can oversee the room",
 "The raised Captain/Pilot tier needs an accessible low-g/high-g transition design",
 aB,aRail,[dict(label="SHARED SHIP STATUS",pos=[0,-2.45,1.72],color="#77d4d3")],
 aLight,aConnect)
B=copy.deepcopy(old)
# Real alternative: narrow central corridor and split work galleries; relatively
# dense command service spine, physically different floor footprint.
seat_move(B,'S2',-3.10,-1.48,3.29,-12)
seat_move(B,'S3',3.10,-1.48,3.29,12)
seat_move(B,'S4',2.75,-3.25,3.30,12)
B['layout']['stand']['anchor_yz']=[0,-1.57]
B['layout']['stand']['eye_xyz']=[2.12,0,-1.57]
B['layout']['work_area']['anchor_yz']=[-2.37,-3.42]
bB=[
 box(0,-.47,.71,2.40,7.95,.14,"#39576a"), # middle spine
 box(-2.90,-1.14,.71,2.37,7.50,.15,"#3e586d"),
 box(2.90,-1.14,.71,2.37,7.50,.15,"#3e586d"),
 box(0,-.34,2.11,2.89,2.9,.16,"#455d75"), # paired command bridge
 box(0,2.3,1.24,2.75,2.76,.16,"#435c72"),
 # independent gallery work surfaces against perimeter
 box(-3.88,-2.20,1.16,.30,2.6,.88,"#4a6072"),
 box(3.88,-1.92,1.16,.30,3.02,.88,"#4a6072"),
 box(0,-3.40,.99,1.82,.33,.52,"#486073"),
 box(-2.4,-3.64,1.05,1.77,.51,.62,"#6b5974"),
 # tall (but thin) holographic status wall separating gallery from spine
 box(0,-2.75,1.35,1.15,.10,.92,"#1e6579",.58)
]
bRail=[
 line([-1.25,-4.18,.89],[-1.25,2.45,.89],"#90d1d1"),
 line([1.25,-4.18,.89],[1.25,2.45,.89],"#90d1d1"),
 line([-1.50,-1.78,2.18],[-1.50,.9,2.18],"#e5bb73"),
 line([1.50,-1.78,2.18],[1.50,.9,2.18],"#e5bb73")
]
bLight=[
 line([-1.09,-3.8,.91],[-1.09,2.8,.91],"#5dc8dd",.024),
 line([1.09,-3.8,.91],[1.09,2.8,.91],"#5dc8dd",.024),
 line([-3.92,-3.55,.83],[-3.92,1.6,.83],"#4ea4b6",.019),
 line([3.92,-3.55,.83],[3.92,1.6,.83],"#4ea4b6",.019)
]
bConnect=[
 dict(start=[-.9,-1.90,.83],end=[-.9,-1.40,2.04],width=.38),
 dict(start=[.9,-1.90,.83],end=[.9,-1.40,2.04],width=.38),
 dict(start=[0,3.25,.81],end=[0,3.11,1.21],width=.5)
]
B=decorate(B,"L1-I2","Central Command Spine",
 "A narrow instrumented command corridor runs between two specialist galleries. The raised Pilot/Captain overlook the common status wall while Navigator occupies the bow station.",
 "Clear organization of ship functions and a strong information spine",
 "More bulkheads and equipment may compete with panorama and informal collaboration",
 bB,bRail,[dict(label="STATUS SPINE",pos=[0,-2.9,2.02],color="#8ae8f0")],
 bLight,bConnect)
C=copy.deepcopy(old)
# observation-oriented arc, large continuous U-shaped work deck, free central
# gathering area and a dedicated aft sheltered mission alcove
seat_move(C,"PILOT",-.99,-.18,1.92,-8)
seat_move(C,"S1",.99,-.18,1.92,8)
seat_move(C,"NAV",0,2.55,2.83,0)
seat_move(C,"S2",-3.12,-.38,3.32,-32)
seat_move(C,"S3",3.12,-.38,3.32,32)
seat_move(C,"S4",2.20,-3.18,3.32,24)
C['layout']['stand']['anchor_yz']=[0,-1.38]
C['layout']['stand']['eye_xyz']=[2.22,0,-1.38]
C['layout']['work_area']['anchor_yz']=[-2.1,-3.30]
cB=[
 box(0,-.65,.67,8.25,8.15,.17,"#34505e"), # broad commons deck
 box(0,-.10,2.07,3.38,3.12,.14,"#566978"), # two-seat panoramic command
 box(0,2.44,1.17,2.55,2.95,.15,"#496c76"), # bowed Navigator platform
 box(-3.90,-.35,1.03,.34,3.24,.63,"#486c71"),
 box(3.90,-.35,1.03,.34,3.24,.63,"#486c71"),
 box(-2.00,-3.70,1.00,2.8,.46,.63,"#617477"), # service alcove
 box(2.15,-3.78,1.03,2.6,.40,.69,"#567174"),
 box(0,-2.08,1.02,1.10,.70,.13,"#467c78"), # shared physical map table
]
cRail=[
 line([-3.54,.70,1.16],[-2.10,2.45,1.16],"#77d8c8"),
 line([3.54,.70,1.16],[2.10,2.45,1.16],"#77d8c8"),
 line([-1.78,-1.43,2.21],[-1.78,1.32,2.21],"#edbd89"),
 line([1.78,-1.43,2.21],[1.78,1.32,2.21],"#edbd89")
]
cLight=[
 line([-3.70,-3.72,.85],[-3.70,.48,.85],"#73d4c4",.025),
 line([3.70,-3.72,.85],[3.70,.48,.85],"#73d4c4",.025),
 line([-1.60,1.43,2.22],[1.60,1.43,2.22],"#f6d6a0",.032),
 line([-1.10,3.82,1.34],[1.10,3.82,1.34],"#9cdbdc",.025)
]
cConnect=[
 dict(start=[-.9,-1.95,.82],end=[-.9,-1.60,2.0],width=.50),
 dict(start=[.9,-1.95,.82],end=[.9,-1.60,2.0],width=.50),
 dict(start=[0,3.60,.82],end=[0,3.45,1.12],width=.5)
]
C=decorate(C,"L1-I3","Panoramic Observation Commons",
 "An open observation-oriented command room with a wide front terrace, peripheral specialist alcoves, communal map table and a secluded mission-work bay.",
 "Crew habitability and exterior awareness without six isolated consoles",
 "More open space may require careful restraint placement during thrust and emergencies",
 cB,cRail,[dict(label="SHARED MISSION MAP",pos=[0,-2.10,1.39],color="#a0efdf")],
 cLight,cConnect)
designs=[A,B,C]
for d in designs:
 assert len(d['layout']['seats'])==6 and d['layout']['work_area']
 assert {s['id'] for s in d['layout']['seats']}=={"PILOT","NAV","S1","S2","S3","S4"}
 assert len(d['interior']['blocks'])>=7 and len(d['interior']['rails'])>=4
 assert len(d['screens'])==6 and d['interior']['connectors']
 # Note: support pillars and paths are concept geometry, not qualified clearances.
out_json=ROOT/'command/L1_THREE_COMPLETE_INTERIOR_CONCEPTS_20261029.json'
out_json.write_text(json.dumps({"classification":"RESEARCH NON-CANON NON-RUNTIME","derived_from":"F1-R2 paired Pilot/Captain design","concepts":designs,"limitations":["Illustrative floors, tier connectors, cabinets, handrails, lighting and screens. Not an engineered builtable pressure hull.","No continuous accessible 3D human transit path or 4g seat/structural load certification","No actual ergonomic or sensor-field-of-view test","Independent workbench is a low-g station, not an acceleration seat"]},indent=2))
page=page.replace("const designs=__DATA__", "const designs=__DATA__")
# Replace in-page controls with 3 choices and more relevant descriptions
page=page.replace("<button data-design=\"0\" aria-pressed=\"true\">NEW · Pilot + Captain raised</button>\n<button data-design=\"1\" aria-pressed=\"false\">OLD · Original F1</button>",
 """<button data-design="0" aria-pressed="true">I1 · Terraced Commons</button>
<button data-design="1" aria-pressed="false">I2 · Command Spine</button>
<button data-design="2" aria-pressed="false">I3 · Observation Commons</button>""")
page=page.replace("Compare the two designs","Three fully furnished interior iterations")
page=page.replace("Pilot and Captain together on the elevated command tier, Navigator forward and lower. The former S4 position becomes a separate workbench.",
 "A connected terraced crew environment with raised Pilot/Captain, forward Navigator and an independent mission bay.")
page=page.replace("F1-R2 · Paired command","L1-I1 · Unified Terraced Commons")
page=page.replace("Android-friendly Canvas renderer · no WebGL required · non-canon research",
 "Three complete interior studies · phone-safe 3D · no WebGL · research only")
page=page.replace("WAYFARER · L1 COMMAND DECK","WAYFARER · L1 INTERIOR STUDIES")
page=page.replace("const state={variant:0,yaw:-0.70,pitch:0.60,zoom:.79,panx:0,pany:0,", 
                  "const state={variant:0,yaw:-0.73,pitch:0.66,zoom:.76,panx:0,pany:0,")
page=page.replace("if(mode===\"orbit\"){state.yaw=-.70;state.pitch=.60}","if(mode===\"orbit\"){state.yaw=-.73;state.pitch=.66}")
page=page.replace("state.zoom=.79;state.panx=state.pany=0;","state.zoom=.76;state.panx=state.pany=0;")
page=page.replace("rect={w:a.width,h:a.height,scale:Math.min(a.width/9.8,a.height/8.5)};",
                  "rect={w:a.width,h:a.height,scale:Math.min(a.width/11.0,a.height/9.8)};")
# Expand info: optional layer architecture on/off tied to 'floors' existing.
# replace floor block in build() from base, preserving remaining.
beg=page.index(" if(state.floors){\n  for(const f of layout.platforms||[]){")
end=page.index(" for(const seat of layout.seats){",beg)
block=r''' if(state.floors){
  const I=design.interior;
  // Continuous, individually authored work decks and built-in cabinetry.
  for(const b of I.blocks){
    box(b.y,b.z,b.height,b.wy,b.wz,b.th,b.color,b.opacity??1);
    // Thin subtle luminous floor stripe for large slabs, visually conveys levels
    if(b.wy>2.2&&b.wz>2.2){
      const top=b.height+b.th/2+.012;
      const l=Math.min(2,b.wy/2-.18);
      segment([b.y-l,b.z-b.wz/2+.18,top],[b.y+l,b.z-b.wz/2+.18,top],.014,"#568d98");
    }
  }
  // Bridge-like low-g access connectors: visible sloping surfaces between tiers.
  // Not measured safe walkways or validated high-g access.
  for(const r of I.connectors){
    const a=r.start,b=r.end,w=r.width||.45;
    polygon([[a[0]-w/2,a[1],a[2]],[a[0]+w/2,a[1],a[2]],
             [b[0]+w/2,b[1],b[2]],[b[0]-w/2,b[1],b[2]]],"#46687c",.98);
    segment([a[0]-w/2,a[1],a[2]+.20],[b[0]-w/2,b[1],b[2]+.20],.019,"#9ac2c7");
    segment([a[0]+w/2,a[1],a[2]+.20],[b[0]+w/2,b[1],b[2]+.20],.019,"#9ac2c7");
  }
  for(const l of I.rails)segment(l.a,l.b,l.radius,l.color);
  for(const l of I.lights)segment(l.a,l.b,l.radius,l.color);
  if(state.screens){
    for(const c of I.consoles){
      const q=c.pos;
      box(q[0],q[1],q[2],1.12,.06,.38,"#3e90a1",.82);
      label([q[0],q[1],q[2]+.30],c.label,c.color);
    }
  }
 }
'''
page=page[:beg]+block+page[end:]
# Fix previous message line and explanatory notes.
page=page.replace('RENDERED · "+designs[state.variant].id+" · 6 acceleration seats"',
                  'RENDERED · "+designs[state.variant].id+" · connected interior concept · 6 acceleration seats"')
page=page.replace("This is a software-rendered, freely arranged concept. It does not certify pressure-hull fit, acceleration tolerance, safe egress, screen ergonomics or crew performance.",
"""The three designs share the raised Pilot/Captain pair, separate Navigator, specialists and independent mission workbench. The floors, cabinets, handrails, connecting decks and shared consoles are authored concept geometry, not yet fitted to the source pressure hull. No acceleration or egress qualification is claimed.""")
page=page.replace("state.variant=n;for(const b of document.querySelectorAll(\"[data-design]\"))",
 "state.variant=n;for(const b of document.querySelectorAll(\"[data-design]\"))")
# Intro for each iteration via idea, include benefit/tradeoff in an element.
page=page.replace('<p id="description">','<p id="description">',1)
page=page.replace('document.getElementById("description").textContent=v.idea;',
 'document.getElementById("description").textContent=v.idea+" Advantage: "+v.advantage+". Trade-off: "+v.tradeoff+".";')
# don't embed previous preview as fallback; new rendered image will be written by screenshot test and generator rerun.
page=page.replace('<img id="static" alt="Static fallback rendering of the paired Pilot-Captain command deck"',
                  '<img id="static" alt="Static fallback rendering of the fully furnished L1"')
preview=HERE/'out/l1_three_interiors_preview.png'
from base64 import b64encode
fallback=("data:image/png;base64,"+b64encode(preview.read_bytes()).decode('ascii')) if preview.exists() else (
"data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20400%20400%22%3E%3Crect%20width%3D%22400%22%20height%3D%22400%22%20fill%3D%22%230b2336%22/%3E%3Ctext%20x%3D%22200%22%20y%3D%22200%22%20fill%3D%22white%22%20text-anchor%3D%22middle%22%3EStatic%20preview%20unavailable%3C/text%3E%3C/svg%3E")
out=HERE/'out/wayfarer_l1_three_furnished_interiors_android.html'
out.write_text(page.replace("__DATA__",json.dumps(designs,separators=(',',':'))).replace("__FALLBACK__",fallback))
print('OUTPUT',out,out.stat().st_size,'DATA',out_json)
for d in designs: print(d['id'],d['name'],len(d['interior']['blocks']),'physical room elements')