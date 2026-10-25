import json,math,sys
sys.path.insert(0,'/tmp/wayfarer-v05-review/wayfarer_v0_5_record')
import build_v05 as B
from certify import ray_density
G=json.load(open('/tmp/wayfarer-v05-review/wayfarer_v0_5_record/out/wayfarer_v05_geometry.json'))
items=[]
for p in G['parts']+G['fluids_by_state']['S5']:
 if 'shuttle' in p.get('tags',[]) or p['volume_m3']<=0:continue
 sh=B.shape_from_spec(p['shape']);items.append((sh,p['mass_t']/p['volume_m3'],sh.bbox()))
N=600;dirs=[]
for i in range(N):
 z=1-2*(i+.5)/N;rr=math.sqrt(1-z*z);ph=i*math.pi*(3-math.sqrt(5));dirs.append((z,rr*math.cos(ph),rr*math.sin(ph)))
# Physical occupied envelopes: radial bunk length 2m from r2.05 to4.05, tangential width .75m, tier center x6.5/7.55.
# Include bunk center and inner/outer body extremes; test corners of person centerline rather than full furniture.
angles=[169,221,259,311,360,420]
origins=[]
for a in angles:
 for x in (6.45,7.55):
  for rad in (2.25,3.05,3.85):
   th=math.radians(a);origins.append((f'{a}:{x}:{rad}',(x,rad*math.cos(th),rad*math.sin(th))))
for thickness in (0,.05,.08,.1):
 layer=B.Sector(5.9,8.2,4.15-thickness,4.15,0,360) if thickness else None
 sample=items+([(layer,1.,layer.bbox())] if layer else [])
 vals=[]
 for label,o in origins:
  scores=[ray_density(o,d,sample,.02,65) for d in dirs]
  vals.append((min(scores),label,dirs[scores.index(min(scores))]))
 vals.sort()
 print('layer_cm',round(thickness*100),'mass_t',round(math.pi*(4.15**2-(4.15-thickness)**2)*2.3,3),'worst',round(vals[0][0],2),'failing',sum(v[0]<40 for v in vals),'of',len(vals),'worst_samples',[(round(v,2),label) for v,label,_ in vals[:6]],flush=True)
