"""Read-only gravity-assist preflight; no runtime modifications."""
import csv, hashlib, json, resource, time
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P = Path(__file__).resolve().parent
ROOT = P.parents[3]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    start=time.monotonic()
    exp=json.loads((P/'experiment.json').read_text())
    old=json.loads((P/'table_manifest_direct_time.json').read_text())
    giant=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text())
    recovered_path=P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json'
    recovered=json.loads(recovered_path.read_text()) if recovered_path.exists() else {'tables':{}}
    world={r['body']:r for r in csv.DictReader((P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())}
    travel=OnDemandTravel(asset_root=exp['asset_root'])
    source,_=travel.adapter.registry.source_for('EARTH',old['first'])
    end,_=travel.adapter.registry.source_for('EARTH',old['last'])
    assert source.sha256==end.sha256 and source.navigation_grade and source.status=='QUALIFIED'
    kernels=[]
    for a in source.kernel_assets:
        assert a.path.exists() and sha(a.path)==a.sha256, ('KERNEL_CHECK',str(a.path))
        kernels.append({'path':str(a.path),'sha256':a.sha256})
    tables=set(old['tables'])|set(giant['tables'])|set(recovered['tables'])|{'EARTH'}
    eligible=[];skipped=[]
    for body in sorted(tables|set(world)):
        w=world.get(body)
        if body not in tables: reason='NO_STATE_TABLE'
        elif w is None or not w['gm_km3_s2']: reason='NO_WORLD_AUTHORITY_GRAVITY'
        elif not w['mean_radius_km']: reason='NO_WORLD_AUTHORITY_RADIUS'
        else: reason=None
        if reason: skipped.append({'body':body,'reason':reason})
        else: eligible.append({'body':body,'mu_km3_s2':w['gm_km3_s2'],'radius_km':w['mean_radius_km']})
    result={'earth_source_sha256':source.sha256,'earth_spice_id':str(travel.adapter.registry.body_identifier('EARTH').identifier_value),'earth_kernel_files':kernels,'table_count_including_earth':len(tables),'table_names':sorted(tables),'eligible_candidates':eligible,'skipped':skipped,'parent_hashes':{str(x):sha(P/x) for x in ('experiment.json','table_manifest_direct_time.json','PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json','RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv')},'sqlite_sha256':sha(ROOT/'data/LOOM_2226.sqlite3'),'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
    print(json.dumps(result,indent=2,sort_keys=True),flush=True)
if __name__=='__main__':main()
