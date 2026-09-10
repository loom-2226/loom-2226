from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any, Mapping, Sequence

from vehicle_dynamics_contract import OPEN, VehicleDynamicsContract, validate_vehicle_dynamics_contract
from loom.navigation.engineering_feasibility_shadow import evaluate_engineering_feasibility_shadow

HANDOFF_VERSION = "LOOM_SHIPYARD_NAVIGATOR_HANDOFF_v0.1"
HANDOFF_AUTHORITY = "ENGINEERING_CONSUMER_QUALIFICATION_ONLY"


class ShipyardNavigatorHandoffError(ValueError):
    pass


def _vec3_unit(value: Sequence[float]) -> tuple[float, float, float]:
    try:
        row = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise ShipyardNavigatorHandoffError("dv_hat must be numeric vec3") from exc
    if len(row) != 3 or not all(math.isfinite(v) for v in row):
        raise ShipyardNavigatorHandoffError("dv_hat must be finite vec3")
    norm = math.sqrt(sum(v * v for v in row))
    if norm <= 0.0:
        raise ShipyardNavigatorHandoffError("dv_hat must be non-zero")
    return tuple(v / norm for v in row)


def _card(contract: VehicleDynamicsContract, mode: str):
    wanted = str(mode).upper()
    for row in contract.torch_cards:
        if row.mode == wanted:
            return row
    raise ShipyardNavigatorHandoffError(f"unknown torch mode {mode!r}")


def build_navigator_engineering_payload(
    contract: VehicleDynamicsContract,
    *,
    mode: str,
    dv_hat: Sequence[float] = (1.0, 0.0, 0.0),
) -> dict[str, Any]:
    """Adapt a Shipyard vehicle contract to Navigator D2i's existing engineering input.

    Consumer-boundary qualification only: no route choice, guidance choice, thermal
    margin, vectoring certification, canon change, or flight-authority promotion.
    """
    validate_vehicle_dynamics_contract(contract)
    if contract.flight_dynamics_authority:
        raise ShipyardNavigatorHandoffError("flight-authority source is not permitted in v0.1")
    card = _card(contract, mode)
    axis = _vec3_unit(dv_hat)
    burn = {
        "torch_mode": card.mode,
        "thrust_N": card.thrust_n_at_contract_mass,
        "thrust_MN": card.thrust_n_at_contract_mass / 1e6,
        "ve_km_s": card.exhaust_velocity_km_s,
        "mdot_kg_s": card.mass_flow_kg_s_at_contract_mass,
        "dv_hat": axis,
        "thermal_numeric_margin": None,
        "shipyard_contract_hash": contract.contract_hash,
        "shipyard_design_state_hash": contract.design_state_hash,
        "shipyard_authority_status": contract.authority_status,
    }
    return {
        "contract": HANDOFF_VERSION,
        "authority": HANDOFF_AUTHORITY,
        "torch": card.mode,
        "thermal": OPEN,
        "leg": {"terminal_burn": burn},
        "flight_dynamics_authority": False,
        "route_authority": False,
        "guidance_authority": False,
        "thermal_qualification": False,
        "vectoring_qualification": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }


def evaluate_shipyard_contract_with_navigator_shadow(
    contract: VehicleDynamicsContract,
    *,
    mode: str,
    trajectory: Mapping[str, Any],
    guidance_shadow: Mapping[str, Any],
    dv_hat: Sequence[float] = (1.0, 0.0, 0.0),
) -> dict[str, Any]:
    """Exercise Navigator's existing D2i engineering consumer using Shipyard state.

    Success proves schema/physics consumption at the diagnostic D2i boundary only.
    It does not qualify a route and does not by itself close full Shipyard M1.
    """
    payload = build_navigator_engineering_payload(contract, mode=mode, dv_hat=dv_hat)
    before = asdict(contract)
    report = evaluate_engineering_feasibility_shadow(trajectory, payload, guidance_shadow)
    if before != asdict(contract):
        raise ShipyardNavigatorHandoffError("Navigator consumer mutated Shipyard contract")
    if report.get("authority") != "DIAGNOSTIC_ENGINEERING_SHADOW_ONLY_NOT_ROUTE_AUTHORITY":
        raise ShipyardNavigatorHandoffError("Navigator D2i authority boundary changed")
    return {
        "version": HANDOFF_VERSION,
        "authority_status": HANDOFF_AUTHORITY,
        "shipyard_contract_hash": contract.contract_hash,
        "torch_mode": str(mode).upper(),
        "navigator_consumer": "LOOM_NAV_PHYSICS_V2_D2I_ENGINEERING_FEASIBILITY_SHADOW_V1",
        "navigator_report": report,
        "consumer_boundary_exercised": True,
        "full_m1_closed": False,
        "m2_candidate_differentiation_closed": False,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
