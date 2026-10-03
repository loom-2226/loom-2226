#!/usr/bin/env python3
import json,subprocess,sys
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engineering.civprop.contracts.actor_jurisdiction_v0_3 import *
root=Path(__file__).resolve().parents[2]
seed=json.load(open(root/'engineering/civprop/candidate_inputs/LOOM_GROUP_AGENT_SEED_2026_v0.3.json'))
raw=subprocess.check_output(['psql','-d','loom_dev','-At','-c',"select iso3 from loom_earth.earth_area where snapshot_id='earth-v0-1-9934d0ac-20260925' and economic_qualified order by iso3"],text=True)
rows=build(seed,raw.split())
doc={"jurisdiction_id":"ACTOR_JURISDICTION_2026_V0_3","classification":"NON_CANON_2026_EVIDENCE_AND_BEST_ESTIMATE_INITIALIZATION","link_count":len(rows),"actor_count":len(set(x.actor_id for x in rows)),"digest":digest(rows),"links":[asdict(x) for x in rows]}
out=root/'engineering/civprop/candidate_inputs/ACTOR_JURISDICTION_2026_V0_3.json';out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
print(doc["actor_count"],doc["link_count"],doc["digest"])
