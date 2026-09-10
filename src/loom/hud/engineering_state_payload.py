from __future__ import annotations

"""JSON payload adapter for typed Wayfarer HUD engineering state.

The payload preserves StateDatum provenance/authority/availability/quality so
browser presentation does not consume raw PR #96 engineering dictionaries.
"""

from enum import Enum
from typing import Any

from loom.hud.contracts import StateDatum
from loom.hud.engineering_state_contract import build_wayfarer_engineering_hud_state

CONTRACT = "LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1"


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(v) for v in value]
    if isinstance(value, list):
        return [_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    return value


def datum_payload(datum: StateDatum) -> dict[str, Any]:
    return {
        "value": _json_value(datum.value),
        "unit": datum.unit,
        "epoch": datum.epoch,
        "frame": datum.frame,
        "source": datum.source,
        "authority": datum.authority.value,
        "derivation": datum.derivation,
        "freshness_seconds": datum.freshness_seconds,
        "availability": datum.availability.value,
        "quality": datum.quality,
    }


def build_wayfarer_engineering_payload(*, epoch: str) -> dict[str, Any]:
    state = build_wayfarer_engineering_hud_state(epoch=epoch)
    return {
        "contract": CONTRACT,
        "typed_state_contract": state.contract,
        "epoch": state.epoch,
        "source_commit": state.source_commit,
        "authority": "QUALIFICATION_ONLY_NON_CANON_HUD_CONSUMER",
        "mass": {
            "reference_wet_mass": datum_payload(state.reference_wet_mass),
            "dry_mass": datum_payload(state.dry_mass),
            "normal_remass": datum_payload(state.normal_remass),
            "protected_water_reserve": datum_payload(state.protected_water_reserve),
        },
        "dispatch": {
            "normal_dispatch_remass": datum_payload(state.normal_dispatch_remass),
            "operational_remass_floor": datum_payload(state.operational_remass_floor),
            "protected_optimizer_reserve": datum_payload(state.protected_optimizer_reserve),
            "routine_optimizer_may_consume_protected_water": datum_payload(
                state.routine_optimizer_may_consume_protected_water
            ),
            "status": datum_payload(state.dispatch_status),
        },
        "attitude": {
            "status": datum_payload(state.attitude_status),
        },
        "power_thermal": {
            "status": datum_payload(state.power_thermal_status),
            "radiator_effective_area_range": datum_payload(state.radiator_effective_area_range),
            "thermal_buffer_range": datum_payload(state.thermal_buffer_range),
            "torch_coupled_heat_ceiling": datum_payload(state.torch_coupled_heat_ceiling),
        },
        "feedstock": {
            "primary": datum_payload(state.feedstock_primary),
            "certified_species": datum_payload(state.feedstock_certified_species),
        },
        "firewalls": {
            "torch_jet_power_is_electrical_bus_power": datum_payload(
                state.torch_jet_power_is_electrical_bus_power
            ),
            "metric_velocity_reset_allowed": datum_payload(state.metric_velocity_reset_allowed),
        },
        "torch_modes": {
            mode: {
                "acceleration_g": datum_payload(card.acceleration_g),
                "exhaust_velocity": datum_payload(card.exhaust_velocity),
                "status": datum_payload(card.status),
                "authorization": datum_payload(card.authorization),
            }
            for mode, card in state.torch_modes.items()
        },
    }


def attach_typed_engineering_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Replace any raw engineering presentation object with typed HUD state."""

    result = dict(snapshot)
    epoch = str(result.get("sim_epoch_utc") or "QUALIFICATION_STATIC")
    result["engineering"] = build_wayfarer_engineering_payload(epoch=epoch)
    return result
