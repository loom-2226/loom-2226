#!/usr/bin/env python3
import json,sys
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engineering.civprop.contracts.actor_roster_audit_v0_3 import classify,coverage
root=Path(__file__).resolve().parents[2]
seed=json.loads((root/"engineering/civprop/candidate_inputs/LOOM_GROUP_AGENT_SEED_2026_v0.3.json").read_text())
rows=classify(seed)
doc={"audit_id":"ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3","classification":"NON_CANON_PRE_ACTOR_EXECUTION_AUDIT",
     "node_count":len(rows),"autonomous_actor_count":sum(x.autonomous_eligible for x in rows),
     "role_coverage":{k:list(v) for k,v in coverage(rows).items()},"nodes":[asdict(x) for x in rows]}
out=root/"engineering/civprop/candidate_inputs/ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json"
out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
print(out,doc["node_count"],doc["autonomous_actor_count"])
