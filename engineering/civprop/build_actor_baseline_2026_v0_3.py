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

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--database",default="loom_dev")
 ap.add_argument("--output",default="engineering/civprop/candidate_inputs/ACTOR_BASELINE_2026_V0_3.json"); a=ap.parse_args()
 root=Path(__file__).resolve().parents[2]
 seedp=root/"engineering/civprop/candidate_inputs/LOOM_GROUP_AGENT_SEED_2026_v0.3.json"
 seed=json.loads(seedp.read_text()); auth=pg_sector_rows(a.database); rows=build_actor_baseline_2026(seed,auth)
 doc={"baseline_id":BASELINE_ID,"classification":"NON_CANON_DERIVED_ESTIMATED_2026_INITIALIZATION",
      "earth_snapshot":EARTH_SNAPSHOT,"actor_count":len(rows),"digest":baseline_digest(rows),
      "sector_authority_2026":[asdict(x) for x in auth],"actors":[asdict(x) for x in rows]}
 out=root/a.output; out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
 print("actors",len(rows),"digest",doc["digest"],"output",out)
if __name__=="__main__": main()
