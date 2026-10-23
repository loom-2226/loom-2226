"""Read-only kernel coverage audit for extension to 2035-12-31."""
import json,hashlib,resource,time
from pathlib import Path
from datetime import datetime,timezone
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();e=json.loads((P/'experiment.json').read_text());old=json.loads((P/'table_manifest_direct_time.json').read_text());giant=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text());t=OnDemandTravel(asset_root=e['asset_root']);first=old['first'];last='2035-12-31T00:00:00Z';names=sorted(set(old['tables'])|set(giant['tables'])|{'EARTH','MARS','VENUS','MERCURY','PLUTO','NEPTUNE'})
 rows=[]
 for b in names:
  row={'body':b,'extension':'EXCLUDED'}
  try:
   a,_=t.adapter.registry.source_for(b,first);z,_=t.adapter.registry.source_for(b,last)
   row.update(source=a.source_id if hasattr(a,'source_id') else str(a),kernel_sha256=a.sha256,source_status=a.status,source_qualified=a.navigation_grade,kernel_files=[str(x.path) for x in a.kernel_assets]);assert a.sha256==z.sha256 and a.navigation_grade and a.status=='QUALIFIED'
   for x in a.kernel_assets:assert x.path.exists() and sha(x.path)==x.sha256
   t.adapter._load_source(a);ident=int(t.adapter.registry.body_identifier(b).identifier_value)
   import spiceypy as spice
   et=spice.str2et(last);t.adapter._require_source_object_coverage(a,ident,et)
   row.update(extension='COVERED',spice_id=ident)
  except Exception as ex:row['reason']=str(ex)
  rows.append(row);print('COVERAGE',json.dumps(row,sort_keys=True),flush=True)
 print('SUMMARY',json.dumps({'covered':[r['body'] for r in rows if r['extension']=='COVERED'],'excluded':[r['body'] for r in rows if r['extension']!='COVERED'],'seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}),flush=True)
if __name__=='__main__':main()
