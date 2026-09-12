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


def _vector3(value: object) -> bool:
    return isinstance(value, (list, tuple)) and len(value) == 3 and all(
        isinstance(component, (int, float)) for component in value
    )


def live_qualification_selection_payload(snapshot: dict) -> dict[str, str]:
    """Derive presentation family only from an earned live relative-state product."""
    moon = snapshot.get("moon") or {}
    wayfarer = snapshot.get("wayfarer") or {}
    tactical_quality = (
        _vector3(moon.get("relative_to_wayfarer_km"))
        and _vector3(moon.get("velocity_earth_centered_km_s"))
        and _vector3(wayfarer.get("velocity_earth_centered_km_s"))
    )
    return selection_payload(
        select_hud_family(HudFamilyContext(tactical_quality_state=tactical_quality))
    )


def rendezvous_selection_payload(result: dict) -> dict[str, str] | None:
    """Expose NAV / FLIGHT PLAN only after the solver earns translational feasibility."""
    quality = result.get("quality") or {}
    if quality.get("status") != "SOLVED_TRANSLATIONAL_FEASIBILITY":
        return None
    return selection_payload(select_hud_family(HudFamilyContext(strategic_planning=True)))
