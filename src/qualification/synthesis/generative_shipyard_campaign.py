from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generative_candidate_compiler import compile_wayfarer_survivor_family
from generative_shipyard_foundation import run_wayfarer_config_experiment
from shipyard_candidate_archive import archive_wayfarer_campaign, campaign_summary
from vehicle_dynamics_contract import family_differentiation_report
from shipyard_visual_library import add_glb_asset

CAMPAIGN_EXECUTOR_VERSION = "LOOM_GENERATIVE_SHIPYARD_CAMPAIGN_EXECUTOR_v0.2"
CAMPAIGN_EXECUTOR_AUTHORITY = "ENGINEERING_RESEARCH_CAMPAIGN_EXECUTION_ONLY"


class GenerativeCampaignError(ValueError):
    pass


def run_and_persist_wayfarer_campaign(db_path: str | Path, seed: int = 2226) -> dict[str, Any]:
    path = Path(db_path).expanduser().resolve()
    experiment = run_wayfarer_config_experiment(seed)
    campaign_id = archive_wayfarer_campaign(path, seed)
    compiled = compile_wayfarer_survivor_family(seed)

    visual_assets = []
    for row in compiled:
        asset = add_glb_asset(
            path,
            row.glb_bytes,
            display_name=f"Wayfarer — {row.candidate_id}",
            ship_name="Wayfarer",
            artifact_class="GOVERNED_SEMANTIC",
            source_candidate_id=row.candidate_id,
            source_candidate_hash=row.governed_package_hash,
            metadata={
                "campaign_id": campaign_id,
                "parent_candidate_id": row.parent_candidate_id,
                "generation": row.generation,
                "choices": row.choices,
                "semantic_package_hash": row.semantic_package_hash,
                "candidate_compiler_authority": row.authority_status,
            },
        )
        visual_assets.append({
            "candidate_id": row.candidate_id,
            "asset_id": asset.asset_id,
            "glb_sha256": asset.sha256,
            "authority_status": asset.authority_status,
        })

    summary = campaign_summary(path, campaign_id)
    dynamics = family_differentiation_report(seed)
    readiness = dynamics["readiness"]
    surviving = [x for x in experiment.outcomes if x.status == "SURVIVED_SCREEN"]
    rejected = [x for x in experiment.outcomes if x.status.startswith("REJECTED_")]
    report = {
        "version": CAMPAIGN_EXECUTOR_VERSION,
        "authority_status": CAMPAIGN_EXECUTOR_AUTHORITY,
        "campaign_id": campaign_id,
        "experiment_hash": experiment.experiment_hash,
        "candidate_count": len(experiment.outcomes),
        "survivor_count": len(surviving),
        "rejected_count": len(rejected),
        "pareto_count": len(experiment.pareto_frontier),
        "visual_asset_count": len(visual_assets),
        "visual_assets": visual_assets,
        "dynamics_differentiation": dynamics,
        "dynamics_readiness": readiness,
        "archive_summary_hash": summary["summary_hash"],
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
        "interpretation": (
            "FIRST_BOUNDED_ITERATIVE_SHIPBUILDING_CAMPAIGN_CLOSED"
            if len(surviving) >= 2 and len(rejected) >= 2 and len(visual_assets) == len(surviving)
            else "CAMPAIGN_INCOMPLETE"
        ),
        "next_blocker": (
            readiness["status"] if not dynamics["translational_mission_behavior_differentiated"] else None
        ),
        "next_admission_priority": readiness["next_admission_priority"],
    }
    return report


def canonical_report(report: dict[str, Any]) -> str:
    if report.get("authority_status") != CAMPAIGN_EXECUTOR_AUTHORITY:
        raise GenerativeCampaignError("campaign authority mismatch")
    if report.get("flight_dynamics_authority") or report.get("canon_changed") or report.get("production_shipclasses_changed"):
        raise GenerativeCampaignError("campaign report authority escalation")
    readiness = report.get("dynamics_readiness", {})
    if readiness.get("phase10_phase11_may_supply_live_dynamics_inputs") is not False:
        raise GenerativeCampaignError("campaign attempted to promote Phase-10/11 probe evidence")
    return json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
