"""Fail-closed table-backed OnDemandTravel adapter; no travel-pilot edits."""
import hashlib,json
from pathlib import Path
from datetime import datetime
import numpy as np
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class TableTravel:
 def __init__(self,asset_root,manifest_path):
  self.manifest_path=Path(manifest_path);self.manifest=json.loads(self.manifest_path.read_text());self.manifest_sha256=digest(self.manifest_path);self.root=Path(self.manifest['table_root']);self.first=datetime.fromisoformat(self.manifest['first'].replace('Z','+00:00'));self.step=self.manifest['step_days']*86400;self.tables={};self.travel=OnDemandTravel(asset_root=Path(asset_root));self.old=self.travel._batch_states;self.travel._batch_states=self._batch_states
 def _batch_states(self,body,epochs):
  if body not in self.manifest['tables']:raise ValueError('MISSING_TABLE:'+body)
  if body not in self.tables:
   p=self.root/(body+'.npy');entry=self.manifest['tables'][body]
   if not p.exists() or digest(p)!=entry['sha256']:raise ValueError('TABLE_HASH_MISMATCH:'+body)
   self.tables[body]=np.load(p,mmap_mode='r')
  a=self.tables[body];idx=[]
  for epoch in epochs:
   tick=(epoch-self.first).total_seconds()/self.step;i=round(tick)
   if i<0 or i>=len(a) or abs(tick-i)>1e-9:raise ValueError('OFF_LATTICE:'+body+':'+_iso(epoch))
   idx.append(i)
  source,coverage=self.travel.adapter.registry.source_for(body,_iso(epochs[0]));entry=self.manifest['tables'][body]
  if source.sha256!=entry['source_sha256']:raise ValueError('SOURCE_HASH_MISMATCH:'+body)
  return np.asarray(a[idx]),source,coverage
 def geometry(self,*a,**kw):return self.travel.geometry(*a,**kw)
 def admissible(self,*a,**kw):return self.travel.admissible(*a,**kw)
