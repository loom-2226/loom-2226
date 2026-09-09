from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping, Sequence, Tuple

from physical_design_core import (
    CandidateDesign,
    DesignVariable,
    EvaluationResult,
    PhysicalDesignError,
)


class SearchError(PhysicalDesignError):
    """Fail-closed error for invalid search configuration or no legal design."""


CandidateBuilder = Callable[[str, int, Mapping[str, float]], CandidateDesign]
CandidateEvaluator = Callable[[CandidateDesign], EvaluationResult]


@dataclass(frozen=True)
class SearchResult:
    candidate: CandidateDesign
    evaluation: EvaluationResult
    examined_count: int
    legal_count: int
    rejected_count: int
    selector: str
    solver_version: str


def variable_values(variable: DesignVariable) -> Tuple[float, ...]:
    low = float(variable.lower)
    high = float(variable.upper)
    step = float(variable.step)
    if not all(math.isfinite(v) for v in (low, high, step)):
        raise SearchError(f"Variable {variable.variable_id} bounds/step must be finite")
    if high < low:
        raise SearchError(f"Variable {variable.variable_id} upper bound is below lower bound")
    if step <= 0.0:
        raise SearchError(f"Variable {variable.variable_id} step must be positive")
    if high == low:
        return (low,)

    span = high - low
    count = int(math.floor(span / step + 1e-12))
    values = [low + i * step for i in range(count + 1)]
    if values[-1] < high - 1e-12:
        values.append(high)
    values = [high if abs(v - high) <= 1e-12 else v for v in values]
    if any(v < low - 1e-12 or v > high + 1e-12 for v in values):
        raise SearchError(f"Variable {variable.variable_id} grid escaped bounds")
    return tuple(values)


def _canonical_value_map(values: Mapping[str, float]) -> str:
    return json.dumps(
        {key: float(values[key]) for key in sorted(values)},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def stable_candidate_id(solver_version: str, seed: int, values: Mapping[str, float]) -> str:
    payload = f"{solver_version}|{int(seed)}|{_canonical_value_map(values)}".encode("utf-8")
    return "CAND-" + hashlib.sha256(payload).hexdigest()[:20].upper()


def _seeded_tie_break(seed: int, candidate_id: str) -> str:
    return hashlib.sha256(f"{int(seed)}|{candidate_id}".encode("utf-8")).hexdigest()


def _objective_key(evaluation: EvaluationResult) -> Tuple[float, ...]:
    values = tuple(float(term.value) for term in evaluation.objective_vector)
    if not values or not all(math.isfinite(v) for v in values):
        raise SearchError("Objective vector must be non-empty and finite")
    return values


class DeterministicGridSearch:
    """Portable exhaustive grid search with visible lexicographic selection."""

    def __init__(
        self,
        *,
        solver_version: str,
        variables: Sequence[DesignVariable],
        candidate_builder: CandidateBuilder,
        evaluator: CandidateEvaluator,
    ) -> None:
        if not solver_version.strip():
            raise SearchError("solver_version is required")
        ids = [v.variable_id for v in variables]
        if not ids or len(set(ids)) != len(ids):
            raise SearchError("Search variables must be non-empty with unique IDs")
        self.solver_version = solver_version
        self.variables = tuple(variables)
        self.candidate_builder = candidate_builder
        self.evaluator = evaluator

    def solve(self, seed: int) -> SearchResult:
        seed = int(seed)
        grids = [variable_values(v) for v in self.variables]
        examined = 0
        legal = []
        for row in itertools.product(*grids):
            examined += 1
            values: Dict[str, float] = {
                variable.variable_id: float(value)
                for variable, value in zip(self.variables, row)
            }
            candidate_id = stable_candidate_id(self.solver_version, seed, values)
            try:
                candidate = self.candidate_builder(candidate_id, seed, values)
                evaluation = self.evaluator(candidate)
                key = _objective_key(evaluation)
            except PhysicalDesignError:
                continue
            if not all(result.passed for result in evaluation.hard_constraints):
                continue
            legal.append((key, _seeded_tie_break(seed, candidate_id), candidate, evaluation))

        if not legal:
            raise SearchError(f"No legal candidate after examining {examined} grid points")

        legal.sort(key=lambda row: (row[0], row[1]))
        _, _, candidate, evaluation = legal[0]
        return SearchResult(
            candidate=candidate,
            evaluation=evaluation,
            examined_count=examined,
            legal_count=len(legal),
            rejected_count=examined - len(legal),
            selector="LEXICOGRAPHIC_OBJECTIVE_VECTOR_THEN_SEEDED_STABLE_HASH",
            solver_version=self.solver_version,
        )
