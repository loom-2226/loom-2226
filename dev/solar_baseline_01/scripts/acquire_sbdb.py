#!/usr/bin/env python3
"""Acquire exact-NAIF-ID SBDB records for existing LOOM small bodies only."""
import json, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'raw'; IDENTITY=RAW/'loom_solar_identity_snapshot.tsv'
SMALL={'ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','COMET','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','INTERSTELLAR_OBJECT'}
records={}
with IDENTITY.open() as f:
    for line in f:
        cols=line.rstrip('\n').split('|')
        if len(cols)!=9: raise SystemExit(f'bad identity snapshot row: {line!r}')
        body,name,cls,parent,bstatus,authority,kind,value,istatus=cols
        if cls in SMALL and authority=='NAIF' and kind=='NAIF_ID' and istatus=='ACTIVE':
            records[body]=value
acquired=[]; failures=[]
for body,spk in sorted(records.items()):
    url='https://ssd-api.jpl.nasa.gov/sbdb.api?'+urllib.parse.urlencode({'spk':spk,'phys-par':'1','alt-des':'1','full-prec':'1'})
    path=RAW/f'sbdb_spk_{spk}.json'
    if path.exists(): raise SystemExit(f'refusing to overwrite frozen acquisition: {path}')
    req=urllib.request.Request(url,headers={'User-Agent':'LOOM-SOLAR-BASELINE-01/1.0 research-data-client'})
    started=datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            payload=response.read(); status=response.status
        path.write_bytes(payload)
        try: obj=json.loads(payload)
        except Exception as e: failures.append({'body_id':body,'spk':spk,'error':f'json:{e}'}); continue
        if obj.get('signature',{}).get('version')!='1.0': failures.append({'body_id':body,'spk':spk,'error':'unexpected API signature'}); continue
        if obj.get('error'): failures.append({'body_id':body,'spk':spk,'error':obj['error']})
        acquired.append({'body_id':body,'spk_id':spk,'artifact':path.name,'url':url,'http_status':status,'acquired_at_utc':started,'signature':obj.get('signature',{}),'object_spkid':obj.get('object',{}).get('spkid'),'phys_par_count':len(obj.get('phys_par') or []),'api_error':obj.get('error')})
    except Exception as e:
        failures.append({'body_id':body,'spk':spk,'error':repr(e)})
    time.sleep(0.12)
manifest={'source':'NASA/JPL SSD SBDB API','api':'https://ssd-api.jpl.nasa.gov/sbdb.api','selection':'existing loom_solar.body NAIF_ID only; exact spk parameter; no name-only lookup','query_parameters':{'phys-par':'1','alt-des':'1','full-prec':'1'},'requested_body_count':len(records),'successful_responses':len(acquired),'failures':failures,'records':acquired}
(ROOT/'reports/sbdb_acquisition_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(json.dumps({'requested':len(records),'received':len(acquired),'failures':failures},sort_keys=True))
