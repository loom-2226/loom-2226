"""Compare PR427 text UTC->ET against numeric UTC seconds + deltet on all ticks."""
import hashlib,json,resource,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import spiceypy as spice
P=Path(__file__).resolve().parent
LSK=Path('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls')
assert hashlib.sha256(LSK.read_bytes()).hexdigest()=='678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b'
spice.furnsh(str(LSK))
def main():
 start=time.monotonic();manifest=json.loads((P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json').read_text());first=datetime.fromisoformat(manifest['first'].replace('Z','+00:00'));n=manifest['time_samples'];step=manifest['step_days']
 ticks=[first+timedelta(days=i*step) for i in range(n)]
 A=np.asarray([spice.str2et(t.strftime('%Y-%m-%dT%H:%M:%S')) for t in ticks],dtype=np.float64)
 # UTC seconds relative to J2000 UTC clock, with each epoch's DELTET(UTC).
 j2000utc=datetime(2000,1,1,12,tzinfo=timezone.utc)
 utc=np.asarray([(t-j2000utc).total_seconds() for t in ticks],dtype=np.float64)
 B=np.asarray([u+spice.deltet(float(u),'UTC') for u in utc],dtype=np.float64)
 diff=np.abs(A-B);equal=bool(np.array_equal(A.view(np.uint64),B.view(np.uint64)))
 # et2utc returns the exact UTC wall-clock tick strings, to whole seconds.
 mismatches=[]
 for i,(t,et) in enumerate(zip(ticks,B)):
  got=spice.et2utc(float(et),'ISOC',0)
  expected=t.strftime('%Y-%m-%dT%H:%M:%S')
  if got!=expected and len(mismatches)<10:mismatches.append({'index':i,'expected':expected,'got':got})
 try:
  from astropy.time import Time
  import astropy.units as u
  sample=np.unique(np.linspace(0,n-1,201,dtype=int));astr=Time([ticks[i] for i in sample],scale='utc');oracle=np.asarray((astr.tdb.jd-2451545.0)*86400,dtype=np.float64);oracle_diff=np.abs(B[sample]-oracle);astro={'available':True,'samples':len(sample),'max_difference_seconds':float(oracle_diff.max())}
 except ImportError:astro={'available':False,'reason':'astropy not installed in existing interpreter; no install authorized'}
 result={'ticks':n,'step_days':step,'lsk_sha256':hashlib.sha256(LSK.read_bytes()).hexdigest(),'max_abs_A_minus_B_seconds':float(diff.max()),'bitwise_equal':equal,'different_ticks':int(np.count_nonzero(A.view(np.uint64)!=B.view(np.uint64))),'roundtrip_mismatches_first_ten':mismatches,'roundtrip_mismatch_count':sum(spice.et2utc(float(et),'ISOC',0)!=t.strftime('%Y-%m-%dT%H:%M:%S') for t,et in zip(ticks,B)),'astropy':astro,'leap_second_assumption':'No leap seconds after last LSK entry; accepted for 2035','elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 print(json.dumps(result,indent=2,sort_keys=True),flush=True)
if __name__=='__main__':main()
