from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from generative_shipyard_foundation import (
    SOLVER_VERSION,
    CandidateOutcome,
    run_wayfarer_config_experiment,
)
from governed_ship_synthesis import build_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from wayfarer_s1_adapter import build_candidate, evaluate_candidate

COMPILER_VERSION = "LOOM_GENERATIVE_CANDIDATE_COMPILER_v0.1"
COMPILER_AUTHORITY = "DERIVED_CANDIDATE_REALIZATION_RESEARCH_ONLY"


class GenerativeCandidateCompilerError(ValueError):
    pass


@dataclass(frozen=True)
class CompiledCandidateArtifact:
    candidate_id: str
    parent_candidate_id: str | None
    generation: int
    choices: dict[str, float]
    mass_kg: float
    center_of_mass_m: tuple[float, float, float]
    governed_package_hash: str
    semantic_package_hash: str
    glb_sha256: str
    glb_bytes: bytes
    geometry_primitive_count: int
    flight_dynamics_authority: bool = False
    authority_status: str = COMPILER_AUTHORITY


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _survivor_to_candidate(outcome: CandidateOutcome, seed: int):
    if outcome.status != "SURVIVED_SCREEN":
        raise GenerativeCandidateCompilerError("only survived candidates may be compiled")
    choices = outcome.lineage.choices
    required = ("relational_x_m", "launch_x_m", "tank_x_m")
    if any(key not in choices for key in required):
        raise GenerativeCandidateCompilerError("survivor lineage missing required admitted choices")
    candidate = build_candidate(
        candidate_id=outcome.candidate_id,
        seed=int(seed),
        relational_x_m=float(choices["relational_x_m"]),
        launch_x_m=float(choices["launch_x_m"]),
        tank_x_m=float(choices["tank_x_m"]),
        solver_version=SOLVER_VERSION,
    )
    evaluation = evaluate_candidate(candidate)
    if evaluation.flight_dynamics_authority:
        raise GenerativeCandidateCompilerError("candidate compiler refuses flight-authority escalation")
    return candidate, evaluation


def compile_survivor(outcome: CandidateOutcome, seed: int = 2226) -> CompiledCandidateArtifact:
    candidate, evaluation = _survivor_to_candidate(outcome, seed)
    governed = build_governed_synthesis(candidate)
    semantic = build_semantic_geometry(governed)
    glb, manifest = build_semantic_glb(governed, semantic)
    digest = _sha256(glb)
    if digest != manifest.get("glb_sha256"):
        raise GenerativeCandidateCompilerError("semantic GLB digest mismatch")
    if governed.flight_dynamics_authority:
        raise GenerativeCandidateCompilerError("governed synthesis unexpectedly claims flight authority")
    return CompiledCandidateArtifact(
        candidate_id=outcome.candidate_id,
        parent_candidate_id=outcome.lineage.parent_candidate_id,
        generation=int(outcome.lineage.generation),
        choices={key: float(value) for key, value in outcome.lineage.choices.items()},
        mass_kg=float(evaluation.mass_kg),
        center_of_mass_m=tuple(float(v) for v in evaluation.center_of_mass_m),
        governed_package_hash=governed.package_hash,
        semantic_package_hash=semantic.package_hash,
        glb_sha256=digest,
        glb_bytes=glb,
        geometry_primitive_count=len(governed.geometry.primitives),
    )


def compile_wayfarer_survivor_family(seed: int = 2226) -> tuple[CompiledCandidateArtifact, ...]:
    experiment = run_wayfarer_config_experiment(seed)
    compiled = tuple(
        compile_survivor(outcome, seed)
        for outcome in experiment.outcomes
        if outcome.status == "SURVIVED_SCREEN"
    )
    if len(compiled) < 2:
        raise GenerativeCandidateCompilerError("candidate family requires at least two surviving realizations")
    if len({row.glb_sha256 for row in compiled}) < 2:
        raise GenerativeCandidateCompilerError("surviving candidates did not produce distinct semantic GLBs")
    return compiled


def result_payload(rows: tuple[CompiledCandidateArtifact, ...]) -> dict[str, Any]:
    summaries = []
    for row in rows:
        payload = asdict(row)
        payload.pop("glb_bytes")
        summaries.append(payload)
    return {
        "version": COMPILER_VERSION,
        "authority_status": COMPILER_AUTHORITY,
        "candidate_count": len(rows),
        "distinct_glb_count": len({row.glb_sha256 for row in rows}),
        "distinct_governed_package_count": len({row.governed_package_hash for row in rows}),
        "candidates": summaries,
        "flight_dynamics_authority": False,
        "canon_changed": False,
        "production_shipclasses_changed": False,
    }


def canonical_result_json(rows: tuple[CompiledCandidateArtifact, ...]) -> str:
    return json.dumps(result_payload(rows), sort_keys=True, separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    print(json.dumps(result_payload(compile_wayfarer_survivor_family()), indent=2, sort_keys=True, allow_nan=False))
