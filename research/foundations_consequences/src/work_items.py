"""Minimal, dependency-free validation for Foundations & Consequences work items.

This module intentionally has no imports from LOOM production/runtime packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


LANES = {
    "EMPIRICAL_MATHEMATICAL",
    "SPECULATIVE_SYNTHETIC",
    "CIVILIZATIONAL_FICTIONAL",
    "ADVERSARIAL_WILD",
}

STATES = {
    "SEED",
    "PROBE",
    "RABBIT_HOLE",
    "PROGRAM_CANDIDATE",
    "QUALIFICATION",
    "PROMOTION_CANDIDATE",
    "RETIRED",
    "GHOST",
}

EPISTEMIC_CLASSES = {"E", "A", "P", "C", "D", "O"}
HAZARDS = {"LOW", "MEDIUM", "HIGH", "EXTREME"}
SCORE_KEYS = {
    "scientific_leverage",
    "speculative_reach",
    "canon_leverage",
    "world_yield",
    "play_yield",
    "rabbit_hole_joy",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def validate_work_item(item: Mapping[str, object]) -> ValidationResult:
    errors: list[str] = []

    if item.get("lane") not in LANES:
        errors.append("invalid lane")
    if item.get("state") not in STATES:
        errors.append("invalid state")
    if item.get("epistemic_class") not in EPISTEMIC_CLASSES:
        errors.append("invalid epistemic_class")
    if item.get("epistemic_hazard") not in HAZARDS:
        errors.append("invalid epistemic_hazard")

    scores = item.get("scores")
    if not isinstance(scores, Mapping):
        errors.append("scores must be a mapping")
    else:
        missing = SCORE_KEYS.difference(scores.keys())
        extra = set(scores.keys()).difference(SCORE_KEYS)
        if missing:
            errors.append("missing scores: " + ", ".join(sorted(missing)))
        if extra:
            errors.append("unknown scores: " + ", ".join(sorted(extra)))
        for key in SCORE_KEYS.intersection(scores.keys()):
            value = scores[key]
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 5:
                errors.append(f"score {key} must be integer 0..5")

    return ValidationResult(ok=not errors, errors=tuple(errors))


def evidence_traffic_warning(source_lane: str, target_lane: str, claim_basis: Sequence[str]) -> tuple[str, ...]:
    """Return warnings for prohibited promotion paths.

    This is intentionally conservative: it flags a scientific promotion attempt
    when its stated basis contains fiction/canon-fit/desirability terms. It does
    not attempt to decide scientific truth.
    """

    warnings: list[str] = []
    scientific_target = target_lane == "EMPIRICAL_MATHEMATICAL"
    basis = " ".join(claim_basis).lower()

    if scientific_target and source_lane == "CIVILIZATIONAL_FICTIONAL":
        warnings.append("fiction may generate scientific questions but is not scientific evidence")
    if scientific_target and "canon fit" in basis:
        warnings.append("canon compatibility is not scientific evidence")
    if scientific_target and "desirable" in basis:
        warnings.append("fictional desirability is not scientific evidence")

    return tuple(warnings)
