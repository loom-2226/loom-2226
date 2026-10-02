"""Geometry-aware Solar transport opportunity contract V0.3.

Lambert calculations are derived accessibility evidence, not astronomical truth.
They consume qualified heliocentric states and emit transfer opportunities. A
transfer opportunity does not grant an actor a vehicle, budget, slot, or access.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import math
from typing import Callable, Sequence

MU_SUN_KM3_S2 = 132712440041.93938
DAY_S = 86400.0
BRIDGE_VERSION = "0.3.0"

@dataclass(frozen=True)
class TransferOpportunity:
    origin_body_id: str
    destination_body_id: str
    departure_epoch_utc: str
    arrival_epoch_utc: str
    time_of_flight_days: float
    departure_vinf_km_s: float
    arrival_vinf_km_s: float
    c3_km2_s2: float
    heliocentric_transfer_dv_km_s: float
    solver: str
    geometry_authority: str
    status: str
    provenance_refs: tuple[str, ...]

def _norm(v): return math.sqrt(sum(x*x for x in v))
def _sub(a,b): return tuple(x-y for x,y in zip(a,b))
def _dot(a,b): return sum(x*y for x,y in zip(a,b))
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _scale(v,s): return tuple(x*s for x in v)

def _stumpff_c(z):
    if z > 1e-8: return (1-math.cos(math.sqrt(z)))/z
    if z < -1e-8: return (math.cosh(math.sqrt(-z))-1)/(-z)
    return 0.5 - z/24 + z*z/720

def _stumpff_s(z):
    if z > 1e-8:
        q=math.sqrt(z); return (q-math.sin(q))/(q**3)
    if z < -1e-8:
        q=math.sqrt(-z); return (math.sinh(q)-q)/(q**3)
    return 1/6 - z/120 + z*z/5040

def lambert_universal(r1: Sequence[float], r2: Sequence[float], tof_s: float, mu: float=MU_SUN_KM3_S2):
    """Zero-revolution prograde universal-variable Lambert solution."""
    r1n,r2n=_norm(r1),_norm(r2)
    if r1n<=0 or r2n<=0 or tof_s<=0: raise ValueError("positive radii and time of flight required")
    cosd=max(-1.0,min(1.0,_dot(r1,r2)/(r1n*r2n)))
    sind=_norm(_cross(r1,r2))/(r1n*r2n)
    A=sind*math.sqrt(r1n*r2n/(1-cosd)) if abs(1-cosd)>1e-14 else 0.0
    if abs(A)<1e-12: raise ValueError("Lambert geometry singular or collinear")
    def F(z):
        C,S=_stumpff_c(z),_stumpff_s(z)
        if C<=0: return None
        y=r1n+r2n+A*(z*S-1)/math.sqrt(C)
        if y<0: return None
        x=math.sqrt(y/C)
        return x**3*S+A*math.sqrt(y)-math.sqrt(mu)*tof_s
    # Deterministic bracket scan avoids scipy dependency in production.
    lo=None; flo=None
    z=-4*math.pi*math.pi
    step=(8*math.pi*math.pi)/4000
    for i in range(4001):
        zz=z+i*step; f=F(zz)
        if f is None: continue
        if flo is not None and f*flo<=0:
            lo,hi=prev,zz; break
        prev,flo=zz,f
    else: raise ValueError("no zero-revolution Lambert root bracket")
    for _ in range(100):
        mid=(lo+hi)/2; fm=F(mid); fl=F(lo)
        if fm is None: lo=mid; continue
        if abs(fm)<1e-8: lo=hi=mid; break
        if fl*fm<=0: hi=mid
        else: lo=mid
    z=(lo+hi)/2; C,S=_stumpff_c(z),_stumpff_s(z)
    y=r1n+r2n+A*(z*S-1)/math.sqrt(C)
    f=1-y/r1n; g=A*math.sqrt(y/mu); gd=1-y/r2n
    if abs(g)<1e-12: raise ValueError("degenerate Lambert g")
    v1=_scale(_sub(r2,_scale(r1,f)),1/g)
    v2=_scale(_sub(_scale(r2,gd),r1),1/g)
    return v1,v2

def opportunity_from_states(origin_body_id, destination_body_id, departure_epoch_utc,
                            arrival_epoch_utc, origin_state, destination_state,
                            geometry_authority, provenance_refs=()):
    dep=datetime.fromisoformat(departure_epoch_utc.replace("Z","+00:00")).astimezone(timezone.utc)
    arr=datetime.fromisoformat(arrival_epoch_utc.replace("Z","+00:00")).astimezone(timezone.utc)
    tof=(arr-dep).total_seconds()
    vt1,vt2=lambert_universal(origin_state[:3],destination_state[:3],tof)
    vinf1=_norm(_sub(vt1,origin_state[3:6])); vinf2=_norm(_sub(vt2,destination_state[3:6]))
    return TransferOpportunity(origin_body_id,destination_body_id,departure_epoch_utc,arrival_epoch_utc,
      tof/DAY_S,vinf1,vinf2,vinf1*vinf1,vinf1+vinf2,"LAMBERT_UNIVERSAL_ZERO_REV_PROGRADE",
      geometry_authority,"GEOMETRY_OPPORTUNITY_ONLY",tuple(provenance_refs))

def scan_transfer_windows(origin_body_id, destination_body_id, departures, tof_days,
                          state_resolver: Callable[[str,str],Sequence[float]],
                          geometry_authority, provenance_refs=()):
    out=[]
    from datetime import timedelta
    for dep_text in departures:
        dep=datetime.fromisoformat(dep_text.replace("Z","+00:00")).astimezone(timezone.utc)
        o=state_resolver(origin_body_id,dep_text)
        for days in tof_days:
            arr=dep+timedelta(days=float(days)); arr_text=arr.isoformat().replace("+00:00","Z")
            d=state_resolver(destination_body_id,arr_text)
            try: out.append(opportunity_from_states(origin_body_id,destination_body_id,dep_text,arr_text,o,d,geometry_authority,provenance_refs))
            except ValueError: pass
    return sorted(out,key=lambda x:(x.heliocentric_transfer_dv_km_s,x.time_of_flight_days,x.departure_epoch_utc))
