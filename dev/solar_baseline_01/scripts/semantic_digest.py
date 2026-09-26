#!/usr/bin/env python3
"""Canonical semantic digest for the baseline candidate, independent of row IDs/order."""
import hashlib,json,sqlite3,sys
TABLES=('meta','authority_body_ref','body_identifier_ref','source_artifact','identity_crosswalk','candidate_assertion','coverage')
def digest(path,body=None):
 c=sqlite3.connect(path); records=[]
 for table in TABLES:
  cols=[r[1] for r in c.execute(f'pragma table_info({table})')]
  for row in c.execute(f'select * from {table}'):
   item=dict(zip(cols,row))
   if body is not None:
    if table=='meta':continue
    if table=='source_artifact':
     used=c.execute('select count(*) from candidate_assertion where body_id=? and source_artifact_id=?',(body,item.get('artifact_id'))).fetchone()[0] + c.execute('select count(*) from identity_crosswalk where body_id=? and source_artifact_id=?',(body,item.get('artifact_id'))).fetchone()[0]
     if not used:continue
    elif item.get('body_id')!=body:continue
   records.append((table,item))
 c.close(); payload=json.dumps(sorted(records,key=lambda x:(x[0],json.dumps(x[1],sort_keys=True,default=str))),sort_keys=True,default=str,separators=(',',':'),ensure_ascii=False)
 return hashlib.sha256(payload.encode()).hexdigest()
if __name__=='__main__':
 p=sys.argv[1]; bodies=sys.argv[2:]
 out={'whole_semantic_digest':digest(p),'body_digests':{b:digest(p,b) for b in bodies}}
 print(json.dumps(out,sort_keys=True))
