"""Batched version of the existing direct-SPICE Izzo search (pilot-only).

Only use on a span whose governing source/coverage is identical at both ends.
The scalar TravelPilot stays available for independent comparison and for
scenarios outside the directly-qualified pilot spans.
"""
from __future__ import annotations
import math, time
from datetime import timedelta
import numpy as np
import spiceypy as spice
from scipy.optimize import minimize_scalar
from numba import njit
from lamberthub import izzo2015
from .utc_et_lattice import utc_epochs_to_et
from . import pilot as mod
from .pilot import TravelPilot,_day,_iso,TECHNOLOGY,TECHNOLOGY_TABLE,SERVICE,TOF_BRACKETS
@njit
def batched_izzo(mu,r1,r2,t):
 n=len(t)
 departure=np.empty((n,3),dtype=np.float64)
 arrival=np.empty((n,3),dtype=np.float64)
 for i in range(n):
  a,b=izzo2015(mu,r1[i],r2[i],t[i],M=0,prograde=True,low_path=True)
  departure[i]=a
  arrival[i]=b
 return departure,arrival

class BatchTravelPilot(TravelPilot):
 def __init__(self,**kwargs):
  super().__init__(**kwargs)
  self.batch_seconds=0.
  self.state_bulk_seconds=0.
  self.tof_search_seconds=0.
  self.bulk_calls=0
  self.state_bulk_calls=0
  self.result_build_seconds=0.

 def _batch_states(self,body,epochs):
  start=time.perf_counter()
  first,last=_iso(min(epochs)),_iso(max(epochs))
  src,cov=self.adapter.registry.source_for(body,first)
  src_last,cov_last=self.adapter.registry.source_for(body,last)
  if (src.ephemeris_source_id != src_last.ephemeris_source_id
      or cov != cov_last or not src.navigation_grade):
   raise ValueError('BULK_SOURCE_COVERAGE_SEAM: '+body)
  self.adapter._load_source(src)
  ident=self.adapter.registry.body_identifier(body)
  et=np.asarray(utc_epochs_to_et(epochs, deltet=spice.deltet),dtype=float)
  # Direct source-object coverage preflight on span endpoints.
  # Refuse non-contiguous or source-switching dates instead of silently
  # treating propagated/missing positions as executable authority.
  self.adapter._require_source_object_coverage(src,int(ident.identifier_value),float(et[0]))
  self.adapter._require_source_object_coverage(src,int(ident.identifier_value),float(et[-1]))
  st,_=spice.spkezr(str(ident.identifier_value),et,'ECLIPJ2000','NONE','10')
  a=np.asarray(st,dtype=np.float64)
  self.state_bulk_seconds+=time.perf_counter()-start
  self.state_bulk_calls+=1
  return a,src,cov

 def _scan(self,origin,destination,departure,*,step_days,keep_samples):
  departure=_day(departure)
  price=self.price_by_year[(departure.year,SERVICE)]
  scanstart=time.perf_counter()
  alltimes=[]
  bracket_ranges=[]
  for a,b in TOF_BRACKETS:
   n=math.ceil((b-a)/step_days)
   times=sorted(set(min(float(b),a+i*step_days) for i in range(n))|{float(b)})
   lo=len(alltimes)
   alltimes.extend(times)
   bracket_ranges.append((lo,len(alltimes)))
  times=np.asarray(alltimes,dtype=float)
  arrival_epochs=[departure+timedelta(days=float(t)) for t in times]
  try:
   s1,q1=self._state(origin,departure)
   arrival_states,src2,cov2=self._batch_states(destination,arrival_epochs)
  except (ValueError,RuntimeError):
   # preserve fail-closed handling of source seams in this limited prototype.
   raise
  r1=np.repeat(np.asarray(s1.position_km,dtype=np.float64)[None,:],len(times),axis=0)
  start=time.perf_counter()
  v1,v2=batched_izzo(mod.legacy.SUN_GM_KM3_S2,r1,arrival_states[:,:3],times*86400)
  batch_elapsed=time.perf_counter()-start
  self.batch_seconds+=batch_elapsed
  self.bulk_calls+=1
  self.solve_count+=len(times)
  depv=np.linalg.norm(v1-np.asarray(s1.velocity_km_s),axis=1)
  arrv=np.linalg.norm(v2-arrival_states[:,3:],axis=1)
  # Match scalar baseline: normalize -> python round(...,7) -> feasibility.
  deps=[round(float(x),7) for x in depv]
  arrs=[round(float(x),7) for x in arrv]
  valid=[(de<=TECHNOLOGY_TABLE[0]['max_departure_vinf_km_s']
          and ar<=TECHNOLOGY_TABLE[0]['max_arrival_vinf_km_s'])
         for de,ar in zip(deps,arrs)]
  self.tof_search_seconds+=time.perf_counter()-scanstart
  admitted=[]
  def build(i):
   started=time.perf_counter()
   dep=deps[i];arr=arrs[i]
   out=dict(origin=origin,destination=destination,
            departure=_iso(departure),arrival=_iso(arrival_epochs[i]),
            flight_days=round(float(times[i]),5),
            departure_vinf_km_s=dep,arrival_vinf_km_s=arr,
            transfer_burden_km_s=round(float(depv[i]+arrv[i]),7),
            c3_km2_s2=round(float(depv[i]**2),7),
            state_class_origin=q1,state_class_destination='DIRECT',
            source_origin=s1.provenance['ephemeris_source_id'],
            source_destination=src2.ephemeris_source_id,
            asset_sha256_origin=s1.provenance['asset_sha256'],
            asset_sha256_destination=src2.sha256,
            standing='DIRECT_PRELIMINARY_LAMBERT_NOT_MISSION_DESIGN')
   self.result_build_seconds+=time.perf_counter()-started
   return out
  if not keep_samples:
   cnt=sum(valid)
   return dict(checked=len(times),feasible_samples=cnt,
               first_feasible=(build(valid.index(True)) if cnt else None),
               scan_step_days=step_days)
  for lo,hi in bracket_ranges:
   group=[]
   groups=[]
   for i in range(lo,hi):
    if valid[i]:
     admitted.append(build(i))
     group.append(i)
    elif group:
     groups.append(group)
     group=[]
   if group:groups.append(group)
   for group in groups:
    if len(group)<2:continue
    low,high=float(times[group[0]]),float(times[group[-1]])
    if high-low<=.1:continue
    def burden(tof):
     r=self._solve(origin,destination,departure,tof)
     if not self._admitted(r):raise ValueError('continuous minimum outside sampled feasible interval')
     return r['transfer_burden_km_s']
    try:
     m=minimize_scalar(burden,method='bounded',bounds=(low,high),options={'xatol':.05,'maxiter':55})
     r=self._solve(origin,destination,departure,float(m.x))
     if self._admitted(r):admitted.append(r)
    except (ValueError,RuntimeError):pass
  for r in admitted:
   r.update(service_type=SERVICE,technology=TECHNOLOGY,
            cost_usd_millions=round(price['usd_millions_per_km_s_burden']*
                       r['transfer_burden_km_s'],6),
            cost_standing=price['standing'],
            price_anchor_sha256=price['source_sha256'])
  admitted.sort(key=lambda r:(r['flight_days'],r['cost_usd_millions']))
  front=[];mincost=float('inf')
  for r in admitted:
   if r['cost_usd_millions']<mincost-1e-6:
    front.append(r)
    mincost=r['cost_usd_millions']
  if len(front)>4:
   indices={0,len(front)-1}
   indices.update(round(i*(len(front)-1)/3) for i in range(1,3))
   front=[front[i] for i in sorted(indices)]
  return front
