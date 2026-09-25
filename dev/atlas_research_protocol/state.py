"""Resumption helpers for campaign state; no scientific inference is performed."""

from __future__ import annotations

from typing import Any


def remaining_work(campaign: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Return applicable lanes not yet covered and stable unresolved gaps."""
    lanes = campaign.get("lanes", {})
    applicable = profile.get("applicable_lanes", [])
    remaining_lanes = [lane for lane in applicable if lanes.get(lane, {}).get("coverage") not in {"COVERED", "NOT_APPLICABLE"}]
    return {
        "campaign_id": campaign.get("campaign_id"),
        "target_body": campaign.get("target_body"),
        "remaining_lanes": remaining_lanes,
        "unresolved_gaps": [gap.get("gap_id") for gap in campaign.get("unresolved_gaps", [])],
        "resumable": campaign.get("status") in {"RESUMABLE", "IN_PROGRESS", "PAUSED"},
    }
