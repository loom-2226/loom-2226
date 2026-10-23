"""Build Earth centre table on pinned time grid, direct SPICE bitwise audit."""
import hashlib,json,resource,time
from pathlib import Path
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent
OUT=Path('/home/ubuntu/LOOM-output/pr427_assist_earth_table_test_only')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 t=time.monotonic();old=json.loads((P/'table_manifest_direct_time.json').read_text());e=json.loads((P/'experiment.json').read_text())
 etp=Path(old['table_root'])/'builder_et.npy';assert sha(etp)==old['builder_et_sha256'];et=np.load(etp)
 travel=OnDemandTravel(asset_root=e['asset_root']);src,_=travel.adapter.registry.source_for('EARTH',old['first']);last,_=travel.adapter.registry.source_for('EARTH',old['last']);assert src.sha256==last.sha256 and src.navigation_grade and src.status=='QUALIFIED'
 for a in src.kernel_assets:assert a.path.exists() and sha(a.path)==a.sha256
 ident=str(travel.adapter.registry.body_identifier('EARTH').identifier_value);assert ident=='399'
 travel.adapter._load_source(src);travel.adapter._require_source_object_coverage(src,399,float(et[0]));travel.adapter._require_source_object_coverage(src,399,float(et[-1]))
 chunks=[]
 for lo in range(0,len(et),1000):
  arr,_=spice.spkezr(ident,et[lo:lo+1000],'ECLIPJ2000','NONE','10');chunks.append(np.asarray(arr,dtype=np.float64))
 array=np.concatenate(chunks);assert array.shape==(len(et),6)
 for i in range(len(et)):
  direct,_=spice.spkezr(ident,float(et[i]),'ECLIPJ2000','NONE','10')
  assert np.array_equal(array[i].view(np.uint64),np.asarray(direct,dtype=np.float64).view(np.uint64)),('BITWISE_MISMATCH',i)
 OUT.mkdir(parents=True,exist_ok=True);file=OUT/'EARTH.npy';assert not file.exists();np.save(file,array)
 report={'spice_id':399,'source_sha256':src.sha256,'kernel_files':[{'path':str(a.path),'sha256':a.sha256} for a in src.kernel_assets],'table_sha256':sha(file),'table_path':str(file),'time_grid_sha256':sha(etp),'validation_samples':len(et),'bitwise_direct_spice':True,'seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 target=P/'PR427_ASSIST_EARTH_TABLE_REPORT_TEST_ONLY.json';assert not target.exists();target.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,sort_keys=True),flush=True)
if __name__=='__main__':main()
