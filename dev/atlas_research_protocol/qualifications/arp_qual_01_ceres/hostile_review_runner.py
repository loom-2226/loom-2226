from __future__ import annotations

import copy
import json
from pathlib import Path

import sys
REPO = Path(__file__).parents[4]
sys.path.insert(0, str(REPO / "dev"))
from atlas_research_protocol.validate import qualify


campaign_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "attempt_02/campaign.json"
BASE = json.loads(campaign_path.read_text())
POLICY = json.loads((REPO / "dev/atlas_research_protocol/policies/source_authority.json").read_text())


def attacked(name, mutate):
    doc = copy.deepcopy(BASE)
    mutate(doc)
    result = qualify(doc, POLICY, campaign_path.parent)
    return {"attack": name, "rejected": result["status"] == "FAIL", "errors": result["errors"]}


results = []
results.append(attacked("secondary_source_replaces_primary", lambda d: (d["sources"].append({"source_id":"secondary","provider":"secondary","authority_domain":"gravity_shape","authority_role":"SECONDARY","source_type":"SUMMARY","locator":"https://example.invalid","primary_available":True}), d["assertions"].append({**d["assertions"][0],"assertion_id":"secondary-assertion","source_id":"secondary","canonical_assertion_key":"secondary|assertion"}))))
results.append(attacked("derived_publications_counted_independent", lambda d: (d["assertions"][0].update(independent=True), d["assertions"][1].update(independent=True), d["assertions"][1].update(independent_evidence_lineage_id=d["assertions"][0]["independent_evidence_lineage_id"]))))
results.append(attacked("regional_to_global", lambda d: d["assertions"][10].update(scope_claim="GLOBAL")))
results.append(attacked("coarse_to_site_resolution", lambda d: d["assertions"][7].update(resolution={"source_grain":"COARSE","claimed_grain":"SITE"})))
results.append(attacked("model_to_direct_measurement", lambda d: d["assertions"][5].update(claim_kind="OBSERVATION")))
results.append(attacked("post_cutoff_source", lambda d: d["sources"][0].update(publication_date="2026-01-01")))
results.append(attacked("range_midpoint_fabrication", lambda d: d["assertions"][11].update(reported_value=100)))
results.append(attacked("unknown_filled_with_value", lambda d: (d["assertions"][11].update(research_coverage="UNKNOWN"), d["assertions"][11].update(reported_value=100))))
results.append(attacked("future_observable_promoted_to_knowable", lambda d: d["epistemic_frontier"][-1].update(state_at_cutoff="KNOWABLE")))
results.append(attacked("forbidden_engineering_frontier", lambda d: d["epistemic_frontier"][0].update(phase="ENGINEERING_DERIVED")))
results.append(attacked("false_completeness", lambda d: d["coverage_summary"].update(complete_claim=True)))
results.append(attacked("blocking_lien_ignored", lambda d: d["liens"].append({"lien_id":"OPEN-BLOCK","state":"OPEN","severity":"BLOCKING","target":"assertion","finding":"synthetic unsupported claim"})))

out = {"status":"PASS" if all(r["rejected"] for r in results) else "FAIL", "attacks":results}
output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "attempt_02/hostile_review.json"
output_path.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
print(json.dumps({"status":out["status"],"attacks":len(results),"rejected":sum(r["rejected"] for r in results)},indent=2))
if out["status"] != "PASS":
    raise SystemExit(1)
