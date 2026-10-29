"""Source-fitted I4 crew room + entire 37-pane outer trapezoidal & inner double dome.

Minimal research viewer reuses Android Canvas2D. Source floor annulus and
two .8m ladder holes replace unconstrained rectangular main floor.
Physical screen is plan-only; full 3D operational/4g qualification pending.
"""
import json,math,re,base64
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
screen=json.loads((ROOT/'command/L1_I4_CONSTRAINED_FIT_SCREEN_20261029.json').read_text())
assert screen['gates_pass_all']
v=json.loads((ROOT/'command/L1_I4_COMMAND_COMMONS_GEOMETRY_20261029.json').read_text())['design']
SRC=json.loads((ROOT/'command/L1_I4_SOURCE_STRUCTURAL_CONTEXT_20261029.json').read_text())
g={x['id']:x['shape'] for x in json.loads((ROOT/'out/wayfarer_v05_geometry.json').read_text())['parts']}
assert SRC['hull']['inner_radius_m']==4.3
T=1.58
def station(s,y,z,x,hdg):
 a=math.radians(hdg);u=(math.sin(a),-math.cos(a))
 h=(y-T/2*u[0],z-T/2*u[1]);f=(y+T/2*u[0],z+T/2*u[1])
 s.update(base_x=x,heading_deg=hdg,center_yz=[y,z],
   head=[round(q,4) for q in h],feet=[round(q,4) for q in f],
   eye=[round(x-.45,4),round(h[0]+.2*u[0],4),round(h[1]+.2*u[1],4)])
p={r['id']:r['position_y_z_x_deg'] for r in screen['seats'] if 'position_y_z_x_deg' in r}
for ss in v['layout']['seats']:station(ss,*p[ss['id']])
v['screens']=[]
for ss in v['layout']['seats']:
 a=math.radians(38 if ss['id'] in ('PILOT','S1','NAV') else 34)
 ang=math.radians(ss['heading_deg']);u=(math.sin(ang),-math.cos(ang))
 dr=(-math.cos(a),u[0]*math.sin(a),u[1]*math.sin(a))
 e=ss['eye']
 v['screens'].append({'for_station':ss['id'],
   'center_xyz':[round(e[k]+.60*dr[k],4) for k in range(3)],
   'half_width_m':.22,'half_height_m':.14})
v['id']='L1-I4-FIT'
v['name']='Command Commons: source-annulus fit + full canopy'
v['idea']='Complete L1 source pressure shell and annular floor, two ladder access holes, moved functional seats, elevated command pair, Navigator, low-g mission areas, and all 37 outer trapezoidal panes over the seamless inner domes.'
v['layout']['stand'].update(anchor_yz=[-1.35,-3.55],eye_xyz=[2.68,-1.35,-3.55],floor_x=3.31)
v['layout']['work_area'].update(anchor_yz=[-2.45,-2.18],floor_x=3.31)
def box(y,z,h,wy,wz,th,color,tag):
 return {'y':y,'z':z,'height':h,'wy':wy,'wz':wz,'th':th,'color':color,'opacity':1,'tag':tag}
v['interior']['blocks']=[
 # no rectangular main deck: actual source annulus generated dynamically
 box(0,-1.96,2.09,3.40,2.10,.17,'#476678','command_terrace_trim_inner'),
 box(0,2.55,1.24,2.65,2.20,.14,'#48737d','navigator_platform'),
 box(-3.45,1.10,1.05,.35,.70,.54,'#40596b','engineering_cabinet'),
 box(3.45,1.10,1.05,.35,.70,.54,'#40596b','sensors_cabinet'),
 box(.40,-3.45,1.08,1.10,.63,.12,'#387f87','shared_map_table'),
 box(-2.45,-2.18,1.07,1.38,.54,.13,'#705d80','equipment_workbench'),
 box(-2.45,-2.44,1.42,1.16,.06,.42,'#5685a6','workbench_display'),
]
v['interior']['rails']=[
 {'a':[-1.72,-3.03,2.23],'b':[-1.72,-.94,2.23],'color':'#82cfcc','radius':.025},
 {'a':[1.72,-3.03,2.23],'b':[1.72,-.94,2.23],'color':'#82cfcc','radius':.025},
 {'a':[-1.36,1.50,1.35],'b':[-1.36,3.57,1.35],'color':'#84cbd2','radius':.022},
 {'a':[1.36,1.50,1.35],'b':[1.36,3.57,1.35],'color':'#84cbd2','radius':.022},
]
v['interior']['lights']=[
 {'a':[-1.60,-2.94,2.22],'b':[1.60,-2.94,2.22],'color':'#e8c18c','radius':.026},
 {'a':[-1.18,3.61,1.35],'b':[1.18,3.61,1.35],'color':'#8cd9dc','radius':.024},
]
v['interior']['transfers']=[
 {'name':'command_off-axis hand/foot access','a':[-1.67,-3.2,.90],'b':[-1.67,-2.9,2.05],'rungs':4},
 {'name':'navigator hand/foot access','a':[-1.14,1.47,.90],'b':[-1.14,1.67,1.20],'rungs':2}
]
v['interior']['observation']={'radius_m':3.95,'from_rad':-.92,'to_rad':.92,'height':1.13,'segments':18}
v['interior']['consoles']=[
 {'label':'COMMON MISSION PLOT','pos':[.40,-3.45,1.38],'color':'#8ee8df'}]
v['constrained_fit']={'6_seat_plan':'PASS',
 '6_key_furniture_areas_plan':'PASS',
 'source_annular_floor':'restored',
 'central_hole_and_ladders':'source geometry preserved in drawn floor',
 '3d_clearance':'NOT TESTED','4g_stability':'NOT TESTED',
 'physical_forward_axis':'ship -X; prior I4 Z-forward was a transverse visual metaphor'}
out_json=ROOT/'command/L1_I4_CONSTRAINED_FULL_CANOPY_SCENE_20261029.json'
out_json.write_text(json.dumps(v,indent=2))
page=(HERE/'out/wayfarer_l1_i4_with_source_structure_android.html').read_text()
m=re.search(r'const designs=(\[.*?\]),cv=document.getElementById\("view"\),ctx=',page,re.S)
assert m, 'could not locate original scene'
page=page[:m.start()]+'const designs='+json.dumps([v],separators=(',',':'))+',cv=document.getElementById("view"),ctx='+page[m.end():]
page=page.replace('WAYFARER · I4 + STRUCTURE','WAYFARER · COMPLETE L1 / I4 FIT')
page=page.replace('I4 · Structure cutaway','L1 · Full canopy / source-fit')
page=page.replace('Source pressure shell / I4 interior · Android-safe 3D · research only',
                  'Full 37 trapezoidal pane crown + seamless dome window · source L1 annulus · research')
page=page.replace('Source 8.6m hull radius and bow dome shown in cutaway. I4 remains an unfitted research interior; outer floor corners and the central original floor opening conflict.',
 '''I4 floor is now the source annulus, with central opening and both original ladder holes retained. All six seat and selected furniture footprints pass an initial radial/shaft clearance screen. **Full 3D crew access and thrust alignment remain unqualified.**''')
page=page.replace('I4 main floor extends beyond the source L1 ring by <strong>13.783 m²</strong> (approx.) and covers part of the source central opening. Toggling fit conflicts marks those areas. Bow is toward the higher source axial X-derived tier, not I4’s plan-view forward direction.',
 '''Source radius 4.3 m; original L1 floor outer radius 4.15 m with 0.9 m central hole and two 0.8 m ladder shafts. 37 outer tiles: [1,12,12,12], projected radii [0,.75,2,2.75,3.5] m. The real bow is toward ship -X, mapped upward in this viewer. Source geometric fit is not full 4g, human or mechanical qualification.''')
page=page.replace('Show fit conflicts','Show source floor outlines')
page=page.replace('data-structure="fit" aria-pressed="false"','data-structure="fit" aria-pressed="false"')
page=page.replace('Bow glazing</button>','Primary pressure dome</button>',1)
page=page.replace('<button data-structure="frames" aria-pressed="true">Rings + deck supports</button>',
'''<button data-structure="backup" aria-pressed="true">Backup pressure dome</button>
<button data-structure="outer" aria-pressed="true">37 outer trapezoid panes</button>
<button data-structure="seams" aria-pressed="true">Pane seams</button>
<button data-structure="sensors" aria-pressed="true">Sensor shoulder</button>
<button data-structure="frames" aria-pressed="true">Ring + supports</button>
<button data-structure="ladders" aria-pressed="true">Ladder openings</button>''')
page=page.replace('<h2>Interior layers</h2>',
'''<h2>Interior toggles</h2>''')
page=page.replace('<button data-layer="screens" aria-pressed="true">Screens</button>',
 '''<button data-layer="screens" aria-pressed="true">Screens</button>
 <button data-layer="furniture" aria-pressed="true">Mission furniture</button>
 <button data-layer="rails" aria-pressed="true">Handholds + lights</button>''')
page=page.replace('const state={hull:true,dome:true,frames:true,fit:false,variant:0,',
                  'const state={hull:true,dome:true,backup:true,outer:true,seams:true,sensors:true,ladders:true,frames:true,fit:false,furniture:true,rails:true,variant:0,')
# Full shell/tile source, replacing previous sourceShell function.
at=page.index('function sourceShell(){')
to=page.index('function build(){',at)
js=r'''
function domeH(r,offset=0){
 const s=SOURCE_STRUCTURE.hull;
 return s.cylinder_shoulder_h_m+s.dome_axial_extent_m*Math.sqrt(Math.max(0,1-(r/s.inner_radius_m)**2))+offset;
}
function tileH(r){
 // Research exterior surface: source +1.2m, flat radius 2m, 50° slope.
 return 5.20-Math.max(0,r-2)*Math.tan(Math.PI*50/180);
}
function ringLine(r,h,color,width=.024,a=-Math.PI,b=Math.PI,n=94){
 for(let i=0;i<n;i++){
  const A=a+(b-a)*i/n,B=a+(b-a)*(i+1)/n;
  segment([r*Math.sin(A),r*Math.cos(A),h],[r*Math.sin(B),r*Math.cos(B),h],width,color);
 }
}
function domeSurface(offset,color,alpha,skipCenter=false){
 const R=3.5,nR=10,nA=54,from=skipCenter?.6:0;
 for(let i=0;i<nR;i++){
  const a=from+(R-from)*i/nR,b=from+(R-from)*(i+1)/nR;
  for(let k=0;k<nA;k++){
   const t=2*Math.PI*k/nA,v=2*Math.PI*(k+1)/nA;
   polygon([[a*Math.sin(t),a*Math.cos(t),domeH(a,offset)],
            [b*Math.sin(t),b*Math.cos(t),domeH(b,offset)],
            [b*Math.sin(v),b*Math.cos(v),domeH(b,offset)],
            [a*Math.sin(v),a*Math.cos(v),domeH(a,offset)]],color,alpha);
  }
 }
}
function fullTrapezoidCrown(){
 const rings=[0,.75,2,2.75,3.5],count=[1,12,12,12],offset=[0,0,0,Math.PI/12];
 // EXACTLY 1+12+12+12=37 individually delimited modules, central disc
 // + three radial trapezoidal bands with the final band staggered.
 for(let band=0;band<4;band++){
  let n=count[band],r0=rings[band],r1=rings[band+1],off=offset[band];
  for(let sector=0;sector<n;sector++){
   const a=off+2*Math.PI*sector/n,b=off+2*Math.PI*(sector+1)/n;
   if(state.outer){
    for(let i=0;i<3;i++)for(let j=0;j<(n===1?42:6);j++){
     const rA=r0+(r1-r0)*i/3,rB=r0+(r1-r0)*(i+1)/3;
     const t=a+(b-a)*j/(n===1?42:6),u=a+(b-a)*(j+1)/(n===1?42:6);
     polygon([[rA*Math.sin(t),rA*Math.cos(t),tileH(rA)],
              [rB*Math.sin(t),rB*Math.cos(t),tileH(rB)],
              [rB*Math.sin(u),rB*Math.cos(u),tileH(rB)],
              [rA*Math.sin(u),rA*Math.cos(u),tileH(rA)]],
              ((band+sector)%2===0)?"#62becf":"#5ba5bc",.15);
    }
   }
   if(state.seams){
    // Every piece boundary is visible even with the glass toggled off.
    for(const rr of [r0,r1]){
     const seg=(n===1?40:6);
     for(let k=0;k<seg;k++){
      const ta=a+(b-a)*k/seg,tb=a+(b-a)*(k+1)/seg;
      segment([rr*Math.sin(ta),rr*Math.cos(ta),tileH(rr)],
              [rr*Math.sin(tb),rr*Math.cos(tb),tileH(rr)],.012,"#90dce3");
     }
    }
    if(n>1)for(let j=0;j<12;j++){
     const A=r0+(r1-r0)*j/12,B=r0+(r1-r0)*(j+1)/12;
     segment([A*Math.sin(a),A*Math.cos(a),tileH(A)],
             [B*Math.sin(a),B*Math.cos(a),tileH(B)],.012,"#8cc5d3");
    }
   }
  }
 }
}
function sourceShell(){
 const s=SOURCE_STRUCTURE,R=s.hull.inner_radius_m;
 const bottom=s.hull.L1_visible_aft_h_m,shoulder=s.hull.cylinder_shoulder_h_m;
 if(state.hull){
  const nn=66,lo=-2.33,hi=2.33; // one cutaway wedge only for seeing interior
  for(let i=0;i<nn;i++){
   const t=lo+(hi-lo)*i/nn,u=lo+(hi-lo)*(i+1)/nn;
   polygon([[R*Math.sin(t),R*Math.cos(t),bottom],
            [R*Math.sin(u),R*Math.cos(u),bottom],
            [R*Math.sin(u),R*Math.cos(u),shoulder],
            [R*Math.sin(t),R*Math.cos(t),shoulder]],"#6b9bad",.11);
  }
  ringLine(R,bottom,"#668d9a",.028,lo,hi);
  ringLine(R,shoulder,"#79b7c6",.034,lo,hi);
 }
 if(state.dome)domeSurface(0,"#90e0e6",.10);
 if(state.backup)domeSurface(.12,"#b5bde7",.08);
 if(state.dome||state.backup){
  // Opaque pressure shoulder beyond the 7m clear crown, not 37 more panes.
  for(let i=0;i<6;i++)for(let k=0;k<72;k++){
   const r=3.5+.8*i/6,u=3.5+.8*(i+1)/6;
   const t=2*Math.PI*k/72,z=2*Math.PI*(k+1)/72;
   polygon([[r*Math.sin(t),r*Math.cos(t),domeH(r)],
            [u*Math.sin(t),u*Math.cos(t),domeH(u)],
            [u*Math.sin(z),u*Math.cos(z),domeH(u)],
            [r*Math.sin(z),r*Math.cos(z),domeH(r)]],"#485766",.41);
  }
 }
 if(state.outer||state.seams)fullTrapezoidCrown();
 if(state.frames){
  ringLine(3.5,domeH(3.5),"#87d4d5",.052);
  ringLine(4.15,shoulder,"#a5a69b",.041);
  // partial floor supports for real source annular frame, not true FEA beams
  for(const [y,z,t] of [[-1.65,-2.60,2.05],[1.65,-2.60,2.05],
                         [-1.16,2.56,1.20],[1.16,2.56,1.20]]){
   segment([y,z,.92],[y,z,t],.048,"#86a4a9");
  }
 }
 if(state.sensors){
  ringLine(2.90,2.0,"#b19b82",.039);
  ringLine(4.15,2.0,"#b19b82",.039);
  for(let k=0;k<16;k++){
   const a=2*Math.PI*k/16;
   segment([2.90*Math.sin(a),2.90*Math.cos(a),2.0],
           [4.15*Math.sin(a),4.15*Math.cos(a),2.0],.027,"#7d8f9b");
  }
 }
 if(state.fit){
  ringLine(s.source_L1_floor.inner_hole_r_m,.98,"#eab475",.046);
  ringLine(s.source_L1_floor.outer_r_m,.98,"#eab475",.043);
 }
}
function sourceFloor(){
 const s=SOURCE_STRUCTURE.source_L1_floor,nR=8,nA=104,lo=s.inner_hole_r_m,hi=s.outer_r_m;
 for(let i=0;i<nR;i++)for(let j=0;j<nA;j++){
  const r0=lo+(hi-lo)*i/nR,r1=lo+(hi-lo)*(i+1)/nR;
  const t=j*2*Math.PI/nA,u=(j+1)*2*Math.PI/nA;
  const rc=(r0+r1)/2,tc=(t+u)/2,
   y=rc*Math.sin(tc),z=rc*Math.cos(tc);
  if(Math.min(Math.hypot(y-1.4,z),Math.hypot(y+1.4,z))<.49)continue;
  polygon([[r0*Math.sin(t),r0*Math.cos(t),.89],
           [r1*Math.sin(t),r1*Math.cos(t),.89],
           [r1*Math.sin(u),r1*Math.cos(u),.89],
           [r0*Math.sin(u),r0*Math.cos(u),.89]],
           (i+j)%2===0?"#354f61":"#355362",1);
 }
 if(state.ladders){
  for(const y of [-1.4,1.4]){
   for(let k=0;k<40;k++){
    const t=2*Math.PI*k/40,u=2*Math.PI*(k+1)/40;
    segment([y+.43*Math.sin(t),.43*Math.cos(t),.92],
            [y+.43*Math.sin(u),.43*Math.cos(u),.92],.039,"#deb080");
   }
   // actual openings are not filled by the annular deck mesh.
   label([y,0,1.05],"LADDER SHAFT","#ebbf9a");
  }
 }
}
'''
page=page[:at]+js+page[to:]
page=page.replace(' sourceShell();\n const design=',' sourceShell();\n if(state.floors)sourceFloor();\n const design=',1)
# Existing interior flooring: only retain raised terraces; all lower cabinets
# and tables now toggle with separate furniture button.
old='''  for(const b of I.blocks){
    box(b.y,b.z,b.height,b.wy,b.wz,b.th,b.color,b.opacity??1);
  }'''
new='''  for(const b of I.blocks){
    if(!state.furniture && !['command_terrace_trim_inner','navigator_platform'].includes(b.tag))continue;
    // No arbitrary full-width deck. The source annulus is the actual main floor.
    box(b.y,b.z,b.height,b.wy,b.wz,b.th,b.color,b.opacity??1);
  }'''
assert old in page
page=page.replace(old,new,1)
page=page.replace('  for(const r of I.rails)segment(r.a,r.b,r.radius,r.color);',
                  '  if(state.rails)for(const r of I.rails)segment(r.a,r.b,r.radius,r.color);')
page=page.replace('  for(const l of I.lights)segment(l.a,l.b,l.radius,l.color);',
                  '  if(state.rails)for(const l of I.lights)segment(l.a,l.b,l.radius,l.color);')
page=page.replace('  for(const tr of I.transfers){','  if(state.rails)for(const tr of I.transfers){')
page=page.replace('  for(let k=0;k<sill.segments;k++){','  if(state.rails)for(let k=0;k<sill.segments;k++){')
# The fixed pilot/nav tiers are conceptually trimmed at central hole: the
# command platform z[-3.01,-.91] ends just clear of central shaft r0.9.
page=page.replace('pressure shell cutaway + 6 acceleration seats',
                  '37 outer panes + seamless dome + source floor + 6 seats')
page=page.replace('I4 · Structure cutaway','Full L1 · fit rebuild')
# Fit overlay now is just a reference outline, so no false claims of fully safe.
page=page.replace("This is one authored room concept, not yet fitted to Wayfarer's actual pressure hull.",
                  'This candidate passes limited plan-footprint checks against the source floor, but is NOT yet a qualified, fitted flight deck.')
# Default camera higher and zoom out to show complete crown in one image.
page=page.replace('zoom:.67,','zoom:.94,',1).replace('state.zoom=.67;','state.zoom=.94;')
# Older default static fallback gets regenerated below with full canopy screenshot.
img=HERE/'out/l1_i4_full_fit_canopy_preview.png'
if img.exists():
 raw='data:image/png;base64,'+base64.b64encode(img.read_bytes()).decode()
 page=re.sub('src="data:image/png;base64,[^"]+"','src="'+raw+'"',page,count=1)
out=HERE/'out/wayfarer_l1_i4_full_trapezoid_dome_constrained_android.html'
out.write_text(page)
print('BUILT',out,'BYTES',out.stat().st_size,'PANELS',sum([1,12,12,12]))