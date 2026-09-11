from __future__ import annotations

"""Canonical presentation-only HUD family selection.

The selector chooses a presentation family from already-earned operational state.
It does not solve trajectories, classify contacts, mutate campaign state, or grant
sensor/navigation authority. Manual override changes presentation only.
"""

from dataclasses import dataclass
from enum import Enum


CONTRACT = "LOOM_HUD_FAMILY_SELECTOR_V1"
AUTHORITY = "PRESENTATION_ONLY_CANON_RULE_APPLICATION"


class HudFamily(str, Enum):
    TACTICAL = "TACTICAL"
    NAV_FLIGHT_PLAN = "NAV / FLIGHT PLAN"
    NAV_METRIC = "NAV / METRIC"
    SENSOR_WIDE = "SENSOR / WIDE"
    TACTICAL_TRACK = "TACTICAL / TRACK"


@dataclass(frozen=True)
class HudFamilyContext:
    strategic_planning: bool = False
    metric_phase: bool = False
    local_reacquisition_complete: bool = True
    tactical_quality_state: bool = False
    near_infrastructure: bool = False
    maneuver_hazard: bool = False
    established_contacts: bool = False


@dataclass(frozen=True)
class HudFamilySelection:
    contract: str
    family: HudFamily
    automatic_family: HudFamily
    selection_mode: str
    reason: str
    authority: str = AUTHORITY


def _automatic(context: HudFamilyContext) -> tuple[HudFamily, str]:
    # Phase-specific modes outrank generic local-context cues. This prevents a
    # nearby known object from forcing TACTICAL while the ship is explicitly in
    # metric operation or incomplete post-transport reacquisition.
    if context.metric_phase:
        return HudFamily.NAV_METRIC, "METRIC_ACQUISITION_CRUISE_OR_COLLAPSE"
    if not context.local_reacquisition_complete:
        return HudFamily.SENSOR_WIDE, "LOCAL_REACQUISITION_INCOMPLETE"
    if context.strategic_planning:
        return HudFamily.NAV_FLIGHT_PLAN, "STRATEGIC_PLANNING"
    if context.tactical_quality_state:
        return HudFamily.TACTICAL_TRACK, "LOCAL_GEOMETRY_TACTICAL_QUALITY"
    if context.near_infrastructure or context.maneuver_hazard or context.established_contacts:
        return HudFamily.TACTICAL, "LOCAL_INFRASTRUCTURE_HAZARD_OR_ESTABLISHED_CONTACT"
    # Fail to the least assumptive local spatial presentation. This is not a
    # claim that a tactical-quality track exists.
    return HudFamily.TACTICAL, "DEFAULT_LOCAL_PRESENTATION_NO_HIGHER_PHASE_CLAIM"


def select_hud_family(
    context: HudFamilyContext,
    *,
    manual_override: HudFamily | str | None = None,
) -> HudFamilySelection:
    automatic, reason = _automatic(context)
    if manual_override is None:
        return HudFamilySelection(
            contract=CONTRACT,
            family=automatic,
            automatic_family=automatic,
            selection_mode="AUTO",
            reason=reason,
        )
    try:
        override = manual_override if isinstance(manual_override, HudFamily) else HudFamily(str(manual_override))
    except ValueError as exc:
        raise ValueError(f"unknown HUD family override: {manual_override}") from exc
    return HudFamilySelection(
        contract=CONTRACT,
        family=override,
        automatic_family=automatic,
        selection_mode="MANUAL_OVERRIDE_PRESENTATION_ONLY",
        reason=f"MANUAL_OVERRIDE_FROM_{automatic.value}",
    )


def selection_payload(selection: HudFamilySelection) -> dict[str, str]:
    return {
        "contract": selection.contract,
        "family": selection.family.value,
        "automatic_family": selection.automatic_family.value,
        "selection_mode": selection.selection_mode,
        "reason": selection.reason,
        "authority": selection.authority,
    }
