"""Reproducible five-run warm comparison; no edits to travel-pilot implementation."""
import hashlib,json,time
from pathlib import Path
from datetime import datetime
import numpy as np
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import dates_for
P=Path(__file__).resolve().parent;C=json.loads((P/'next_lattice_slice_config.json').read_text());B=json.loads((P/C['lattice_source_config']).read_text());E=json.loads((P/'experiment.json').read_text());OUT=Path(C['output_root']);M=json.loads((OUT/'slice_manifest.json').read_text());body=sorted(M['built'])[0];year=min(E['years']);departures=dates_for(year,E['sampling']);warm=departures[0];date=departures[1];assert len(departures)>1
first=datetime.fromisoformat(M['first'].replace('Z','+00:00'));table=np.load(OUT/(body+'.npy'),mmap_mode='r');direct=OnDemandTravel(asset_root=Path(E['asset_root']));cached=OnDemandTravel(asset_root=Path(E['asset_root']));old=cached._batch_states

def from_table(b,epochs):
 if b!=body:return old(b,epochs)
 ids=[round((x-first).total_seconds()/(B['lattice_step_days']*86400)) for x in epochs]
 if any(i<0 or i>=len(table) or abs((epochs[j]-first).total_seconds()-i*B['lattice_step_days']*86400)>1e-6 for j,i in enumerate(ids)):raise ValueError('OFF_LATTICE')
 src,cov=cached.adapter.registry.source_for(b,_iso(epochs[0]));return np.asarray(table[ids]),src,cov
cached._batch_states=from_table
kw={'strategy':E['sampling']['strategy'],'flight_range_days':E['sampling']['flight_range_days']};print('TIMING_CONFIG_SHA256',hashlib.sha256((P/'next_lattice_slice_config.json').read_bytes()).hexdigest(),'BODY',body,'WARMUP',warm,'MEASURE',date,flush=True)
for obj in (direct,cached):obj.geometry(E['origin'],body,warm,**kw)
measure={}
for label,obj in [('direct',direct),('table',cached)]:
 samples=[];hashes=[]
 for i in range(C['benchmark_runs_per_path']):
  # Fresh object geometry memo, same loaded kernel and warmed solver.
  obj._geometry.clear();t=time.perf_counter();g=obj.geometry(E['origin'],body,date,**kw);samples.append(time.perf_counter()-t);hashes.append(hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest())
 measure[label]={'seconds':samples,'hashes':hashes};print('TIMING',label,samples,flush=True)
assert len(set(measure['direct']['hashes']+measure['table']['hashes']))==1,'GEOMETRY_MISMATCH';print('GEOMETRY_HASH',measure['direct']['hashes'][0],flush=True)
print('TIMING_REPORT',json.dumps(measure,sort_keys=True),flush=True)
