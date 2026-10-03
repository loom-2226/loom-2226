#!/usr/bin/env python3
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from dataclasses import asdict
from engineering.civprop.contracts.actor_baseline_2026_v0_3 import *

def pg_sector_rows(db):
 q="""select sector,sum(gross_output),sum(investment),sum(capital),sum(employment) from loom_earth.earth_sector_year
 where snapshot_id='earth-v0-1-9934d0ac-20260925' and year=2026
 and sector in ('BULK_MATERIALS','CERTIFICATION_METROLOGY','COMPUTE','SERVICES','SHIPS_AEROSPACE','TRANSPORT_LOGISTICS')
 group by sector order by sector"""
 raw=subprocess.check_output(["psql","-d",db,"-At","-F","|","-c",q],text=True)
 return tuple(SectorAuthority2026(s,float(g),float(i),float(c),float(e)) for s,g,i,c,e in (x.split("|") for x in raw.splitlines() if x))

def pg_country_sector_rows(db):
 q="""select iso3,sector,gross_output,investment,capital,employment from loom_earth.earth_sector_year
 where snapshot_id='earth-v0-1-9934d0ac-20260925' and year=2026
 and sector in ('BULK_MATERIALS','CERTIFICATION_METROLOGY','COMPUTE','SERVICES','SHIPS_AEROSPACE','TRANSPORT_LOGISTICS')
 order by iso3,sector"""
 raw=subprocess.check_output(["psql","-d",db,"-At","-F","|","-c",q],text=True)
 return tuple(CountrySectorAuthority2026(i,s,float(g),float(v),float(c),float(e)) for i,s,g,v,c,e in (x.split("|") for x in raw.splitlines() if x))

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--database",default="loom_dev")
 ap.add_argument("--output",default="engineering/civprop/candidate_inputs/ACTOR_BASELINE_2026_V0_3.json"); a=ap.parse_args()
 root=Path(__file__).resolve().parents[2]
 seedp=root/"engineering/civprop/candidate_inputs/LOOM_GROUP_AGENT_SEED_2026_v0.3.json"
 seed=json.loads(seedp.read_text()); auth=pg_sector_rows(a.database); country_auth=pg_country_sector_rows(a.database)
 j=json.loads((root/"engineering/civprop/candidate_inputs/ACTOR_JURISDICTION_2026_V0_3.json").read_text())
 home={x["actor_id"]:x["iso3"] for x in j["links"] if x["relation"]=="HOME"}
 rows=build_actor_baseline_2026(seed,auth,country_sector_authority=country_auth,home_by_actor=home)
 doc={"baseline_id":BASELINE_ID,"classification":"NON_CANON_DERIVED_ESTIMATED_2026_INITIALIZATION",
      "earth_snapshot":EARTH_SNAPSHOT,"actor_count":len(rows),"digest":baseline_digest(rows),
      "sector_authority_2026":[asdict(x) for x in auth],"country_sector_authority_used":True,
      "home_actor_count":len(home),"actors":[asdict(x) for x in rows]}
 out=root/a.output; out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
 print("actors",len(rows),"digest",doc["digest"],"output",out)
if __name__=="__main__": main()
