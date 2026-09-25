"""Deterministic ARP invariants; these do not determine scientific truth."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .models import AssertionCandidate, FrontierEntry, Lien

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

COVERAGE = {"COVERED", "PARTIAL", "MODEL_ONLY", "CONFLICTED", "NOT_APPLICABLE", "UNKNOWN", "SOURCE_NOT_FOUND"}
EVIDENCE = {"DIRECT_SAMPLE", "IN_SITU_DIRECT", "IN_SITU_REMOTE", "EARTH_REMOTE", "DYNAMICAL_INFERENCE", "ANALOG_INFERENCE", "PHYSICAL_MODEL", "THEORETICAL_EXPECTATION", "DERIVED"}
FRONTIER_PHASES = {"KNOWABLE", "INFERRED", "FUTURE_OBSERVABLE", "ENGINEERING_DERIVED", "ECONOMIC_DERIVED"}
LIEN_STATES = {"OPEN", "RESOLVED", "ACCEPTED_UNKNOWN", "DEFERRED_SCHEMA", "SOURCE_UNAVAILABLE"}
DIRECT = {"DIRECT_SAMPLE", "IN_SITU_DIRECT", "IN_SITU_REMOTE", "EARTH_REMOTE"}
FORBIDDEN_AUTHORITY = {"ENGINEERING_DERIVED", "ECONOMIC_DERIVED", "RESOURCE_POTENTIAL", "HABITATION_POTENTIAL", "CIVPROP", "TRANSPORT"}


def _error(errors: list[str], code: str, detail: str) -> None:
    errors.append(f"{code}: {detail}")


def valid_time(value: str) -> bool:
    try:
        if DATE_RE.fullmatch(value):
            date.fromisoformat(value)
            return True
        if TIMESTAMP_RE.fullmatch(value):
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            return True
    except ValueError:
        return False
    return False


def _before_cutoff(value: str | None, cutoff: str) -> bool:
    return value is None or value <= cutoff


def validate_artifacts(campaign: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    seen_sha: dict[str, str] = {}
    source_ids = {s.get("source_id") for s in campaign.get("sources", [])}
    for artifact in campaign.get("artifacts", []):
        aid = artifact.get("artifact_id")
        if artifact.get("source_id") not in source_ids:
            _error(errors, "PROVENANCE", f"artifact {aid} references unknown source")
        if not SHA_RE.fullmatch(str(artifact.get("sha256", ""))):
            _error(errors, "ARTIFACT_HASH", f"artifact {aid} has malformed SHA-256")
        if not isinstance(artifact.get("byte_count"), int) or artifact["byte_count"] < 0:
            _error(errors, "ARTIFACT_SIZE", f"artifact {aid} has invalid byte count")
        if aid in {a.get("artifact_id") for a in campaign.get("artifacts", []) if a is not artifact}:
            _error(errors, "DUPLICATE_ARTIFACT", f"artifact id {aid} is repeated")
        digest = artifact.get("sha256")
        if digest in seen_sha and seen_sha[digest] != aid:
            _error(errors, "DUPLICATE_ARTIFACT", f"artifacts {seen_sha[digest]} and {aid} share a hash")
        seen_sha[digest] = aid
        if root is not None and artifact.get("local_path"):
            path = root / artifact["local_path"]
            if not path.exists():
                _error(errors, "ARTIFACT_MISSING", f"{aid} local artifact is absent")
            else:
                if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    _error(errors, "ARTIFACT_HASH", f"{aid} hash does not match local bytes")
                if path.stat().st_size != artifact["byte_count"]:
                    _error(errors, "ARTIFACT_SIZE", f"{aid} byte count does not match local bytes")
    return errors


def validate_campaign(campaign: dict[str, Any], authority_policy: dict[str, Any] | None = None, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    required = ("campaign_id", "target_body", "body_profile", "knowledge_cutoff", "research_tier", "arp_version", "solar_facts_schema_version", "repository_baseline", "status", "qualification_state")
    for key in required:
        if not campaign.get(key):
            _error(errors, "CAMPAIGN", f"missing {key}")
    cutoff = campaign.get("knowledge_cutoff", "")
    if not valid_time(cutoff):
        _error(errors, "CAMPAIGN_TIME", "knowledge_cutoff is not a valid canonical date/time")
    if campaign.get("arp_version") != "1.0.0":
        _error(errors, "CAMPAIGN_VERSION", "campaign is not ARP 1.0")
    lanes = campaign.get("lanes", {})
    for name, lane in lanes.items():
        if lane.get("coverage") not in COVERAGE:
            _error(errors, "COVERAGE", f"lane {name} has invalid coverage")
    for gap in campaign.get("unresolved_gaps", []):
        if not gap.get("gap_id") or not gap.get("lane"):
            _error(errors, "RESUMABILITY", "unresolved gap lacks stable id/lane")
    errors.extend(validate_artifacts(campaign, root))
    source_map = {s.get("source_id"): s for s in campaign.get("sources", [])}
    artifact_map = {a.get("artifact_id"): a for a in campaign.get("artifacts", [])}
    keys: set[str] = set()
    lineages: dict[str, list[dict[str, Any]]] = {}
    for assertion in campaign.get("assertions", []):
        aid = assertion.get("assertion_id", "<missing>")
        source = source_map.get(assertion.get("source_id"))
        artifact = artifact_map.get(assertion.get("artifact_id"))
        if source is None or artifact is None:
            _error(errors, "PROVENANCE", f"assertion {aid} lacks source/artifact path")
        if not assertion.get("provenance_complete", False):
            _error(errors, "PROVENANCE", f"assertion {aid} is marked incomplete")
        if assertion.get("evidence_class") not in EVIDENCE:
            _error(errors, "EVIDENCE_CLASS", f"assertion {aid} has invalid evidence class")
        if assertion.get("scope_type") not in {"GLOBAL", "REGIONAL", "SITE", "INSTRUMENT_FOOTPRINT", "UNKNOWN"}:
            _error(errors, "SCOPE", f"assertion {aid} has invalid scope")
        if assertion.get("status") != "CANDIDATE":
            _error(errors, "AUTHORITY", f"assertion {aid} is not CANDIDATE")
        if assertion.get("scope_type") in {"REGIONAL", "SITE", "INSTRUMENT_FOOTPRINT"} and assertion.get("scope_claim") == "GLOBAL":
            _error(errors, "SCOPE_LAUNDERING", f"assertion {aid} promotes local evidence globally")
        resolution = assertion.get("resolution") or {}
        if resolution.get("source_grain") in {"GLOBAL", "REGIONAL", "COARSE"} and resolution.get("claimed_grain") in {"SITE", "LOCAL", "FINE"}:
            _error(errors, "RESOLUTION_LAUNDERING", f"assertion {aid} promotes coarse evidence to site scale")
        if assertion.get("claim_kind") in {"OBSERVATION", "DIRECT_MEASUREMENT"} and assertion.get("evidence_class") in {"PHYSICAL_MODEL", "DERIVED", "DYNAMICAL_INFERENCE"}:
            _error(errors, "EPISTEMIC_PROMOTION", f"assertion {aid} labels non-direct evidence as measurement")
        if assertion.get("method_type") == "MODEL" and assertion.get("evidence_class") in DIRECT:
            _error(errors, "MODEL_PROMOTION", f"assertion {aid} labels a model method as direct evidence")
        if assertion.get("value_min") is not None and assertion.get("value_max") is not None and assertion.get("reported_value") is not None:
            _error(errors, "RANGE_MIDPOINT", f"assertion {aid} contains a scalar alongside a reported range")
        if assertion.get("reported_value") is not None and assertion.get("reported_unit") is None:
            _error(errors, "UNIT", f"assertion {aid} has a value without reported unit")
        if assertion.get("research_coverage") == "UNKNOWN" and assertion.get("reported_value") is not None:
            _error(errors, "UNKNOWN_FABRICATION", f"assertion {aid} fills UNKNOWN with a value")
        key = assertion.get("canonical_assertion_key")
        if key and key in keys:
            _error(errors, "DUPLICATE_ASSERTION", f"assertion {aid} repeats canonical key {key}")
        if key:
            keys.add(key)
        lineage = assertion.get("independent_evidence_lineage_id")
        if lineage:
            lineages.setdefault(lineage, []).append(assertion)
        if source:
            if not _before_cutoff(source.get("publication_date"), cutoff) or not _before_cutoff(source.get("release_date"), cutoff):
                _error(errors, "CUTOFF", f"assertion {aid} uses source evidence after cutoff")
            if authority_policy and source.get("authority_role") == "SECONDARY" and source.get("primary_available"):
                _error(errors, "AUTHORITY_LAUNDERING", f"assertion {aid} selects secondary source while primary is represented")
    for lineage, members in lineages.items():
        if len(members) > 1 and any(a.get("independent", False) for a in members):
            _error(errors, "DUPLICATE_LINEAGE", f"lineage {lineage} is counted as independent more than once")
    frontier_ids = {f.get("variable") for f in campaign.get("epistemic_frontier", [])}
    for entry in campaign.get("epistemic_frontier", []):
        if entry.get("phase") not in FRONTIER_PHASES:
            _error(errors, "FRONTIER", f"{entry.get('variable')} has invalid phase")
        if entry.get("research_coverage") not in COVERAGE:
            _error(errors, "FRONTIER", f"{entry.get('variable')} has invalid coverage")
        if entry.get("phase") == "FUTURE_OBSERVABLE" and entry.get("state_at_cutoff") == "KNOWABLE":
            _error(errors, "FRONTIER_PROMOTION", f"{entry.get('variable')} is future-observable but knowable")
        if entry.get("phase") in FORBIDDEN_AUTHORITY:
            _error(errors, "CONTAMINATION", f"frontier {entry.get('variable')} enters forbidden authority")
    for lien in campaign.get("liens", []):
        if lien.get("state") not in LIEN_STATES:
            _error(errors, "LIEN", f"{lien.get('lien_id')} has invalid state")
    if any(l.get("state") == "OPEN" and l.get("severity") == "BLOCKING" for l in campaign.get("liens", [])):
        _error(errors, "BLOCKING_LIEN", "campaign has an open blocking lien")
    summary = campaign.get("coverage_summary", {})
    if summary.get("complete_claim") and any(l.get("coverage") not in {"COVERED", "NOT_APPLICABLE"} for l in lanes.values() if l.get("applicable", True)):
        _error(errors, "FALSE_COMPLETENESS", "campaign claims complete coverage with unresolved applicable lanes")
    return errors


def qualify(campaign: dict[str, Any], authority_policy: dict[str, Any] | None = None, root: Path | None = None) -> dict[str, Any]:
    errors = validate_campaign(campaign, authority_policy, root)
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "blocking": bool(errors)}


def efficiency_metrics(campaign: dict[str, Any]) -> dict[str, Any]:
    metrics = campaign.get("metrics", {})
    return {
        "sources_discovered": metrics.get("sources_discovered", len(campaign.get("sources", []))),
        "sources_acquired": metrics.get("sources_acquired", len(campaign.get("artifacts", []))),
        "sources_rejected": metrics.get("sources_rejected", 0),
        "artifacts_reused": metrics.get("artifacts_reused", 0),
        "duplicate_work_avoided": metrics.get("duplicate_work_avoided", 0),
        "assertions_extracted": metrics.get("assertions_extracted", len(campaign.get("assertions", []))),
        "assertions_accepted": metrics.get("assertions_accepted", len(campaign.get("assertions", []))),
        "assertions_rejected": metrics.get("assertions_rejected", 0),
        "coverage_before": metrics.get("coverage_before", {}),
        "coverage_after_pass_1": metrics.get("coverage_after_pass_1", {}),
        "coverage_after_pass_2": metrics.get("coverage_after_pass_2", {}),
        "external_research_operations": metrics.get("external_research_operations", 0),
        "independent_evidence_lineages": len({a.get("independent_evidence_lineage_id") for a in campaign.get("assertions", []) if a.get("independent_evidence_lineage_id")}),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
