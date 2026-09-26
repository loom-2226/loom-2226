#!/usr/bin/env python3
"""Build M4-B disposable Solar Facts candidate from frozen corpus inputs; no network."""
from __future__ import annotations
import csv, hashlib, importlib.util, json, shutil, sqlite3, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from validate_m4b import validate_campaign

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASELINE=ROOT/'dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
SF3=ROOT/'dev/solar_facts_multi_body/sf_promote_03_europa_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3'
OUT=HERE/'LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3'
REPORTS=HERE/'reports'
FAMILIES=('VOLATILES','METALS','SILICATES_ROCK','CARBONACEOUS_ORGANICS')
EXPECTED_BASELINE_SHA='fc14d9f37f47e990a458fb434fec0e3419a3a45f6ffb9d6b35db406e59c71ee5'
EXPECTED_SF3_SHA='f25681e27ec3beb320c4983f4a59436f8471e8322208157039be0d21ecea6f53'
ELIGIBLE={'ASTEROID','BINARY_ASTEROID_PRIMARY','CENTAUR','COMET','DWARF_PLANET','INTERSTELLAR_OBJECT','NATURAL_SATELLITE','NEAR_EARTH_ASTEROID','PLANET','TRANS_NEPTUNIAN_OBJECT','TROJAN_ASTEROID'}
COVERAGE=('SUPPORTED_QUANTIFIED','SUPPORTED_BOUNDED','SUPPORTED_PRESENT_UNQUANTIFIED','SUPPORTED_NONDETECTION_OR_ABSENCE','SUPPORTED_UPPER_LIMIT','SUPPORTED_INFERRED_OR_MODELLED','UNKNOWN_AFTER_SEARCH','SOURCE_NOT_FOUND','NOT_APPLICABLE')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,default=str)
def loadjson(path): return json.loads(Path(path).read_text())
def writejson(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def insert(c,table,row):
 cols=list(row); c.execute(f"insert into {table} ({','.join(cols)}) values ({','.join('?' for _ in cols)})",[row[x] for x in cols])
def sf02_digest():
 p=ROOT/'dev/solar_facts_multi_body/sf_promote_02_ceres_67p/qualify.py'
 sys.path.insert(0,str(p.parent))
 spec=importlib.util.spec_from_file_location('_m4b_sf02_qualify',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def inherited_row_proof(before_path,after_path):
 """Prove every pre-existing SF3 row occurs unchanged in the candidate."""
 from collections import Counter
 b=sqlite3.connect(before_path); a=sqlite3.connect(after_path)
 tables=[x[0] for x in b.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
 matched={}; baseline_hashes={}
 for t in tables:
  before=[tuple(r) for r in b.execute(f'select * from {t}')]
  after=[tuple(r) for r in a.execute(f'select * from {t}')]
  needed=Counter(canon(r) for r in before); available=Counter(canon(r) for r in after)
  matched[t]=all(available[k]>=n for k,n in needed.items())
  baseline_hashes[t]=hashlib.sha256(canon(sorted(canon(r) for r in before)).encode()).hexdigest()
 b.close();a.close()
 proof={'table_row_subset_exact':matched,'all_baseline_rows_preserved':all(matched.values()),'baseline_table_row_digests':baseline_hashes}
 proof['baseline_row_subset_proof_sha256']=hashlib.sha256(canon(proof).encode()).hexdigest()
 return proof

def main():
 start=time.perf_counter(); REPORTS.mkdir(parents=True,exist_ok=True)
 catalog=loadjson(HERE/'source_catalog.json'); campaign=loadjson(HERE/'campaign_assertions.json'); acquired=loadjson(REPORTS/'source_acquisition.json')
 if not BASELINE.exists() or not SF3.exists(): raise SystemExit('required frozen input absent')
 baseline_sha=sha(BASELINE); sf3_sha=sha(SF3)
 if baseline_sha!=EXPECTED_BASELINE_SHA: raise SystemExit(f'Solar Baseline 02 authority mismatch: {baseline_sha}')
 if sf3_sha!=EXPECTED_SF3_SHA: raise SystemExit(f'SF-PROMOTE-03 authority mismatch: {sf3_sha}')
 baseline_meta=sqlite3.connect(BASELINE); bodies=baseline_meta.execute('select body_id,canonical_name,body_class,parent_body_id,authority,source_snapshot_sha256 from authority_body_ref order by body_id').fetchall(); baseline_meta.close()
 if len(bodies)!=110: raise SystemExit(f'expected frozen 110 identity rows; found {len(bodies)}')
 body_map={r[0]:r for r in bodies}; eligible=[r for r in bodies if r[2] in ELIGIBLE]
 if len(eligible)!=95: raise SystemExit(f'expected 95 eligible bodies; found {len(eligible)}')
 validate_campaign(campaign,{r[0] for r in eligible})
 digest=sf02_digest(); pre_sf3_body={b:digest.body_digest(SF3,b) for b in ('CERES','COMET_67P','EUROPA')}
 shutil.copy2(SF3,OUT)
 c=sqlite3.connect(OUT);c.execute('pragma foreign_keys=on');c.execute('begin immediate')
 # Add only catalog identities that the candidate's existing FK structure needs; exact IDs come from the frozen identity crosswalk.
 pending={r[0]:r for r in bodies if r[0] not in {x[0] for x in c.execute('select body_id from body')}}
 while pending:
  progressed=False
  for bid,r in list(pending.items()):
   _,name,cls,parent,*_=r
   if parent and parent not in {x[0] for x in c.execute('select body_id from body')}: continue
   insert(c,'body',{'body_id':bid,'canonical_name':name,'body_class':cls,'parent_body_id':parent,'status':'CANDIDATE'})
   insert(c,'body_authority',{'body_id':bid,'authority_system':'loom_solar.body','authority_identifier':bid,'authority_class':'PHASE4_IDENTITY_REFERENCE'})
   del pending[bid];progressed=True
  if not progressed: raise SystemExit(f'unresolved identity parent cycle: {sorted(pending)}')
 # Existing body rows are verified, never rewritten.
 for bid,r in body_map.items():
  got=c.execute('select canonical_name,body_class from body where body_id=?',(bid,)).fetchone()
  if not got or got!=(r[1],r[2]): raise SystemExit(f'identity mismatch for {bid}: {got}')
 # Attach provenance through ordinary source rows. Hashes remain in the artifact manifest even when publishers forbid redistributing their source files.
 acqmap={x['source_key']:x for x in acquired['sources']}
 sourcemap={x['source_key']:x for x in catalog['sources']}; source_ids={}
 for s in catalog['sources']:
  a=acqmap.get(s['source_key'])
  if not a or a.get('status')!='ACQUIRED': continue
  u=s['url']; doi=s.get('doi')
  found=c.execute('select source_id from source where (doi is not null and doi=?) or url=?',(doi,u)).fetchone() if doi else c.execute('select source_id from source where url=?',(u,)).fetchone()
  if found: sid=found[0]
  else:
   notes='M4-B frozen source acquisition; artifact_sha256='+a['sha256']+'; artifact_path='+a['artifact_path']+'; license='+s.get('license','unspecified')
   source_type={'PEER_REVIEWED_SUMMARY':'PEER_REVIEWED','NASA_TECHNICAL_REPORTS_SERVER_ABSTRACT':'PEER_REVIEWED'}.get(s['source_type'],s['source_type'])
   row={'source_type':source_type,'provider':s['authority'],'title':s['title'],'authors':None,'journal':None,'doi':doi,'url':u,'publication_date':s.get('published'),'product_name':s['title'] if source_type=='DATA_PRODUCT' else None,'product_version':None,'persistent_identifier':doi or s.get('source_key'),'retrieved_at':a.get('retrieved_at',datetime.now(timezone.utc).isoformat()),'citation_text':s['title']+'; '+u,'notes':notes}
   insert(c,'source',row);sid=c.execute('select last_insert_rowid()').fetchone()[0]
  source_ids[s['source_key']]=sid
 # Any pre-existing matching source is linked by source key too.
 for s in catalog['sources']:
  if s['source_key'] not in source_ids and s.get('doi'):
   r=c.execute('select source_id from source where doi=?',(s['doi'],)).fetchone()
   if r:source_ids[s['source_key']]=r[0]
 # Use the existing provenance table for each frozen artifact. Paths identify the
 # acquisition workspace; repository redistribution status remains in the manifest.
 for s in catalog['sources']:
  if s['source_key'] not in source_ids: continue
  a=acqmap.get(s['source_key'],{})
  for n,artifact in enumerate([a]+a.get('related_artifacts',[]),1):
   if artifact.get('status')!='ACQUIRED': continue
   artifact_id=f"M4B:{s['source_key']}:{n}"
   if c.execute('select 1 from source_artifact where artifact_id=?',(artifact_id,)).fetchone(): continue
   path=artifact.get('artifact_path','')
   insert(c,'source_artifact',{'artifact_id':artifact_id,'source_id':source_ids[s['source_key']],'locator':artifact.get('resolved_url') or artifact.get('requested_url') or s['url'],'local_path':path,'retrieved_at':artifact.get('retrieved_at') or a.get('retrieved_at') or datetime.now(timezone.utc).isoformat(),'sha256':artifact['sha256'],'byte_count':artifact['bytes'],'media_type':artifact.get('content_type'),'original_filename':Path(path).name if path else None,'version':s.get('version')})
 # Body-scoped regions and observations are explicit even when coordinates are unavailable.
 region_ids={}
 for r in campaign['region_definitions']:
  sid=source_ids.get(r.get('source_key')) if r.get('source_key') else r.get('existing_source_id')
  if sid is None: raise SystemExit('region source not acquired: '+r['key'])
  existing=c.execute('select region_id from body_region where body_id=? and canonical_name=?',(r['body_id'],r['name'])).fetchone()
  if existing: rid=existing[0]
  else:
   insert(c,'body_region',{'body_id':r['body_id'],'parent_region_id':None,'region_type':r['type'],'canonical_name':r['name'],'latitude_min_deg':None,'latitude_max_deg':None,'longitude_min_deg':None,'longitude_max_deg':None,'reference_frame':None,'description':r['description'],'confidence_class':'UNKNOWN','source_id':sid,'notes':'M4-B scoped region reference; coordinates intentionally omitted unless source input specifies them.'})
   rid=c.execute('select last_insert_rowid()').fetchone()[0]
  region_ids[r['key']]=rid
 obs_ids={}
 for o in campaign['observation_definitions']:
  sid=source_ids.get(o['source_key'])
  if sid is None: raise SystemExit('observation source not acquired: '+o['source_key'])
  insert(c,'observation',{'body_id':o['body_id'],'region_id':region_ids.get({'BENNU_SAMPLE_LAB':'BENNU_NIGHTINGALE','BENNU_SAMPLE_LAB_2025':'BENNU_NIGHTINGALE','RYUGU_SAMPLE_LAB':'RYUGU_TD1_TD2','RYUGU_SAMPLE_LAB_ORGANICS':'RYUGU_TD1_TD2','ITOKAWA_SAMPLE_LAB':'ITOKAWA_FIRST_TOUCHDOWN','WILD2_STARDUST_SAMPLE':'WILD2_COMA_SAMPLE','ENCELADUS_CASSINI_PLUME':'ENCELADUS_SOUTH_POLAR_PLUME','ENCELADUS_CASSINI_PLUME_2025':'ENCELADUS_SOUTH_POLAR_PLUME','MARS_CURIOSITY_CHEMIN':'MARS_GALE_CRATER','MARS_CURIOSITY_SIDERITE_2025':'MARS_GALE_CRATER','MARS_CUMBERLAND_SAM':'MARS_CUMBERLAND','MOON_LRO_LCROSS_WATER':'MOON_POLAR_PSR','MOON_APOLLO_SAMPLE_COMPOSITION':'MOON_SAMPLE_POPULATION','TITAN_CASSINI_HUYGENS':'TITAN_DUNES_HUYGENS','PLUTO_NEW_HORIZONS_RALPH':'PLUTO_WATER_ICE_OUTCROPS'}.get(o['key'])),'mission':o['mission'],'spacecraft':o['spacecraft'],'instrument':o['instrument'],'observation_product_id':o['product'],'observation_time_start':o.get('time_start'),'observation_time_end':o.get('time_end'),'observation_method':o['method'],'spatial_context':o['spatial_context'],'source_id':sid,'notes':o['notes'],'spatial_resolution_value':None,'spatial_resolution_unit':None,'spatial_resolution_semantics':None,'vertical_sensitivity_min':None,'vertical_sensitivity_max':None,'vertical_sensitivity_unit':None})
  obs_ids[o['key']]=c.execute('select last_insert_rowid()').fetchone()[0]
 # Use exact pre-existing qualified records without alteration; map actual evidence rows to contract lanes.
 existing_map={
  1:['VOLATILES'],2:['VOLATILES'],3:['VOLATILES','SILICATES_ROCK'],4:['SILICATES_ROCK'],5:['SILICATES_ROCK'],6:['VOLATILES'],7:['METALS']
 }
 evidence_ledger=[]
 for mid,fams in existing_map.items():
  row=c.execute('select material_evidence_id,body_id,material_family,material_species,source_id,observation_id,fact_status,evidence_class,abundance_semantics,abundance_value,abundance_min,abundance_max,abundance_unit,location_context,notes from material_evidence where material_evidence_id=?',(mid,)).fetchone()
  if not row: raise SystemExit(f'missing reusable material assertion {mid}')
  evidence_ledger.append({'assertion_key':f'SF3_MATERIAL_{mid}','material_evidence_id':mid,'body_id':row[1],'material_family':row[2],'material_species':row[3],'source_id':row[4],'observation_id':row[5],'resource_families':fams,'evidence_class':row[7],'abundance_semantics':row[8],'abundance_value':row[9],'abundance_min':row[10],'abundance_max':row[11],'abundance_unit':row[12],'scope':'REUSED_QUALIFIED_ROW','lineage':f'SF-PROMOTE-03:material_evidence:{mid}','notes':row[14]})
 for a in campaign['evidence_assertions']:
  bid=a['body_id']
  if bid not in body_map: raise SystemExit('unknown body identity in frozen assertion '+a['key'])
  sid=source_ids.get(a.get('source_key')) if a.get('source_key') else a.get('existing_source_id')
  oid=obs_ids.get(a.get('observation_key')) if a.get('observation_key') else a.get('existing_observation_id')
  rid=region_ids.get(a.get('region_key')) if a.get('region_key') else None
  if sid is None or oid is None: raise SystemExit('missing source/observation for '+a['key'])
  o=c.execute('select body_id from observation where observation_id=?',(oid,)).fetchone()
  if not o or o[0]!=bid: raise SystemExit('observation/body mismatch '+a['key'])
  if rid:
   rg=c.execute('select body_id from body_region where region_id=?',(rid,)).fetchone()
   if not rg or rg[0]!=bid: raise SystemExit('region/body mismatch '+a['key'])
  if a.get('scope','').startswith(('REGIONAL','SITE','RETURNED_SAMPLE','COMA','PLUME','INSTRUMENT','SINGLE_DRILL','SAMPLED','POLAR')) and rid is None: raise SystemExit('scoped claim missing region '+a['key'])
  m={'body_id':bid,'region_id':rid,'material_family':a['material_family'],'material_species':a.get('material_species'),'physical_form':a.get('physical_form'),'host_material':a.get('host_material'),'location_context':a.get('location_context'),'evidence_class':a['evidence_class'],'abundance_semantics':a['abundance_semantics'],'abundance_value':a.get('abundance_value'),'abundance_min':a.get('abundance_min'),'abundance_max':a.get('abundance_max'),'abundance_unit':a.get('abundance_unit'),'reported_abundance':a.get('reported_abundance'),'depth_min':a.get('depth_min'),'depth_max':a.get('depth_max'),'depth_unit':a.get('depth_unit'),'thickness_min':a.get('thickness_min'),'thickness_max':a.get('thickness_max'),'thickness_unit':a.get('thickness_unit'),'areal_extent':a.get('areal_extent'),'areal_extent_unit':a.get('areal_extent_unit'),'estimated_volume':a.get('estimated_volume'),'estimated_volume_unit':a.get('estimated_volume_unit'),'spatial_heterogeneity':a.get('scope'),'measurement_resolution':a.get('location_context'),'measurement_method':a.get('measurement_method'),'confidence_class':a['confidence_class'],'fact_status':'CANDIDATE','observation_id':oid,'source_id':sid,'notes':a['notes']}
  insert(c,'material_evidence',m);mid=c.execute('select last_insert_rowid()').fetchone()[0]
  x=dict(a);x.update(material_evidence_id=mid,source_id=sid,observation_id=oid,region_id=rid,provenance_sha256=sha(HERE/'campaign_assertions.json'));evidence_ledger.append(x)
 c.commit()
 fk=c.execute('pragma foreign_key_check').fetchall(); integrity=c.execute('pragma integrity_check').fetchone()[0]
 if fk or integrity!='ok': raise SystemExit(f'SQLite integrity failure: {integrity}; {fk[:3]}')
 # No preferred facts are selected by this campaign.
 preferred={b:c.execute('select count(*) from preferred_fact where body_id=?',(b,)).fetchone()[0] for b in [r[0] for r in eligible]}
 if sum(preferred.values())!=0: raise SystemExit('preferred_fact firewall violated')
 # Build coverage by using frozen source assertions and a transparent material-to-family crosswalk.
 evidence_by_lane=defaultdict(list)
 for e in evidence_ledger:
  for f in e['resource_families']:
   evidence_by_lane[(e['body_id'],f)].append(e)
 scopes={
  'BENNU':['BENNU_SAMPLE_ANALYSIS_NTRS_2024','BENNU_ORGANICS_PNAS_2025','BENNU_PHYLLOSILICATE_2025'],
  'RYUGU':['RYUGU_SAMPLE_INITIAL_2022','RYUGU_ORGANIC_MOLECULES_2023','RYUGU_SAMPLE_CATALOG_2022'],
  'ITOKAWA':['ITOKAWA_SAMPLE_CURATION','ITOKAWA_MINERALOGY_2014'],
  'WILD2':['STARDUST_SAMPLE_CATALOG','WILD2_MINERALOGY_2006','WILD2_ORGANICS_2006'],
  'ENCELADUS':['ENCELADUS_CASSINI_PLUME','ENCELADUS_ORGANICS_2025'],
  'VESTA':['VESTA_DAWN_MINERALOGY'], 'EROS':['EROS_XRS_2016'],
  'MARS':['MARS_CURIOSITY_CHEMIN','MARS_CURIOSITY_ORGANICS_2025','MARS_SIDERITE_2025'],
  'MOON':['MOON_COMPOSITION_NASA','MOON_WATER_NASA'],
  'TITAN':['TITAN_SURFACE_NASA','TITAN_FACTS_NASA'],
  'PLUTO':['PLUTO_NEW_HORIZONS_NASA'], 'CERES':['CERES_ORGANICS_2017'],
  'COMET_67P':['SF_PROMOTE_01_67P','ARP_QUAL_01B_67P_TRANSFER'],
  'EUROPA':['ARP_QUAL_02_EUROPA_CAMPAIGN','SF_PROMOTE_03_EUROPA']
 }
 existing_inputs=['SF_PROMOTE_03_QUALIFIED_MATERIAL_EVIDENCE','SF_PROMOTE_03_QUALIFIED_OBSERVATIONS_AND_SOURCE_ASSERTIONS','SOLAR_BASELINE_02_WGCCRE_CANDIDATE_SOURCE_AND_ASSERTION_CATALOG','ARP_QUALIFIED_CAMPAIGN_ARCHIVE']
 coverage=[]
 for b in eligible:
  bid,name,cls=b[0],b[1],b[2]
  for fam in FAMILIES:
   ev=evidence_by_lane.get((bid,fam),[])
   if ev:
    sem=[str(e.get('abundance_semantics') or '').upper() for e in ev]
    classes=[e.get('evidence_class') for e in ev]
    if any(s.startswith('QUANTIFIED') for s in sem): disp='SUPPORTED_QUANTIFIED'
    elif any(s in ('BOUNDED','RANGE') or e.get('abundance_min') is not None or e.get('abundance_max') is not None for s,e in zip(sem,ev)): disp='SUPPORTED_BOUNDED'
    elif any('UPPER_LIMIT' in s or s.startswith('UPPER') for s in sem): disp='SUPPORTED_UPPER_LIMIT'
    elif all(x in ('PHYSICAL_MODEL','DYNAMICAL_INFERENCE','ANALOG_INFERENCE','THEORETICAL_EXPECTATION') for x in classes): disp='SUPPORTED_INFERRED_OR_MODELLED'
    else: disp='SUPPORTED_PRESENT_UNQUANTIFIED'
    rationale='One or more provenance-linked candidate material assertions support this family; each assertion retains its epistemic class and scope. This is evidence coverage, not preference or global inventory.'
    unresolved='See per-assertion notes; no missing abundance or unsampled region has been inferred.'
   else:
    disp='UNKNOWN_AFTER_SEARCH';rationale='No target-specific material assertion survived the bounded reuse, bulk source-catalog, and prioritized targeted-review passes. This is not a claim of absence and not a zero.'
    unresolved='No direct/inferred assertion admitted for this family in the bounded 2026 campaign scope.'
   source_examined=existing_inputs+scopes.get(bid,[])
   coverage.append({'body_id':bid,'canonical_name':name,'body_class':cls,'resource_family':fam,'research_state':'ASSESSED','sources_examined':source_examined,'evidence_records':[e['assertion_key'] if 'assertion_key' in e else e['key'] for e in ev],'coverage_disposition':disp,'rationale':rationale,'unresolved_uncertainty':unresolved})
 # Use exactly 380 finite lanes.
 if len(coverage)!=380 or len({(x['body_id'],x['resource_family']) for x in coverage})!=380: raise SystemExit('coverage lane completeness failure')
 with (REPORTS/'M4B_COVERAGE_MATRIX.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(coverage[0]),lineterminator='\n');w.writeheader();
  for x in coverage:w.writerow({**x,'sources_examined':';'.join(x['sources_examined']),'evidence_records':';'.join(x['evidence_records'])})
 # Assertion/provenance ledger keeps multiplicity and source lineages distinct.
 with (REPORTS/'M4B_ASSERTION_PROVENANCE_LEDGER.csv').open('w',newline='') as f:
  fields=['assertion_key','material_evidence_id','body_id','resource_families','material_family','material_species','evidence_class','abundance_semantics','abundance_value','abundance_min','abundance_max','abundance_unit','reported_abundance','scope','lineage','source_id','observation_id','region_id','notes']
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader()
  for e in evidence_ledger:
   x=dict(e);x['assertion_key']=x.get('assertion_key',x.get('key'));x['resource_families']=';'.join(x['resource_families']);w.writerow(x)
 disp_counts=Counter(x['coverage_disposition'] for x in coverage)
 by_class=defaultdict(Counter)
 for x in coverage:by_class[x['body_class']][x['coverage_disposition']]+=1
 body_evidence=defaultdict(list)
 for e in evidence_ledger: body_evidence[e['body_id']].append(e)
 direct_classes={'DIRECT_SAMPLE','IN_SITU_DIRECT','IN_SITU_REMOTE','EARTH_REMOTE'}
 direct_bodies=sorted(b for b,es in body_evidence.items() if any(e.get('evidence_class') in direct_classes for e in es))
 inference_only=sorted(b for b,es in body_evidence.items() if es and all(e.get('evidence_class') not in direct_classes for e in es))
 # Physical inventory readiness uses baseline evidence only; no taxonomy or inferred density is generated.
 bc=sqlite3.connect(BASELINE);bc.row_factory=sqlite3.Row
 props=defaultdict(set)
 for r in bc.execute('select body_id,property_code from candidate_assertion'):props[r['body_id']].add(r['property_code'])
 inventory=[]
 for bid,name,cls,*_ in eligible:
  p=props.get(bid,set());mass=('MASS' in p);size=bool({'MEAN_RADIUS','EFFECTIVE_DIAMETER','TRIAXIAL_DIMENSIONS','TRIAXIAL_RADII','LONG_AXIS'}&p);density='BULK_DENSITY' in p
  status='MASS_CANDIDATE_AVAILABLE' if mass else 'DERIVABLE_CANDIDATE_SIZE_AND_DENSITY' if size and density else 'PHYSICAL_INVENTORY_GAP'
  inventory.append({'body_id':bid,'canonical_name':name,'body_class':cls,'mass_candidate':mass,'size_or_shape_candidate':size,'density_candidate':density,'readiness':status,'note':'Baseline values remain CANDIDATE and are not converted to accepted resource inventory.'})
 bc.close()
 with (REPORTS/'M4B_BODY_RESOURCE_READINESS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(inventory[0]),lineterminator='\n');w.writeheader();w.writerows(inventory)
 writejson(REPORTS/'M4B_UNRESOLVED_FRONTIER.json',{'campaign_id':'SOLAR_CIVPROP_M4B_2026','unknown_lane_count':disp_counts['UNKNOWN_AFTER_SEARCH'],'unknown_lanes':[{'body_id':x['body_id'],'resource_family':x['resource_family'],'sources_examined':x['sources_examined'],'rationale':x['rationale']} for x in coverage if x['coverage_disposition']=='UNKNOWN_AFTER_SEARCH'],'source_not_found_lane_count':disp_counts['SOURCE_NOT_FOUND'],'not_applicable_lane_count':disp_counts['NOT_APPLICABLE'],'note':'Unknown is absence of sufficient admitted evidence after the bounded campaign; it is not zero or material absence.'})
 writejson(REPORTS/'M4B_COVERAGE_SUMMARY.json',{'body_count':len(eligible),'eligible_body_count':len(eligible),'lane_count':len(coverage),'disposition_counts':dict(sorted(disp_counts.items())),'by_body_class':{k:dict(sorted(v.items())) for k,v in sorted(by_class.items())},'body_classes':dict(Counter(x[2] for x in eligible)),'supported_lane_count':sum(1 for x in coverage if x['coverage_disposition'].startswith('SUPPORTED_')),'bodies_with_direct_material_evidence':direct_bodies,'direct_body_count':len(direct_bodies),'bodies_supported_only_by_inference_or_model':inference_only,'inference_only_body_count':len(inference_only),'bodies_with_any_material_evidence':sorted(body_evidence),'quantified_abundance_assertion_count':sum(1 for e in evidence_ledger if str(e.get('abundance_semantics','')).upper().startswith('QUANTIFIED')),'bounded_abundance_assertion_count':sum(1 for e in evidence_ledger if e.get('abundance_min') is not None or e.get('abundance_max') is not None),'material_evidence_row_count':c.execute('select count(*) from material_evidence').fetchone()[0],'new_m4b_material_evidence_rows':len(campaign['evidence_assertions']),'preferred_fact_counts':{'TOTAL':sum(preferred.values()),**preferred},'physical_inventory_readiness_counts':dict(Counter(x['readiness'] for x in inventory))})
 # Source and artifact provenance manifests.
 src_rows=[]
 for s in catalog['sources']:
  a=acqmap.get(s['source_key'],{})
  src_rows.append({**s,'acquisition':a,'admission':'ADMITTED_SOURCE' if a.get('status')=='ACQUIRED' else 'REJECTED_OR_UNAVAILABLE','lineage_role':'EVIDENCE' if any(x.get('source_key')==s['source_key'] for x in campaign['evidence_assertions']) else 'DISCOVERY_OR_COVERAGE'})
 writejson(REPORTS/'M4B_SOURCE_MANIFEST.json',{'campaign_id':'SOLAR_CIVPROP_M4B_2026','source_count':len(catalog['sources']),'acquired_count':acquired['acquisition_count'],'failed_acquisition_count':sum(x.get('status')!='ACQUIRED' for x in acquired['sources']),'sources':src_rows})
 raw=[]
 for a in acquired['sources']:
  for artifact in [a]+a.get('related_artifacts',[]):
   item={**artifact,'source_key':a['source_key'],'retained_in_repository':artifact.get('retained_in_repository',False),'retention_reason':artifact.get('retention_reason','Raw source bytes are retained locally for audit; source redistribution/license policy is not uniform. Offline replay consumes the frozen assertion JSON and verified input databases, not network or publisher full text.')}
   raw.append(item)
 writejson(REPORTS/'M4B_RAW_ARTIFACT_MANIFEST.json',{'campaign_id':'SOLAR_CIVPROP_M4B_2026','artifact_count':sum(1 for x in raw if x.get('status')=='ACQUIRED'),'failed_or_unavailable_count':sum(1 for x in raw if x.get('status')!='ACQUIRED'),'raw_artifacts':raw,'offline_replay_inputs':['source_catalog.json','campaign_assertions.json','reports/source_acquisition.json','reports/M4B_CANDIDATE_INPUT_FREEZE.json','qualified input databases']})
 # Baseline and selected controls.
 post_sf3_sha=sha(SF3); post_sf3_body={b:digest.body_digest(SF3,b) for b in ('CERES','COMET_67P','EUROPA')}
 inherited=inherited_row_proof(SF3,OUT)
 noninterference={'qualified_sf3_database_sha_before':sf3_sha,'qualified_sf3_database_sha_after':post_sf3_sha,'qualified_sf3_unchanged':sf3_sha==post_sf3_sha,'body_digests_before':pre_sf3_body,'body_digests_after':post_sf3_body,'body_digests_exactly_unchanged':pre_sf3_body==post_sf3_body,'inherited_qualified_rows_exactly_unchanged':inherited['all_baseline_rows_preserved'],'inherited_row_proof':inherited,'preferred_fact_counts_after_candidate_build':preferred,'candidate_only_new_rows_all_candidate':c.execute("select count(*) from material_evidence where fact_status!='CANDIDATE'").fetchone()[0]==0,'new_identity_count':c.execute('select count(*) from body').fetchone()[0]-3,'note':'Three-body production input is read-only; candidate adds scoped candidate evidence and identity references in a separate database. Every pre-existing SF3 row is verified as an exact subset of the candidate.'}
 writejson(REPORTS/'M4B_NON_INTERFERENCE.json',noninterference)
 artifact_hashes={f"{s['source_key']}:{i}":a.get('sha256') for s in acquired['sources'] for i,a in enumerate([s]+s.get('related_artifacts',[]),1)}
 input_freeze={'campaign_id':'SOLAR_CIVPROP_M4B_2026','starting_main':'f2d92effee571a615791fd3a56d9c8d17914e3fe','solar_baseline_02_candidate_sha256':baseline_sha,'sf_promote_03_database_sha256':sf3_sha,'sf_promote_03_whole_semantic_digest':digest.whole_digest(SF3),'sf_promote_03_body_digests':pre_sf3_body,'identity_count':len(bodies),'eligible_body_count':len(eligible),'source_artifact_hashes':artifact_hashes,'m4a_contract_sha256':sha(ROOT/'dev/solar_civprop_resource_contract/M4A_POPULATION_MANIFEST_V1.json'),'resource_coverage_contract_sha256':sha(ROOT/'dev/solar_civprop_resource_contract/RESOURCE_COVERAGE_CONTRACT_V1.json'),'campaign_assertions_sha256':sha(HERE/'campaign_assertions.json'),'source_catalog_sha256':sha(HERE/'source_catalog.json')}
 writejson(REPORTS/'M4B_CANDIDATE_INPUT_FREEZE.json',input_freeze)
 candidate_sha=sha(OUT); candidate_digest=digest.whole_digest(OUT)
 c.close()
 replay={'candidate_sha256':candidate_sha,'candidate_semantic_digest':candidate_digest,'candidate_body_count':len(bodies),'eligible_body_count':len(eligible),'lane_count':len(coverage),'foreign_key_check':'PASS','integrity_check':integrity,'preferred_fact_total':sum(preferred.values()),'build_runtime_seconds':round(time.perf_counter()-start,6),'network_used_by_build':False}
 all_artifacts=[x for s in acquired['sources'] for x in [s]+s.get('related_artifacts',[])]
 writejson(REPORTS/'M4B_BUILD_METRICS.json',{'source_count':len(catalog['sources']),'source_acquisitions':acquired['acquisition_count'],'failed_source_acquisitions':sum(x.get('status')!='ACQUIRED' for x in acquired['sources']),'artifact_count':sum(x.get('status')=='ACQUIRED' for x in all_artifacts),'raw_artifact_bytes':sum(x.get('bytes',0) for x in all_artifacts if x.get('status')=='ACQUIRED'),'body_count':len(bodies),'eligible_body_count':len(eligible),'lane_count':len(coverage),'assertions_inherited':7,'new_assertions':len(campaign['evidence_assertions']),'candidate_assertion_total':len(evidence_ledger),'unique_evidence_lineages':len({x.get('lineage') for x in evidence_ledger if x.get('lineage')}),'assertions_per_acquisition':round(len(campaign['evidence_assertions'])/max(1,acquired['acquisition_count']),3),'eligible_bodies_per_acquisition':round(len(eligible)/max(1,acquired['acquisition_count']),3),'build_runtime_seconds':replay['build_runtime_seconds'],'bytes_and_corpus_metrics':'Source acquisitions count requested source records; artifact_count also counts the separately frozen full primary Bennu article. Exact hashes and paths are in the raw artifact manifest.'})
 writejson(REPORTS/'M4B_BUILD_REPLAY.json',replay)
 print(json.dumps({'candidate':str(OUT),'sha256':candidate_sha,'semantic_digest':candidate_digest,'coverage':dict(disp_counts),'assertions':len(evidence_ledger),'runtime_s':replay['build_runtime_seconds'],'fk':'PASS'},indent=2))
if __name__=='__main__': main()
