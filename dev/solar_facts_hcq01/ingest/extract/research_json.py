from __future__ import annotations

import json
from pathlib import Path
from dataclasses import replace

from ..models import (
    FactCandidate,
    MaterialCandidate,
    RegionCandidate,
    DerivedQuantityCandidate,
    ActivityCandidate,
    GravityModelCandidate,
    ModelProductCandidate,
    OrientationModelCandidate,
    ObservationCandidate,
    SourceCandidate,
    StagingRecord,
)


def _round2_semantic_remediation(payload: dict) -> dict:
    """Map preserved Round-1 staging labels into the frozen v0.2 vocabulary.

    The source JSON is preserved evidence; this adapter is the typed ingestion
    boundary where scientific semantic review is applied.
    """
    import copy
    p = copy.deepcopy(payload)
    source = p["source"]
    title = source.get("title", "")
    if title.startswith("Ahuna Mons:"):
        source["source_type"] = "OTHER"  # LPSC abstract, not peer-reviewed journal article
    if source.get("url") == "https://arxiv.org/pdf/2003.11045":
        source["source_type"] = "OTHER"  # preserved artifact is the arXiv preprint, not the later journal object
        source["citation_text"] = source.get("citation_text", "") + " Preserved artifact is an arXiv preprint; later journal publication is not represented by this artifact."
    confidence_map = {"MEDIUM": "MODERATE"}
    for fact in p.get("facts", []):
        # This is an earliest-public-availability lower bound, not an assertion
        # that publication date equals observation date.
        fact.setdefault("knowledge_valid_from", source.get("publication_date"))
        fact["confidence_class"] = confidence_map.get(fact.get("confidence_class", "UNKNOWN"), fact.get("confidence_class", "UNKNOWN"))
        if fact.get("evidence_class") in {"OBSERVED", "ASSERTED"}:
            if title == "Planetary Physical Parameters":
                if fact["property_code"] == "MASS":
                    fact["evidence_class"] = "DYNAMICAL_INFERENCE"
                elif fact["property_code"] == "BULK_DENSITY":
                    fact["evidence_class"] = "DERIVED"
                    fact["notes"] = "lineage: JPL total mass and equivalent-volume mean radius"
                else:
                    fact["evidence_class"] = "IN_SITU_REMOTE"
            elif fact["property_code"] == "GM":
                fact["evidence_class"] = "DYNAMICAL_INFERENCE"
            elif fact["property_code"] == "ROTATION_PERIOD":
                fact["evidence_class"] = "IN_SITU_REMOTE"
            elif fact["property_code"] == "THERMAL_INERTIA":
                fact["evidence_class"] = "PHYSICAL_MODEL"
            else:
                fact["evidence_class"] = "IN_SITU_REMOTE"
    for observation in p.get("observations", []):
        product = observation.get("observation_product_id", "")
        if product == "AHUNA_FC_DTM_140M":
            observation["region_ref"] = "AHUNA_MONS"
        elif product == "GRaND_CERES_HYDROGEN_2017":
            observation["region_ref"] = "MID_HIGH_LATITUDES"
        elif product == "DAWN_FC_OCCATOR_XM2":
            observation["region_ref"] = "OCCATOR"
    for material in p.get("materials", []):
        material["confidence_class"] = confidence_map.get(material.get("confidence_class", "UNKNOWN"), material.get("confidence_class", "UNKNOWN"))
        if title == "Exposed water ice on Ceres from neutron spectroscopy":
            material["evidence_class"] = "IN_SITU_REMOTE"
        elif title == "Herschel discovers water vapour around dwarf planet Ceres":
            material["evidence_class"] = "EARTH_REMOTE"
        elif title == "Recent cryovolcanic activity at Occator crater on Ceres":
            material["evidence_class"] = "IN_SITU_REMOTE"
        elif title == "A partially differentiated interior for (1) Ceres deduced from its gravity field and shape":
            material["evidence_class"] = "PHYSICAL_MODEL"
        elif title == "Global and localized mineralogical composition of Ceres from Dawn VIR":
            material["evidence_class"] = "IN_SITU_REMOTE"
    # A modeled PSR area is not a material inventory. Preserve the PSR model
    # product and region, but do not load the misleading water_ice row.
    if title == "The permanently shadowed regions of dwarf planet Ceres":
        p["materials"] = []
    for activity in p.get("activities", []):
        activity["confidence_class"] = confidence_map.get(activity.get("confidence_class", "UNKNOWN"), activity.get("confidence_class", "UNKNOWN"))
        activity["evidence_class"] = "PHYSICAL_MODEL" if "INTERPRETATION" in activity.get("activity_type", "") else "IN_SITU_REMOTE"
    for product in p.get("model_products", []):
        name = product.get("model_name", "").lower()
        if "ahuna" in name:
            product["region_ref"] = "AHUNA_MONS"
        elif "polar psr" in name:
            product["region_ref"] = "NORTH_POLAR_PSR"
            product["notes"] = (product.get("notes") or "") + " Modeled northern polar PSR area is approximately 1800 km^2; this is not measured water-ice extent."
        elif "regional dtm" in name:
            product["region_ref"] = "CERES_REGIONAL_DTM_COVERAGE"
    for gravity in p.get("gravity_models", []):
        if title == "Dawn Ceres Gravity Science Derived Science Data V4.0":
            # Values are the first header record of the preserved SHA artifact:
            # reference radius 470 km and GM 62.6288969025 km^3/s^2.
            gravity["gravitational_parameter"] = 62.6288969025
            gravity["reference_radius"] = 470.0
            gravity["normalization"] = "PDS header normalization flag 1"
            gravity["coefficient_convention"] = "Cmn and Smn spherical-harmonic coefficients"
            gravity["validity_notes"] = "Reference epoch is not present in the preserved TAB/header artifact; remains UNKNOWN."
    return p


def extract_payload(payload: dict, *, artifact, extractor_name: str = "research_json") -> StagingRecord:
    payload = _round2_semantic_remediation(payload)
    source = payload["source"]
    artifact = replace(artifact, original_url=source["url"])
    candidate_source = SourceCandidate(
        source_type=source["source_type"], provider=source["provider"], title=source["title"],
        url=source["url"], publication_date=source["publication_date"],
        retrieved_at=artifact.retrieved_at, citation_text=source["citation_text"],
        persistent_identifier=source.get("persistent_identifier"), doi=source.get("doi"),
        authors=source.get("authors"), product_name=source.get("product_name"),
        product_version=source.get("product_version"), raw_artifact=artifact,
    )
    observations = tuple(ObservationCandidate(**item) for item in payload.get("observations", []))
    facts = tuple(FactCandidate(**item) for item in payload.get("facts", []))
    materials = tuple(MaterialCandidate(**item) for item in payload.get("materials", []))
    regions = tuple(RegionCandidate(**item) for item in payload.get("regions", []))
    model_products = tuple(ModelProductCandidate(**item) for item in payload.get("model_products", []))
    gravity_models = tuple(GravityModelCandidate(**item) for item in payload.get("gravity_models", []))
    activities = tuple(ActivityCandidate(**item) for item in payload.get("activities", []))
    orientation_models = tuple(OrientationModelCandidate(**item) for item in payload.get("orientation_models", []))
    derived_quantities = tuple(
        DerivedQuantityCandidate(**item) for item in payload.get("derived_quantities", [])
    )
    return StagingRecord(
        source=candidate_source, observations=observations, facts=facts,
        materials=materials, regions=regions,
        model_products=model_products, gravity_models=gravity_models,
        derived_quantities=derived_quantities,
        activities=activities, orientation_models=orientation_models,
        extractor_name=extractor_name, metadata=payload.get("metadata", {}),
    )


def extract(path: Path, *, artifact, extractor_name: str = "research_json") -> StagingRecord:
    return extract_payload(json.loads(path.read_text(encoding="utf-8")), artifact=artifact, extractor_name=extractor_name)
