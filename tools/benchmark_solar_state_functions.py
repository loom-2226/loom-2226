#!/usr/bin/env python3
import argparse,json,time
from src.loom_solar_inspector import Inspector
from src.loom_solar_chebyshev import compile_chebyshev,ChebyshevStateFunction
from src.loom_solar_temporal import adaptive_samples
from src.loom_solar_state_runtime import HermiteStateFunction,StateRuntimeError
DAY=86400.; DEFAULT_TOL={'NATURAL_SATELLITE':25.,'PLANET':2000.,'DWARF_PLANET':2000.,'SPACECRAFT':100.}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--asset-root',required=True); p.add_argument('--database',default='loom_dev'); p.add_argument('--start',default='2226-01-01T00:00:00 TDB'); p.add_argument('--days',type=float,default=8); p.add_argument('--degree',type=int,default=24); p.add_argument('bodies',nargs='+'); a=p.parse_args(); I=Inspector.connect(a.database,a.asset_root); s=I.time.parse(a.start); e=s+a.days*DAY
 for b in a.bodies:
  c=I.orbital_center(b); tol=DEFAULT_TOL.get(I.bodies[b]['body_class'],5000.); t=time.time(); hs,he=adaptive_samples(I,b,c,s,e,tol); ht=time.time()-t; ho={'body_id':b,'center_id':c,'reference_frame':'ECLIPJ2000','declared_error_km':tol,'samples':hs}; hb=len(json.dumps(ho,separators=(',',':')))
  row={'body':b,'center':c,'tolerance_km':tol,'hermite_samples':len(hs),'hermite_json_bytes':hb,'hermite_compile_s':round(ht,3),'hermite_observed_km':he}
  try:
   t=time.time(); cs=compile_chebyshev(I,b,c,s,e,a.degree,tol); ct=time.time()-t; row.update(chebyshev_degree=a.degree,chebyshev_json_bytes=len(json.dumps(cs,separators=(',',':'))),chebyshev_compile_s=round(ct,3),chebyshev_observed_km=cs['observed_error_km'],byte_ratio=round(len(json.dumps(cs,separators=(',',':')))/hb,4),status='PASS')
  except StateRuntimeError as x: row.update(status='FAIL',error=str(x))
  print(json.dumps(row,sort_keys=True),flush=True)
if __name__=='__main__': main()
