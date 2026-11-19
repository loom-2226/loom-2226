#!/usr/bin/env python3
"""B4-S source-hash D9. Exact #563 installed BReps + authored rolled B4-S
convex collision hull. Rechecks all installed pairs under unchanged criteria.
Original BReps are NOT re-exported or recreated, especially the pressure vessel.
"""
import argparse,hashlib,json,subprocess,sys,math
from pathlib import Path
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
from build123d import Solid
HERE=Path(__file__).resolve().parent
LAB=HERE.parent
ROOT=LAB.parent
sys.path.insert(0,str(LAB/"metric_nodes"))
sys.path.insert(0,str(LAB))
import nacelle_d9_pair as N
import d9_sharded as D
P,T=D.P,D.T
PREVIOUS_COMMIT="f629364bc9629bbc0858c1a4c1028505379e909d"
PREVIOUS_SHA="f83939a5f2b959e7289f5f6fb584fc21fe475bd0980266f56a6e124dd1f985d0"
SOURCE_DIR=LAB/"metric_nodes/nacelle_candidates"
PRIOR=LAB/"metric_nodes/nacelle_candidates/pr563_D9_NACELLE_TWO_STATE_REPORT.json"
RESULT=ROOT/"results/out/b4s_d9"
FINAL=ROOT/"results/out/D9_B4S_TWO_STATE_REPORT.json"
GEO=ROOT/"results/out/wayfarer_v05_geometry.json"
CONF=ROOT/"config/cert_criteria.json"
STATES=("torch","Metric")

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def output(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")

def source():
 G=read(GEO);C=read(CONF)
 past_bytes=subprocess.check_output(["git","show",f"{PREVIOUS_COMMIT}:wayfarer/results/out/wayfarer_v05_geometry.json"],cwd=ROOT.parent)
 assert hashlib.sha256(past_bytes).hexdigest()==PREVIOUS_SHA
 O=json.loads(past_bytes)
 assert G['dry_t']==O['dry_t']==868.1922552640087
 assert C["D9"]["min_intersection_m3"]==0.01
 assert all(G["thrust_line_offset_m"][k]==O["thrust_line_offset_m"][k]==v for k,v in (("y",.03),("z",-.26)))
 old={p["id"]:p for p in O['parts']}
 new={p["id"]:p for p in G['parts']}
 assert old.keys()==new.keys()
 assert len(new)==328
 assert G['fluids_by_state']==O['fluids_by_state']
 assert G['metric_states'].keys()==O['metric_states'].keys()
 for n in old:
  a,b=old[n],new[n]
  if n!="shuttle":
   assert (a["shape"],a["mat"],a["tags"])==(b["shape"],b["mat"],b["tags"]),("nonshuttle_changed",n)
  else:
   assert a['shape']['k']=='tube' and b['shape']['k']=='polyhull' and 'b4s_rolled90' in b['tags']
   assert abs(b['mass_t']-36.48)<1e-8
 # Ensure no source physical part other than the shuttle has been moved.
 assert G["plant_node_booking"]==O["plant_node_booking"]
 assert read(PRIOR)["pass"] is True
 assert read(PRIOR)["geometry_sha256"]==PREVIOUS_SHA
 return G,O,C

def hull(shape):
 assert shape["k"]=="polyhull"
 verts=shape["vertices"];faces=shape["triangles"]
 center=[sum(v[k] for v in verts)/len(verts) for k in range(3)]
 sew=BRepBuilderAPI_Sewing(1e-6)
 for face in faces:
  a,b,c=(verts[i] for i in face)
  # Authored triangles are already outward as verified by hull generator.
  poly=BRepBuilderAPI_MakePolygon()
  for v in (a,b,c):poly.Add(gp_Pnt(*v))
  poly.Close()
  sew.Add(BRepBuilderAPI_MakeFace(poly.Wire()).Face())
 sew.Perform()
 solid=BRepBuilderAPI_MakeSolid(TopoDS.Shell(sew.SewedShape())).Solid()
 assert BRepCheck_Analyzer(solid).IsValid()
 sh=Solid(solid)
 assert sh is not None and sh.is_valid and sh.volume>0
 assert abs(sh.volume-86.50582706110434)<1e-6,sh.volume
 return sh

def context(state):
 G,O,C=source()
 bas=N.read(N.OLD)
 shapes,factor=N.import_candidate(state,bas)
 assert factor==.001 and len(shapes)==335
 # The 194 #559 installed BReps and 20 #563 STEP-overlay BReps are the same
 # immutable bytes used in the earlier independent paired PASS.
 m=read(SOURCE_DIR/"candidate_manifest.json")
 assert m['states'][state]['base_step_sha']==sha(LAB/"packing_phase1b/current_g3_3p8_forward.step.gz")
 assert m['states'][state]['step_sha']==sha(SOURCE_DIR/f"candidate_{state}.step.gz")
 assert m['approved_protected_pressure_BRep_is_reused_byte_for_byte'] is True
 row=next(p for p in G['parts'] if p['id']=='shuttle')
 new=hull(row["shape"]);new.label="dry:shuttle"
 shapes["dry:shuttle"]=new
 names=sorted(["dry:"+p["id"] for p in G["parts"] if "no_render" not in p['tags']]
              +[f"S1:{p['id']}:{i:02d}" for i,p in enumerate(G['fluids_by_state']['S1']) if "no_render" not in p['tags']])
 assert len(names)==214 and len(set(names))==214
 assert set(names)<=set(shapes)
 assert sum(n.startswith('dry:metric_') for n in names)>=20
 assert all(read(PRIOR)['states'][state][q] for q in ('pass',))
 return G,O,C,shapes,names,new

def screen(state):
 G,O,C,shapes,names,shuttle=context(state)
 b=P.bounds(shuttle)
 clashes=[];err=[];touches=[]
 for n in names:
  if n=="dry:shuttle":continue
  s=shapes[n]
  if P.bbox_intersection_upper(b,P.bounds(s))<=.01:continue
  try:
   intersection=shuttle&s
   if intersection is None:continue
   vol=float(intersection.volume)
   if vol<=.01:continue
   cat,reason=T.classify({"a":"dry:shuttle","b":n})
   rec=dict(other=n,volume_m3=round(vol,9),category=cat,why=reason)
   touches.append(rec)
   if cat=="d":clashes.append(rec)
  except Exception as e:err.append(dict(other=n,error=repr(e)))
 out=dict(state=state,geometry_sha256=sha(GEO),shuttle_brep_valid=True,
          conservative_collision_hull_m3=shuttle.volume,
          compared_other_installed_solids=len(names)-1,intersections=touches,
          category_d=clashes,errors=err,pass_=not clashes and not err)
 out['pass']=out.pop('pass_')
 output(RESULT/f"screen_{state}.json",out)
 print('B4S_D9_DELTA_SCREEN',state,'PASS',out['pass'],'touches',touches,'errors',err,flush=True)
 return 0 if out["pass"] else 1

def pairs(state,shard,shards):
 assert shards==8 and 0<=shard<shards
 G,O,C,shapes,names,new=context(state)
 tot=len(names)*(len(names)-1)//2
 assert tot==22791
 lo,hi=tot*shard//shards,tot*(shard+1)//shards
 before=D.pair_scan(shapes,names,lo,hi,.01)
 # The old #563 source shape/water accounting remains unchanged, including
 # the independent S1 water debit. Test the forward-debited state too.
 meta=read(LAB/"packing_phase1b/frozen_research_3p8_forward.json")
 I=read(ROOT/"config/wayfarer_v05_inputs.json")
 ratio=I['states']['S1']['remass_t']/meta['masses']['core_R_t']
 post=dict(shapes)
 for name in names:
  if name.startswith("S1:water_"):
   post[name]=D.D.trim_liquid_forward(post[name],ratio)
 after=D.pair_scan(post,names,lo,hi,.01)
 ok=all(x['category_d_count']==0 and not x['collision_errors'] for x in (before,after))
 result=dict(state=state,shard=shard,shards=shards,
             geometry_sha256=sha(GEO),
             source_step_sha256=sha(LAB/"packing_phase1b/current_g3_3p8_forward.step.gz"),
             nacelle_overlay_sha256=sha(SOURCE_DIR/f"candidate_{state}.step.gz"),
             threshold_m3=.01,range=[lo,hi],total_pairs=tot,before=before,after=after,
             pass_=ok)
 result['pass']=result.pop('pass_')
 output(RESULT/state/f"pairs-{shard}.json",result)
 print('B4S_D9_PAIRS',state,shard,result['pass'],
       before['category_d_count'],after['category_d_count'],flush=True)
 return 0 if ok else 1

def merge():
 G,O,C=source()
 sha_now=sha(GEO)
 states={}
 for state in STATES:
  shards=[read(RESULT/state/f"pairs-{i}.json") for i in range(8)]
  delta=read(RESULT/f"screen_{state}.json")
  assert delta['pass'] and delta['geometry_sha256']==sha_now
  assert all(s['geometry_sha256']==sha_now and s['threshold_m3']==.01 for s in shards)
  assert all(s['pass'] for s in shards)
  assert [s['range'] for s in shards]==[[22791*i//8,22791*(i+1)//8] for i in range(8)]
  assert sum(s[x]['pair_count'] for s in shards for x in ('before',))==22791
  assert sum(s[x]['pair_count'] for s in shards for x in ('after',))==22791
  d=sum(s['before']['category_d_count']+s['after']['category_d_count'] for s in shards)
  errors=[e for s in shards for k in ('before','after') for e in s[k]['collision_errors']]
  states[state]=dict(pass_=d==0 and not errors,pairs_per_assembly=22791,
          original_protected_solids=194,new_nacelles=20,
          shuttle_replaced=1,category_d_intersections=d,errors=errors,
          unchanged_primary_members_from_pr563=43,
          inherited_prior_pair_pass=read(PRIOR)['states'][state]['pass'],
          changed_source_shape='dry:shuttle only',
          source_assembly='byte-identical #559 base 315 BReps plus #563 20 state STEP overlay, dry:shuttle substituted with rolled B4-S source convex hull')
  states[state]['pass']=states[state].pop('pass_')
 assert all(x['pass'] for x in states.values())
 final=dict(authority='kT B4-S +90 rolled source 2026-11-19',
            geometry_sha256=sha_now,threshold_m3=.01,both_required=True,
            old_source_sha256=PREVIOUS_SHA,prior_pair_pass_source_sha256=read(PRIOR)['geometry_sha256'],
            states=states,pass_=True,
            qualification='Full B-rep pair screen before and after water debit, 2 states; conservative convex outer hull derived from authored B4-S flight mesh. Primary BReps inherited only from byte-identical source; no new physical clearances credited to source proxy.')
 final['pass']=final.pop('pass_')
 output(FINAL,final)
 # Existing D9 consumer expects one report. This one is derived from REAL
 # two-state pair evidence and the unchanged 43 primary BReps, not the v1 hash.
 summary=dict(pass_=True,geometry_sha256=sha_now,category_d_count=0,
              pair_count=22791,expected_pairs=22791,
              geometry_conversion_or_boolean_errors=[],primary_invariant_failures=[],
              D8_primary_shape_unchanged=True,
              excluded_source_no_render_proxy_count=len([p for p in G['parts'] if 'no_render' in p['tags']]),
              derived_from='wayfarer/results/out/D9_B4S_TWO_STATE_REPORT.json',
              two_state_required=True,two_state_pass=True,
              no_criteria_change=True,conservative_B4S_polyhull=True)
 summary['pass']=summary.pop('pass_')
 output(ROOT/"results/out/D9_BREP_CLASH_REPORT.json",summary)
 print('B4S_D9_FINAL',states,'SHA',sha_now,flush=True)
 return 0

def main():
 p=argparse.ArgumentParser()
 p.add_argument('action',choices=('screen','pairs','merge'))
 p.add_argument('--state',choices=STATES)
 p.add_argument('--shard',type=int,default=0)
 p.add_argument('--shards',type=int,default=8)
 args=p.parse_args()
 if args.action=='merge':return merge()
 assert args.state
 if args.action=='screen':return screen(args.state)
 return pairs(args.state,args.shard,args.shards)

if __name__=='__main__':raise SystemExit(main())
