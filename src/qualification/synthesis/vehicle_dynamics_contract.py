from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from generative_candidate_compiler import CompiledCandidateArtifact, compile_wayfarer_survivor_family

CONTRACT_VERSION = "LOOM_SHIPYARD_VEHICLE_DYNAMICS_CONTRACT_v0.2"
CONTRACT_AUTHORITY = "ENGINEERING_HANDOFF_RESEARCH_ONLY"
TORCH_CARD_AUTHORITY = "SOURCE_DERIVED_WORKING_ENGINEERING_CARD_ONLY"
READINESS_VERSION = "LOOM_SHIPYARD_DYNAMICS_READINESS_v0.1"
READINESS_AUTHORITY = "ENGINEERING_RESEARCH_GATE_ONLY"
READINESS_BLOCKED = "BLOCKED_BY_UNADMITTED_PHYSICAL_DEGREES_OF_FREEDOM"
OPEN = "OPEN_NOT_QUALIFIED"
G0_M_S2 = 9.80665

# Source: engineering/current/LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v1.0 §7.3.
# These are explicitly working engineering cards, not universal spacecraft constants
# and not flight-qualified by this Shipyard research slice.
_TORCH_CARDS = (
    ("ECON", 0.30, 3000.0),
    ("CRUISE", 1.00, 2000.0),
    ("EXPEDITE", 2.00, 1000.0),
    ("FAST", 3.00, 700.0),
    ("HARD", 5.00, 450.0),
    ("LIMIT", 7.50, 300.0),
)

# These gates describe what must become admitted before the current family can
# claim physically differentiated ordinary translational mission behaviour.
# They are deliberately separate from Phase-10/11 remass-feed probes, which are
# analytic research evidence only and explicitly admit zero live engineering inputs.
_REQUIRED_TRANSLATIONAL_ADMISSIONS = (
    "CANDIDATE_DEPENDENT_WET_OR_DRY_MASS_STATE",
    "CANDIDATE_DEPENDENT_NORMAL_REMASS_STATE_OR_CAPACITY",
    "CANDIDATE_DEPENDENT_ADMITTED_PROPULSION_PERFORMANCE_OR_DUTY_LIMIT",
)
_OPTIONAL_COUPLED_ADMISSIONS = (
    "QUALIFIED_INERTIA_AND_ATTITUDE_CONTROL_EFFECTS",
    "QUALIFIED_THERMAL_DURATION_CONSTRAINTS",
    "QUALIFIED_PLUME_OR_VECTORING_CONSTRAINTS",
)
_REMASS_FEED_EVIDENCE = {
    "phase10_status": "DECOMPOSITION_RESEARCH_ONLY_NOT_LIVE_ENGINEERING_INPUT",
    "phase11_authority": "ANALYTIC_FEED_BOUND_EVIDENCE_ONLY",
    "phase11_selection_status": "NO_FEED_ARCHITECTURE_SELECTED",
    "phase11_live_engineering_input_admission_count": 0,
    "phase11_propulsion_inlet_pressure_admitted": False,
    "phase11_pump_efficiency_admitted": False,
    "provenance": (
        "src/shipyard_phase10_remass_feed.py;"
        "src/shipyard_phase11_remass_feed_bounds.py"
    ),
}


class VehicleDynamicsContractError(ValueError):
    pass


@dataclass(frozen=True)
class TorchOperatingCard:
    mode: str
    acceleration_g: float
    exhaust_velocity_km_s: float
    thrust_n_at_contract_mass: float
    mass_flow_kg_s_at_contract_mass: float
    authority_status: str = TORCH_CARD_AUTHORITY
    provenance: str = "engineering/current/LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v1.0#7.3"


@dataclass(frozen=True)
class VehicleDynamicsContract:
    version: str
    candidate_id: str
    design_state_hash: str
    semantic_glb_sha256: str
    wet_mass_kg: float
    center_of_mass_m: tuple[float, float, float]
    normal_remass_kg: float
    protected_water_kg: float
    thrust_axis_body: tuple[float, float, float]
    torch_cards: tuple[TorchOperatingCard, ...]
    inertia_tensor_status: str
    attitude_control_status: str
    thermal_duration_status: str
    plume_geometry_status: str
    metric_transport_contract_status: str
    loom_transport_contract_status: str
    flight_dynamics_authority: bool
    authority_status: str
    contract_hash: str


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _positive(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise VehicleDynamicsContractError(f"{label} must be finite and positive")
    return value


def _torch_cards(wet_mass_kg: float) -> tuple[TorchOperatingCard, ...]:
    mass = _positive(wet_mass_kg, "wet_mass_kg")
    rows = []
    for mode, acceleration_g, exhaust_km_s in _TORCH_CARDS:
        acceleration = float(acceleration_g) * G0_M_S2
        thrust = mass * acceleration
        exhaust_m_s = float(exhaust_km_s) * 1000.0
        mdot = thrust / exhaust_m_s
        rows.append(TorchOperatingCard(mode, acceleration_g, exhaust_km_s, thrust, mdot))
    return tuple(rows)


def build_vehicle_dynamics_contract(
    artifact: CompiledCandidateArtifact,
    *,
    normal_remass_kg: float = 250_000.0,
    protected_water_kg: float = 50_000.0,
) -> VehicleDynamicsContract:
    if artifact.flight_dynamics_authority:
        raise VehicleDynamicsContractError("source artifact may not claim flight authority")
    mass = _positive(artifact.mass_kg, "artifact mass")
    remass = _positive(normal_remass_kg, "normal remass")
    protected = _positive(protected_water_kg, "protected water")
    if remass + protected > mass:
        raise VehicleDynamicsContractError("water/remass stores exceed vehicle mass")
    if len(artifact.center_of_mass_m) != 3 or any(not math.isfinite(float(v)) for v in artifact.center_of_mass_m):
        raise VehicleDynamicsContractError("center_of_mass_m must be a finite vec3")

    provisional = VehicleDynamicsContract(
        version=CONTRACT_VERSION,
        candidate_id=artifact.candidate_id,
        design_state_hash=artifact.governed_package_hash,
        semantic_glb_sha256=artifact.glb_sha256,
        wet_mass_kg=mass,
        center_of_mass_m=tuple(float(v) for v in artifact.center_of_mass_m),
        normal_remass_kg=remass,
        protected_water_kg=protected,
        thrust_axis_body=(1.0, 0.0, 0.0),
        torch_cards=_torch_cards(mass),
        inertia_tensor_status=OPEN,
        attitude_control_status=OPEN,
        thermal_duration_status=OPEN,
        plume_geometry_status=OPEN,
        metric_transport_contract_status=OPEN,
        loom_transport_contract_status=OPEN,
        flight_dynamics_authority=False,
        authority_status=CONTRACT_AUTHORITY,
        contract_hash="",
    )
    payload = asdict(provisional)
    payload["contract_hash"] = ""
    final = VehicleDynamicsContract(**{**asdict(provisional), "torch_cards": provisional.torch_cards, "contract_hash": _sha(payload)})
    validate_vehicle_dynamics_contract(final)
    return final


def validate_vehicle_dynamics_contract(contract: VehicleDynamicsContract) -> None:
    if contract.version != CONTRACT_VERSION or contract.authority_status != CONTRACT_AUTHORITY:
        raise VehicleDynamicsContractError("contract authority/version mismatch")
    if contract.flight_dynamics_authority:
        raise VehicleDynamicsContractError("v0.2 handoff cannot claim flight dynamics authority")
    _positive(contract.wet_mass_kg, "wet mass")
    _positive(contract.normal_remass_kg, "normal remass")
    if contract.thrust_axis_body != (1.0, 0.0, 0.0):
        raise VehicleDynamicsContractError("v0.2 Wayfarer thrust axis must remain explicit +X body")
    if tuple(card.mode for card in contract.torch_cards) != tuple(row[0] for row in _TORCH_CARDS):
        raise VehicleDynamicsContractError("torch card mode set/order mismatch")
    for card in contract.torch_cards:
        if card.authority_status != TORCH_CARD_AUTHORITY:
            raise VehicleDynamicsContractError("torch card authority escalation")
        expected_thrust = contract.wet_mass_kg * card.acceleration_g * G0_M_S2
        expected_mdot = expected_thrust / (card.exhaust_velocity_km_s * 1000.0)
        if not math.isclose(card.thrust_n_at_contract_mass, expected_thrust, rel_tol=0.0, abs_tol=1e-6):
            raise VehicleDynamicsContractError("torch thrust derivation mismatch")
        if not math.isclose(card.mass_flow_kg_s_at_contract_mass, expected_mdot, rel_tol=0.0, abs_tol=1e-12):
            raise VehicleDynamicsContractError("torch mass-flow derivation mismatch")
    for status in (
        contract.inertia_tensor_status,
        contract.attitude_control_status,
        contract.thermal_duration_status,
        contract.plume_geometry_status,
        contract.metric_transport_contract_status,
        contract.loom_transport_contract_status,
    ):
        if status != OPEN:
            raise VehicleDynamicsContractError("v0.2 open dynamics field was silently promoted")
    payload = asdict(contract)
    digest = payload.pop("contract_hash")
    payload["contract_hash"] = ""
    if digest != _sha(payload):
        raise VehicleDynamicsContractError("contract hash mismatch")


def translational_signature(contract: VehicleDynamicsContract) -> str:
    """Hash only inputs currently consumable by the ordinary translational burn model.

    COM is deliberately excluded: without qualified inertia/attitude/vectoring models,
    moving the same mass around the vehicle may change geometry but cannot yet be
    claimed to change translational mission performance.
    """
    validate_vehicle_dynamics_contract(contract)
    payload = {
        "wet_mass_kg": contract.wet_mass_kg,
        "normal_remass_kg": contract.normal_remass_kg,
        "thrust_axis_body": contract.thrust_axis_body,
        "torch_cards": [
            {
                "mode": row.mode,
                "acceleration_g": row.acceleration_g,
                "exhaust_velocity_km_s": row.exhaust_velocity_km_s,
                "thrust_n_at_contract_mass": row.thrust_n_at_contract_mass,
                "mass_flow_kg_s_at_contract_mass": row.mass_flow_kg_s_at_contract_mass,
            }
            for row in contract.torch_cards
        ],
    }
    return _sha(payload)


def build_wayfarer_contract_family(seed: int = 2226) -> tuple[VehicleDynamicsContract, ...]:
    return tuple(build_vehicle_dynamics_contract(row) for row in compile_wayfarer_survivor_family(seed))


def dynamics_readiness_report(contracts: tuple[VehicleDynamicsContract, ...]) -> dict[str, Any]:
    if not contracts:
        raise VehicleDynamicsContractError("readiness report requires at least one contract")
    for contract in contracts:
        validate_vehicle_dynamics_contract(contract)

    wet_masses = {row.wet_mass_kg for row in contracts}
    remass_states = {row.normal_remass_kg for row in contracts}
    propulsion_signatures = {
        tuple((card.mode, card.acceleration_g, card.exhaust_velocity_km_s) for card in row.torch_cards)
        for row in contracts
    }
    admission_state = {
        "candidate_dependent_wet_or_dry_mass_state": len(wet_masses) > 1,
        "candidate_dependent_normal_remass_state_or_capacity": len(remass_states) > 1,
        "candidate_dependent_admitted_propulsion_performance_or_duty_limit": len(propulsion_signatures) > 1,
        "qualified_inertia_and_attitude_control_effects": all(
            row.inertia_tensor_status != OPEN and row.attitude_control_status != OPEN for row in contracts
        ),
        "qualified_thermal_duration_constraints": all(row.thermal_duration_status != OPEN for row in contracts),
        "qualified_plume_or_vectoring_constraints": all(row.plume_geometry_status != OPEN for row in contracts),
    }
    translational_core_ready = any(
        admission_state[key]
        for key in (
            "candidate_dependent_wet_or_dry_mass_state",
            "candidate_dependent_normal_remass_state_or_capacity",
            "candidate_dependent_admitted_propulsion_performance_or_duty_limit",
        )
    )
    missing_required = [
        gate for gate, admitted in zip(
            _REQUIRED_TRANSLATIONAL_ADMISSIONS,
            (
                admission_state["candidate_dependent_wet_or_dry_mass_state"],
                admission_state["candidate_dependent_normal_remass_state_or_capacity"],
                admission_state["candidate_dependent_admitted_propulsion_performance_or_duty_limit"],
            ),
        ) if not admitted
    ]
    missing_optional = [
        gate for gate, admitted in zip(
            _OPTIONAL_COUPLED_ADMISSIONS,
            (
                admission_state["qualified_inertia_and_attitude_control_effects"],
                admission_state["qualified_thermal_duration_constraints"],
                admission_state["qualified_plume_or_vectoring_constraints"],
            ),
        ) if not admitted
    ]
    status = "READY_FOR_DIFFERENTIATED_TRANSLATIONAL_EVALUATION" if translational_core_ready else READINESS_BLOCKED
    report = {
        "version": READINESS_VERSION,
        "authority_status": READINESS_AUTHORITY,
        "status": status,
        "candidate_count": len(contracts),
        "translational_core_ready": translational_core_ready,
        "admission_state": admission_state,
        "missing_required_admissions": missing_required,
        "missing_coupled_admissions": missing_optional,
        "remass_feed_evidence": dict(_REMASS_FEED_EVIDENCE),
        "phase10_phase11_may_supply_live_dynamics_inputs": False,
        "next_admission_priority": (
            "ADMIT_ONE_CANDIDATE_DEPENDENT_PHYSICAL_DRIVER_FROM_GOVERNED_ENGINEERING_EVIDENCE"
            if not translational_core_ready else None
        ),
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }
    report["report_hash"] = _sha(report)
    return report


def family_differentiation_report(seed: int = 2226) -> dict[str, Any]:
    contracts = build_wayfarer_contract_family(seed)
    signatures = {row.candidate_id: translational_signature(row) for row in contracts}
    differentiated = len(set(signatures.values())) > 1
    readiness = dynamics_readiness_report(contracts)
    return {
        "version": CONTRACT_VERSION,
        "candidate_count": len(contracts),
        "distinct_design_state_count": len({row.design_state_hash for row in contracts}),
        "distinct_semantic_glb_count": len({row.semantic_glb_sha256 for row in contracts}),
        "distinct_translational_signature_count": len(set(signatures.values())),
        "translational_mission_behavior_differentiated": differentiated,
        "reason_if_not_differentiated": (
            None if differentiated else
            "CURRENT_BOUNDED_DOMAIN_MOVES_PACKAGING_WITH_FIXED_WET_MASS_REMASS_AND_TORCH_CARDS; QUALIFIED_INERTIA_ATTITUDE_EFFECTS_REMAIN_OPEN"
        ),
        "readiness": readiness,
        "signatures": signatures,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }


if __name__ == "__main__":
    print(json.dumps(family_differentiation_report(), indent=2, sort_keys=True, allow_nan=False))
