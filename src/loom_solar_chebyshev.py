"""Compile governed Solar state functions to bounded Chebyshev segments."""
from __future__ import annotations
import math
from src.loom_solar_state_runtime import RuntimeState,StateRuntimeError

def _nodes(n): return [math.cos(math.pi*(k+.5)/n) for k in range(n)]
def _et(x,a,b): return (a+b)/2 + x*(b-a)/2
def _x(t,a,b): return (2*t-a-b)/(b-a)

def _coeff(values):
 n=len(values); out=[]
 for j in range(n): out.append((2/n)*sum(values[k]*math.cos(j*math.pi*(k+.5)/n) for k in range(n)))
 out[0]*=.5; return out

def _eval(c,x):
 # Clenshaw for sum c_j T_j(x)
 b1=b2=0.0
 for cj in reversed(c[1:]): b0=2*x*b1-b2+cj; b2,b1=b1,b0
 return c[0]+x*b1-b2

class ChebyshevStateFunction:
 representation='CHEBYSHEV_STATE_SEGMENT'
 def __init__(self,segment):
  self.body_id=segment['body_id']; self.center_id=segment['center_id']; self.frame=segment['reference_frame']; self.start_et=float(segment['start_et']); self.end_et=float(segment['end_et']); self.coefficients=segment['coefficients']; self.authority_class=segment['authority_class']; self.source_ref=segment['source_ref']; self.center_source_ref=segment['center_source_ref']; self.declared_error_km=float(segment['declared_error_km']); self.observed_error_km=float(segment['observed_error_km'])
 def state(self,et):
  et=float(et)
  if not self.start_et<=et<=self.end_et: raise StateRuntimeError('epoch outside function validity')
  x=_x(et,self.start_et,self.end_et); p=tuple(_eval(c,x) for c in self.coefficients)
  return RuntimeState(self.body_id,self.center_id,et,p,self.authority_class,self.source_ref,self.center_source_ref,self.representation,self.declared_error_km)

def compile_chebyshev(inspector,body,center,start_et,end_et,degree,error_km,validation_points=257,sample_many=None):
 n=degree+1; rows=[]
 node_times=[_et(x,start_et,end_et) for x in _nodes(n)]
 if sample_many is None:
  for t in node_times:
   r=inspector.at(body,t,center)
   if r.get('resolution')!='RESOLVED' or 'relative' not in r: raise StateRuntimeError(f'unresolved governed state {body} at {t}')
   prov=r['state']['provenance']; cp=inspector.record(center,t)['state']['provenance']; rows.append((r,prov['ephemeris_source_id'],cp['ephemeris_source_id']))
 else:
  rows=list(sample_many(node_times))
 keys={(r['authority_class'],s,c) for r,s,c in rows}
 if len(keys)!=1: raise StateRuntimeError('authority/source transition requires segment boundary')
 authority,source,center_source=next(iter(keys)); coeff=[_coeff([r['relative']['position_km'][axis] for r,_,_ in rows]) for axis in range(3)]
 seg={'body_id':body,'center_id':center,'reference_frame':'ECLIPJ2000','start_et':start_et,'end_et':end_et,'degree':degree,'coefficients':coeff,'authority_class':authority,'source_ref':source,'center_source_ref':center_source,'declared_error_km':error_km,'observed_error_km':0.0}
 f=ChebyshevStateFunction(seg); worst=0.0
 validation_times=[start_et+(end_et-start_et)*i/(validation_points-1) for i in range(validation_points)]
 if sample_many is None:
  validation_rows=[]
  for t in validation_times:
   r=inspector.at(body,t,center)
   if r.get('resolution')!='RESOLVED' or 'relative' not in r: raise StateRuntimeError(f'unresolved validation state {body} at {t}')
   validation_rows.append(r)
 else:
  validation_rows=[r for r,_,_ in sample_many(validation_times)]
 for t,r in zip(validation_times,validation_rows):
  worst=max(worst,math.dist(f.state(t).position_km,r['relative']['position_km']))
 seg['observed_error_km']=worst
 if worst>error_km: raise StateRuntimeError(f'Chebyshev qualification failed {body}: {worst:.6g} km > {error_km:g} km')
 return seg
