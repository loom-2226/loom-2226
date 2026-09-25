"""Fresh-context hostile qualification for the frozen 67P campaign."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from dev.atlas_research_protocol.validate import load_json, qualify

ROOT = Path(__file__).resolve().parent


def run_attack(campaign: dict, mutate, expected: str) -> dict:
    candidate = copy.deepcopy(campaign)
    mutate(candidate)
    result = qualify(candidate, None, ROOT)
    passed = result["status"] == "FAIL" and any(e.startswith(expected + ":") for e in result["errors"])
    return {"expected_rejection": expected, "passed": passed, "errors": result["errors"]}


def main() -> int:
    campaign = load_json(ROOT / "campaign.json")
    attacks = {
        "regional_to_global": run_attack(campaign, lambda c: c["assertions"][0].update(scope_type="REGIONAL", scope_claim="GLOBAL"), "SCOPE_LAUNDERING"),
        "coarse_to_site": run_attack(campaign, lambda c: c["assertions"][0].update(resolution={"source_grain":"COARSE", "claimed_grain":"SITE"}), "RESOLUTION_LAUNDERING"),
        "model_to_observation": run_attack(campaign, lambda c: c["assertions"][1].update(claim_kind="OBSERVATION"), "EPISTEMIC_PROMOTION"),
        "post_cutoff": run_attack(campaign, lambda c: c["sources"][0].update(publication_date="2026-01-01"), "CUTOFF"),
        "range_midpoint": run_attack(campaign, lambda c: c["assertions"][2].update(value_min=1, value_max=3, reported_value=2, reported_unit="kg"), "RANGE_MIDPOINT"),
        "unknown_fabrication": run_attack(campaign, lambda c: c["assertions"][0].update(research_coverage="UNKNOWN", reported_value=1, reported_unit="km"), "UNKNOWN_FABRICATION"),
        "frontier_promotion": run_attack(campaign, lambda c: c["epistemic_frontier"][0].update(phase="ENGINEERING_DERIVED"), "CONTAMINATION"),
        "duplicate_assertion": run_attack(campaign, lambda c: c["assertions"].append(dict(c["assertions"][0], assertion_id="DUP", canonical_assertion_key=c["assertions"][0]["canonical_assertion_key"])), "DUPLICATE_ASSERTION"),
        "coverage_basis_removal": run_attack(campaign, lambda c: c["lanes"]["gravity_shape"].pop("coverage_basis"), "COVERAGE_BASIS"),
        "forbidden_frontier": run_attack(campaign, lambda c: c["epistemic_frontier"][0].update(phase="ECONOMIC_DERIVED"), "CONTAMINATION"),
    }
    # The model-to-observation mutation is written explicitly because it must
    # target the model-product assertion, not a Ceres-specific index.
    model_attack = copy.deepcopy(campaign)
    model = next(a for a in model_attack["assertions"] if a["claim_kind"] == "MODEL_PRODUCT")
    model.update(claim_kind="OBSERVATION", evidence_class="PHYSICAL_MODEL")
    model_result = qualify(model_attack, None, ROOT)
    attacks["model_to_observation"] = {"expected_rejection":"EPISTEMIC_PROMOTION", "passed": any(e.startswith("EPISTEMIC_PROMOTION:") for e in model_result["errors"]), "errors":model_result["errors"]}
    liens = []
    if not all(a["passed"] for a in attacks.values()):
        liens.append({"lien_id":"L-67P-HOSTILE-001","state":"OPEN","severity":"BLOCKING","target":"campaign","finding":"One hostile fixture was not rejected."})
    else:
        liens.extend([
            {"lien_id":"L-67P-ORBIT-001","state":"SOURCE_UNAVAILABLE","severity":"NON_BLOCKING","target":"orbit_geometry","finding":"No orbit-element artifact admitted."},
            {"lien_id":"L-67P-REGION-001","state":"ACCEPTED_UNKNOWN","severity":"NON_BLOCKING","target":"regional","finding":"No complete regional evidence matrix."},
            {"lien_id":"L-67P-GEO-001","state":"ACCEPTED_UNKNOWN","severity":"NON_BLOCKING","target":"geology_geotechnical","finding":"Site-scale geotechnical values unknown."},
        ])
    output = {"campaign_id": campaign["campaign_id"], "fresh_context": True, "attacks": attacks, "attack_count": len(attacks), "all_attacks_rejected": all(a["passed"] for a in attacks.values()), "liens": liens, "status": "PASS" if all(a["passed"] for a in attacks.values()) and not any(l["severity"] == "BLOCKING" for l in liens) else "FAIL"}
    (ROOT / "hostile_review.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
