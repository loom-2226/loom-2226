"""Five source-based 3D L1 crew layout finalists, selectable in one offline viewer.

Source renderer from make_l1_full_3d_current_canopy.py, same 37 outer
panels and source geometry. Replaces the old command meshes ONLY inside
this viewer with a compact contoured seat visual model + actual standing
console and controls. Data: executed 500-candidate bounded sweep.
"""
from pathlib import Path
import json,re,subprocess
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
base=HERE/'out/wayfarer_l1_full_3d_37panel_optogel.html'
R=json.loads((ROOT/'command/l1_crew_layout_iteration_20261029_results.json').read_text())
assert R['sample_count']==500 and len(R['visual_finalists_5'])==5
assert len(R['operational_proxy_finalists_2'])==2
src=base.read_text()
src=src.replace('function commandMeshes(sc, opt = {})','function commandMeshesLegacy(sc, opt = {})',1)
assert 'function commandMeshesLegacy' in src
# Need renderer MATS for physically differentiated seat forms, not bed slabs.
src=src.replace('const DATA=',r'''// Viewer-specific custom command meshes. The source L1 geometry and
// ladders remain; the earlier elongated couches are *not* drawn.
MATS.l1_seat_shell={c:[.15,.24,.32],m:.45,r:.30,em:[.004,.007,.012],nosec:1};
MATS.l1_seat_pad={c:[.12,.38,.43],m:0,r:.70,em:[.005,.010,.011],nosec:1};
MATS.l1_harness={c:[.82,.62,.23],m:.12,r:.55,nosec:1};
MATS.l1_control={c:[.04,.26,.32],m:.4,r:.15,em:[.008,.04,.06],nosec:1};
MATS.l1_shared={c:[.08,.42,.55],m:.45,r:.22,em:[.04,.07,.12],nosec:1};
function commandMeshes(sc,opt={}){
 const G=commandMeshesLegacy({...sc,couches:[],displays:[]},opt);
 const mb=mat=>(G[mat] ||= new MB(opt.xc));
 const uN=v=>v.map(x=>x/Math.hypot(...v));
 const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 for(const s of sc.couches){
  const u=uN([0,s.feet[0]-s.head[0],s.feet[1]-s.head[1]]),side=[0,-u[2],u[1]],normal=[-1,0,0];
  const P=(long,lat,face)=>[s.base_x-face,s.head[0]+u[1]*long+side[1]*lat,s.head[1]+u[2]*long+side[2]*lat];
  const block=(mat,s0,s1,w0,w1,t0,t1)=>{
   meshOBox(mb(mat),P((s0+s1)/2,(w0+w1)/2,(t0+t1)/2),[u,side,normal],
          [(s1-s0)/2,(w1-w0)/2,(t1-t0)/2]);
  };
  // Anatomically suggested segmented tub seat; separately supported head,
  // torso, hips, bent knees and raised feet. No flat 2.1m couch.
  block('l1_seat_shell',.02,.30,-.28,.28,.13,.31);
  block('l1_seat_pad',.08,.28,-.21,.21,.29,.40);
  block('l1_seat_shell',.28,.89,-.33,.33,.10,.26);
  block('l1_seat_pad',.31,.86,-.27,.27,.24,.36);
  block('l1_seat_shell',.88,1.15,-.30,.30,.11,.27);
  block('l1_seat_pad',.91,1.14,-.25,.25,.25,.38);
  block('l1_seat_shell',1.15,1.36,-.26,.26,.25,.41);
  block('l1_seat_pad',1.15,1.34,-.20,.20,.38,.50);
  block('l1_seat_shell',1.36,1.56,-.23,.23,.19,.31);
  block('l1_seat_pad',1.38,1.54,-.19,.19,.31,.43);
  for(let sign of [-1,1]){
   block('l1_seat_shell',.24,.88,sign*.30-.025,sign*.30+.025,.23,.45);
   block('l1_seat_shell',.035,.29,sign*.245-.045,sign*.245+.045,.27,.50);
   // shape-bearing cradle support and forearm controller mount
   meshTube(mb('rail'),{p0:P(.50,sign*.35,.22),p1:P(.85,sign*.35,.35),r:.018},8);
   meshOBox(mb('l1_control'),P(.79,sign*.40,.54),[u,side,normal],[.11,.09,.04]);
   meshTube(mb('l1_harness'),{p0:P(.39,sign*.25,.38),p1:P(.67,-sign*.02,.52),r:.017},8);
  }
  // Contoured structure supports a seated person through their back under +g.
  meshTube(mb('l1_seat_shell'),{p0:P(.25,0,.10),p1:P(1.20,0,.10),r:.047},10);
  meshTube(mb('rail'),{p0:P(.90,0,.1),p1:[s.base_x-.01,...P(.90,0,.1).slice(1)],r:.05},10);
  if((opt.hideCrew||new Set()).has(s.id))continue;
  meshSphere(mb('helmet'),P(.16,0,.57),.15,12);
  meshTube(mb('crew'),{p0:P(.36,0,.49),p1:P(.94,0,.49),r:.155},12);
  meshSphere(mb('crew'),P(.92,0,.50),.15,10);
  for(let sign of [-1,1]){
   meshTube(mb('crew'),{p0:P(.41,sign*.155,.52),p1:P(.79,sign*.31,.52),r:.064},9);
   meshSphere(mb('crew'),P(.82,sign*.32,.56),.075,9);
   meshTube(mb('crew'),{p0:P(1.00,sign*.09,.51),p1:P(1.28,sign*.12,.65),r:.09},10);
   meshTube(mb('crew'),{p0:P(1.28,sign*.12,.65),p1:P(1.51,sign*.12,.46),r:.073},9);
  }
 }
 for(const d of sc.displays){
  const c=d.center_xyz,seat=sc.couches.find(s=>s.id===d.for_station);
  if(!seat)continue;
  const n=uN(seat.eye.map((v,i)=>v-c[i])),u=uN([0,seat.feet[0]-seat.head[0],seat.feet[1]-seat.head[1]]);
  let lateral=[0,-u[2],u[1]];
  const vdot=lateral.reduce((a,b,i)=>a+b*n[i],0);
  lateral=uN(lateral.map((x,i)=>x-vdot*n[i]));
  const vertical=cross(n,lateral);
  meshOBox(mb('screen'),c,[lateral,vertical,n],[d.half_width_m,d.half_height_m,.014]);
  meshOBox(mb('l1_seat_shell'),c.map((v,i)=>v-.025*n[i]),[lateral,vertical,n],[d.half_width_m+.015,d.half_height_m+.018,.012]);
  meshTube(mb('rail'),{p0:c.map((v,i)=>v-.04*n[i]),p1:[seat.base_x-.08,c[1],c[2]],r:.017},9);
 }
 if(sc.stand){
  const [y,z]=sc.stand.anchor_yz;
  // genuine 0g-anchored command position, NOT a seventh acceleration seat.
  const floor=3.,x=2.36;
  for(let dy of [-.16,.16]){
   meshOBox(mb('l1_seat_shell'),[floor-.035,y+dy,z],[[1,0,0],[0,1,0],[0,0,1]],[.032,.11,.13]);
   meshTube(mb('rail'),{p0:[floor-.12,y+dy,z],p1:[x,y+dy,z+.11],r:.014},8);
  }
  for(let dy of [-.4,.4]){
   meshTube(mb('rail'),{p0:[2.50,y+dy,z+.12],p1:[2.05,y+dy,z+.45],r:.026},10);
  }
  meshOBox(mb('l1_shared'),[2.05,y,z+.45],[[0,1,0],[0,0,1],[-1,0,0]],[.55,.27,.035]);
  meshOBox(mb('l1_control'),[2.28,y,z+.19],[[0,1,0],[0,0,1],[-1,0,0]],[.30,.09,.048]);
 }
 return G;
}
const DATA=''',1)
# Replace source DATA literal with augmented candidates; keep all original payload.
m=re.search(r'const DATA=(\{.*?\});\nconst G=DATA\.geo,C=DATA\.cmd;',src,re.S)
assert m,'DATA and scene variables expected'
payload=json.loads(m.group(1))
payload['designs']=[{'id':r['id'],'layout':r['layout'],'screens':r['screens'],
                     'proxy':r['coarse'],'path':r['path'],
                     'sightline':r['sightline'],'scenario_proxy':r['scenario_proxy'],
                     'detailed_gate_pass':all(r['critical_consistency'].values())}
                   for r in R['visual_finalists_5']]
src=src[:m.start()]+ 'const DATA='+json.dumps(payload,separators=(',',':'))+';\nconst G=DATA.geo;let C=DATA.cmd;'+src[m.end():]
# Replace view draw labeling strings and insert variant control row near camera.
src=src.replace('<h2>Camera / views</h2>',
'''<h2>Five computational finalists · select one</h2>
<div class="line" id="variantBtns">
<button class="chip" data-variant="0" aria-pressed="true">1 · selected</button>
<button class="chip" data-variant="1" aria-pressed="false">2</button>
<button class="chip" data-variant="2" aria-pressed="false">3</button>
<button class="chip" data-variant="3" aria-pressed="false">4</button>
<button class="chip" data-variant="4" aria-pressed="false">5</button>
</div><p class="note" id="variantInfo">Five measured geometric alternatives; no human-in-loop validation.</p>
<h2>Camera / views</h2>''',1)
src=src.replace('Source-based six-station interior · held 37 protective tiles · optogel seamless-canopy research overlay',
                '500→20→5 crew-function design search · five 3D finalists · held 37-panel research canopy')
src=src.replace('six source-positioned crew stations, occupants', 'six revised workstations, occupants')
# Bypass old code 'commandMeshes' transformation assumptions if source changed
src=src.replace("if(opts.view==='STAND')return [[2.05,0,1.4],[-1,0,0],[0,0,1]];",
                "if(opts.view==='STAND')return [C.stand.eye_xyz,[-1,0,0],[0,0,1]];",1)
# Add datum and remove bed visual.
src=src.replace("cmd:C,cmdHideCrew:", "cmd:C,cmdHideCrew:",1)
# insert design switch function before final invocation
needle='rebuild();resize();redraw();\n</script>'
assert needle in src
src=src.replace(needle,'''let selectedDesign=0;
function adoptDesign(i){
  selectedDesign=i;
  const k=DATA.designs[i];C={...DATA.cmd,
    couches:k.layout.seats.map(s=>({id:s.id,role:s.role,base_x:s.base_x,head:s.head,feet:s.feet,L:s.L,eye:s.eye})),
    displays:k.screens,stand:k.layout.stand};
  document.querySelectorAll('[data-variant]').forEach(b=>b.setAttribute('aria-pressed',+b.dataset.variant===i?'true':'false'));
  const p=k.layout.settings;
  document.getElementById('variantInfo').textContent=k.id+
    ' · support seats '+Math.round(p.radial_in_m*100)+'cm inward · orientation '+p.chair_yaw_deg.toFixed(1)+'° · standing anchor (y '+p.stand_y_m.toFixed(2)+', z '+p.stand_z_m.toFixed(2)+')m · min Pilot/NAV ideal forward view '+Math.round(k.sightline.PILOT.forward_cone_60_fraction*100)+'% (geometric upper bound)';
  rebuild();
}
document.querySelectorAll('[data-variant]').forEach(b=>b.addEventListener('click',()=>adoptDesign(+b.dataset.variant)));
adoptDesign(0);resize();redraw();
</script>''',1)
# Update text to be honest; prior source currently says no built station.
src=src.replace('the cockpit, consoles, occupants', 'the command level, controls, occupants')
src=src.replace('The cockpit, consoles, occupants, flight deck, floor and ladders come from the L1 model.',
'''The six station anchor points, flight deck, floor and ladders originate with the L1 model.
The newly contoured seats, physical standing console, shared surface and screens are
NON-CANON geometry derived from the five shortlisted candidates.''')
src=src.replace('all dimensions in metres · Crew/furniture from source Rev 7',
                'all dimensions in metres · crew positions from search; ship shell from source Rev 7')
src=src.replace('6 (2 flight + 4 support)','6 · Kazbek-inspired contoured')
src=src.replace('No change to structural hull', 'No change to structural hull')
out=HERE/'out/wayfarer_l1_500_search_five_3d_finalists.html'
out.write_text(src)
print('HTML',out,'bytes',out.stat().st_size,'5 variants',len(payload['designs']))