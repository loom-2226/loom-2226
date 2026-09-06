"""Live CORE-backed D2h gravity-aware guidance shadow for Navigator previews.

This layer reuses the qualified D2e/D2g live gravity field and body-radius cutoff,
then runs the D2h bounded terminal retargeting shadow over exactly the same
physically valid ordinary-space reference interval. It is diagnostic only.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from loom.spatial.gravity import GravityEvaluation
from .gravity_guidance_shadow import compare_gravity_guidance_shadow
from .gravity_shadow import GravityShadowError, ordinary_samples_from_route_trajectory
from .live_gravity_compare import LiveGravityCompareError, SQLiteDynamicGravityField


LIVE_GRAVITY_GUIDANCE_COMPARE_CONTRACT = "LOOM_NAV_PHYSICS_V2_D2H_LIVE_GRAVITY_GUIDANCE_COMPARE_V1"


def compare_live_route_guidance(
    trajectory: Mapping[str,Any],
    db_path: Path | str,
    *,
    max_step_s: float = 10.0,
    minimum_acceleration_km_s2: float = 1e-12,
    guidance_accel_limit_km_s2: float = 0.02,
) -> dict[str,Any]:
    samples = ordinary_samples_from_route_trajectory(trajectory)
    field = SQLiteDynamicGravityField(db_path,samples[0].epoch_utc)
    qualified,cutoff = field.physically_valid_reference(samples)

    def gravity(position: tuple[float,float,float], epoch: str) -> GravityEvaluation:
        return field.evaluator(position,epoch,minimum_acceleration_km_s2=minimum_acceleration_km_s2)

    try:
        report = compare_gravity_guidance_shadow(
            qualified,
            gravity,
            max_step_s=max_step_s,
            guidance_accel_limit_km_s2=guidance_accel_limit_km_s2,
        )
    except (GravityShadowError,LiveGravityCompareError) as exc:
        raise LiveGravityCompareError(str(exc)) from exc

    return {
        "contract":LIVE_GRAVITY_GUIDANCE_COMPARE_CONTRACT,
        "authority":"DIAGNOSTIC_GUIDANCE_SHADOW_ONLY_NOT_ROUTE_AUTHORITY",
        "trajectory_authority":trajectory.get("authority"),
        "route_plan_id":trajectory.get("route_plan_id"),
        "solution_key":trajectory.get("solution_key"),
        "coordinate_frame":trajectory.get("coordinate_frame"),
        "reference_cutoff":cutoff,
        "field":field.diagnostics(),
        "report":asdict(report),
        "qualification":{
            "campaign_mutation":False,
            "route_mutation":False,
            "remass_reoptimization":False,
            "metric_relational_segment_integrated":False,
            "reference_interval":"SAME_BODY_RADIUS_QUALIFIED_ORDINARY_INTERVAL_AS_D2E_D2G",
            "guidance_scope":"TERMINAL_STATE_RETARGETING_SHADOW_ONLY",
        },
    }
