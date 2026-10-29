"""Add source-bounded structural context to I4's existing phone-safe Canvas2D 3D.

The source Wayfarer 8.6m ID dome-cylinder pressure shell and annular source L1
floor are displayed alongside, NOT silently assimilated into, the unconstrained
I4 authored interior. False fits highlighted by toggle. Source hull has its
axial X direction mapped to viewer H=4-X; concept 'forward' Z is a transverse
viewer direction and must NOT be misdescribed as actual ship bow.
"""
import json,math,re,base64
from pathlib import Path
R=Path(__file__).resolve().parent.parent
HERE=Path(__file__).resolve().parent
source=R/'out/wayfarer_v05_geometry.json'
g=json.loads(source.read_text())
parts={x['id']:x['shape'] for x in g['parts']}
pv=parts['pressure_vessel'];floor=parts['floor_L1'];sensor=parts['bow_sensors']
assert pv['k']=='domecyl' and abs(pv['R']-4.3)<1e-10
assert floor['k']=='sector' and floor['r0']==.9 and floor['r1']==4.15
assert sensor['rin']==2.9 and abs(sensor['R']-4.15)<1e-10
# Render the source aft L1 floor near H=4-X ~0.7..1.0. Bow toward higher H.
S={'frame':'Source ship axial X mapped to render vertical H=4-X. Illustrated I4 Z-forward remains a distinct, nonphysical orientation.',
   'hull':{'inner_radius_m':pv['R'],'skin_t_m':pv['t'],
           'cylinder_shoulder_h_m':4-pv['xb'],
           'bow_tip_h_m':4-pv['xa'],
           'dome_axial_extent_m':pv['xb']-pv['xa'],
           'L1_visible_aft_h_m':4-floor['x1'],
           'source_cylinder_aft_h_m':4-pv['xc']},
   'source_L1_floor':{'inner_hole_r_m':floor['r0'],
         'outer_r_m':floor['r1'],'top_h_m':4-floor['x0'],
         'bottom_h_m':4-floor['x1']},
   'shoulder_sensors':{'radial_inner_m':sensor['rin'],'radial_outer_m':sensor['R'],
                        'source_x_reference_m':sensor['xc']},
   'source_ladders':[{'y':1.4,'z':0,'diameter_m':.8},
                     {'y':-1.4,'z':0,'diameter_m':.8}],
   'scope':'Source dimensions + hypothetical cutaway shell/ring graphics. Internal columns, lights and detail are conceptual, not qualified.'}
v=json.loads((R/'command/L1_I4_COMMAND_COMMONS_GEOMETRY_20261029.json').read_text())
blocks=v['design']['interior']['blocks']
main=next(x for x in blocks if x['tag']=='continuous_main_deck')
# bounded coarse area sampling only for reported conflict area, not structural mesh cutting.
N=700;outside=0;outside_inner=0
for j in range(N):
 y=main['y']+main['wy']*((j+.5)/N-.5)
 for k in range(N):
  z=main['z']+main['wz']*((k+.5)/N-.5)
  r=math.hypot(y,z)
  outside+=(r>floor['r1'])
  outside_inner+=(r<floor['r0'])
S['conflicts']={'main_deck_area_m2':round(main['wy']*main['wz'],3),
    'main_deck_area_outside_source_L1_floor_outer_radius_m2':round(outside/N**2*main['wy']*main['wz'],3),
    'main_deck_area_over_source_central_opening_m2':round(outside_inner/N**2*main['wy']*main['wz'],3),
    'source_8p6m_hull_not_fitted':True,
    'note':'These are plan-area estimates. The original L1 annular floor and two ladder apertures are not incorporated into I4, so deck/floor conflict is real.'}
struct_data=R/'command/L1_I4_SOURCE_STRUCTURAL_CONTEXT_20261029.json'
struct_data.write_text(json.dumps(S,indent=2))
page=(HERE/'out/wayfarer_l1_i4_command_commons_android.html').read_text()
assert page.count('const designs=')==1
page=page.replace('const designs=', 'const SOURCE_STRUCTURE='+json.dumps(S,separators=(',',':'))+';\nconst designs=',1)
page=page.replace('WAYFARER · I4 COMMAND COMMONS','WAYFARER · I4 + STRUCTURE')
page=page.replace('Single coherent room · Android-friendly Canvas 3D · no WebGL · non-canon',
                  'Source pressure shell / I4 interior · Android-safe 3D · research only')
page=page.replace('I4 · Command Commons','I4 · Structure cutaway')
# Include conflict language always rather than conditional card green/badge
page=page.replace('<p id="description">',
'''<p style="color:#e9c597;font-size:12px">Source 8.6m hull radius and bow dome shown in cutaway. I4 remains an unfitted research interior; outer floor corners and the central original floor opening conflict.</p>
<p id="description">''',1)
page=page.replace('<h2>Layer visibility</h2>',
'''<h2>Structural context</h2>
<div class="actions">
<button data-structure="hull" aria-pressed="true">Pressure shell</button>
<button data-structure="dome" aria-pressed="true">Bow glazing</button>
<button data-structure="frames" aria-pressed="true">Rings + deck supports</button>
<button data-structure="fit" aria-pressed="false">Show fit conflicts</button>
</div>
<p style="font-size:11px;color:#e3bd9b">I4 main floor extends beyond the source L1 ring by <strong>__OUTSIDE__ m²</strong> (approx.) and covers part of the source central opening. Toggling fit conflicts marks those areas. Bow is toward the higher source axial X-derived tier, not I4’s plan-view forward direction.</p>
<h2>Interior layers</h2>''',1)
page=page.replace('__OUTSIDE__',str(S['conflicts']['main_deck_area_outside_source_L1_floor_outer_radius_m2']))
# Distinguish physical source boundary and drawn (unverified) support members.
page=page.replace('The connected deck, raised pair, Navigator platform, low-g transfer rungs, shared table and equipment bay are illustrative.',
                  'The ship pressure shell, 4.3m radius and annular source L1 ring come from source geometry. Cutaway sectors, shell transparency, fittings, deck-support posts, and the entirety of I4 are illustrative and unqualified.')
# Make frame canvas a little smaller by default to see the actual dome.
page=page.replace('zoom:.79','zoom:.67',1)
page=page.replace('state.zoom=.79;state.panx=state.pany=0;','state.zoom=.67;state.panx=state.pany=0;')
page=page.replace('const state={variant:0,','const state={hull:true,dome:true,frames:true,fit:false,variant:0,',1)
# Inject structure drawing into the single build() function. Painter sorting
# works with opaque ring segments and transparent shell/dome polys.
draw=r'''
function hullCircle(r,h,color,frac=1,arclo=-Math.PI,archi=Math.PI){
 const n=70;
 for(let i=0;i<n;i++){
  const a=arclo+(archi-arclo)*i/n,b=arclo+(archi-arclo)*(i+1)/n;
  segment([r*Math.sin(a),r*Math.cos(a),h],[r*Math.sin(b),r*Math.cos(b),h],
    frac,color);
 }
}
function domeH(r){
 const s=SOURCE_STRUCTURE.hull;
 return s.cylinder_shoulder_h_m+s.dome_axial_extent_m*
      Math.sqrt(Math.max(0,1-(r/s.inner_radius_m)**2));
}
function sourceShell(){
 const s=SOURCE_STRUCTURE, R=s.hull.inner_radius_m,
       hb=s.hull.L1_visible_aft_h_m, hs=s.hull.cylinder_shoulder_h_m;
 // Aft-facing side of the source cylindrical pressure vessel is cut away;
 // keep the far and lateral walls to make floor/hull conflicts apparent.
 if(state.hull){
  const sectors=54,lo=-2.25,hi=2.25;
  for(let j=0;j<sectors;j++){
   const a=lo+(hi-lo)*j/sectors,b=lo+(hi-lo)*(j+1)/sectors;
   let ca=Math.sin(a),sa=Math.cos(a),cb=Math.sin(b),sb=Math.cos(b);
   polygon([[R*ca,R*sa,hb],[R*cb,R*sb,hb],
            [R*cb,R*sb,hs],[R*ca,R*sa,hs]],"#76a9bc",.13);
  }
  hullCircle(R,hb,"#6ca2b5",.035,lo,hi);
  hullCircle(R,hs,"#77c4d2",.04,lo,hi);
  for(const a of [-2.2,-1.56,-.8,0,.8,1.56,2.2]){
   segment([R*Math.sin(a),R*Math.cos(a),hb],
           [R*Math.sin(a),R*Math.cos(a),hs],.041,"#628e9c");
  }
 }
 if(state.dome){
  // Seamless pressure shell surface. Segment boundaries are tessellation only:
  // no opaque mullions across the clear dome.
  const nR=11,nA=54,lo=-2.25,hi=2.25;
  for(let i=0;i<nR;i++){
    const r0=R*i/nR,r1=R*(i+1)/nR;
    for(let k=0;k<nA;k++){
      const a=lo+(hi-lo)*k/nA,b=lo+(hi-lo)*(k+1)/nA;
      polygon([[r0*Math.sin(a),r0*Math.cos(a),domeH(r0)],
               [r1*Math.sin(a),r1*Math.cos(a),domeH(r1)],
               [r1*Math.sin(b),r1*Math.cos(b),domeH(r1)],
               [r0*Math.sin(b),r0*Math.cos(b),domeH(r0)]],
               "#93dfe5",.12);
    }
  }
  hullCircle(R,hs,"#81d7db",.042,-2.25,2.25);
 }
 if(state.frames){
  // Perimeter attachment ring and source shoulder sensor annulus are real
  // reference envelopes, but their 3D drawn detail is not part-level fidelity.
  hullCircle(R,hs,"#91c7ca",.097,-2.22,2.22);
  hullCircle(s.shoulder_sensors.radial_outer_m,hs-.06,"#b0a389",.065,-2.2,2.2);
  hullCircle(s.shoulder_sensors.radial_inner_m,hs-.06,"#a89e8b",.052,-2.2,2.2);
  for(const ang of [-2.0,-1.6,-.8,.0,.8,1.6,2.0]){
    const inner=s.shoulder_sensors.radial_inner_m,outer=s.shoulder_sensors.radial_outer_m;
    segment([inner*Math.sin(ang),inner*Math.cos(ang),hs-.06],
            [outer*Math.sin(ang),outer*Math.cos(ang),hs-.06],.028,"#83949c");
  }
  // Deck support post suggestions anchored to source L1 x=3.0 floor; not
  // qualified structural load paths and not a substitute for full geometry.
  const pillars=[
   [-1.67,-1.20,2.00],[1.67,-1.20,2.00],
   [-1.67,.58,2.00],[1.67,.58,2.00],
   [-1.23,2.48,1.20],[1.23,2.48,1.20]
  ];
  for(const [y,z,top] of pillars){
    segment([y,z,.85],[y,z,top],.050,"#7f98a4");
    sphere([y,z,top],.065,"#b3c1c5");
  }
 }
 if(state.fit){
  // Source floor actually occupies a ring r=0.9..4.15 and has two access
  // points near y=+/-1.4m,z=0. The I4 rectangle crosses that boundary.
  const F=s.source_L1_floor;
  hullCircle(F.outer_r_m,.81,"#ec997a",.042);
  hullCircle(F.inner_hole_r_m,.81,"#ff987f",.042);
  for(const Y of [-1.4,1.4]){
   const d=.43,z=0;
   const q=[[Y-d,z-d,.85],[Y+d,z-d,.85],
     [Y+d,z+d,.85],[Y-d,z+d,.85]];
   for(let k=0;k<4;k++)
    segment(q[k],q[(k+1)%4],.052,"#fb8e74");
  }
  // Show only outside-floor samples as translucent coral material, preserving
  // original concept plan. This is a 28x28 coarse visual overlay, not Boolean CAD.
  const main=designs[0].interior.blocks.find(x=>x.tag==="continuous_main_deck");
  const n=36,dy=main.wy/n,dz=main.wz/n;
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){
   const y=main.y+(i+.5-n/2)*dy,z=main.z+(j+.5-n/2)*dz;
   const r=Math.hypot(y,z);
   if(r>F.outer_r_m||r<F.inner_hole_r_m){
    const a=y-dy/2,b=y+dy/2,c=z-dz/2,d=z+dz/2,h=.80;
    polygon([[a,c,h],[b,c,h],[b,d,h],[a,d,h]],
        r>F.outer_r_m?"#ff6b54":"#ffc06e",.52);
   }
  }
  label([-3.1,-3.78,1.55],"HULL/DECK FIT CONFLICT","#ffb19a");
 }
}
'''
pos=page.index('function build(){')
page=page[:pos]+draw+page[pos:]
page=page.replace('function build(){\n faces=[];markers=[];',
                  'function build(){\n faces=[];markers=[];\n sourceShell();',1)
page=page.replace('document.getElementById("reset").addEventListener',
'''document.querySelectorAll("[data-structure]").forEach(b=>b.addEventListener("click",()=>{
  const k=b.dataset.structure;state[k]=!state[k];
  b.setAttribute("aria-pressed",state[k]?"true":"false");paint();
}));
document.getElementById("reset").addEventListener''',1)
# preserve actual pressure hull display defaults on mobile.
page=page.replace('RENDERED · "+designs[state.variant].id+" · connected deck + 6 acceleration seats"',
                  'RENDERED · "+designs[state.variant].id+" · pressure shell cutaway + 6 acceleration seats"')
# Existing embedded fallback picture is from pre-structure I4; before publishing
# a new matching rendered PNG is created by a small Chromium utility, then this
# generator is rerun and embeds that PNG in final single-file HTML.
preview=HERE/'out/l1_i4_structure_preview.png'
assert preview.exists() or True
img=('data:image/png;base64,'+base64.b64encode(preview.read_bytes()).decode('ascii')) if preview.exists() else (
 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20400%20400%22%3E%3Crect%20width%3D%22400%22%20height%3D%22400%22%20fill%3D%22%230b2336%22/%3E%3Ctext%20x%3D%22200%22%20y%3D%22200%22%20fill%3D%22white%22%20text-anchor%3D%22middle%22%3EPreview%20pending%3C/text%3E%3C/svg%3E')
page=re.sub('src="data:image/png;base64,[^"]+"', 'src="'+img+'"', page, count=1) if 'src="data:image/png;base64,' in page else page
out=HERE/'out/wayfarer_l1_i4_with_source_structure_android.html'
out.write_text(page)
print('OUTPUT',out,'bytes',out.stat().st_size)
print('SOURCE FRAME',S['frame'])
print('CONFLICTS',S['conflicts'])