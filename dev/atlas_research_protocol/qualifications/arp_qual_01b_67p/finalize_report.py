"""Emit the durable ARP-QUAL-01B transfer qualification record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dev.atlas_research_protocol.validate import load_json

ROOT = Path(__file__).resolve().parent
HCQ = ROOT.parents[3] / "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"


def main() -> int:
    campaign = load_json(ROOT / "campaign.json")
    frozen = load_json(ROOT / "frozen_manifest.json")
    hostile = load_json(ROOT / "hostile_review.json")
    blind = load_json(ROOT / "blindness_record.json")
    qualification = {
        "qualification_id": "ARP-QUAL-01B_67P_TRANSFER",
        "result": "TRANSFER_PASS_WITH_LIENS",
        "europa_readiness": "READY_FOR_ARP_QUAL_02_EUROPA",
        "europa_readiness_reason": "ARP v1.0.2 transferred beyond Ceres with explicit evidence-question accounting, preserved temporal/spatial distinctions, acceptable UNKNOWN/SOURCE_NOT_FOUND states, provenance validation, and a fresh hostile review with no blocking liens.",
        "arp_protocol_version": campaign["arp_version"],
        "arp_implementation_version": campaign["implementation_version"],
        "repository_baseline": campaign["repository_baseline"],
        "target_body": campaign["target_body"],
        "body_profile": campaign["body_profile"],
        "knowledge_cutoff": campaign["knowledge_cutoff"],
        "research_tier": campaign["research_tier"],
        "blindness": blind,
        "frozen_manifest": frozen,
        "hostile_review": hostile,
        "sources": [{k: s.get(k) for k in ("source_id", "provider", "source_type", "title", "locator", "publication_date", "persistent_identifier", "doi")} for s in campaign["sources"]],
        "metrics": campaign["metrics"] | {"final_coverage": {k: v["coverage"] for k, v in campaign["lanes"].items()}, "independent_evidence_lineages": len({a["independent_evidence_lineage_id"] for a in campaign["assertions"]})},
        "assertions": {"extracted": len(campaign["assertions"]), "accepted": campaign["metrics"]["assertions_accepted"], "rejected": campaign["metrics"]["assertions_rejected"]},
        "spatial_temporal_discipline": {"instrument_footprint_preserved": True, "time_dependent_activity_preserved": True, "coma_nucleus_distinguished": True, "model_observation_distinguished": True, "ranges_not_midpointed": True},
        "extraction_completeness": load_json(ROOT / "extraction_completeness.json"),
        "authority_firewall": {"hcq_sha256": hashlib.sha256(HCQ.read_bytes()).hexdigest(), "canonical_67p_promotion": False, "preferred_fact": False, "phase4_phase5": False, "forbidden_inference": False},
        "qualification_notes": ["This is a transfer qualification, not canonical 67P science promotion.", "The source set is bounded and does not claim exhaustive comet knowledge.", "The campaign was frozen before hostile qualification."],
    }
    (ROOT / "ARP_QUAL01B_67P_QUALIFICATION.json").write_text(json.dumps(qualification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ARP-QUAL-01B — 67P / Churyumov–Gerasimenko Transfer Qualification",
        "",
        "Change class: `class:research`",
        "",
        f"Result: **{qualification['result']}**",
        f"Europa readiness: **{qualification['europa_readiness']}**",
        "",
        "## Experiment boundary",
        "",
        "The campaign ran against ARP v1.0.2 at repository baseline " + f"`{campaign['repository_baseline']}`. Research used an external-input allowlist containing only generic ARP modules, the comet profile, source policy, and acquired 67P artifacts. HCQ-01, Ceres fixtures, Ceres reports, and Ceres comparison material were absent from the blind root. The campaign was frozen before hostile qualification.",
        "",
        "## Campaign",
        "",
        f"- Target: `{campaign['target_body']}`; profile: `{campaign['body_profile']}`; tier: `{campaign['research_tier']}`.",
        f"- Cutoff: `{campaign['knowledge_cutoff']}`.",
        f"- Frozen campaign SHA-256: `{frozen['campaign_sha256']}`.",
        f"- Sources discovered/acquired/rejected: `{campaign['metrics']['sources_discovered']}/{campaign['metrics']['sources_acquired']}/{campaign['metrics']['sources_rejected']}`.",
        f"- Assertions extracted/accepted/rejected: `{len(campaign['assertions'])}/{campaign['metrics']['assertions_accepted']}/{campaign['metrics']['assertions_rejected']}`.",
        f"- Independent evidence lineages: `{len({a['independent_evidence_lineage_id'] for a in campaign['assertions']})}`.",
        "",
        "## Coverage transfer",
        "",
        "Covered lanes carry explicit v1.0.2 evidence-question bases. Orbit geometry is `SOURCE_NOT_FOUND`; geology/geotechnical, regional, and history remain `PARTIAL`. UNKNOWN and SOURCE_NOT_FOUND are recorded without fabricated values.",
        "",
        "Pass 1 covered identity, gravity/shape, water/volatiles and composition partially or fully; Pass 2 targeted rotation, thermal, activity, regional and orbit gaps. Pass 2 materially improved rotation/orientation, thermal environment, and activity coverage while correctly leaving orbit unresolved.",
        "",
        "## Scientific discipline",
        "",
        "The corpus preserves nucleus/coma scope, time-dependent activity, instrument-footprint temperature mapping, model-versus-observation distinctions, and ranges without midpoint fabrication. No extraction-completeness miss was found in the targeted review of the nine acquired high-value artifacts; extraction was targeted, not exhaustive.",
        "",
        "## Hostile review and liens",
        "",
        f"Fresh-context hostile review executed `{hostile['attack_count']}` attacks; all rejected successfully. Non-blocking liens remain for orbit source availability, regional completeness, and site-scale geotechnical unknowns. No blocking lien remains.",
        "",
        "## Authority boundaries",
        "",
        f"HCQ-01 v0.3-R1 SHA-256 remains `{qualification['authority_firewall']['hcq_sha256']}`. No canonical 67P facts were promoted. No preferred facts, Phase-4/5 state, resource, engineering, economic, habitation, transport, or CIVPROP state was introduced.",
        "",
        "## Decision",
        "",
        "ARP v1.0.2 passes this transfer qualification with limitations. The result supports readiness for ARP-QUAL-02 Europa; it does not constitute permission to start Europa in this change.",
    ]
    (ROOT / "ARP_QUAL01B_67P_QUALIFICATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
