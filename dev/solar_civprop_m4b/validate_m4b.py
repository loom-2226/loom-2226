"""Body-neutral M4-B semantic guardrails for frozen candidate assertions."""
from __future__ import annotations

FAMILIES = {"VOLATILES", "METALS", "SILICATES_ROCK", "CARBONACEOUS_ORGANICS"}
FORBIDDEN = {"delta_v", "flight_time", "accessibility_score", "mining_rate", "extraction_efficiency", "recovery_efficiency", "price", "cost", "npv", "bemr", "profit", "resource_score", "habitation_suitability", "settlement_attractiveness"}
QUANTIFIED = {"QUANTIFIED", "QUANTIFIED_APPROXIMATE", "QUANTIFIED_RANGE"}


def violations(assertion: dict, eligible_body_ids: set[str]) -> list[str]:
    """Return deterministic blocking reason codes; never infers missing science."""
    out = []
    if assertion.get("body_id") not in eligible_body_ids:
        out.append("IDENTITY_NOT_ELIGIBLE")
    families = assertion.get("resource_families") or []
    if not families or set(families) - FAMILIES:
        out.append("RESOURCE_FAMILY_INVALID")
    if not assertion.get("material_species"):
        out.append("MATERIAL_IDENTITY_MISSING")
    if not assertion.get("evidence_class") or not assertion.get("lineage"):
        out.append("EPISTEMIC_OR_LINEAGE_PROVENANCE_MISSING")
    if not assertion.get("source_key") and not assertion.get("existing_source_id"):
        out.append("SOURCE_REFERENCE_MISSING")
    if not assertion.get("observation_key") and not assertion.get("existing_observation_id"):
        out.append("OBSERVATION_REFERENCE_MISSING")
    sem = str(assertion.get("abundance_semantics", "UNKNOWN")).upper()
    val, low, high = (assertion.get(k) for k in ("abundance_value", "abundance_min", "abundance_max"))
    if sem == "UNKNOWN" and any(x is not None for x in (val, low, high)):
        out.append("UNKNOWN_LAUNDERED_TO_NUMERIC")
    species = str(assertion.get("material_species", "")).lower()
    if any(token in species for token in ("-type asteroid", "taxonomy", "taxonomic class")) and sem in QUANTIFIED | {"BOUNDED", "RANGE"}:
        out.append("TAXONOMY_LAUNDERED_TO_ABUNDANCE")
    if sem in QUANTIFIED and (val is None or not assertion.get("abundance_unit")):
        out.append("QUANTIFIED_WITHOUT_VALUE_OR_UNIT")
    if (sem in {"BOUNDED", "RANGE", "QUANTIFIED_RANGE"} or low is not None or high is not None) and not assertion.get("abundance_unit"):
        out.append("BOUNDED_ABUNDANCE_WITHOUT_UNIT")
    if (low is not None or high is not None) and (low is None or high is None or low > high):
        out.append("INVALID_ABUNDANCE_BOUNDS")
    if val is not None and (not isinstance(val, (float, int)) or val < 0):
        out.append("INVALID_ABUNDANCE_VALUE")
    if low is not None and low < 0 or high is not None and high < 0:
        out.append("NEGATIVE_ABUNDANCE_BOUND")
    unit = str(assertion.get("abundance_unit", "")).lower()
    if unit in {"wt%", "vol%", "mass%", "atomic%"} and any(x is not None and x > 100 for x in (val, low, high)):
        out.append("PERCENT_ABUNDANCE_OVER_100")
    if any(str(k).lower() in FORBIDDEN or any(token in str(k).lower() for token in ("economic", "profit", "attractiveness", "suitability", "mining", "delta_v", "flight_time")) for k in assertion):
        out.append("DOWNSTREAM_ECONOMIC_OR_ENGINEERING_LEAKAGE")
    return out


def validate_campaign(campaign: dict, eligible_body_ids: set[str]) -> None:
    seen = set()
    for a in campaign["evidence_assertions"]:
        if a["key"] in seen:
            raise ValueError("DUPLICATE_ASSERTION_KEY:" + a["key"])
        seen.add(a["key"])
        errors = violations(a, eligible_body_ids)
        if errors:
            raise ValueError(a["key"] + ":" + ",".join(errors))
