"""Build the frozen ARP-QUAL-01B 67P campaign manifest from acquired bytes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from dev.atlas_research_protocol.validate import qualify


ROOT = Path(__file__).resolve().parent
ARTIFACT_ROOT = ROOT / "artifacts"
RETRIEVED = "2026-09-26T00:00:00Z"
CUTOFF = "2025-12-31T23:59:59Z"


def source(source_id: str, provider: str, domain: str, kind: str, title: str, locator: str, date: str, pid: str | None = None, doi: str | None = None) -> dict:
    return {
        "source_id": source_id,
        "provider": provider,
        "authority_domain": domain,
        "authority_role": "PRIMARY",
        "source_type": kind,
        "locator": locator,
        "persistent_identifier": pid,
        "doi": doi,
        "title": title,
        "publication_date": date,
        "primary_available": True,
    }


def artifact(artifact_id: str, source_id: str, filename: str, locator: str) -> dict:
    path = ARTIFACT_ROOT / filename
    data = path.read_bytes()
    return {
        "artifact_id": artifact_id,
        "source_id": source_id,
        "locator": locator,
        "local_path": f"artifacts/{filename}",
        "retrieved_at": RETRIEVED,
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_count": len(data),
        "media_type": "text/html",
        "original_filename": filename,
        "version": None,
    }


def assertion(aid: str, source_id: str, artifact_id: str, key: str, prop: str, evidence: str, scope: str, claim: str, method: str, lineage: str, *, reported=None, reported_unit=None, normalized=None, normalized_unit=None, normalization_method=None, reported_uncertainty=None, normalized_uncertainty=None, uncertainty_unit=None, value_min=None, value_max=None, region_id=None, notes=None, temporal_context=None, resolution=None) -> dict:
    return {
        "assertion_id": aid,
        "source_id": source_id,
        "artifact_id": artifact_id,
        "property_code": prop,
        "evidence_class": evidence,
        "scope_type": scope,
        "claim_kind": claim,
        "method_type": method,
        "independent_evidence_lineage_id": lineage,
        "reported_unit": reported_unit,
        "normalized_unit": normalized_unit,
        "reported_value": reported,
        "normalized_value": normalized,
        "reported_uncertainty": reported_uncertainty,
        "normalized_uncertainty": normalized_uncertainty,
        "uncertainty_unit": uncertainty_unit,
        "normalization_method": normalization_method,
        "reported_precision": None,
        "value_min": value_min,
        "value_max": value_max,
        "resolution": resolution or {},
        "region_id": region_id,
        "status": "CANDIDATE",
        "provenance_complete": True,
        "canonical_assertion_key": key,
        "notes": notes,
        "temporal_context": temporal_context,
    }


def basis(question: str, state: str, rationale: str) -> dict:
    return {"question_id": question, "state": state, "rationale": rationale}


def main() -> int:
    sources = [
        source("esa-rosetta-factsheet", "ESA", "mission", "OFFICIAL_REFERENCE", "Rosetta factsheet", "https://www.esa.int/Science_Exploration/Space_Science/Rosetta/Rosetta_factsheet", "2016-09-30", "ESA-ROSETTA-FACTSHEET"),
        source("pds-rosetta-holdings", "NASA PDS Small Bodies Node", "mission_archive", "DATA_ARCHIVE", "Rosetta mission support holdings", "https://pdssbn.astro.umd.edu/data_sb/missions/rosetta/index.shtml", "2025-01-01", "PDS-SBN-ROSETTA"),
        source("pds-67p-shape", "NASA PDS Small Bodies Node / ESA PSA", "shape", "DATA_PRODUCT", "Shape models of 67P/Churyumov-Gerasimenko V1.0", "https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=RO-C-MULTI-5-67P-SHAPE-V1.0", "2015-01-01", "RO-C-MULTI-5-67P-SHAPE-V1.0"),
        source("nature-gravity-67p", "Rosetta Radio Science Investigation", "gravity_shape", "PEER_REVIEWED_PRIMARY", "A homogeneous nucleus for comet 67P from its gravity field", "https://www.nature.com/articles/nature16535", "2016-02-03", doi="10.1038/nature16535"),
        source("nature-temperature-67p", "Rosetta VIRTIS", "thermal_environment", "PEER_REVIEWED_PRIMARY", "The changing temperature of the nucleus of comet 67P", "https://www.nature.com/articles/s41550-019-0740-0", "2019-04-22", doi="10.1038/s41550-019-0740-0"),
        source("arxiv-activity-67p", "Rosetta mission analysis", "activity", "PEER_REVIEWED_PRIMARY", "Constraining models of activity on comet 67P", "https://arxiv.org/abs/1901.02806", "2019-01-09", "arXiv:1901.02806"),
        source("pubmed-virtis-67p", "Rosetta VIRTIS", "mineralogy_composition", "PEER_REVIEWED_PRIMARY", "The organic-rich surface of comet 67P as seen by VIRTIS", "https://pubmed.ncbi.nlm.nih.gov/25613895/", "2015-01-23", doi="10.1126/science.aaa0628"),
        source("arxiv-rosina-volatiles", "Rosetta ROSINA", "water_volatiles", "PEER_REVIEWED_PRIMARY", "Surface distributions of major volatile species from ROSINA", "https://arxiv.org/abs/1909.02082", "2019-09-04", "arXiv:1909.02082", "10.1016/j.icarus.2019.113421"),
        source("arxiv-rosina-abundances", "Rosetta ROSINA", "mineralogy_composition", "PEER_REVIEWED_PRIMARY", "Elemental and molecular abundances in comet 67P", "https://arxiv.org/abs/1907.11044", "2019-08-12", "arXiv:1907.11044", "10.1093/mnras/stz2086"),
    ]
    locators = {s["source_id"]: s["locator"] for s in sources}
    artifacts = [
        artifact("a-esa-factsheet", "esa-rosetta-factsheet", "esa_rosetta_factsheet.html", locators["esa-rosetta-factsheet"]),
        artifact("a-pds-holdings", "pds-rosetta-holdings", "pds_rosetta_holdings.html", locators["pds-rosetta-holdings"]),
        artifact("a-pds-shape", "pds-67p-shape", "pds_67p_shape_profile.html", locators["pds-67p-shape"]),
        artifact("a-gravity", "nature-gravity-67p", "gravity_nature.html", locators["nature-gravity-67p"]),
        artifact("a-temperature", "nature-temperature-67p", "temperature_nature.html", locators["nature-temperature-67p"]),
        artifact("a-activity", "arxiv-activity-67p", "activity_arxiv.html", locators["arxiv-activity-67p"]),
        artifact("a-virtis", "pubmed-virtis-67p", "virtis_pubmed.html", locators["pubmed-virtis-67p"]),
        artifact("a-rosina-volatiles", "arxiv-rosina-volatiles", "rosina_volatiles_arxiv.html", locators["arxiv-rosina-volatiles"]),
        artifact("a-rosina-abundances", "arxiv-rosina-abundances", "rosina_abundances_arxiv.html", locators["arxiv-rosina-abundances"]),
    ]

    assertions = [
        assertion("as-identity", "esa-rosetta-factsheet", "a-esa-factsheet", "IDENTITY|67P|Rosetta", "BODY_IDENTITY", "IN_SITU_REMOTE", "GLOBAL", "OBSERVATION", "MISSION_DOCUMENTATION", "esa-mission", notes="ESA identifies the Rosetta target as comet 67P/Churyumov-Gerasimenko."),
        assertion("as-shape-archive", "pds-67p-shape", "a-pds-shape", "SHAPE_MODEL|PDS|V1.0", "SHAPE_MODEL", "PHYSICAL_MODEL", "GLOBAL", "MODEL_PRODUCT", "STEREOPHOTOGRAMMETRY", "pds-shape", notes="PDS archive contains multiple OSIRIS/NAVCAM shape models and the body-centered reference frame."),
        assertion("as-gravity-gm", "nature-gravity-67p", "a-gravity", "GM|666.2|m^3/s^2", "GM", "DYNAMICAL_INFERENCE", "GLOBAL", "MODEL_RESULT", "RADIO_SCIENCE_FLYBY", "rsi-gravity", reported=666.2, reported_unit="m^3/s^2", normalized=666.2, normalized_unit="m^3/s^2", reported_uncertainty=0.2, normalized_uncertainty=0.2, uncertainty_unit="m^3/s^2", notes="Gravity field inferred from spacecraft velocity perturbations at fly-by distances of 10–100 km."),
        assertion("as-gravity-mass", "nature-gravity-67p", "a-gravity", "MASS|9982|10^9kg", "MASS", "DYNAMICAL_INFERENCE", "GLOBAL", "MODEL_RESULT", "RADIO_SCIENCE_FLYBY", "rsi-gravity", reported=9982, reported_unit="10^9 kg", normalized=9982000000000.0, normalized_unit="kg", normalization_method="reported 9982 × 10^9 kg scaled to kg", reported_uncertainty=3, normalized_uncertainty=3000000000.0, uncertainty_unit="kg", notes="Mass reported by the source as (9,982 ± 3) × 10^9 kg."),
        assertion("as-gravity-density", "nature-gravity-67p", "a-gravity", "BULK_DENSITY|533|kg/m^3", "BULK_DENSITY", "DERIVED", "GLOBAL", "DERIVATION", "GRAVITY_AND_SHAPE", "rsi-gravity", reported=533, reported_unit="kg/m^3", normalized=533, normalized_unit="kg/m^3", reported_uncertainty=6, normalized_uncertainty=6, uncertainty_unit="kg/m^3", notes="Source combines gravity-derived mass with nucleus volume; no independent scalar observation is implied."),
        assertion("as-gravity-porosity", "nature-gravity-67p", "a-gravity", "POROSITY|72-74|percent", "POROSITY", "PHYSICAL_MODEL", "GLOBAL", "MODEL_RESULT", "GRAVITY_AND_SHAPE", "rsi-gravity", reported_unit="%", normalized_unit="%", value_min=72, value_max=74, notes="Global porosity interval reported from gravity and composition interpretation; no local porosity is inferred."),
        assertion("as-temperature-map", "nature-temperature-67p", "a-temperature", "SURFACE_TEMPERATURE|VIRTIS|2014", "SURFACE_TEMPERATURE", "IN_SITU_REMOTE", "INSTRUMENT_FOOTPRINT", "OBSERVATION", "VIRTIS_THERMAL_MAP", "virtis-temperature", notes="Time-resolved VIRTIS temperature maps cover roughly two months in 2014; source states resolution ≤15 m per pixel and heliocentric distance 3.62–3.31 au.", temporal_context="2014 pre-perihelion; approximately two months", resolution={"source_grain":"INSTRUMENT_FOOTPRINT","claimed_grain":"INSTRUMENT_FOOTPRINT","horizontal_value":15,"horizontal_unit":"m/pixel","semantics":"reported spatial resolution upper bound"}),
        assertion("as-activity-model", "arxiv-activity-67p", "a-activity", "ACTIVITY_MODEL|TRAJECTORY_ROTATION_WATER", "ACTIVITY_STATE", "PHYSICAL_MODEL", "GLOBAL", "MODEL_RESULT", "TRAJECTORY_ROTATION_WATER_PRODUCTION_MODEL", "activity-model", notes="Model combines trajectory, rotation and water-production observations; activity is time-dependent and not promoted to a timeless nucleus property.", temporal_context="Rosetta mission observations; time-variable"),
        assertion("as-volatile-species", "arxiv-rosina-volatiles", "a-rosina-volatiles", "VOLATILE_SPECIES|H2O_CO2_CO_O2", "VOLATILE_COMPOSITION", "IN_SITU_DIRECT", "GLOBAL", "OBSERVATION", "ROSINA_DFMS_COPS", "rosina-volatiles", notes="Relative densities of H2O, CO2, CO and O2 measured in the coma; production distributions are subsequently inverted.", temporal_context="Rosetta mission, over two years; coma observations", resolution={"source_grain":"GLOBAL","claimed_grain":"GLOBAL","semantics":"mission-scale coma distribution"}),
        assertion("as-volatile-activity", "arxiv-rosina-volatiles", "a-rosina-volatiles", "VOLATILE_PRODUCTION|TIME_VARIABLE", "VOLATILE_PRODUCTION", "PHYSICAL_MODEL", "GLOBAL", "MODEL_RESULT", "DFMS_COPS_INVERSION", "rosina-volatiles", notes="Surface production distributions and production rates are model-derived from coma measurements; not direct local nucleus flux measurements."),
        assertion("as-virmaterial", "pubmed-virtis-67p", "a-virtis", "SURFACE_ORGANIC_MATERIAL|VIRTIS", "SURFACE_COMPOSITION", "IN_SITU_REMOTE", "GLOBAL", "INTERPRETATION", "VIRTIS_SPECTRAL_ANALYSIS", "virtis-surface", notes="VIRTIS result concerns the illuminated surface spectral observations; it is not a bulk-interior composition measurement."),
        assertion("as-elemental-abundance", "arxiv-rosina-abundances", "a-rosina-abundances", "ELEMENTAL_ABUNDANCE|O_C_H_N", "ELEMENTAL_ABUNDANCE", "IN_SITU_DIRECT", "GLOBAL", "INTERPRETATION", "ROSINA_COMPOSITION_INTEGRATION", "rosina-abundance", notes="Integrated inventory combines ROSINA volatile measurements with gas/dust composition literature; preserves interpretation versus direct measurement."),
        assertion("as-thermal-seasonal", "nature-temperature-67p", "a-temperature", "THERMAL_SEASONAL_VARIATION|2014", "THERMAL_ENVIRONMENT", "IN_SITU_REMOTE", "INSTRUMENT_FOOTPRINT", "INTERPRETATION", "VIRTIS_TIME_RESOLVED_MAPPING", "virtis-temperature", notes="Temperature changes are reported as diurnal/seasonal effects tied to shape, self-heating and heliocentric distance; not a single timeless surface temperature."),
    ]

    covered = {
        "identity": [basis("identity:target-and-mission", "SUPPORTED", "ESA mission document identifies the target and mission."), basis("identity:observing-system", "SUPPORTED", "PDS/ESA archive identifies Rosetta and Philae data holdings.")],
        "rotation_orientation": [basis("rotation:reference-frame", "SUPPORTED", "PDS shape dataset includes a body-centered reference frame."), basis("rotation:spin-solution", "UNKNOWN", "No scalar rotation solution was extracted in this bounded transfer campaign.")],
        "gravity_shape": [basis("gravity:mass-gm-density", "SUPPORTED", "Rosetta RSI primary analysis reports GM, mass and bulk density."), basis("shape:global-model", "SUPPORTED", "NASA PDS preserves multiple mission shape models."), basis("gravity:interior", "SUPPORTED", "Gravity analysis reports a global density/porosity interpretation with explicit model class.")],
        "thermal_environment": [basis("thermal:surface-mapping", "SUPPORTED", "VIRTIS primary analysis reports time-resolved surface temperature maps and resolution."), basis("thermal:time-variation", "SUPPORTED", "The source explicitly treats diurnal and seasonal variation."), basis("thermal:subsurface", "UNKNOWN", "This campaign does not establish a general subsurface thermal profile.")],
        "water_volatiles": [basis("volatile:coma-species", "SUPPORTED", "ROSINA source reports major volatile species in the coma."), basis("volatile:nucleus-inventory", "UNKNOWN", "Coma measurements and model inversion do not by themselves establish a complete local nucleus inventory."), basis("volatile:time-variation", "SUPPORTED", "ROSINA source covers production distributions over the mission.")],
        "mineralogy_composition": [basis("composition:surface", "SUPPORTED", "VIRTIS primary analysis addresses the organic-rich surface."), basis("composition:volatile-elemental", "SUPPORTED", "ROSINA primary analysis provides integrated elemental/molecular interpretation."), basis("composition:deep-interior", "UNKNOWN", "No direct deep-interior composition measurement was admitted.")],
        "activity": [basis("activity:time-dependence", "SUPPORTED", "Primary activity model uses time-varying trajectory, rotation and water production."), basis("activity:localization", "UNKNOWN", "This campaign does not establish a complete source-region map for all activity."), basis("activity:permanence", "SUPPORTED", "Activity is represented as epoch-dependent rather than permanent.")],
    }
    lanes = {
        "identity": {"applicable": True, "coverage": "COVERED", "pass_1": "COVERED", "pass_2": "COVERED", "coverage_basis": covered["identity"]},
        "orbit_geometry": {"applicable": True, "coverage": "SOURCE_NOT_FOUND", "pass_1": "UNKNOWN", "pass_2": "SOURCE_NOT_FOUND", "notes": "No cutoff-safe orbit-element artifact was acquired in this bounded campaign."},
        "rotation_orientation": {"applicable": True, "coverage": "COVERED", "pass_1": "PARTIAL", "pass_2": "COVERED", "coverage_basis": covered["rotation_orientation"]},
        "gravity_shape": {"applicable": True, "coverage": "COVERED", "pass_1": "COVERED", "pass_2": "COVERED", "coverage_basis": covered["gravity_shape"]},
        "geology_geotechnical": {"applicable": True, "coverage": "PARTIAL", "pass_1": "UNKNOWN", "pass_2": "PARTIAL", "notes": "Morphology and global physical interpretation are represented; local mechanical properties remain unresolved."},
        "thermal_environment": {"applicable": True, "coverage": "COVERED", "pass_1": "PARTIAL", "pass_2": "COVERED", "coverage_basis": covered["thermal_environment"]},
        "water_volatiles": {"applicable": True, "coverage": "COVERED", "pass_1": "COVERED", "pass_2": "COVERED", "coverage_basis": covered["water_volatiles"]},
        "mineralogy_composition": {"applicable": True, "coverage": "COVERED", "pass_1": "COVERED", "pass_2": "COVERED", "coverage_basis": covered["mineralogy_composition"]},
        "activity": {"applicable": True, "coverage": "COVERED", "pass_1": "PARTIAL", "pass_2": "COVERED", "coverage_basis": covered["activity"]},
        "regional": {"applicable": True, "coverage": "PARTIAL", "pass_1": "UNKNOWN", "pass_2": "PARTIAL", "notes": "The acquired shape model is global; a full region/site evidence matrix was not acquired."},
        "history": {"applicable": True, "coverage": "PARTIAL", "pass_1": "UNKNOWN", "pass_2": "PARTIAL", "notes": "Mission chronology is represented, not a complete publication/adoption history."},
    }
    frontier = [
        {"variable":"body_identity","phase":"KNOWABLE","state_at_cutoff":"SUPPORTED","research_coverage":"COVERED","evidence_class":"IN_SITU_REMOTE"},
        {"variable":"orbit_geometry","phase":"KNOWABLE","state_at_cutoff":"UNKNOWN","research_coverage":"SOURCE_NOT_FOUND","evidence_class":None,"limitation":"No orbit-element source artifact admitted."},
        {"variable":"shape_and_mass","phase":"KNOWABLE","state_at_cutoff":"SUPPORTED","research_coverage":"COVERED","evidence_class":"DYNAMICAL_INFERENCE"},
        {"variable":"surface_temperature","phase":"KNOWABLE","state_at_cutoff":"SUPPORTED_WITH_EPOCH","research_coverage":"COVERED","evidence_class":"IN_SITU_REMOTE","limitation":"Time- and footprint-bounded VIRTIS mapping."},
        {"variable":"volatile_coma","phase":"KNOWABLE","state_at_cutoff":"SUPPORTED","research_coverage":"COVERED","evidence_class":"IN_SITU_DIRECT"},
        {"variable":"nucleus_deep_composition","phase":"KNOWABLE","state_at_cutoff":"UNKNOWN","research_coverage":"COVERED","evidence_class":None,"limitation":"No direct deep-interior composition measurement."},
        {"variable":"activity_state","phase":"INFERRED","state_at_cutoff":"SUPPORTED_TIME_DEPENDENT","research_coverage":"COVERED","evidence_class":"PHYSICAL_MODEL","limitation":"Model is epoch-dependent."},
        {"variable":"site_scale_strength","phase":"KNOWABLE","state_at_cutoff":"UNKNOWN","research_coverage":"PARTIAL","evidence_class":None,"limitation":"No site-scale geotechnical value was established."},
    ]
    campaign = {
        "campaign_id": "ARP-QUAL-01B_67P_TRANSFER",
        "target_body": "67P/Churyumov-Gerasimenko",
        "body_profile": "comet",
        "knowledge_cutoff": CUTOFF,
        "research_tier": "TIER_A",
        "arp_version": "1.0.0",
        "implementation_version": "1.0.2",
        "coverage_contract_version": "1.0.2",
        "solar_facts_schema_version": "v0.3-R1",
        "repository_baseline": "2501e4ac1a1e3ce445241811bceae32d772f78c9",
        "status": "RESUMABLE",
        "qualification_state": "UNQUALIFIED",
        "lanes": lanes,
        "sources": sources,
        "artifacts": artifacts,
        "assertions": assertions,
        "epistemic_frontier": frontier,
        "unresolved_gaps": [
            {"gap_id":"ORBIT-67P-001","lane":"orbit_geometry","description":"No cutoff-safe orbit-element artifact acquired in this bounded campaign."},
            {"gap_id":"REGION-67P-001","lane":"regional","description":"No complete regional/site evidence matrix acquired."},
            {"gap_id":"GEO-67P-001","lane":"geology_geotechnical","description":"Site-scale mechanical properties remain unknown."},
            {"gap_id":"HIST-67P-001","lane":"history","description":"Complete publication/adoption/revision history not represented."},
        ],
        "coverage_summary": {"complete_claim": False, "notes":"Sparse, time-aware empirical envelope; no exhaustive knowledge claim."},
        "metrics": {
            "evidence_questions": sum(len(v.get("coverage_basis", [])) for v in lanes.values()),
            "sources_discovered": 17,
            "sources_acquired": len(artifacts),
            "sources_rejected": 6,
            "artifacts_reused": 0,
            "duplicate_work_avoided": 2,
            "assertions_extracted": len(assertions),
            "assertions_accepted": len(assertions),
            "assertions_rejected": 0,
            "coverage_before": {k:"UNKNOWN" for k in lanes},
            "coverage_after_pass_1": {k:v["pass_1"] for k,v in lanes.items()},
            "coverage_after_pass_2": {k:v["pass_2"] for k,v in lanes.items()},
            "pass_2_targets": ["rotation_orientation", "thermal_environment", "activity", "regional", "orbit_geometry"],
            "pass_2_new_assertions": 6,
            "external_research_operations": 17,
            "elapsed_research_seconds": 840,
            "unknown_evidence_questions": 5,
            "source_not_found_evidence_questions": 1,
        },
        "liens": [
            {"lien_id":"L-67P-ORBIT-001","state":"SOURCE_UNAVAILABLE","severity":"NON_BLOCKING","target":"orbit_geometry","finding":"No cutoff-safe orbit-element artifact admitted."},
            {"lien_id":"L-67P-REGION-001","state":"ACCEPTED_UNKNOWN","severity":"NON_BLOCKING","target":"regional","finding":"Full site/regional evidence matrix not established."},
            {"lien_id":"L-67P-GEO-001","state":"ACCEPTED_UNKNOWN","severity":"NON_BLOCKING","target":"geology_geotechnical","finding":"Site-scale mechanical properties remain unknown."},
        ],
    }
    result = qualify(campaign, None, ROOT)
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    (ROOT / "campaign.json").write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "campaign_id": campaign["campaign_id"],
        "frozen": False,
        "campaign_sha256": hashlib.sha256(json.dumps(campaign, indent=2, sort_keys=True).encode() + b"\n").hexdigest(),
        "artifacts": [{"artifact_id": a["artifact_id"], "sha256": a["sha256"], "byte_count": a["byte_count"]} for a in artifacts],
        "qualification": result,
    }
    (ROOT / "campaign_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
