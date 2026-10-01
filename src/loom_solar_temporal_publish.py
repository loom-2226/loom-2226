"""Immutable chunk publisher for the governed Solar temporal product."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,shutil,tempfile
from pathlib import Path
from src.loom_solar_inspector import Inspector
from src.loom_solar_temporal import compile_chunk

DAY=86400.0
DEFAULT_TOL={'NATURAL_SATELLITE':25.0,'PLANET':2000.0,'DWARF_PLANET':2000.0,'SPACECRAFT':100.0}

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def write(root,kind,obj):
 raw=canonical(obj); h=hashlib.sha256(raw).hexdigest(); p=root/kind/f'{h}.json'; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw); Path(str(p)+'.gz').write_bytes(gzip.compress(raw,mtime=0)); return {'uri':str(p.relative_to(root)),'sha256':h,'bytes':len(raw),'gzip_bytes':len(gzip.compress(raw,mtime=0))}
def center_for(I,b): return I.orbital_center(b)
def tolerance(I,b):
 base=DEFAULT_TOL.get(I.bodies[b]['body_class'],5000.0)
 estimates=[I.registry.sources[c.ephemeris_source_id].uncertainty_km for c in I.registry.coverage
            if c.body_id==b and c.status=='QUALIFIED'
            and I.registry.sources[c.ephemeris_source_id].state_capability=='ESTIMATED_RELATIVE'
            and I.registry.sources[c.ephemeris_source_id].uncertainty_km is not None]
 return min(base,max(0.001,min(estimates)*0.01)) if estimates else base

def publish(I,out,start,end,chunk_days=32,body_ids=None):
 ids=sorted(body_ids or I.bodies); out=Path(out); out.mkdir(parents=True,exist_ok=True); stage=Path(tempfile.mkdtemp(prefix='.temporal-',dir=out))
 try:
  chunks=[]; t=start
  while t<end:
   u=min(end,t+chunk_days*DAY)
   c=compile_chunk(I,ids,t,u,lambda b:center_for(I,b),lambda b:tolerance(I,b)); desc=write(stage,'chunks',c); chunks.append({'start_et':t,'end_et':u,**desc}); t=u
  dispositions=[]
  for b in ids:
   states=[]
   for t in (start,end):
    r=I.at(b,t,center_for(I,b)); states.append({'epoch_et':t,'resolution':r['resolution'],'authority_class':r.get('authority_class'),'reason':r.get('reason')})
   dispositions.append({'body_id':b,'center_id':center_for(I,b),'boundary_states':states})
  manifest={'schema':'loom.solar-temporal.manifest/1.0','start_et':start,'end_et':end,'frame':'ECLIPJ2000','units':'km,km/s','chunk_days':chunk_days,'catalog_count':len(ids),'chunks':chunks,'dispositions':dispositions,'authority':I.authority}
  manifest['build_id']=hashlib.sha256(canonical(manifest)).hexdigest(); bd=stage/'builds'/manifest['build_id']; bd.mkdir(parents=True); mb=canonical(manifest); (bd/'manifest.json').write_bytes(mb); (bd/'manifest.json.gz').write_bytes(gzip.compress(mb,mtime=0))
  for d in ('chunks','builds'): shutil.copytree(stage/d,out/d,dirs_exist_ok=True)
  ptr={'build_id':manifest['build_id'],'manifest_uri':f"builds/{manifest['build_id']}/manifest.json",'manifest_sha256':hashlib.sha256(mb).hexdigest()}; tmp=out/'current.json.tmp';tmp.write_bytes(canonical(ptr));os.replace(tmp,out/'current.json')
  return manifest
 finally: shutil.rmtree(stage,ignore_errors=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--database',default='loom_dev');p.add_argument('--asset-root',required=True);p.add_argument('--output',required=True);p.add_argument('--start',default='2226-01-01T00:00:00 TDB');p.add_argument('--end',default='2226-02-01T00:00:00 TDB');p.add_argument('--chunk-days',type=int,default=32);p.add_argument('--bodies',nargs='*');a=p.parse_args();I=Inspector.connect(a.database,a.asset_root);m=publish(I,Path(a.output),I.time.parse(a.start),I.time.parse(a.end),a.chunk_days,a.bodies);print(json.dumps({'build_id':m['build_id'],'catalog_count':m['catalog_count'],'chunks':len(m['chunks'])},sort_keys=True))
if __name__=='__main__':main()
