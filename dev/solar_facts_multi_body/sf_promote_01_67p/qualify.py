"""Qualification checks for SF-PROMOTE-01; no external research is used."""
from __future__ import annotations
import hashlib, json, shutil, sqlite3, tempfile
from pathlib import Path
from promote import build, CAMPAIGN, V3

EXPECTED_CAMPAIGN="2f5637c36fa657017f6668b42a7f05f356ebdd0d4db8953be51a0bffca0f38fa"
EXPECTED_HCQ="0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6"
OUT=Path(__file__).with_name("LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3")

def digest(p):
 c=sqlite3.connect(p); rows=[]
 for t in [x[0] for x in c.execute("select name from sqlite_master where type='table' order by name")]:
  rows.append((t,list(c.execute(f"select * from {t} order by rowid"))))
 return hashlib.sha256(json.dumps(rows,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def check(p):
 c=sqlite3.connect(p); c.execute("pragma foreign_keys=on")
 assert c.execute("pragma integrity_check").fetchone()[0]=="ok"
 assert c.execute("pragma foreign_key_check").fetchall()==[]
 assert c.execute("select count(*) from body").fetchone()[0]==1
 assert c.execute("select body_id from body").fetchone()[0]=="COMET_67P"
 assert c.execute("select count(*) from source_artifact").fetchone()[0]==9
 assert c.execute("select count(*) from promotion_assertion").fetchone()[0]==13
 assert c.execute("select count(*) from promotion_review where disposition='PROMOTE'").fetchone()[0]==13
 assert c.execute("select count(*) from fact where fact_status<>'CANDIDATE'").fetchone()[0]==0
 assert c.execute("select count(*) from preferred_fact").fetchone()[0]==0
 assert c.execute("select count(*) from observation where spatial_resolution_value is not null").fetchone()[0]==1
 # The thermal observation's resolution is retained; no temperature scalar exists.
 assert c.execute("select value_numeric from fact where property_code='SURFACE_TEMPERATURE'").fetchone() is None
 assert c.execute("select value_numeric,value_min,value_max from fact where property_code='POROSITY'").fetchone()==(None,72.0,74.0)
 assert c.execute("select source_type from source where persistent_identifier='arXiv:1901.02806'").fetchone()[0]=='PREPRINT'
 assert c.execute("select count(*) from promotion_lineage").fetchone()[0]==1
 # Frontier gaps do not become facts.
 assert c.execute("select count(*) from epistemic_frontier where state_at_cutoff='UNKNOWN'").fetchone()[0]>=2
 # No dynamics or downstream judgment tables/rows are introduced.
 assert c.execute("select value from promotion_manifest where key='phase4_writes'").fetchone()[0]=='0'
 return digest(p)

def main():
 assert hashlib.sha256(V3.read_bytes()).hexdigest()==EXPECTED_HCQ, "HCQ reference drift"
 d=json.loads((CAMPAIGN/'campaign.json').read_text())
 assert hashlib.sha256((CAMPAIGN/'campaign.json').read_bytes()).hexdigest()==EXPECTED_CAMPAIGN
 check(OUT)
 with tempfile.TemporaryDirectory() as td:
  a=build(Path(td)/'a.sqlite3'); b=build(Path(td)/'b.sqlite3')
  da,db=check(a),check(b); assert da==db, (da,db)
 result={"status":"PASS","campaign_sha256":EXPECTED_CAMPAIGN,"hcq_sha256":EXPECTED_HCQ,"database":str(OUT),"database_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),"semantic_digest":digest(OUT),"deterministic_replay":True,"preferred_fact":0,"facts_candidate_only":True,"new_science":False,"phase4_writes":0,"resource_engineering_world_state":False}
 (OUT.parent/'qualification.json').write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=='__main__': main()
