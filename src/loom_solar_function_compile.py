"""Adaptive compiler for qualified continuous Solar state functions."""
from __future__ import annotations
from src.loom_solar_chebyshev import compile_chebyshev
from src.loom_solar_state_runtime import StateRuntimeError

DEFAULT_DEGREES=(12,24,36,48)

def compile_adaptive(inspector,body,center,start_et,end_et,error_km,degrees=DEFAULT_DEGREES,min_span_s=3600,max_depth=16,validation_points=65,sample_many=None):
 """Compile governed state(T) to piecewise Chebyshev functions.

 Hermite is intentionally not a production fallback. If no qualified
 Chebyshev representation exists above min_span_s, compilation fails closed.
 """
 def one(a,b,depth):
  failures=[]
  for degree in degrees:
   try:
    c=compile_chebyshev(inspector,body,center,a,b,degree,error_km,validation_points,sample_many)
    c['representation']='CHEBYSHEV_STATE_SEGMENT'
    return [c]
   except StateRuntimeError as e: failures.append(str(e))
  if depth<max_depth and b-a>2*min_span_s:
   m=(a+b)/2
   return one(a,m,depth+1)+one(m,b,depth+1)
  raise StateRuntimeError(f'no qualified continuous function for {body} on [{a},{b}]: '+failures[-1])
 segs=one(float(start_et),float(end_et),0)
 return {'representation':'PIECEWISE_STATE_FUNCTION','body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','start_et':float(start_et),'end_et':float(end_et),'declared_error_km':error_km,'segments':segs}
