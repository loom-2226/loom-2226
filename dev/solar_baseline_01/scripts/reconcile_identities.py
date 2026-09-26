#!/usr/bin/env python3
"""Apply the documented NAIF numbered-asteroid alias rule, then class-check identities."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'raw'; R=ROOT/'reports'
naif_doc=(RAW/'naif_ids_required_reading.html').read_text(errors='replace')
barycenter_ids={m.group(1) for m in __import__('re').finditer(r"(?m)^\s*(\d+)\s+'[^']*BARYCENTER[^']*'",naif_doc,__import__('re').I)}
small={'ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','COMET','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','INTERSTELLAR_OBJECT'}
bodies={}
for line in (RAW/'loom_solar_identity_snapshot.tsv').read_text().splitlines():
 x=line.split('|'); b=x[0]
 bodies.setdefault(b,{'body_id':b,'canonical_name':x[1],'body_class':x[2],'ids':[]})['ids'].append({'authority':x[5],'type':x[6],'value':x[7],'status':x[8]})
def naif_alias_pair(v):
 n=int(v)
 if 20_000_001<=n<=49_999_999:return (str(2_000_000+(n-20_000_000)), 'NAIF numbered-asteroid legacy/extended alias formula')
 if 2_000_001<=n<=2_999_999:return (str(20_000_000+(n-2_000_000)), 'NAIF numbered-asteroid legacy/extended alias formula')
 return None
def is_barycenter_assignment(body,identifier):
 return bodies[body]['body_class']!='BARYCENTER' and (str(identifier) in barycenter_ids or (bodies[body]['body_class']=='BINARY_ASTEROID_PRIMARY' and 20_000_001<=int(identifier)<=49_999_999))
# Input: first pass kept all successful raw responses and explicit failures.
first=json.loads((R/'first_pass_sbdb_acquisition_manifest.json').read_text())
records=[]; held=[]
for rec in first['records']:
 body,spk=rec['body_id'],str(rec['spk_id']); obj=json.loads((RAW/rec['artifact']).read_text())
 got=str((obj.get('object') or {}).get('spkid'))
 alias=naif_alias_pair(spk)
 alias_match=bool(alias and got==alias[0])
 if got!=spk and not alias_match:
  held.append({'body_id':body,'requested_spk_id':spk,'response_spk_id':got,'disposition':'AMBIGUOUS_IDENTITY','reason':'no exact ID or documented NAIF alias match'});continue
 record={**rec,'response_spk_id':got,'crosswalk_basis':'EXACT_NAIF_ID' if got==spk else alias[1],'crosswalk_disposition':'MATCH_ALIAS' if alias_match else 'MATCH_EXACT'}
 if is_barycenter_assignment(body,spk):
  record['crosswalk_disposition']='HOLD'
  record['hold_reason']='LOOM body class is BINARY_ASTEROID_PRIMARY but the assigned 8-digit NAIF code denotes the system barycenter; primary-body code is not present.'
 records.append(record)
for fail in first['failures']:
 body,spk=fail['body_id'],str(fail['spk']); p=RAW/f'sbdb_spk_{spk}.json'
 if p.exists():
  obj=json.loads(p.read_text());got=str((obj.get('object') or {}).get('spkid'));alias=naif_alias_pair(spk)
  if got==spk or (alias and got==alias[0]):
   basis='EXACT_NAIF_ID' if got==spk else alias[1]
   disposition='MATCH_EXACT' if got==spk else 'MATCH_ALIAS'
   reason='STRICT_VERSION_CHECK_FAILURE_PRESERVED' if fail.get('error')=='unexpected API signature' else None
   record={'body_id':body,'spk_id':spk,'artifact':p.name,'url':f'https://ssd-api.jpl.nasa.gov/sbdb.api?spk={spk}&phys-par=1&alt-des=1&full-prec=1','object_spkid':got,'phys_par_count':len(obj.get('phys_par') or []),'signature':obj.get('signature'),'crosswalk_basis':basis,'crosswalk_disposition':disposition,'first_pass':reason}
   if is_barycenter_assignment(body,spk):
    record['crosswalk_disposition']='HOLD';record['hold_reason']='NAIF reference names this identifier as a system barycenter, but the LOOM body class is not BARYCENTER.'
   records.append(record)
  else:held.append({'body_id':body,'requested_spk_id':spk,'response_spk_id':got,'disposition':'AMBIGUOUS_IDENTITY','reason':fail['error']})
 else:held.append({'body_id':body,'requested_spk_id':spk,'disposition':'SOURCE_DOES_NOT_COVER_BODY_CLASS','reason':fail['error']})
out={'policy_source':'NAIF Integer ID codes Required Reading, Asteroids section: original 7-digit permanent-asteroid IDs remain allowed alongside the documented 8-digit extension; transformations use only that declared arithmetic scheme and then verify response identity','api_signature':'1.3','documented_api_signature':'1.0','records':records,'held':held,'request_count':56,'response_count':len(records),'match_exact':sum(x['crosswalk_disposition']=='MATCH_EXACT' for x in records),'match_alias':sum(x['crosswalk_disposition']=='MATCH_ALIAS' for x in records),'identity_hold':sum(x['crosswalk_disposition']=='HOLD' for x in records),'source_not_found':sum(x['disposition']=='SOURCE_DOES_NOT_COVER_BODY_CLASS' for x in held)}
(R/'sbdb_identity_crosswalk.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:out[k] for k in ('request_count','response_count','match_exact','match_alias','identity_hold','source_not_found')},sort_keys=True))
