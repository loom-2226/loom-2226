"""Immutable publisher for qualified representation-neutral Solar state functions."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,shutil,tempfile
from pathlib import Path
from src.loom_solar_inspector import Inspector
from src.loom_solar_function_compile import compile_adaptive
from src.loom_solar_temporal_publish import DAY,DEFAULT_TOL,canonical,write,center_for,tolerance

def publish(I,out,start,end,chunk_days=8,body_ids=None):
 ids=sorted(body_ids or I.bodies);out=Path(out);out.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.functions-',dir=out))
 try:
  chunks=[];t=start
  while t<end:
   u=min(end,t+chunk_days*DAY);objects=[]
   for b in ids:
    c=center_for(I,b);r0=I.at(b,t,c);r1=I.at(b,u,c)
    if r0['resolution']=='RESOLVED' and r1['resolution']=='RESOLVED': objects.append(compile_adaptive(I,b,c,t,u,tolerance(I,b)))
    else: objects.append({'representation':'UNRESOLVED_STATE_FUNCTION','body_id':b,'center_id':c,'reference_frame':'ECLIPJ2000','start_et':t,'end_et':u,'declared_error_km':tolerance(I,b),'resolution':'UNRESOLVED','reason':r0.get('reason') or r1.get('reason')})
   payload={'schema':'loom.solar-state-functions/1.0','start_et':t,'end_et':u,'frame':'ECLIPJ2000','units':'km','objects':objects,'authority':I.authority};desc=write(stage,'chunks',payload);chunks.append({'start_et':t,'end_et':u,**desc});t=u
  manifest={'schema':'loom.solar-state-functions.manifest/1.0','start_et':start,'end_et':end,'frame':'ECLIPJ2000','units':'km','chunk_days':chunk_days,'catalog_count':len(ids),'chunks':chunks,'authority':I.authority};manifest['build_id']=hashlib.sha256(canonical(manifest)).hexdigest();bd=stage/'builds'/manifest['build_id'];bd.mkdir(parents=True);mb=canonical(manifest);(bd/'manifest.json').write_bytes(mb);(bd/'manifest.json.gz').write_bytes(gzip.compress(mb,mtime=0));shutil.copytree(stage/'chunks',out/'chunks',dirs_exist_ok=True);shutil.copytree(stage/'builds',out/'builds',dirs_exist_ok=True);ptr={'build_id':manifest['build_id'],'manifest_uri':f"builds/{manifest['build_id']}/manifest.json",'manifest_sha256':hashlib.sha256(mb).hexdigest()};tmp=out/'current.json.tmp';tmp.write_bytes(canonical(ptr));os.replace(tmp,out/'current.json');return manifest
 finally:shutil.rmtree(stage,ignore_errors=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--database',default='loom_dev');p.add_argument('--asset-root',required=True);p.add_argument('--output',required=True);p.add_argument('--start',default='2226-01-01T00:00:00 TDB');p.add_argument('--end',default='2226-01-02T00:00:00 TDB');p.add_argument('--chunk-days',type=float,default=1);p.add_argument('--bodies',nargs='*');a=p.parse_args();I=Inspector.connect(a.database,a.asset_root);m=publish(I,a.output,I.time.parse(a.start),I.time.parse(a.end),a.chunk_days,a.bodies);print(json.dumps({'build_id':m['build_id'],'catalog_count':m['catalog_count'],'chunks':len(m['chunks'])},sort_keys=True))
if __name__=='__main__':main()
