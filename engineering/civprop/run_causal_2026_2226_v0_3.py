#!/usr/bin/env python3
"""Pre-actor-expansion 2026-2226 causal-world qualification campaign.

NON-CANON / UNPROMOTED. Runs CausalWorldV03 only. HybridEngineV1 is neither
imported nor executed. Intended for detached shell execution and later review.
"""
from __future__ import annotations
import argparse, dataclasses, hashlib, json, os, sys, tempfile, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world, apply_causal_publication_semantics
from engineering.civprop.compile_inputs_v1 import capture_live_authority
from engineering.civprop.contracts.gap014_scenario_bridge_v1 import inject_demographic_authority
from engineering.civprop.contracts.timeline_causal_input_v0_3 import (
    load_timeline_causal_input, timeline_seed_events, timeline_lane,
)

def _flush(msg):
    print(msg,flush=True)

def _sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def _plain(x):
    if dataclasses.is_dataclass(x):
        return {f.name:_plain(getattr(x,f.name)) for f in dataclasses.fields(x)}
    if isinstance(x,dict): return {str(k):_plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [_plain(v) for v in x]
    if isinstance(x,(str,int,float,bool)) or x is None: return x
    return str(x)

def _write_json_atomic(path,obj):
    path=Path(path); tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:
        enc=json.JSONEncoder(indent=2,sort_keys=True,allow_nan=False)
        for chunk in enc.iterencode(obj): f.write(chunk)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def _activate_gap014(bundle_dir,database):
    capture=capture_live_authority(Path(bundle_dir)/'gap014_authority_capture.json',database=database)
    sp=Path(bundle_dir)/'scenario_v1.json'
    scenario=inject_demographic_authority(scenario=json.loads(sp.read_text()),capture=capture)
    sp.write_text(json.dumps(scenario,indent=2,sort_keys=True)+'\n')
    mp=Path(bundle_dir)/'manifest_v1.json'; manifest=json.loads(mp.read_text())
    sb=sp.read_bytes(); tb=(Path(bundle_dir)/manifest['truth_file']).read_bytes()
    manifest['sha256'][manifest['scenario_file']]=hashlib.sha256(sb).hexdigest()
    manifest['bundle_sha256']=hashlib.sha256(sb+b'\n'+tb).hexdigest()
    mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return capture

def _counts(run):
    fields=(
      'annual_states','facilities','flows','offworld_migrant_cohorts','missions',
      'observations','knowledge_states','mission_decisions','mission_opportunity_dispositions',
      'mission_opportunity_disposition_summaries','resource_states','resource_flows','power_states','power_flows','traffic_demand_states',
      'traffic_service_states','fleet_states','voyage_states','route_traffic_states',
      'location_traffic_states','facility_production_states','sector_production_states',
      'location_production_states','body_production_states','economic_constraints',
      'economic_pressures','economic_opportunities')
    return {k:len(getattr(run,k)) for k in fields}

def execute(*,seed,database,start_year,end_year):
    with tempfile.TemporaryDirectory(prefix='civprop_causal_world_v03_') as td:
        _flush('phase BUILD_SOLAR_BUNDLE')
        bundle_dir=build_bundle_dir(Path(td))
        _flush('phase CAPTURE_EARTH_AUTHORITY')
        capture=_activate_gap014(bundle_dir,database)
        bundle=load_bundle(bundle_dir)
        timeline=load_timeline_causal_input(database=database)
        tseeds=timeline_seed_events(timeline,start_year=start_year,end_year=end_year)
        _flush(f'phase RUN_CAUSAL_WORLD years={start_year}-{end_year} timeline_events={len(tseeds)}')
        t=time.time()
        run=run_causal_world(
            bundle=bundle,seed=seed,start_year=start_year,end_year=end_year,
            extra_seed_events=tseeds,extra_lanes={'TIMELINE':timeline_lane},
        )
        elapsed=time.time()-t
        return run,capture,timeline,elapsed,bundle

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--output',required=True)
    ap.add_argument('--database',default='loom_dev')
    ap.add_argument('--start-year',type=int,default=2026)
    ap.add_argument('--end-year',type=int,default=2226)
    ap.add_argument('--verify',action='store_true')
    a=ap.parse_args()
    if a.start_year<2026 or a.end_year>2226 or a.end_year<a.start_year:
        raise SystemExit('year bounds must satisfy 2026 <= start <= end <= 2226')
    outp=Path(a.output); outp.parent.mkdir(parents=True,exist_ok=True)
    _flush('LOOM CAUSAL WORLD V0.3 — PRE-ACTOR-EXPANSION QUALIFICATION')
    _flush(f'period {a.start_year} {a.end_year} seed {a.seed}')
    _flush('world_state_engine CAUSAL_WORLD_V0_3')
    _flush('hybrid_execution FALSE')
    _flush('expanded_233_actor_set FALSE')
    wall=time.time()
    run,capture,timeline,elapsed,bundle_for_publication=execute(seed=a.seed,database=a.database,start_year=a.start_year,end_year=a.end_year)
    payload=apply_causal_publication_semantics(_plain(run),bundle_for_publication)
    _flush(f'phase WRITE_OUTPUT event_count={run.event_count}')
    _write_json_atomic(outp,payload)
    counts=_counts(run)
    represented_opportunities=(len(run.mission_opportunity_dispositions)+
        sum(int(x["opportunity_count"]) for x in run.mission_opportunity_disposition_summaries))
    manifest={
      'format':'LOOM_CAUSAL_WORLD_CAMPAIGN_V0_3',
      'classification':'NON_CANON_QUALIFICATION_REALIZATION_UNPROMOTED',
      'period':{'start_year':a.start_year,'end_year':a.end_year},'seed':a.seed,
      'world_state_engine':'CAUSAL_WORLD_V0_3','hybrid_execution':False,
      'expanded_233_actor_set':False,'governed_actor_fixture_count':13,
      'earth_authority_snapshot_id':capture['earth']['snapshot']['snapshot_id'],
      'timeline_snapshot_id':timeline.snapshot_id,'timeline_milestone_events':len(timeline_seed_events(timeline,start_year=a.start_year,end_year=a.end_year)),
      'open_boundaries':['GAP-016_GENERIC_TRANSPORT_PHYSICS','GAP-015_ATLAS_DERIVED_METRICS','OFFWORLD_DEMOGRAPHIC_ENDOGENEITY','PRESSURE_TO_INVESTMENT_THRESHOLD_AUTHORITY'],
      'run':{'qualification_class':run.qualification_class,'conductor_sha256':run.conductor_sha256,
             'final_state_digest':run.final_state_digest,'event_count':run.event_count,
             'annual_lane_invocations':dict(run.annual_lane_invocations),'ledger_rows':counts,
             'mission_opportunity_accounting':{
                 'representation':'COMPACT_EXCLUSIONS_V1',
                 'represented_opportunities':represented_opportunities,
                 'explicit_rows':len(run.mission_opportunity_dispositions),
                 'summary_rows':len(run.mission_opportunity_disposition_summaries)},
             'simulation_seconds':round(elapsed,6)},
      'output':{'path':str(outp),'raw_sha256':_sha(outp),'bytes':outp.stat().st_size},
    }
    mp=outp.with_suffix(outp.suffix+'.manifest.json')
    _write_json_atomic(mp,manifest)
    _flush('conductor_sha256 '+run.conductor_sha256)
    _flush('final_state_digest '+run.final_state_digest)
    _flush('ledger_rows '+json.dumps(counts,sort_keys=True))
    _flush(f'output {outp} bytes={outp.stat().st_size} raw_sha256={manifest["output"]["raw_sha256"]}')
    _flush('manifest '+str(mp))
    if a.verify:
        _flush('phase VERIFY_REPLAY')
        replay,_,_,replay_elapsed,_=execute(seed=a.seed,database=a.database,start_year=a.start_year,end_year=a.end_year)
        ok=(replay.conductor_sha256==run.conductor_sha256 and replay.final_state_digest==run.final_state_digest and _counts(replay)==counts)
        _flush(f'deterministic {"PASS" if ok else "FAIL"} replay_seconds={replay_elapsed:.3f}')
        if not ok: raise SystemExit(1)
    _flush(f'COMPLETE wall_seconds={time.time()-wall:.3f}')

if __name__=='__main__':
    main()
