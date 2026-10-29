"""LOOM L1 freeform exploration: eight separate concept topologies, no Rev7 fit gates.

Only six role-specific contoured acceleration seats are mandatory.
Author physical 3D platforms, stations, local screens and optional shared
standing work area. Existing hull, bow sensors, ladders and canopy may be
shown only as context after concept selection, never used to exclude layouts.

Generate a self-contained WebGL viewer by reusing existing LOOM renderer.
"""
from pathlib import Path
import re,math,json,html,collections
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TEMPLATE=(HERE/'out/wayfarer_l1_five_distinct_layouts_corrected.html').read_text()
L=1.58
ROLE_NAMES={'PILOT':'Flight','NAV':'Navigation / Loom','S1':'Captain / command',
            'S2':'Engineering','S3':'Sensors / EW','S4':'Mission operations'}
# A seat: (Y, Z, X of rear seat support, YZ heading clockwise from -Z in degrees)
# Spacecraft axial X: more negative = farther bowward; YZ is the transverse plan.
# Distinguish X elevation/fore-aft explicitly from YZ "behind", a human
# plan-view relationship; no attempt to canonize a gravity-frame orientation.
def seat(key,y,z,x,deg):
 a=math.radians(deg);u=(math.sin(a),-math.cos(a))
 h=(y-L/2*u[0],z-L/2*u[1]);f=(y+L/2*u[0],z+L/2*u[1])
 eye=[round(x-.45,3),round(h[0]+.20*u[0],3),round(h[1]+.20*u[1],3)]
 return {'id':key,'role':ROLE_NAMES[key],'base_x':x,
   'head':[round(v,3) for v in h],'feet':[round(v,3) for v in f],
   'eye':eye,'L':L,'width':.7,'heading_deg':deg,
   'center_yz':[y,z]}
# (X,Y,Z,widthY,widthZ) for actual visible tier slabs
def slab(x,y,z,wy,wz):return {'x':x,'y':y,'z':z,'wy':wy,'wz':wz}
# initial, deliberate radical concepts. No Rev7 bounds.
D=[
 dict(id='F1',name='Tiered command',
   idea='Pilot and Navigator forward/lower, Captain centred behind and raised; 3 supporting mission stations.',
   main='Command supervision and external view',weak='Raised Captain could lose screen sightlines; tier access remains unresolved',
   positions=[(-.83,1.62,2.75,0),(.83,1.62,2.75,0),(0,-.63,1.88,0),(-2.55,-1.15,3.28,-38),(2.55,-1.15,3.28,38),(0,-3.0,3.28,0)],
   stand=[0,-1.45,2.50],surface='stepped trio',
   platforms=[slab(2.84,0,1.65,2.65,2.8),slab(1.98,0,-.75,1.55,2.25),
              slab(3.34,-1.85,-1.35,2.6,3.4),slab(3.34,1.85,-1.35,2.6,3.4)]),
 dict(id='F2',name='Triangular command cluster',
   idea='Three command seats face a shared triangular decision area; specialist stations surround it.',
   main='Rapid Pilot-NAV-Captain conversation',weak='Denser primary cluster may obstruct mutual screens',
   positions=[(-1.40,1.70,2.45,5),(1.40,1.70,2.45,-5),(0,-.05,2.42,0),(-2.8,-1.2,2.82,-50),(2.8,-1.2,2.82,50),(0,-3.15,2.82,0)],
   stand=[0,-1.45,2.70],surface='triangle',
   platforms=[slab(2.80,0,.90,5.2,3.65),slab(2.91,0,-2.6,6.7,2.5)]),
 dict(id='F3',name='Horseshoe bridge',
   idea='A curved crew arc surrounds open command space and a reachable shared workpoint.',
   main='Shared situational awareness across all six roles',weak='Longer cross-bridge communication and no privileged Captain view',
   positions=[(-1.8,2.25,2.45,25),(1.8,2.25,2.45,-25),(0,-2.6,2.55,0),(-3.20,-.55,2.55,-60),(3.20,-.55,2.55,60),(-1.65,-2.45,2.55,-20)],
   stand=[.6,-.4,2.85],surface='horseshoe',
   platforms=[slab(2.68,-1.65,.75,3.65,5.3),slab(2.68,1.65,.75,3.65,5.3),
              slab(2.68,0,-2.75,4.1,1.1)]),
 dict(id='F4',name='Amphitheatre command',
   idea='Flight stations on a low forward tier; Captain on a raised middle tier; three specialists on an even higher aft tier.',
   main='Tiered command visibility and distinct specialist levels',weak='Multiple step changes may be awkward in weightlessness and faults',
   positions=[(-1.0,2.35,3.25,0),(1.0,2.35,3.25,0),(0,.32,2.50,0),(-2.15,-1.45,1.93,-20),(2.15,-1.45,1.93,20),(0,-3.32,1.48,0)],
   stand=[0,-1.03,2.42],surface='amphitheatre',
   platforms=[slab(3.36,0,2.25,3.6,2.55),slab(2.62,0,.38,2.0,1.7),
              slab(2.05,0,-1.55,5.3,2.25),slab(1.60,0,-3.3,1.7,1.45)]),
 dict(id='F5',name='Mission pods',
   idea='Pilot/NAV paired; engineering and mission form a separate task pod; sensors and Captain form another.',
   main='Specialist workflows and local collaboration',weak='Separated groups reduce cross-role awareness',
   positions=[(-.90,2.85,2.4,0),(.90,2.85,2.4,0),(2.45,-1.7,2.60,60),(-2.65,.25,2.70,-50),(2.45,.10,2.60,50),(-2.65,-1.75,2.70,-50)],
   stand=[0,-.75,2.85],surface='mission pods',
   platforms=[slab(2.55,0,2.75,3.2,2.25),slab(2.84,-2.6,-.75,2.35,4.3),
              slab(2.75,2.45,-.75,2.35,4.3),slab(2.95,0,-.8,1.7,2.2)]),
 dict(id='F6',name='Split-level command',
   idea='Two-level bridge: flight pair on lower forward deck; Captain and specialists on a separate elevated command gallery.',
   main='Clear command oversight with specialist work physically separated',weak='Movement between tiers and direct reach difficult in emergency',
   positions=[(-.95,2.15,3.35,0),(.95,2.15,3.35,0),(0,.25,1.70,0),(-2.50,-1.32,1.72,-30),(2.50,-1.32,1.72,30),(0,-3.18,1.72,0)],
   stand=[0,-1.45,1.73],surface='split levels',
   platforms=[slab(3.48,0,2.10,3.45,3.1),
              slab(1.86,0,-1.28,6.30,4.9)]),
 dict(id='F7',name='Central command well',
   idea='Captain at the middle of an inward-facing cluster; Pilot/NAV split toward opposite sides of the view.',
   main='Collective command coordination and captain access',weak='Pilot/NAV lose some close-pair synchronization',
   positions=[(-2.75,1.80,2.55,-30),(2.75,1.80,2.55,30),(0,.05,1.92,0),(-2.85,-1.60,2.85,-60),(2.85,-1.60,2.85,60),(0,-3.20,2.85,0)],
   stand=[0,-1.15,2.60],surface='command well',
   platforms=[slab(2.98,0,-.6,6.5,7.0),slab(2.05,0,.08,1.8,1.8)]),
 dict(id='F8',name='Panoramic observation arc',
   idea='Broad forward crew crescent, one rear centre Captain and specialist group, designed around the view.',
   main='Shared experience of the panorama and distributed external observation',weak='Larger lateral separation weakens urgent crew cross-checking',
   positions=[(-2.90,1.15,2.45,-30),(-1.05,3.02,2.45,-10),(0,-1.25,2.14,0),(2.90,1.15,2.45,30),(1.05,3.02,2.45,10),(0,-3.20,2.64,0)],
   stand=[0,-.05,2.57],surface='observation arc',
   platforms=[slab(2.63,-2.25,1.5,2.8,3.75),slab(2.63,0,2.0,2.45,4.4),
              slab(2.63,2.25,1.5,2.8,3.75),slab(2.75,0,-2.2,3.6,2.7)])
]
def make(d):
 seats=[seat(k,*a) for k,a in zip(ROLE_NAMES,d['positions'])]
 screens=[]
 for st in seats:
  a=math.radians(38 if st['id'] in ('PILOT','NAV') else 35)
  ang=math.radians(st['heading_deg'])
  u=(math.sin(ang),-math.cos(ang))
  e=st['eye'];direction=(-math.cos(a),u[0]*math.sin(a),u[1]*math.sin(a))
  pos=[round(e[i]+.60*direction[i],4) for i in range(3)]
  screens.append(dict(for_station=st['id'],center_xyz=pos,half_width_m=.22,
        half_height_m=.14,angle_deg=round(math.degrees(a),1)))
 stand_y,stand_z,stand_x=d['stand']
 return {'id':d['id'],'name':d['name'],'idea':d['idea'],
   'advantage':d['main'],'tradeoff':d['weak'],
   'layout':{'seats':seats,'stand':{'eye_xyz':[stand_x-.63,stand_y,stand_z],
     'floor_x':stand_x,'anchor_yz':[stand_y,stand_z],
     'foot_restraints':True,'handholds':True,'low_g_only':True},
    'platforms':d['platforms']},'screens':screens,
   'levels':len(set(x['base_x'] for x in seats)),
   'role_centres':{s['role']:s['center_yz'] for s in seats}}
data_designs=[make(d) for d in D]
# Tiny no-fabrication checks
for x in data_designs:
 assert len(x['layout']['seats'])==6
 assert sorted(s['id'] for s in x['layout']['seats'])==sorted(ROLE_NAMES)
 assert len(x['screens'])==6
assert data_designs[0]['layout']['seats'][2]['base_x']<data_designs[0]['layout']['seats'][0]['base_x']
assert data_designs[3]['levels']>=4
report={'classification':'EXPLORATORY RESEARCH NON-CANON NON-RUNTIME, UNCONSTRAINED CONCEPT GEOMETRY NOT QUALIFIED',
 'requirements':['Six working contoured acceleration chairs','Six crew operational functions'],
 'deliberately_unconstrained':['Existing hull','Existing ladders','Existing source L1 flight-deck elevation',
       'Existing support ring','Number and shape of internal deck tiers',
       'Standing-station location','Screen mount topology','Interior plan size'],
 'important_caveat':'Initial 2226 layouts deliberately ignore pressure hull fit and all access/egress, structural and load-path qualification. A concept is not a buildable part of Wayfarer yet.',
 'shared_seat_reference':'Illustrative segmented 1.58m projected-length Kazbek-inspired shell, not fitted or qualified. Acceleration orientation is visually represented but no real g-load test.',
 'designs':data_designs,
 'assessment':{
  'candidate_shortlist':['F1','F3','F6'],
  'why':['F1: directly provides raised centred Captain with forward Pilot/NAV pair and is simplest crew supervision topology',
         'F3: strong crew interaction and shared information across a continuous open horseshoe',
         'F6: true alternative with multiple physical levels and separated flight versus command responsibilities'],
  'not_proven':'This is qualitative selection for discussion and user viewing, not measured human performance or a demonstrated optimum. The other five remain equally selectable.',
  'next_real_test':'Compare actual task movements and views in the 3D render; select a topology before applying 3D hull, circulation and g-load fit checks.'}}
out=ROOT/'command/L1_EIGHT_FREEFORM_2226_CONCEPTS_20261029.json'
out.write_text(json.dumps(report,indent=2))
# convert earlier standalone WebGL viewer, keeping code engine and custom chair support.
m=re.search(r'const DATA=(\{.*?\});\nconst G=DATA\.geo;let C=DATA\.cmd;',TEMPLATE,re.S)
assert m, 'viewer source data not found'
data=json.loads(m.group(1))
data['designs']=data_designs
# Remove all source fixed structure; these are deliberately NOT Rev7 fits.
data['geo']['parts']=[]
data['cmd']['ladders']=[]
data['cmd']['flight_deck_ladder']=None
src=TEMPLATE[:m.start()]+'const DATA='+json.dumps(data,separators=(',',':'))+';\nconst G=DATA.geo;let C=DATA.cmd;'+TEMPLATE[m.end():]
# default model has no source structure, shell is just optional contextual old research canopy
src=src.replace('FIVE DISTINCT L1 FLOORPLANS · SAME SHIP','EIGHT UNCONSTRAINED COMMAND-DECK CONCEPTS')
src=src.replace('FIVE DISTINCT L1 ARCHITECTURES · SAME HULL','EIGHT FREEFORM COMMAND-DECK CONCEPTS')
src=src.replace('Five distinct L1 floorplan families · corrected comparison','Eight different L1 command architectures · no fixed interior')
src=src.replace('five distinct floorplan concepts; ship shell from source Rev 7','freely authored crew decks; not fitted to source Rev 7')
src=src.replace('Choose a genuinely different arrangement. All five diagrams share the same scale.','Choose a different command organization. These are unconstrained concept studies, NOT a physical fit to the current hull. All diagrams share the same scale.')
src=src.replace('Original bow sensor ring','Rev7 sensor reference (optional)')
# Original sensor geometry is intentionally not part of any freeform concept,
# so do not advertise a toggle that would have no visible effect.
src=re.sub(r'<label><input type="checkbox" id="sensors"[^>]*>[^<]*</label>', '', src)
src=src.replace('37 outer replaceable tiles','37 outer research tiles (reference only)')
src=src.replace('37 replaceable outer protective panels','37 outer research tiles (reference only)')
src=src.replace('held 37-panel research canopy','optional original-canopy reference')
src=src.replace("['outer','pressure','seams','gel','crew','sensors','rim','labels']", "['outer','pressure','seams','gel','crew','rim','labels']")
src=src.replace('The six station anchor points, flight deck, floor and ladders originate with the L1 model.','All seats, decks and standing workpoints are newly authored freeform concepts; the prior L1 structure is intentionally omitted.')
src=src.replace('all dimensions in metres · five distinct floorplan concepts','all dimensions in metres · eight unrestricted floorplan concepts')
# Build eight interactive cards with same-scale YZ diagrams and clear relative chair X levels.
def plan(k):
 c=112;scale=18.3;res=['<svg viewBox="0 0 224 224" xmlns="http://www.w3.org/2000/svg">']
 res.append('<rect x="0" y="0" width="224" height="224" rx="10" fill="#0b1d2b"/>')
 res.append('<path d="M112 10 L100 25 L124 25 Z" fill="#69b4b5" opacity=".7"/>')
 for st in k['layout']['seats']:
  y,z=st['center_yz'];ang=math.radians(st['heading_deg']);u=(math.sin(ang),-math.cos(ang));v=(-u[1],u[0])
  pts=[]
  for t,s in [(-.79,-.35),(.79,-.35),(.79,.35),(-.79,.35)]:
   yy=y+u[0]*t+v[0]*s;zz=z+u[1]*t+v[1]*s
   pts.append(f'{c+scale*yy:.1f},{c-scale*zz:.1f}')
  col='#eed09b' if st['id'] in ('PILOT','NAV') else '#85d1e1' if st['id']=='S1' else '#82c4b3'
  res.append(f'<polygon points="{" ".join(pts)}" fill="{col}" fill-opacity=".45" stroke="{col}" stroke-width="1.8"/>')
  res.append(f'<text x="{c+scale*y:.1f}" y="{c-scale*z+3:.1f}" text-anchor="middle" fill="#f4f9ff" font-size="10">{st["id"]}</text>')
  # elevation annotation: lower X means closer to bow/raised along thrust axis
  res.append(f'<text x="{c+scale*y:.1f}" y="{c-scale*z+13:.1f}" text-anchor="middle" fill="#bed5df" font-size="7.4">{st["base_x"]:.1f}</text>')
 yy,zz=k['layout']['stand']['anchor_yz']
 res.append(f'<circle cx="{c+scale*yy:.1f}" cy="{c-scale*zz:.1f}" r="7.5" stroke="#faaf68" fill="#28465e" stroke-width="2"/>')
 res.append(f'<text x="{c+scale*yy:.1f}" y="{c-scale*zz+3:.1f}" font-size="9" fill="white" text-anchor="middle">C</text>')
 res.append('</svg>')
 return ''.join(res)
start='<h2>EIGHT UNCONSTRAINED COMMAND-DECK CONCEPTS</h2>';end='<h2>Camera / views</h2>'
assert start in src and end in src
beg=src.index(start);last=src.index(end,beg)
cards=['<h2>EIGHT FREEFORM COMMAND-DECK CONCEPTS</h2>',
 '<p class="note">Only the six functions and proper acceleration work seats are retained. NO hull, existing ladder, deck or crown fit constraints. All floorplans use the same scale; small numbers in chairs are their X-tier levels. C is a proposed anchored command workpoint.</p>',
 '<div class="families">']
for i,k in enumerate(data_designs):
 cards.append(f'<button class="family" data-variant="{i}" aria-pressed="{"true" if i==0 else "false"}">'
     f'<span class="family-name"><b>{k["id"]}</b> · {html.escape(k["name"])}</span>{plan(k)}'
     f'<span class="family-detail">{html.escape(k["idea"])}</span></button>')
cards.append('</div><p class="note" id="variantInfo">Select one of eight different organizations</p>')
src=src[:beg]+'\n'.join(cards)+'\n'+src[last:]
src=src.replace('flex:0 0 185px;min-width:185px','flex:0 0 205px;min-width:205px')
# Create unique decks in each layout instead of fixed source floor + fixed mezzanine.
needle=" for(const s of sc.couches){"
where=src.index('function commandMeshes(sc,opt={})')
i=src.index(needle,where)
floor_js=""" for(const f of sc.platforms||[]){
  const X=[1,0,0],Y=[0,1,0],Z=[0,0,1];
  meshOBox(mb('floor'),[f.x,f.y,f.z],[X,Y,Z],[.040,f.wy/2,f.wz/2]);
 }
 // Small chair mounting pads at each authored X tier. These are conceptual
 // supports only, not pressure-vessel structural attachment claims.
 for(const ss of sc.couches){
   const u=[0,(ss.feet[0]-ss.head[0])/ss.L,(ss.feet[1]-ss.head[1])/ss.L];
   const v=[0,-u[2],u[1]];
   const mid=[ss.base_x+.078,(ss.head[0]+ss.feet[0])/2,(ss.head[1]+ss.feet[1])/2];
   meshOBox(mb('equipment'),mid,[[1,0,0],u,v],[.044,.90,.48]);
 }
"""
src=src[:i]+floor_js+src[i:]
# Model actual standing station at per-layout x; physical low-g anchor
src=src.replace("const floor=3.,x=2.36;", "const floor=sc.stand.floor_x||3.,x=floor-.64;")
src=src.replace("p0:[2.50,y+dy,z+.12],p1:[2.05,y+dy,z+.45]","p0:[floor-.50,y+dy,z+.12],p1:[floor-.95,y+dy,z+.45]")
src=src.replace("[2.05,y,z+.45]", "[floor-.95,y,z+.45]")
src=src.replace("[2.28,y,z+.19]", "[floor-.72,y,z+.19]")
# Change a viewer input to C with custom decks. Keep previous code exactly otherwise.
src=src.replace('stand:k.layout.stand,stand_style:k.stand_style};',
                'stand:k.layout.stand,stand_style:"wide",platforms:k.layout.platforms,ladders:[],flight_deck_ladder:null};')
# Fix actual active 3D repaint and camera targets AFTER switching.
old="  rebuild();\n}\ndocument.querySelectorAll('[data-variant]')"
assert old in src
src=src.replace(old,"""  rebuild();
  // Explicit paint on every change, not just updating buffers and label text.
  redraw();
  requestAnimationFrame(()=>{dirty=true;redraw();});
}
document.querySelectorAll('[data-variant]')""",1)
# informational text must refer to the topology instead of stale old data keys
info_start=src.index("  document.getElementById('variantInfo').textContent=")
info_end=src.index("  document.getElementById('viewname').textContent=",info_start)
src=src[:info_start]+"""  document.getElementById('variantInfo').textContent =
   k.id+' · '+k.name+' | '+k.idea+' | Strongest feature: '+k.advantage+
   ' | Main trade-off: '+k.tradeoff+' | *CONCEPT ONLY*, free of prior hull constraints';
""" +src[info_end:]
# 8 variants. Remove old sources' static metrics that imply tested original source
src=src.replace('6 · Kazbek-inspired contoured','6 · Kazbek-inspired contoured')
src=src.replace('0.12 m</strong>','Research reference only</strong>')
src=src.replace('The six station anchor points, flight deck, floor and ladders come from the L1 model.',
                'Freeform arrangement. No existing deck/floor/ladder geometry is retained.')
# Output file
out=HERE/'out/wayfarer_l1_eight_unconstrained_3d.html'
out.write_text(src)
print('RESULT',out,out.stat().st_size,'bytes',len(data_designs),'distinct concepts')
print('JSON',ROOT/'command/L1_EIGHT_FREEFORM_2226_CONCEPTS_20261029.json')