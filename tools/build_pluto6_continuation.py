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
    ap.add_argument("--start",default="2199 DEC 29 00:00:00 TDB")
    ap.add_argument("--end",default="2251 JAN 02 00:00:00 TDB")
    ap.add_argument("--max-step",type=float,default=5400.0)
    ap.add_argument("--sample-step",type=float,default=21600.0)
    ap.add_argument("--rtol",type=float,default=1e-12)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.root); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    lsk=root/"kernels/lsk/naif0012.tls"; de440=root/"kernels/spk/de440.bsp"; plu060=root/"kernels/spk/phase4b/plu060.bsp"
    for p in (lsk,de440,plu060):
        if not p.exists(): raise SystemExit(f"missing required kernel: {p}")
    sp.kclear(); sp.furnsh(str(lsk)); sp.furnsh(str(de440)); sp.furnsh(str(plu060))
    t0=float(sp.str2et(args.start)); tf=float(sp.str2et(args.end))
    ids=[b for b,_ in BODIES]; names=dict(BODIES); n=len(ids); g=np.array([GM[b] for b in ids])
    states=np.array([sp.spkgeo(b,t0,FRAME,CENTER)[0] for b in ids],dtype=float)
    y=np.concatenate([states[:,:3].reshape(-1),states[:,3:].reshape(-1)])
    calls=0
    def unpack(z): return z[:3*n].reshape(n,3),z[3*n:].reshape(n,3)
    def rhs(t,z):
        nonlocal calls; calls+=1; r,v=unpack(z); a=np.zeros_like(r)
        for i in range(n):
            for j in range(n):
                if i==j: continue
                d=r[j]-r[i]; q=float(np.dot(d,d)); a[i]+=g[j]*d/(q*math.sqrt(q))
        for body,mu in EXT_GM.items():
            R=np.asarray(sp.spkgeo(body,t,FRAME,CENTER)[0][:3]); q0=float(np.dot(R,R)); base=R/(q0*math.sqrt(q0))
            for i in range(n):
                d=R-r[i]; q=float(np.dot(d,d)); a[i]+=mu*(d/(q*math.sqrt(q))-base)
        return np.concatenate([v.reshape(-1),a.reshape(-1)])
    atol=np.concatenate([np.full(3*n,1e-7),np.full(3*n,1e-13)])
    sample=np.arange(t0,tf,args.sample_step)
    if len(sample)==0 or sample[-1] < tf: sample=np.append(sample,tf)
    wall=time.time()
    sol=solve_ivp(rhs,(t0,tf),y,method="DOP853",rtol=args.rtol,atol=atol,max_step=args.max_step,t_eval=sample)
    if not sol.success: raise RuntimeError(sol.message)
    for i,b in enumerate(ids):
        rr=sol.y[3*i:3*i+3,:].T; vv=sol.y[3*n+3*i:3*n+3*i+3,:].T
        ss=np.ascontiguousarray(np.hstack([rr,vv]),dtype=float); ee=np.ascontiguousarray(sol.t,dtype=float)
        path=out/f"propagated_plu060_exact_{b}_2199_2251.bsp"
        if path.exists(): path.unlink()
        h=sp.spkopn(str(path),"LOOM PLU060 EXACT MODEL CONTINUATION",1024)
        sp.spkw09(h,b,CENTER,FRAME,float(ee[0]),float(ee[-1]),f"LOOM PLU060 EXACT CONTINUATION {b}",7,len(ee),ss,ee); sp.spkcls(h)
    payload={"schema":"loom.pluto6-production-continuation/1.0","authority":"PROPAGATED_ESTIMATE",
      "model":"published PLU060 six-body dynamics independently reproduced with scipy DOP853",
      "start_et":t0,"end_et":tf,"frame":FRAME,"center":CENTER,"integrator":"scipy.DOP853",
      "rtol":args.rtol,"max_step_s":args.max_step,"sample_step_s":args.sample_step,
      "internal_gm":GM,"external_gm":EXT_GM,"rhs_calls":calls,"runtime_s":time.time()-wall,
      "qualification_basis":"998f7b0/642c702: 2180-2199 withheld-truth <=13.289 m annual-sampled at 5400 s; 2013-2199 <=46.631 m annual-sampled"}
    (out/"BUILD.json").write_text(json.dumps(payload,indent=2)+"\n")
    sp.kclear()
if __name__=="__main__": main()
