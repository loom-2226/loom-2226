#!/usr/bin/env python3
"""Experimental reproduction of the published PLU060 six-body dynamical model.

This tool is intentionally outside the production authority path. It validates a
candidate continuation against PLU060 while PLU060 truth exists. It requires
numpy, spiceypy, and scipy. It does not mutate the database, registry, manifests,
or viewer products.
"""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
import spiceypy as sp
try:
    from scipy.integrate import solve_ivp
except ImportError as exc:
    raise SystemExit("scipy is required for this experimental validation tool") from exc

BODIES=((999,"PLUTO"),(901,"CHARON"),(902,"NIX"),(903,"HYDRA"),(904,"KERBEROS"),(905,"STYX"))
# Exact values from NAIF/JPL plu060.cmt, not rounded web-display values.
GM={999:8.693261226311508E+02,901:1.061011388236118E+02,902:1.496176095836919E-03,
    903:2.007962473606101E-03,904:6.038450780269370E-05,905:4.045391585487917E-05}
EXT_GM={5:1.267127618414429E+08,6:3.794058484180000E+07,7:5.794556400000000E+06,
        8:6.836531640925204E+06,10:1.327132332633514E+11}
FRAME="J2000"; CENTER=9

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default="/home/ubuntu/loom_solar_assets")
    ap.add_argument("--start",default="2180 JAN 01 00:00:00 TDB")
    ap.add_argument("--years",type=int,default=19)
    ap.add_argument("--max-step",type=float,default=21600.0)
    ap.add_argument("--rtol",type=float,default=1e-12)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.root); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    lsk=root/"kernels/lsk/naif0012.tls"; de440=root/"kernels/spk/de440.bsp"; plu060=root/"kernels/spk/phase4b/plu060.bsp"
    for p in (lsk,de440,plu060):
        if not p.exists(): raise SystemExit(f"missing required kernel: {p}")
    sp.kclear(); sp.furnsh(str(lsk)); sp.furnsh(str(de440)); sp.furnsh(str(plu060))
    t0=float(sp.str2et(args.start)); ids=[b for b,_ in BODIES]; names=dict(BODIES); n=len(ids); g=np.array([GM[b] for b in ids])
    states=np.array([sp.spkgeo(b,t0,FRAME,CENTER)[0] for b in ids],dtype=float)
    y=np.concatenate([states[:,:3].reshape(-1),states[:,3:].reshape(-1)])
    calls=0
    def unpack(z): return z[:3*n].reshape(n,3),z[3*n:].reshape(n,3)
    def rhs(trel,z):
        nonlocal calls; calls+=1; et=t0+trel; r,v=unpack(z); a=np.zeros_like(r)
        for i in range(n):
            for j in range(n):
                if i==j: continue
                d=r[j]-r[i]; q=float(np.dot(d,d)); a[i]+=g[j]*d/(q*math.sqrt(q))
        for body,mu in EXT_GM.items():
            R=np.asarray(sp.spkgeo(body,et,FRAME,CENTER)[0][:3]); q0=float(np.dot(R,R)); base=R/(q0*math.sqrt(q0))
            for i in range(n):
                d=R-r[i]; q=float(np.dot(d,d)); a[i]+=mu*(d/(q*math.sqrt(q))-base)
        return np.concatenate([v.reshape(-1),a.reshape(-1)])
    def errors(trel,z):
        et=t0+trel; r,v=unpack(z); rows=[]
        for i,b in enumerate(ids):
            truth=np.asarray(sp.spkgeo(b,et,FRAME,CENTER)[0])
            rows.append({"body_id":b,"body":names[b],"position_error_km":float(np.linalg.norm(r[i]-truth[:3])),
                         "velocity_error_km_s":float(np.linalg.norm(v[i]-truth[3:]))})
        rb=(g[:,None]*r).sum(axis=0)/g.sum(); vb=(g[:,None]*v).sum(axis=0)/g.sum()
        return rows,float(np.linalg.norm(rb)),float(np.linalg.norm(vb))
    year=365.25*86400.0; atol=np.concatenate([np.full(3*n,1e-7),np.full(3*n,1e-13)])
    annual=[]; current=0.0; start_wall=time.time()
    print(f"PLU060 reproduction start={args.start} years={args.years} max_step={args.max_step}s",flush=True)
    for k in range(1,args.years+1):
        target=k*year; w=time.time(); c0=calls
        sol=solve_ivp(rhs,(current,target),y,method="DOP853",rtol=args.rtol,atol=atol,max_step=args.max_step,t_eval=[target])
        if not sol.success: raise RuntimeError(sol.message)
        y=sol.y[:,-1]; current=target; er,rb,vb=errors(current,y)
        annual.append({"year":k,"segment_s":time.time()-w,"rhs_calls":calls-c0,"barycenter_position_km":rb,
                       "barycenter_velocity_km_s":vb,"errors":er})
        worst=max(er,key=lambda x:x["position_error_km"])
        print(f"year={k:02d} worst={worst['body']} {worst['position_error_km']:.9f} km",flush=True)
    payload={"schema":"loom.pluto6-jpl-model-reproduction/0.2-experiment","authority":"EXPERIMENT_ONLY_NOT_QUALIFIED",
             "start":args.start,"years":args.years,"frame":FRAME,"center":CENTER,"integrator":"scipy.DOP853",
             "rtol":args.rtol,"max_step_s":args.max_step,"internal_gm":GM,"external_gm":EXT_GM,
             "rhs_calls":calls,"runtime_s":time.time()-start_wall,"annual":annual}
    (out/"validation.json").write_text(json.dumps(payload,indent=2)+"\n")
    sp.kclear()
if __name__=="__main__": main()
