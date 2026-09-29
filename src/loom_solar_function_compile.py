"""Adaptive compiler selecting compact qualified runtime state representations."""
from __future__ import annotations
import json
from src.loom_solar_chebyshev import compile_chebyshev
from src.loom_solar_temporal import adaptive_samples
from src.loom_solar_state_runtime import StateRuntimeError

def _size(x): return len(json.dumps(x,sort_keys=True,separators=(',',':')))

def _hermite(inspector,body,center,a,b,tol):
 samples,err=adaptive_samples(inspector,body,center,a,b,tol)
 obj={'representation':'HERMITE_STATE_SEGMENT','body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','start_et':a,'end_et':b,'declared_error_km':tol,'observed_error_km':err,'samples':samples}
 return obj

def compile_adaptive(inspector,body,center,start_et,end_et,error_km,degrees=(12,24,36),min_span_s=3600,max_depth=16,validation_points=65):
 """Compile the longest qualified Chebyshev spans, Hermite only as fallback.

 Candidate functions are always checked against governed truth. A failed
 candidate is bisected; successful candidates stop recursion immediately.
 """
 def one(a,b,depth):
  qualified=[]
  for degree in degrees:
   try:
    c=compile_chebyshev(inspector,body,center,a,b,degree,error_km,validation_points)
    c['representation']='CHEBYSHEV_STATE_SEGMENT'; qualified.append(c); break
   except StateRuntimeError: pass
  if qualified:
   # Lowest degree is normally cheapest; avoid needless higher-degree resolver calls.
   return [min(qualified,key=_size)]
  if depth<max_depth and b-a>2*min_span_s:
   m=(a+b)/2
   return one(a,m,depth+1)+one(m,b,depth+1)
  return [_hermite(inspector,body,center,a,b,error_km)]
 segs=one(float(start_et),float(end_et),0)
 # Compare with one Hermite representation only after function segmentation.
 h=_hermite(inspector,body,center,float(start_et),float(end_et),error_km)
 if _size(h) < _size({'segments':segs}): segs=[h]
 return {'representation':'PIECEWISE_STATE_FUNCTION','body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','start_et':float(start_et),'end_et':float(end_et),'declared_error_km':error_km,'segments':segs}
