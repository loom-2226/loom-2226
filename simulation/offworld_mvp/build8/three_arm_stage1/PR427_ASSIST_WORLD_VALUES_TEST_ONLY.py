"""Read-only world celestial_dynamics GM/radius authority for assist pilot."""
import hashlib,json,resource,sqlite3,time
from pathlib import Path
P=Path(__file__).resolve().parent;DB=P.parents[3]/'data/LOOM_2226.sqlite3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();c=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 names={'EARTH':'EA','JUPITER':'JU','SATURN':'SA','URANUS':'UR','NEPTUNE':'NE'}
 vals={}
 for body,id in names.items():
  row=c.execute('select entity_id,gm_km3_s2,mean_radius_km from celestial_dynamics where entity_id=?',(id,)).fetchone()
  assert row is not None,('MISSING_BODY',body,id)
  assert row['gm_km3_s2'] is not None and row['mean_radius_km'] is not None,('MISSING_GM_OR_RADIUS',body,id)
  vals[body]={'entity_id':id,'gm_km3_s2':row['gm_km3_s2'],'mean_radius_km':row['mean_radius_km'],'source':'data/LOOM_2226.sqlite3:celestial_dynamics','source_entity_id':id,'source_columns':['gm_km3_s2','mean_radius_km']}
 print(json.dumps({'database_sha256':sha(DB),'values':vals,'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024},sort_keys=True,indent=2),flush=True)
if __name__=='__main__':main()
