from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Sequence, Tuple


COMPILER_VERSION = "LOOM_PHYSICAL_DESIGN_REQUIREMENTS_COMPILER_v0.1"


class RequirementsError(ValueError):
    """Fail-closed error for invalid or unsupported design requirements."""


@dataclass(frozen=True)
class ScalarRequirement:
    requirement_id: str
    value: float
    unit: str
    relation: str
    authority_status: str
    provenance: str


@dataclass(frozen=True)
class DoctrineProfile:
    doctrine_id: str
    objective_priority: Tuple[str, ...]
    required_capabilities: Tuple[str, ...] = ()
    authority_status: str = "QUALIFICATION_ONLY"
    provenance: str = "UNSET"


@dataclass(frozen=True)
class LinearDerivationRule:
    rule_id: str
    input_requirement_id: str
    output_requirement_id: str
    coefficient: float
    offset: float
    output_unit: str
    output_relation: str
    authority_status: str
    provenance: str


@dataclass(frozen=True)
class OpenDerivation:
    output_requirement_id: str
    reason: str
    provenance: str


@dataclass(frozen=True)
class CompiledRequirementSet:
    compiler_version: str
    doctrine: DoctrineProfile
    direct_requirements: Tuple[ScalarRequirement, ...]
    derived_requirements: Tuple[ScalarRequirement, ...]
    open_derivations: Tuple[OpenDerivation, ...]
    input_hash: str

    @property
    def all_requirements(self) -> Tuple[ScalarRequirement, ...]:
        return self.direct_requirements + self.derived_requirements


def _clean_text(value: str, label: str) -> str:
    text = str(value).strip()
    if not text:
        raise RequirementsError(f"{label} is required")
    return text


def _finite_nonnegative(value: float, label: str) -> float:
    v = float(value)
    if not math.isfinite(v) or v < 0.0:
        raise RequirementsError(f"{label} must be finite and non-negative")
    return v


def _validate_relation(relation: str) -> str:
    relation = _clean_text(relation, "requirement relation").upper()
    if relation not in {"MIN", "MAX", "EXACT"}:
        raise RequirementsError(f"Unsupported requirement relation: {relation}")
    return relation


def validate_requirement(row: ScalarRequirement) -> None:
    _clean_text(row.requirement_id, "requirement_id")
    _finite_nonnegative(row.value, f"requirement {row.requirement_id}")
    _clean_text(row.unit, f"unit {row.requirement_id}")
    _validate_relation(row.relation)
    _clean_text(row.authority_status, f"authority_status {row.requirement_id}")
    _clean_text(row.provenance, f"provenance {row.requirement_id}")


def validate_doctrine(doctrine: DoctrineProfile) -> None:
    _clean_text(doctrine.doctrine_id, "doctrine_id")
    _clean_text(doctrine.authority_status, "doctrine authority_status")
    _clean_text(doctrine.provenance, "doctrine provenance")
    if not doctrine.objective_priority:
        raise RequirementsError("Doctrine objective_priority must be non-empty")
    if len(set(doctrine.objective_priority)) != len(doctrine.objective_priority):
        raise RequirementsError("Doctrine objective_priority must contain unique IDs")
    for objective_id in doctrine.objective_priority:
        _clean_text(objective_id, "objective_id")
    if len(set(doctrine.required_capabilities)) != len(doctrine.required_capabilities):
        raise RequirementsError("Doctrine required_capabilities must contain unique IDs")


def validate_rule(rule: LinearDerivationRule) -> None:
    _clean_text(rule.rule_id, "rule_id")
    _clean_text(rule.input_requirement_id, "input_requirement_id")
    _clean_text(rule.output_requirement_id, "output_requirement_id")
    coefficient = float(rule.coefficient)
    offset = float(rule.offset)
    if not math.isfinite(coefficient) or coefficient < 0.0:
        raise RequirementsError(f"Rule {rule.rule_id} coefficient must be finite and non-negative")
    if not math.isfinite(offset) or offset < 0.0:
        raise RequirementsError(f"Rule {rule.rule_id} offset must be finite and non-negative")
    _clean_text(rule.output_unit, f"output_unit {rule.rule_id}")
    _validate_relation(rule.output_relation)
    _clean_text(rule.authority_status, f"authority_status {rule.rule_id}")
    _clean_text(rule.provenance, f"provenance {rule.rule_id}")


def _canonical_payload(
    direct_requirements: Sequence[ScalarRequirement],
    doctrine: DoctrineProfile,
    rules: Sequence[LinearDerivationRule],
    expected_outputs: Sequence[str],
) -> str:
    payload = {
        "compiler_version": COMPILER_VERSION,
        "direct_requirements": [row.__dict__ for row in sorted(direct_requirements, key=lambda r: r.requirement_id)],
        "doctrine": doctrine.__dict__,
        "rules": [row.__dict__ for row in sorted(rules, key=lambda r: r.rule_id)],
        "expected_outputs": sorted(str(v) for v in expected_outputs),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compile_requirements(
    direct_requirements: Sequence[ScalarRequirement],
    *,
    doctrine: DoctrineProfile,
    rules: Sequence[LinearDerivationRule] = (),
    expected_outputs: Sequence[str] = (),
) -> CompiledRequirementSet:
    """Compile direct demands into derived engineering requirements without hidden defaults.

    v0.1 supports deterministic one-input affine rules. A derivation rule marked OPEN is
    never used. If no admitted rule can produce an expected output, that output remains
    explicit in ``open_derivations`` rather than being guessed.
    """

    validate_doctrine(doctrine)

    direct_map: Dict[str, ScalarRequirement] = {}
    for row in direct_requirements:
        validate_requirement(row)
        if row.requirement_id in direct_map:
            raise RequirementsError(f"Duplicate direct requirement {row.requirement_id}")
        direct_map[row.requirement_id] = row

    rule_ids = set()
    output_rule_ids = set()
    for rule in rules:
        validate_rule(rule)
        if rule.rule_id in rule_ids:
            raise RequirementsError(f"Duplicate derivation rule {rule.rule_id}")
        rule_ids.add(rule.rule_id)
        if rule.output_requirement_id in output_rule_ids:
            raise RequirementsError(
                f"v0.1 permits only one derivation rule per output: {rule.output_requirement_id}"
            )
        output_rule_ids.add(rule.output_requirement_id)

    compiled: Dict[str, ScalarRequirement] = dict(direct_map)
    derived: Dict[str, ScalarRequirement] = {}
    open_rows: Dict[str, OpenDerivation] = {}

    pending = sorted(rules, key=lambda r: r.rule_id)
    progress = True
    while progress:
        progress = False
        for rule in pending:
            output_id = rule.output_requirement_id
            if output_id in compiled or output_id in open_rows:
                continue
            if rule.authority_status.upper() == "OPEN":
                open_rows[output_id] = OpenDerivation(
                    output_requirement_id=output_id,
                    reason=f"RULE_OPEN_NOT_ADMITTED:{rule.rule_id}",
                    provenance=rule.provenance,
                )
                progress = True
                continue
            source = compiled.get(rule.input_requirement_id)
            if source is None:
                continue
            value = float(source.value) * float(rule.coefficient) + float(rule.offset)
            if not math.isfinite(value) or value < 0.0:
                raise RequirementsError(f"Rule {rule.rule_id} produced invalid value")
            row = ScalarRequirement(
                requirement_id=output_id,
                value=value,
                unit=rule.output_unit,
                relation=rule.output_relation,
                authority_status=rule.authority_status,
                provenance=f"{rule.provenance};derived_from={source.requirement_id};rule={rule.rule_id}",
            )
            validate_requirement(row)
            compiled[output_id] = row
            derived[output_id] = row
            progress = True

    for rule in pending:
        output_id = rule.output_requirement_id
        if output_id not in compiled and output_id not in open_rows:
            open_rows[output_id] = OpenDerivation(
                output_requirement_id=output_id,
                reason=f"MISSING_INPUT:{rule.input_requirement_id};rule={rule.rule_id}",
                provenance=rule.provenance,
            )

    for output_id in expected_outputs:
        output_id = _clean_text(output_id, "expected output")
        if output_id not in compiled and output_id not in open_rows:
            open_rows[output_id] = OpenDerivation(
                output_requirement_id=output_id,
                reason="NO_ADMITTED_DERIVATION_RULE",
                provenance="REQUIREMENTS_COMPILER_v0.1",
            )

    canonical = _canonical_payload(direct_requirements, doctrine, rules, expected_outputs)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return CompiledRequirementSet(
        compiler_version=COMPILER_VERSION,
        doctrine=doctrine,
        direct_requirements=tuple(sorted(direct_map.values(), key=lambda r: r.requirement_id)),
        derived_requirements=tuple(sorted(derived.values(), key=lambda r: r.requirement_id)),
        open_derivations=tuple(sorted(open_rows.values(), key=lambda r: r.output_requirement_id)),
        input_hash=digest,
    )


def canonical_json(compiled: CompiledRequirementSet) -> str:
    payload = {
        "compiler_version": compiled.compiler_version,
        "doctrine": compiled.doctrine.__dict__,
        "direct_requirements": [row.__dict__ for row in compiled.direct_requirements],
        "derived_requirements": [row.__dict__ for row in compiled.derived_requirements],
        "open_derivations": [row.__dict__ for row in compiled.open_derivations],
        "input_hash": compiled.input_hash,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
