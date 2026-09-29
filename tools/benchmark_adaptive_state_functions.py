#!/usr/bin/env python3
import argparse,json,time
from src.loom_solar_inspector import Inspector
from src.loom_solar_function_compile import compile_adaptive
DAY=86400.; TOL={'NATURAL_SATELLITE':25.,'PLANET':2000.,'DWARF_PLANET':2000.,'SPACECRAFT':100.}
def main():
 p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--database',default='loom_dev');p.add_argument('--start',default='2226-01-01T00:00:00 TDB');p.add_argument('--days',type=float,default=1);p.add_argument('bodies',nargs='+');a=p.parse_args();I=Inspector.connect(a.database,a.asset_root);s=I.time.parse(a.start);e=s+a.days*DAY
 for b in a.bodies:
  c=I.orbital_center(b);tol=TOL.get(I.bodies[b]['body_class'],5000.);t=time.time();f=compile_adaptive(I,b,c,s,e,tol);dt=time.time()-t;segs=f['segments'];print(json.dumps({'body':b,'center':c,'segments':len(segs),'representations':{r:sum(x['representation']==r for x in segs) for r in sorted({x['representation'] for x in segs})},'bytes':len(json.dumps(f,separators=(',',':'))),'compile_s':round(dt,3),'max_observed_error_km':max(x.get('observed_error_km',0) for x in segs)},sort_keys=True),flush=True)
if __name__=='__main__':main()
