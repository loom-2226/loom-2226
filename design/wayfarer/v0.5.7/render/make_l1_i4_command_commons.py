"""I4 Command Commons: single render-ready freeform Wayfarer L1 3D interior.

Reuses I1 crew-function geometry and I3's common-space intent, but authors
one coherent physical room and a tiny mobile-safe Canvas2D viewer.
Not fitted to current pressure hull or qualified for acceleration.
"""
from __future__ import annotations
import copy,json,math,re,base64
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
prior=json.loads((ROOT/'command/L1_THREE_COMPLETE_INTERIOR_CONCEPTS_20261029.json').read_text())
assert [x['id'] for x in prior['concepts']]==['L1-I1','L1-I2','L1-I3']
I1,I3=prior['concepts'][0],prior['concepts'][2]
v=copy.deepcopy(I1)
v['id']='L1-I4'
v['name']='Command Commons'
v['idea']=('Unified main operations deck, broad raised Pilot/Captain command terrace, '
           'forward lower Navigator, panoramic observation edge, shared mission plotting table, '
           'and integrated separate work bay.')
v['advantage']='A recognisable six-person command deck that also supports low-g collaboration and observation'
v['tradeoff']='Tier movement, structural loads and final pressure-hull fit remain unresolved'

# Coordinate definition preserved from the preceding Canvas2D research visualisation.
# Y lateral; Z toward bow in rendered floor plan; conceptual H=4-X deck elevation.
# This is not an approved physical Wayfarer coordinate transformation.
def move(role,y,z,x,hdg):
 s=next(s for s in v['layout']['seats'] if s['id']==role)
 a=math.radians(hdg);u=[math.sin(a),-math.cos(a)];L=1.58
 h=[y-u[0]*L/2,z-u[1]*L/2]
 foot=[y+u[0]*L/2,z+u[1]*L/2]
 s.update(center_yz=[y,z],base_x=x,heading_deg=hdg,
          head=[round(q,4) for q in h],feet=[round(q,4) for q in foot],
          eye=[round(x-.45,4),round(h[0]+u[0]*.2,4),round(h[1]+u[1]*.2,4)])
def box(y,z,height,wy,wz,th=.12,color='#40596d',opacity=1,tag=''):
 return dict(y=y,z=z,height=height,wy=wy,wz=wz,th=th,color=color,opacity=opacity,tag=tag)
def line(a,b,color='#88cad0',radius=.02):
 return dict(a=a,b=b,color=color,radius=radius)
# From I1 command orientation, I3's more open support crew arc. No duplicate chairs.
move('PILOT',-.93,-.46,1.91,-5)
move('S1',.93,-.46,1.91,5)  # Captain paired on the same raised X tier
move('NAV',0,2.50,2.76,0)
move('S2',-3.04,-.95,3.31,-28) # Engineering port
move('S3',3.06,-.60,3.31,28) # Sensors starboard
move('S4',2.48,-3.06,3.31,22) # Mission ops aft starboard
v['layout']['stand']={
 'eye_xyz':[2.70,.26,-2.03],'floor_x':3.31,
 'anchor_yz':[.26,-2.03],'foot_restraints':True,'handholds':True,
 'low_g_only':True}
v['layout']['work_area']={
 'label':'Independent mission equipment bay','floor_x':3.31,
 'anchor_yz':[-2.43,-3.17],'purpose':'Robotics/EVA/survey and equipment handling in low-g',
 'surface_width_m':1.45,'foot_restraints':True,'handholds':True,
 'local_display':True}
v['layout']['platforms']=[]
v['screens']=[]
for s in v['layout']['seats']:
 a=math.radians(38 if s['id'] in ('PILOT','NAV','S1') else 34)
 hd=math.radians(s['heading_deg'])
 u=(math.sin(hd),-math.cos(hd))
 dr=(-math.cos(a),u[0]*math.sin(a),u[1]*math.sin(a))
 e=s['eye']
 v['screens'].append(dict(for_station=s['id'],
   center_xyz=[round(e[i]+.60*dr[i],4) for i in range(3)],
   half_width_m=.22,half_height_m=.14,angle_deg=round(math.degrees(a),2)))

# All major floor elevations here are in conceptual renderer height H.
blocks=[
 box(0,-.56,.68,8.15,8.05,.16,'#365264',tag='continuous_main_deck'), # z[-4.585,3.465]
 box(0,-.47,2.09,3.62,3.16,.18,'#496b75',tag='broad_pilot_captain_terrace'),
 box(0,2.48,1.24,2.80,2.52,.16,'#3f6974',tag='navigator_forward_platform'),
 # recessed low, perimeter equipment, broken up to retain open visual field
 box(-3.85,-1.20,1.04,.37,2.72,.56,'#4b6570',tag='engineering_side_storage'),
 box(3.85,-.88,1.04,.37,2.45,.56,'#4b6570',tag='sensor_side_storage'),
 box(3.24,-3.78,1.10,1.24,.37,.68,'#4a6170',tag='mission_ops_lockers'),
 box(-3.07,-3.90,1.02,1.62,.38,.67,'#5b6673',tag='work_bay_storage'),
 # central commons: a low open-table with no hard partition
 box(.21,-3.25,1.06,1.52,.80,.11,'#397e83',tag='mission_table_top'),
 box(.21,-3.25,.83,.40,.42,.34,'#365d6e',tag='mission_table_base'),
 # stand local workpoint (separate from shared mission table)
 box(.22,-2.06,1.06,.72,.43,.07,'#377988',tag='command_lean_support'),
 # workbench on port/aft, not at the shared table
 box(-2.42,-3.27,1.08,1.44,.55,.11,'#695a73',tag='independent_mission_bench'),
 box(-2.42,-3.65,1.42,1.25,.06,.51,'#50688b',tag='workbench_local_display'),
]
rails=[
 # command terrace side handrails leave clear centre and bow-facing edge
 line([-1.88,-1.85,2.21],[-1.88,.97,2.21],'#85d5ce'),
 line([1.88,-1.85,2.21],[1.88,.97,2.21],'#85d5ce'),
 # Navigator low open side rails (no internal pressure-shell mullions)
 line([-1.50,1.36,1.37],[-1.50,3.55,1.37],'#7ec5ce'),
 line([1.50,1.36,1.37],[1.50,3.55,1.37],'#7ec5ce'),
 # handhold continuity in main deck; segmented so it is not a full obstruction
 line([-3.67,-3.65,.94],[-3.67,-1.75,.94],'#7cb7ba'),
 line([3.67,-3.22,.94],[3.67,-1.30,.94],'#7cb7ba'),
]
lights=[
 line([-3.70,-3.67,.86],[-3.70,1.38,.86],'#70c9c2',.023),
 line([3.70,-3.67,.86],[3.70,1.38,.86],'#70c9c2',.023),
 line([-1.65,-1.89,2.22],[1.65,-1.89,2.22],'#edc58a',.025),
 line([-1.30,3.71,1.39],[1.30,3.71,1.39],'#86dbde',.026),
 line([-1.02,-3.86,.86],[1.07,-3.86,.86],'#6ab6bd',.02),
]
# Transfer elements are labelled low-g hand/foot rung *concepts*, not walking ramps.
transfers=[
 dict(name='port_terrace_access',a=[-1.70,-1.47,.84],b=[-1.70,-1.47,2.04],rungs=5),
 dict(name='starboard_terrace_access',a=[1.70,-1.47,.84],b=[1.70,-1.47,2.04],rungs=5),
 dict(name='navigator_access',a=[-1.16,1.59,.84],b=[-1.16,1.59,1.20],rungs=2),
]
# Bowward observation edge is low-profile handrail, not a structural pressure canopy.
observation={'radius_m':3.92,'from_rad':-.92,'to_rad':.92,'height':1.09,
             'segments':18,'type':'low_profile_view_handhold_not_glazing'}
v['interior']={'blocks':blocks,'rails':rails,'lights':lights,
  'transfers':transfers,'observation':observation,
  'consoles':[dict(label='MISSION TABLE',pos=[.21,-3.25,1.35],color='#9be2df'),
              dict(label='SHIP CONDITION',pos=[.25,-2.03,1.39],color='#9acee9')],
  'phases':['coast+standing collaboration','approach+six specialist stations','4g+six occupied seats; standing stations inactive']}
# Restrict to minimal factually defensible checks.
seats=v['layout']['seats']
assert len(seats)==6 and len({s['id'] for s in seats})==6
assert seats[0]['base_x']==seats[2]['base_x']<seats[1]['base_x']
assert v['layout']['work_area']['anchor_yz']!=v['layout']['stand']['anchor_yz']
assert len(v['screens'])==6
assert len([b for b in blocks if b['tag']=='continuous_main_deck'])==1
assert len(transfers)==3
j={'classification':'RESEARCH / NON-CANON / NON-RUNTIME / NOT HULL- OR 4G-QUALIFIED',
 'basis':{'I1':'Continuous terraced lower operations deck','I3':'Open observation and social/mission plotting commons'},
 'coordinates':'Renderer plan: Y lateral, Z toward forward canopy, H=4-X visual tier height in metres. Not governing ship-frame coordinates.',
 'design':v,
 'acceptance_checks':{'six_seat_roles':'PASS geometric count','raised_pilot_and_captain':'PASS authored levels',
  'single_lower_underside':'PASS authored main floor','separate_anchored_workbench':'PASS authored positions',
  'crew_reach/egress/4g':'NOT TESTED','ship_hull_pressure_fit':'NOT TESTED'},
 'stop':'One phone-viewable, coherent furnished 3D concept; no new runtime systems or architectural speculation'}
(ROOT/'command/L1_I4_COMMAND_COMMONS_GEOMETRY_20261029.json').write_text(json.dumps(j,indent=2))

# Start from already validated Android Canvas2D viewing page.
base=(HERE/'make_l1_canvas2d_android_viewer.py').read_text()
t=re.search(r"page=r'''(.*?)'''",base,re.S)
assert t
page=t.group(1)
page=page.replace('WAYFARER · L1 COMMAND DECK','WAYFARER · I4 COMMAND COMMONS')
page=page.replace('Interactive 3D · Android-friendly Canvas renderer · no WebGL required · non-canon research',
                  'Single coherent room · Android-friendly Canvas 3D · no WebGL · non-canon')
page=page.replace('F1-R2 · Paired command','I4 · Command Commons')
page=page.replace('Compare the two designs','Command Commons')
page=page.replace('<div class="actions">\n<button data-design="0" aria-pressed="true">NEW · Pilot + Captain raised</button>\n<button data-design="1" aria-pressed="false">OLD · Original F1</button>\n</div>',
                  '<p class="note">One integrated design, not another chair-position search.</p>')
page=page.replace('Pilot and Captain together on the elevated command tier, Navigator forward and lower. The former S4 position becomes a separate workbench.',
                  'I1’s continuous working deck with I3’s shared observation commons: Pilot/Captain raised, Navigator forward, three specialist seats, central mission plot, and a separate workbench.')
page=page.replace('const state={variant:0,yaw:-0.70,pitch:0.60,zoom:.79,panx:0,pany:0,',
                  'const state={variant:0,yaw:-0.79,pitch:0.70,zoom:.79,panx:0,pany:0,')
page=page.replace('if(mode==="orbit"){state.yaw=-.70;state.pitch=.60}',
                  'if(mode==="orbit"){state.yaw=-.79;state.pitch=.70}')
page=page.replace('state.zoom=.79;state.panx=state.pany=0;',
                  'state.zoom=.79;state.panx=state.pany=0;')
page=page.replace('rect={w:a.width,h:a.height,scale:Math.min(a.width/9.8,a.height/8.5)};',
                  'rect={w:a.width,h:a.height,scale:Math.min(a.width/11.7,a.height/10.0)};')
# Replace the old independent floor platforms drawing with actual I4 room geometry.
b=page.index(' if(state.floors){\n  for(const f of layout.platforms||[]){')
e=page.index(' for(const seat of layout.seats){',b)
room_js=r''' if(state.floors){
  const I=design.interior;
  // Single authored contiguous operations room, two clearly distinct raised terraces.
  for(const b of I.blocks){
    box(b.y,b.z,b.height,b.wy,b.wz,b.th,b.color,b.opacity??1);
  }
  // Physical handrails and low-profile observation perimeter.
  for(const r of I.rails)segment(r.a,r.b,r.radius,r.color);
  for(const l of I.lights)segment(l.a,l.b,l.radius,l.color);
  // Compact low-g hand/foot rung connections, NOT imagined long ramps.
  for(const tr of I.transfers){
    segment(tr.a,tr.b,.035,"#a3c4ca");
    for(let k=0;k<tr.rungs;k++){
      const f=(k+.7)/tr.rungs;
      const yy=tr.a[0]+(tr.b[0]-tr.a[0])*f;
      const zz=tr.a[1]+(tr.b[1]-tr.a[1])*f;
      const hh=tr.a[2]+(tr.b[2]-tr.a[2])*f;
      segment([yy-.25,zz,hh],[yy+.25,zz,hh],.017,"#d5c18e");
    }
  }
  const sill=I.observation;
  for(let k=0;k<sill.segments;k++){
    const t0=sill.from_rad+(sill.to_rad-sill.from_rad)*k/sill.segments;
    const t1=sill.from_rad+(sill.to_rad-sill.from_rad)*(k+1)/sill.segments;
    segment([sill.radius_m*Math.sin(t0),sill.radius_m*Math.cos(t0),sill.height],
            [sill.radius_m*Math.sin(t1),sill.radius_m*Math.cos(t1),sill.height],
            .022,"#7ad8d0");
  }
  if(state.screens){
    for(const con of I.consoles){
      const [y,z,h]=con.pos;
      box(y,z,h,1.08,.060,.30,"#328da1",.82);
      label([y,z,h+.24],con.label,con.color);
    }
  }
 }
'''
page=page[:b]+room_js+page[e:]
# Keep separate active elements and increase social table presence (derived from actual model blocks).
page=page.replace('This is a software-rendered, freely arranged concept. It does not certify pressure-hull fit, acceleration tolerance, safe egress, screen ergonomics or crew performance.',
'''This is one authored room concept, not yet fitted to Wayfarer's actual pressure hull. The connected deck, raised pair, Navigator platform, low-g transfer rungs, shared table and equipment bay are illustrative. No 4g structural, access or ergonomics qualification is claimed.''')
page=page.replace('console.log','console.log')
page=page.replace('const designs=__DATA__','const designs=__DATA__')
# Remove redundant compare controls: choose(0) is the only design available.
page=page.replace('document.getElementById("status").textContent=\n  "RENDERED · "+designs[state.variant].id+" · 6 acceleration seats"',
                  'document.getElementById("status").textContent=\n  "RENDERED · "+designs[state.variant].id+" · connected deck + 6 acceleration seats"')
page=page.replace('<img id="static" alt="Static fallback rendering of the paired Pilot-Captain command deck"',
                  '<img id="static" alt="I4 Command Commons 3D fallback preview"')
# Compact descriptive labels; keep the table and central command station distinct.
page=page.replace('"COMMAND WORKPOINT"','"COMMAND STAND"')
page=page.replace('"INDEPENDENT MISSION WORK AREA"','"MISSION WORKBENCH"')
page=page.replace('COMMON MISSION PLOT','MISSION TABLE')
old_labels=''' if(state.labels){
  ctx.textAlign="center";ctx.font="600 10px system-ui";
  for(const m of markers){
   const text=m.text,tw=ctx.measureText(text).width;
   let x=Math.max(6+tw/2,Math.min(rect.w-6-tw/2,m.x));
   let y=Math.max(16,Math.min(rect.h-12,m.y-15));
   ctx.fillStyle="#10273eea";ctx.fillRect(x-tw/2-6,y-13,tw+12,18);
   ctx.strokeStyle="#46718a";ctx.lineWidth=.75;ctx.strokeRect(x-tw/2-6,y-13,tw+12,18);
   ctx.fillStyle=m.color;ctx.fillText(text,x,y);
  }
 }'''
new_labels=''' if(state.labels){
  ctx.textAlign="center";ctx.font="600 10px system-ui";
  const placed=[];
  // Deconflict labels at phone width. Their anchor remains the 3D station.
  const order={"PILOT":0,"CAPTAIN":1,"NAVIGATOR":2,"ENGINEERING":3,
    "SENSORS / EW":4,"MISSION OPS":5,"MISSION WORKBENCH":6,
    "COMMAND STAND":7,"MISSION TABLE":8,"SHIP CONDITION":9};
  for(const m of markers.slice().sort((a,b)=>(order[a.text]??50)-(order[b.text]??50))){
   const text=m.text,tw=ctx.measureText(text).width,w=tw+12,h=18;
   let chosen=null;
   for(const [dx,dy] of [[0,-17],[0,-36],[0,8],[0,27],[36,-17],[-36,-17],
     [50,-36],[-50,-36],[0,-56],[55,8],[-55,8],[0,48],[80,-17],[-80,-17]]){
    let x=Math.max(7+w/2,Math.min(rect.w-7-w/2,m.x+dx));
    let y=Math.max(71,Math.min(rect.h-43,m.y+dy));
    const q=[x-w/2-3,y-14,x+w/2+3,y+5];
    if(placed.every(p=>q[2]<p[0]||p[2]<q[0]||q[3]<p[1]||p[3]<q[1])){
      chosen={x,y,q};break;
    }
   }
   if(!chosen)continue;placed.push(chosen.q);
   if(Math.hypot(chosen.x-m.x,chosen.y-m.y)>26){
     ctx.beginPath();ctx.moveTo(m.x,m.y);ctx.lineTo(chosen.x,chosen.y-9);
     ctx.lineWidth=.65;ctx.strokeStyle="#6c97acaa";ctx.stroke();
   }
   ctx.fillStyle="#10273ef0";ctx.fillRect(chosen.x-w/2,chosen.y-13,w,h);
   ctx.strokeStyle="#46718a";ctx.lineWidth=.75;
   ctx.strokeRect(chosen.x-w/2,chosen.y-13,w,h);
   ctx.fillStyle=m.color;ctx.fillText(text,chosen.x,chosen.y);
  }
 }'''
assert old_labels in page, 'Source label drawing changed'
page=page.replace(old_labels,new_labels)
# Deliberately preserve embedded static preview for JS-disabled phone files.
png=HERE/'out/l1_i4_command_commons_preview.png'
preview=('data:image/png;base64,'+base64.b64encode(png.read_bytes()).decode('ascii')) if png.exists() else (
 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20400%20400%22%3E%3Crect%20width%3D%22400%22%20height%3D%22400%22%20fill%3D%22%230b2336%22/%3E%3Ctext%20x%3D%22200%22%20y%3D%22200%22%20fill%3D%22white%22%20text-anchor%3D%22middle%22%3EI4%20Preview%20Pending%3C/text%3E%3C/svg%3E')
out=HERE/'out/wayfarer_l1_i4_command_commons_android.html'
out.write_text(page.replace('__DATA__',json.dumps([v],separators=(',',':'))).replace('__FALLBACK__',preview))
print('I4 GENERATED',out,'bytes',out.stat().st_size)
print('I4 GEOMETRY',len(blocks),'floor/furniture blocks,',len(rails),'rails,',len(lights),'light lines,',len(transfers),'connectors')