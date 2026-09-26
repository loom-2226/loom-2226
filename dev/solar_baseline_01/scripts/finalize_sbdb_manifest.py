#!/usr/bin/env python3
"""Validate and freeze the first-pass exact-SPK acquisitions; never replaces bytes."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]; raw=root/'raw'
first=json.loads((root/'reports/sbdb_acquisition_manifest.json').read_text())
records=[]; rejected=[]
for attempt in first['failures']:
    body,spk=attempt['body_id'],attempt['spk']
    p=raw/f'sbdb_spk_{spk}.json'
    if not p.exists():
        rejected.append({'body_id':body,'spk_id':spk,'disposition':'SOURCE_DOES_NOT_COVER_BODY_CLASS','reason':attempt['error'],'requested_url':f'https://ssd-api.jpl.nasa.gov/sbdb.api?spk={spk}&phys-par=1&alt-des=1&full-prec=1'})
        continue
    x=json.loads(p.read_text()); sig=x.get('signature',{})
    got=(x.get('object') or {}).get('spkid')
    if sig.get('source')!='NASA/JPL Small-Body Database (SBDB) API' or sig.get('version')!='1.3':
        rejected.append({'body_id':body,'spk_id':spk,'disposition':'HOLD','reason':'unexpected API signature','signature':sig});continue
    if str(got)!=str(spk):
        rejected.append({'body_id':body,'spk_id':spk,'disposition':'AMBIGUOUS_IDENTITY','reason':'response SPK does not exactly match requested SPK','response_spk_id':got});continue
    records.append({'body_id':body,'spk_id':spk,'artifact':p.name,'source_url':f'https://ssd-api.jpl.nasa.gov/sbdb.api?spk={spk}&phys-par=1&alt-des=1&full-prec=1','acquired_at_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'signature':sig,'phys_par_count':len(x.get('phys_par') or []),'object_spk_id':got,'orbit_retained_as_raw_context_only':True})
out={'authority':'NASA/JPL Solar System Dynamics','product':'SBDB API exact-object endpoint','documented_api_version':'1.0 (published API doc)','observed_api_version':'1.3 (response signature)','version_discrepancy':'Adapter pins observed response signature 1.3 and validates its shape; source documentation lags deployed response. Initial strict 1.0 check is preserved in first_pass_sbdb_acquisition_manifest.json.','requested_scope':'exact NAIF_ID lookups for existing LOOM small-body-class identities only; no name-only matching; no bulk import','parameters':{'phys-par':'1','alt-des':'1','full-prec':'1'},'successful':len(records),'rejected_or_held':len(rejected),'records':records,'rejected_or_held_records':rejected}
(root/'reports/sbdb_acquisition_manifest_v1_3.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(root/'reports/first_pass_sbdb_acquisition_manifest.json').write_text(json.dumps(first,indent=2,sort_keys=True)+'\n')
print(json.dumps({'successful':len(records),'rejected_or_held':len(rejected),'rejected':rejected},sort_keys=True))
