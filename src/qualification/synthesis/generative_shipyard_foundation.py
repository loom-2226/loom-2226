from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from wayfarer_s1_adapter import WayfarerS1Error, build_candidate, evaluate_candidate

FOUNDATION_VERSION = "LOOM_GENERATIVE_SHIPYARD_FOUNDATION_v0.2"
FOUNDATION_AUTHORITY = "ENGINEERING_RESEARCH_ORCHESTRATION_ONLY"
EXPERIMENT_VERSION = "LOOM_WAYFARER_GENERATIVE_CONFIG_EXPERIMENT_v0.1"
EXPERIMENT_AUTHORITY = "QUALIFICATION_CANDIDATE_NON_CANON_NON_PRODUCTION"
SOLVER_VERSION = "LOOM_WAYFARER_GENERATIVE_CONFIG_EXPERIMENT_v0.1"

UNCERTAINTY_CLASSES = frozenset({
    "FIXED_KNOWN",
    "DESIGN_VARIABLE",
    "ALEATORY",
    "EPISTEMIC",
    "MODEL_FORM",
    "MANUFACTURING_TOLERANCE",
    "OPERATIONAL_VARIABILITY",
    "OPEN_NOT_ADMITTED",
})

CHOICE_STATUSES = frozenset({"FIXED_CANON", "BOUNDED_DESIGN_CHOICE", "DERIVED", "OPEN_NOT_ADMITTED"})


class GenerativeShipyardError(ValueError):
    pass


@dataclass(frozen=True)
class ArchitectureChoiceSpec:
    choice_id: str
    status: str
    allowed_values: tuple[Any, ...]
    units: str | None
    provenance: str


@dataclass(frozen=True)
class ArchitectureDomain:
    domain_id: str
    version: str
    choices: tuple[ArchitectureChoiceSpec, ...]
    authority_status: str = FOUNDATION_AUTHORITY


@dataclass(frozen=True)
class ModelAdequacyContract:
    model_id: str
    fidelity: str
    validity_domain: str
    known_omissions: tuple[str, ...]
    calibration_basis: str
    adequate_for_screening: bool
    adequate_for_rejection: bool
    adequate_for_selection: bool
    admissible_rejection_reasons: tuple[str, ...]
    authority_status: str = FOUNDATION_AUTHORITY


@dataclass(frozen=True)
class UncertaintyItem:
    item_id: str
    uncertainty_class: str
    description: str
    provenance: str


@dataclass(frozen=True)
class CandidateLineage:
    candidate_id: str
    parent_candidate_id: str | None
    generation: int
    mutation_id: str
    choices: Mapping[str, Any]


@dataclass(frozen=True)
class CandidateOutcome:
    candidate_id: str
    lineage: CandidateLineage
    status: str
    rejection_reason: str | None
    failed_constraint_ids: tuple[str, ...]
    mass_kg: float | None
    center_of_mass_m: tuple[float, float, float] | None
    objective_values: Mapping[str, float]
    flight_dynamics_authority: bool


@dataclass(frozen=True)
class ParetoRecord:
    candidate_id: str
    objective_values: Mapping[str, float]


@dataclass(frozen=True)
class ExperimentResult:
    version: str
    authority_status: str
    domain: ArchitectureDomain
    adequacy: ModelAdequacyContract
    uncertainty: tuple[UncertaintyItem, ...]
    outcomes: tuple[CandidateOutcome, ...]
    pareto_frontier: tuple[ParetoRecord, ...]
    experiment_hash: str
    canon_changed: bool = False
    production_shipclasses_changed: bool = False
    flight_dynamics_authority: bool = False


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def validate_domain(domain: ArchitectureDomain) -> None:
    if domain.authority_status != FOUNDATION_AUTHORITY:
        raise GenerativeShipyardError("architecture domain authority mismatch")
    seen: set[str] = set()
    for choice in domain.choices:
        if choice.choice_id in seen:
            raise GenerativeShipyardError(f"duplicate architecture choice {choice.choice_id}")
        seen.add(choice.choice_id)
        if choice.status not in CHOICE_STATUSES:
            raise GenerativeShipyardError(f"unsupported choice status {choice.status}")
        if choice.status in {"FIXED_CANON", "BOUNDED_DESIGN_CHOICE"} and not choice.allowed_values:
            raise GenerativeShipyardError(f"choice {choice.choice_id} requires allowed values")
        if choice.status == "OPEN_NOT_ADMITTED" and choice.allowed_values:
            raise GenerativeShipyardError(f"OPEN choice {choice.choice_id} may not carry admitted values")


def validate_adequacy(contract: ModelAdequacyContract) -> None:
    if contract.authority_status != FOUNDATION_AUTHORITY:
        raise GenerativeShipyardError("model adequacy authority mismatch")
    if contract.adequate_for_rejection and not contract.admissible_rejection_reasons:
        raise GenerativeShipyardError("rejection-capable model must enumerate admissible rejection reasons")
    if contract.adequate_for_selection and not contract.adequate_for_screening:
        raise GenerativeShipyardError("selection adequacy requires screening adequacy")


def validate_uncertainty(items: Sequence[UncertaintyItem]) -> None:
    seen: set[str] = set()
    for item in items:
        if item.item_id in seen:
            raise GenerativeShipyardError(f"duplicate uncertainty item {item.item_id}")
        seen.add(item.item_id)
        if item.uncertainty_class not in UNCERTAINTY_CLASSES:
            raise GenerativeShipyardError(f"unsupported uncertainty class {item.uncertainty_class}")


def wayfarer_config_domain() -> ArchitectureDomain:
    # This first experiment intentionally varies only choices already admitted by
    # the S1 qualification-candidate model. It is configuration search, not yet
    # whole-vehicle architecture search.
    domain = ArchitectureDomain(
        domain_id="WAYFARER_S1_CONFIG_DOMAIN_v0.1",
        version=FOUNDATION_VERSION,
        choices=(
            ArchitectureChoiceSpec(
                "relational_x_m", "FIXED_CANON", (26.0,), "m",
                "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            ),
            ArchitectureChoiceSpec(
                "launch_x_m", "BOUNDED_DESIGN_CHOICE",
                (20.5, 21.25, 21.5, 21.75, 22.0, 22.5, 22.75, 23.5), "m",
                "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            ),
            ArchitectureChoiceSpec(
                "tank_x_m", "BOUNDED_DESIGN_CHOICE",
                (17.0, 18.0, 20.0, 24.0, 28.0, 30.0, 32.0, 33.0), "m",
                "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            ),
            ArchitectureChoiceSpec(
                "tank_axial_geometry", "OPEN_NOT_ADMITTED", (), None,
                "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            ),
            ArchitectureChoiceSpec(
                "radiator_panel_geometry", "OPEN_NOT_ADMITTED", (), None,
                "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            ),
        ),
    )
    validate_domain(domain)
    return domain


def wayfarer_s1_adequacy() -> ModelAdequacyContract:
    contract = ModelAdequacyContract(
        model_id="WAYFARER_S1_MODE_A",
        fidelity="L1_DETERMINISTIC_REDUCED_ORDER",
        validity_domain="S1 admitted mass/centroid, two admitted full bodies, tank cross-section keep-outs, bounded station choices",
        known_omissions=(
            "tank axial geometry",
            "radiator panel geometry",
            "docking geometry",
            "qualified full-body inertia",
            "structural load cases and sizing",
            "thermal and radiation fields",
            "coupled MDAO convergence",
            "manufacturing feasibility",
        ),
        calibration_basis="WAYFARER_S0 authority manifest + WAYFARER_S1 test definition",
        adequate_for_screening=True,
        adequate_for_rejection=True,
        adequate_for_selection=False,
        admissible_rejection_reasons=(
            "PHYSICAL_INPUTS_FINITE_POSITIVE",
            "TOTAL_WET_MASS_EXACT",
            "NORMAL_REMASS_EXACT",
            "WORKING_FLUID_WATER_EXACT",
            "RELATIONAL_ENVELOPE_IN_REGION",
            "LAUNCH_WITHIN_BAY",
            "LAUNCH_PLUS_Z_EXTRACTION_SIDE",
            "TANK_QUADRATURE_MASS_STATION",
            "ADMITTED_BODY_COLLISION_FREE",
            "OPEN_GEOMETRY_NOT_USED",
        ),
    )
    validate_adequacy(contract)
    return contract


def wayfarer_uncertainty_state() -> tuple[UncertaintyItem, ...]:
    items = (
        UncertaintyItem("relational_x_m", "FIXED_KNOWN", "S1 relational equivalent body center fixed at x=26 m", "WAYFARER_S1_TEST_DEFINITION_v0.1.md"),
        UncertaintyItem("launch_x_m", "DESIGN_VARIABLE", "bounded launch working-envelope station", "WAYFARER_S1_TEST_DEFINITION_v0.1.md"),
        UncertaintyItem("tank_x_m", "DESIGN_VARIABLE", "common remass tank centroid station", "WAYFARER_S1_TEST_DEFINITION_v0.1.md"),
        UncertaintyItem("tank_axial_geometry", "OPEN_NOT_ADMITTED", "tank axial length not admitted to S1 collision authority", "WAYFARER_S1_TEST_DEFINITION_v0.1.md"),
        UncertaintyItem("full_inertia", "MODEL_FORM", "centroidal inertia unresolved for point-mass-only systems", "physical_design_core.py"),
    )
    validate_uncertainty(items)
    return items


def _probe_definitions() -> tuple[tuple[str, float, float], ...]:
    # Deliberately includes admissible and inadmissible probes. Inadmissible
    # values exist to prove rejection provenance, not to expand the admitted
    # design domain.
    return (
        ("P01", 21.25, 18.0),
        ("P02", 22.0, 24.0),
        ("P03", 22.75, 32.0),
        ("P04", 20.5, 24.0),
        ("P05", 23.5, 24.0),
        ("P06", 22.0, 17.0),
        ("P07", 22.0, 33.0),
        ("P08", 21.5, 28.0),
        ("P09", 22.5, 20.0),
        ("P10", 21.75, 30.0),
    )


def _failed_constraint_ids_from_error(message: str, admissible: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(cid for cid in admissible if f"{cid}:" in message))


def _dominates(a: Mapping[str, float], b: Mapping[str, float]) -> bool:
    keys = tuple(sorted(a))
    if keys != tuple(sorted(b)):
        raise GenerativeShipyardError("Pareto vectors have different objective keys")
    return all(float(a[k]) <= float(b[k]) for k in keys) and any(float(a[k]) < float(b[k]) for k in keys)


def pareto_frontier(outcomes: Sequence[CandidateOutcome]) -> tuple[ParetoRecord, ...]:
    legal = [o for o in outcomes if o.status == "SURVIVED_SCREEN" and o.objective_values]
    frontier: list[ParetoRecord] = []
    for row in legal:
        if any(_dominates(other.objective_values, row.objective_values) for other in legal if other.candidate_id != row.candidate_id):
            continue
        frontier.append(ParetoRecord(row.candidate_id, dict(row.objective_values)))
    return tuple(sorted(frontier, key=lambda r: r.candidate_id))


def run_wayfarer_config_experiment(seed: int = 2226) -> ExperimentResult:
    domain = wayfarer_config_domain()
    adequacy = wayfarer_s1_adequacy()
    uncertainty = wayfarer_uncertainty_state()
    outcomes: list[CandidateOutcome] = []
    parent: str | None = None

    for generation, (probe_id, launch_x, tank_x) in enumerate(_probe_definitions()):
        candidate_id = f"WAYFARER::{probe_id}::SEED-{int(seed)}"
        lineage = CandidateLineage(
            candidate_id=candidate_id,
            parent_candidate_id=parent,
            generation=generation,
            mutation_id=f"SET_LAUNCH_{launch_x:.2f}_TANK_{tank_x:.2f}",
            choices={"relational_x_m": 26.0, "launch_x_m": launch_x, "tank_x_m": tank_x},
        )
        candidate = build_candidate(
            candidate_id=candidate_id,
            seed=int(seed),
            relational_x_m=26.0,
            launch_x_m=launch_x,
            tank_x_m=tank_x,
            solver_version=SOLVER_VERSION,
        )
        try:
            evaluation = evaluate_candidate(candidate)
            objective_values = {term.objective_id: float(term.value) for term in evaluation.objective_vector}
            outcomes.append(CandidateOutcome(
                candidate_id=candidate_id,
                lineage=lineage,
                status="SURVIVED_SCREEN",
                rejection_reason=None,
                failed_constraint_ids=(),
                mass_kg=float(evaluation.mass_kg),
                center_of_mass_m=tuple(float(v) for v in evaluation.center_of_mass_m),
                objective_values=objective_values,
                flight_dynamics_authority=False,
            ))
            parent = candidate_id
        except WayfarerS1Error as exc:
            message = str(exc)
            failed = _failed_constraint_ids_from_error(message, adequacy.admissible_rejection_reasons)
            if not failed:
                raise GenerativeShipyardError(f"rejection not covered by adequacy contract: {message}") from exc
            outcomes.append(CandidateOutcome(
                candidate_id=candidate_id,
                lineage=lineage,
                status="REJECTED_BY_ADEQUATE_MODEL",
                rejection_reason=message,
                failed_constraint_ids=failed,
                mass_kg=None,
                center_of_mass_m=None,
                objective_values={},
                flight_dynamics_authority=False,
            ))

    frontier = pareto_frontier(outcomes)
    payload = {
        "version": EXPERIMENT_VERSION,
        "authority_status": EXPERIMENT_AUTHORITY,
        "domain": asdict(domain),
        "adequacy": asdict(adequacy),
        "uncertainty": [asdict(x) for x in uncertainty],
        "outcomes": [asdict(x) for x in outcomes],
        "pareto_frontier": [asdict(x) for x in frontier],
        "canon_changed": False,
        "production_shipclasses_changed": False,
        "flight_dynamics_authority": False,
    }
    return ExperimentResult(
        version=EXPERIMENT_VERSION,
        authority_status=EXPERIMENT_AUTHORITY,
        domain=domain,
        adequacy=adequacy,
        uncertainty=uncertainty,
        outcomes=tuple(outcomes),
        pareto_frontier=frontier,
        experiment_hash=_sha(payload),
    )


def result_payload(result: ExperimentResult) -> dict[str, Any]:
    return {
        "version": result.version,
        "authority_status": result.authority_status,
        "domain": asdict(result.domain),
        "adequacy": asdict(result.adequacy),
        "uncertainty": [asdict(x) for x in result.uncertainty],
        "outcomes": [asdict(x) for x in result.outcomes],
        "pareto_frontier": [asdict(x) for x in result.pareto_frontier],
        "experiment_hash": result.experiment_hash,
        "canon_changed": result.canon_changed,
        "production_shipclasses_changed": result.production_shipclasses_changed,
        "flight_dynamics_authority": result.flight_dynamics_authority,
    }


def canonical_result_json(result: ExperimentResult) -> str:
    return _canonical(result_payload(result))


if __name__ == "__main__":
    print(json.dumps(result_payload(run_wayfarer_config_experiment()), indent=2, sort_keys=True))
