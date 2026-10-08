"""Representation-neutral Solar state runtime.

Physical authority remains the governed resolver.  Runtime representations are
compiled approximations and must carry bounded validity and qualification data.
"""
from __future__ import annotations
from dataclasses import dataclass
from bisect import bisect_right
from typing import Mapping
from src.loom_solar_temporal import hermite_position

class StateRuntimeError(RuntimeError): pass

@dataclass(frozen=True)
class RuntimeState:
    body_id: str
    center_id: str
    epoch_et: float
    position_km: tuple[float,float,float]
    authority_class: str
    source_ref: str
    center_source_ref: str
    representation: str
    declared_error_km: float

class HermiteStateFunction:
    """One qualified, bounded parent-relative state function."""
    representation='HERMITE_STATE_SEGMENT'
    def __init__(self,obj:Mapping):
        self.body_id=obj['body_id']; self.center_id=obj['center_id']; self.frame=obj['reference_frame']
        self.declared_error_km=float(obj['declared_error_km']); self.samples=tuple(obj['samples'])
        self._times=tuple(float(s['epoch_et']) for s in self.samples)
        if len(self.samples)<2: raise ValueError('state function needs >=2 samples')
    @property
    def start_et(self): return self._times[0]
    @property
    def end_et(self): return self._times[-1]
    def state(self,et:float)->RuntimeState:
        et=float(et)
        if not self.start_et <= et <= self.end_et: raise StateRuntimeError('epoch outside function validity')
        i=max(0,min(len(self.samples)-2,bisect_right(self._times,et)-1)); a,b=self.samples[i],self.samples[i+1]
        if et==b['epoch_et']: a=b
        if a['resolution']!='RESOLVED' or b['resolution']!='RESOLVED': raise StateRuntimeError('unresolved runtime state')
        keys=('authority_class','source_ref','center_source_ref')
        if any(a[k]!=b[k] for k in keys): raise StateRuntimeError('authority/source transition requires segment boundary')
        pos=a['position_km'] if a is b or et==a['epoch_et'] else hermite_position(a,b,et)
        return RuntimeState(self.body_id,self.center_id,et,tuple(pos),a['authority_class'],a['source_ref'],a['center_source_ref'],self.representation,self.declared_error_km)

class SolarStateRuntime:
    """Scene-independent hierarchical evaluator: state(body,T), then world(body,T)."""
    def __init__(self,functions:Mapping[str,HermiteStateFunction]): self.functions=dict(functions)
    @classmethod
    def from_chunk(cls,chunk:Mapping): return cls({o['body_id']:HermiteStateFunction(o) for o in chunk['objects']})
    def relative(self,body_id:str,et:float)->RuntimeState:
        if body_id=='SUN': return RuntimeState('SUN','SUN',float(et),(0.,0.,0.),'ORIGIN','','','ORIGIN',0.)
        try:return self.functions[body_id].state(et)
        except KeyError as e: raise StateRuntimeError(f'no runtime function for {body_id}') from e
    def world_position(self,body_id:str,et:float):
        memo={'SUN':(0.,0.,0.)}; visiting=set()
        def world(b):
            if b in memo:return memo[b]
            if b in visiting:raise StateRuntimeError(f'center cycle at {b}')
            visiting.add(b); s=self.relative(b,et); parent=world(s.center_id); visiting.remove(b)
            memo[b]=tuple(x+y for x,y in zip(parent,s.position_km)); return memo[b]
        return world(body_id)
    def scene(self,et:float): return {b:self.world_position(b,et) for b in sorted(self.functions)}

class PiecewiseStateFunction:
    representation='PIECEWISE_STATE_FUNCTION'
    def __init__(self,obj):
        from src.loom_solar_chebyshev import ChebyshevStateFunction
        self.body_id=obj['body_id']; self.center_id=obj['center_id']; self.frame=obj['reference_frame']
        self.start_et=float(obj['start_et']); self.end_et=float(obj['end_et']); self.declared_error_km=float(obj['declared_error_km'])
        self.segments=[]
        for s in obj['segments']:
            rep=s.get('representation')
            if rep=='CHEBYSHEV_STATE_SEGMENT': self.segments.append(ChebyshevStateFunction(s))
            elif rep=='HERMITE_STATE_SEGMENT': self.segments.append(HermiteStateFunction(s))
            else: raise ValueError(f'unsupported state representation {rep}')
        self.segments.sort(key=lambda x:x.start_et)
    def state(self,et):
        et=float(et)
        for segment in self.segments:
            if segment.start_et<=et<=segment.end_et: return segment.state(et)
        raise StateRuntimeError('epoch outside piecewise function validity')
