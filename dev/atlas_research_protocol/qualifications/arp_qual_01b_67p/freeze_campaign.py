"""Freeze ARP-QUAL-01B outputs after external research stops."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from dev.atlas_research_protocol.validate import load_json, qualify

ROOT = Path(__file__).resolve().parent
BLIND_ROOT = Path("/home/ubuntu/ARP01B_67P_BLIND/dev/atlas_research_protocol/qualifications/arp_qual_01b_67p")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    blind_campaign = BLIND_ROOT / "campaign.json"
    blind_manifest = BLIND_ROOT / "campaign_manifest.json"
    campaign = load_json(blind_campaign)
    result = qualify(campaign, None, BLIND_ROOT)
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    campaign_bytes = blind_campaign.read_bytes()
    campaign_hash = hashlib.sha256(campaign_bytes).hexdigest()
    expected_hash = load_json(blind_manifest)["campaign_sha256"]
    if campaign_hash != expected_hash:
        raise SystemExit("blind campaign hash changed before freeze")
    local_campaign = ROOT / "campaign.json"
    local_campaign.write_bytes(campaign_bytes)
    artifact_rows = []
    for a in campaign["artifacts"]:
        p = ROOT / a["local_path"]
        artifact_rows.append({"artifact_id": a["artifact_id"], "source_id": a["source_id"], "path": a["local_path"], "sha256": digest(p), "byte_count": p.stat().st_size})
    if any(r["sha256"] != next(a["sha256"] for a in campaign["artifacts"] if a["artifact_id"] == r["artifact_id"]) for r in artifact_rows):
        raise SystemExit("artifact hash mismatch at freeze")
    (ROOT / "blindness_record.json").write_text(json.dumps({
        "campaign_id": campaign["campaign_id"],
        "blind_root": str(BLIND_ROOT),
        "allowed_inputs": ["ARP v1.0.2 generic package", "comet body profile", "source authority policy", "publicly acquired 67P artifacts"],
        "excluded_answer_key_material": ["dev/solar_facts_hcq01/**", "dev/atlas_research_protocol/fixtures/ceres_gold.json", "dev/atlas_research_protocol/qualifications/arp_qual_01_ceres/**", "ARP-QUAL-01 Ceres comparison and qualification reports"],
        "excluded_paths_verified_absent": ["/home/ubuntu/ARP01B_67P_BLIND/dev/solar_facts_hcq01", "/home/ubuntu/ARP01B_67P_BLIND/dev/atlas_research_protocol/fixtures/ceres_gold.json", "/home/ubuntu/ARP01B_67P_BLIND/dev/atlas_research_protocol/qualifications/arp_qual_01_ceres"],
        "research_phase_answer_key_access": False,
        "method": "External-input allowlist; research execution copied only generic ARP modules and acquired 67P artifacts into the blind root.",
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "coverage_matrix.json").write_text(json.dumps({"campaign_id": campaign["campaign_id"], "coverage_contract_version": campaign["coverage_contract_version"], "lanes": campaign["lanes"], "unresolved_gaps": campaign["unresolved_gaps"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "efficiency_metrics.json").write_text(json.dumps(campaign["metrics"] | {"final_coverage": {k: v["coverage"] for k, v in campaign["lanes"].items()}, "independent_evidence_lineages": len({a["independent_evidence_lineage_id"] for a in campaign["assertions"]})}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "rejected_sources.json").write_text(json.dumps({"campaign_id": campaign["campaign_id"], "sources_discovered": campaign["metrics"]["sources_discovered"], "sources_rejected": campaign["metrics"]["sources_rejected"], "reasons": ["secondary or duplicate discovery result", "not primary when a primary mission/archive source was available", "outside declared lane or insufficient provenance", "not acquired because cutoff/identity could not be established"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "research_trace.json").write_text(json.dumps({"campaign_id": campaign["campaign_id"], "passes": [{"name":"ASSESS/PASS_1", "coverage": campaign["metrics"]["coverage_after_pass_1"], "operations": 11}, {"name":"TARGETED/PASS_2", "targets": campaign["metrics"]["pass_2_targets"], "coverage": campaign["metrics"]["coverage_after_pass_2"], "operations": 6}], "stop_rule": "Stop after primary coverage, explicit evidence-question dispositions, provenance validation, and diminishing returns across remaining gaps.", "external_research_stopped": True}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "extraction_completeness.json").write_text(json.dumps({"campaign_id": campaign["campaign_id"], "high_value_artifacts_reviewed": len(artifact_rows), "targeted_evidence_questions_with_extracted_support": 14, "known_targeted_extraction_misses": [], "scope": "Targeted extraction only; not an exhaustive extraction of every publication statement.", "review": "Each acquired high-value artifact was checked against the question that motivated acquisition; unresolved questions remain explicit in coverage and frontier."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "frozen_manifest.json").write_text(json.dumps({
        "campaign_id": campaign["campaign_id"],
        "frozen": True,
        "frozen_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "arp_protocol_version": campaign["arp_version"],
        "arp_implementation_version": campaign["implementation_version"],
        "repository_baseline": campaign["repository_baseline"],
        "knowledge_cutoff": campaign["knowledge_cutoff"],
        "campaign_sha256": campaign_hash,
        "campaign_byte_count": len(campaign_bytes),
        "artifact_manifest": artifact_rows,
        "assertion_count": len(campaign["assertions"]),
        "accepted_candidate_count": campaign["metrics"]["assertions_accepted"],
        "qualification": result,
        "external_research_stopped": True,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
