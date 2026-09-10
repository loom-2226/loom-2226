from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

from vehicle_dynamics_contract import VehicleDynamicsContract, validate_vehicle_dynamics_contract

BINDING_VERSION = "LOOM_SHIPYARD_CAMPAIGN_BINDING_v0.1"
BINDING_AUTHORITY = "ENGINEERING_STATE_COMPATIBILITY_GATE_ONLY"
EXPECTED_SHIP_CLASS = "WAYFARER"
EXPECTED_SHIP_TEMPLATE = "WAYFARER_BASELINE"


class ShipyardCampaignBindingError(ValueError):
    pass


def _sha(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _number(mapping: Mapping[str, Any], key: str) -> float:
    try:
        value = float(mapping[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ShipyardCampaignBindingError(f"campaign ship.{key} is required and numeric") from exc
    if not math.isfinite(value):
        raise ShipyardCampaignBindingError(f"campaign ship.{key} must be finite")
    return value


def validate_campaign_binding(
    contract: VehicleDynamicsContract,
    campaign_state: Mapping[str, Any],
    *,
    mass_tolerance_t: float = 1e-9,
) -> dict[str, Any]:
    """Prove a Shipyard contract matches the Navigator campaign ship state.

    This function is deliberately a compatibility gate, not a state mutation or
    authority transfer. Navigator remains owner of campaign state and planning.
    Shipyard supplies an immutable engineering contract; any material mismatch
    fails closed before a caller may use that contract to evaluate the campaign.
    """
    validate_vehicle_dynamics_contract(contract)
    if contract.flight_dynamics_authority:
        raise ShipyardCampaignBindingError("Shipyard contract may not claim flight authority")
    if not isinstance(campaign_state, Mapping):
        raise ShipyardCampaignBindingError("campaign_state must be a mapping")

    identity = campaign_state.get("ship_identity")
    ship = campaign_state.get("ship")
    if not isinstance(identity, Mapping):
        raise ShipyardCampaignBindingError("campaign ship_identity is required")
    if not isinstance(ship, Mapping):
        raise ShipyardCampaignBindingError("campaign ship block is required")

    ship_class = str(identity.get("ship_class") or "").upper()
    ship_template = str(identity.get("ship_template") or ship.get("baseline") or "").upper()
    if ship_class != EXPECTED_SHIP_CLASS:
        raise ShipyardCampaignBindingError(f"ship_class mismatch: {ship_class!r}")
    if ship_template != EXPECTED_SHIP_TEMPLATE:
        raise ShipyardCampaignBindingError(f"ship_template mismatch: {ship_template!r}")

    campaign_wet_t = _number(ship, "wet_mass_t")
    campaign_remass_t = _number(ship, "remass_t")
    campaign_capacity_t = _number(ship, "remass_capacity_t")
    if campaign_wet_t <= 0.0:
        raise ShipyardCampaignBindingError("campaign wet mass must be positive")
    if campaign_remass_t < 0.0:
        raise ShipyardCampaignBindingError("campaign remass may not be negative")
    if campaign_capacity_t <= 0.0 or campaign_remass_t > campaign_capacity_t + mass_tolerance_t:
        raise ShipyardCampaignBindingError("campaign remass state exceeds valid capacity")

    contract_wet_t = contract.wet_mass_kg / 1000.0
    contract_remass_t = contract.normal_remass_kg / 1000.0
    checks = {
        "ship_class_matches": True,
        "ship_template_matches": True,
        "wet_mass_matches_contract": math.isclose(campaign_wet_t, contract_wet_t, rel_tol=0.0, abs_tol=mass_tolerance_t),
        "remass_capacity_matches_contract": math.isclose(campaign_capacity_t, contract_remass_t, rel_tol=0.0, abs_tol=mass_tolerance_t),
        "current_remass_within_contract_capacity": campaign_remass_t <= contract_remass_t + mass_tolerance_t,
    }
    if not all(checks.values()):
        failed = [key for key, passed in checks.items() if not passed]
        raise ShipyardCampaignBindingError("campaign/Shipyard incompatibility: " + ",".join(failed))

    payload = {
        "version": BINDING_VERSION,
        "authority_status": BINDING_AUTHORITY,
        "ship_instance_id": identity.get("ship_instance_id"),
        "ship_class": ship_class,
        "ship_template": ship_template,
        "shipyard_candidate_id": contract.candidate_id,
        "shipyard_contract_hash": contract.contract_hash,
        "shipyard_design_state_hash": contract.design_state_hash,
        "campaign_wet_mass_t": campaign_wet_t,
        "campaign_remass_t": campaign_remass_t,
        "campaign_remass_capacity_t": campaign_capacity_t,
        "checks": checks,
        "compatible_for_navigator_consumption": True,
        "campaign_state_mutated": False,
        "navigator_authority_changed": False,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
    payload["binding_hash"] = _sha(payload)
    return payload
