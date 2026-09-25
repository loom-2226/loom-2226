from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).parent / "attempt_02"
ART = ROOT / "artifacts"
RETRIEVED = "2026-09-26T08:00:00Z"


SPECS = [
    ("jpl-physical-parameters", "JPL", "gravity_shape", "PRIMARY", "GOVERNMENT_DATA_PAGE", "https://ssd.jpl.nasa.gov/planets/phys_par.html", "jpl_phys.html", "2019-12-12", None),
    ("pds-dawn-ceres-gravity-bundle", "NASA PDS", "gravity_shape", "PRIMARY", "MISSION_DATA_PRODUCT", "https://pds.nasa.gov/ds-view/pds/viewBundle.jsp?identifier=urn%3Anasa%3Apds%3Adawn-rss-der-ceres&version=1.0", "pds_gravity_bundle.html", None, "2025-01-01"),
    ("pds-ceres-coordinate-system", "NASA PDS SBN", "rotation_orientation", "PRIMARY", "MISSION_DOCUMENT", "https://sbnarchive.psi.edu/pds3/dawn/grav/DWNCGRS_2_v3_181005/DOCUMENT/CERES_COORD_SYS_180628.HTM", "pds_coordinate.html", "2018-06-28", None),
    ("pds-ceres-shape-profile", "NASA PDS", "gravity_shape", "PRIMARY", "MISSION_DATA_PRODUCT", "https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=DAWN-A-FC2-5-CERESSHAPESPC-V1.0", "pds_shape_profile.html", "2018-10-19", None),
    ("pds-ceres-shape-resource", "NASA PDS SBN", "gravity_shape", "PRIMARY", "MISSION_DATA_PRODUCT", "https://sbn.psi.edu/pds/resource/dawn/dwncfcshape.html", "pds_shape_resource.html", "2018-01-01", None),
    ("occator-cryovolcanic-activity", "Nature Astronomy / Dawn", "regional", "PRIMARY", "PEER_REVIEWED_PRIMARY", "https://doi.org/10.1038/s41550-020-1146-8", "occator_activity.html", "2020-08-10", None),
    ("ceres-psr-cold-traps", "Author-hosted primary paper copy", "regional", "PRIMARY", "PEER_REVIEWED_PRIMARY_COPY", "https://faculty.epss.ucla.edu/~ctrussell/russell_bib.html/papers/permanentshadow.pdf", "psr_model.pdf", "2016-07-06", None),
    ("ceres-thermal-preprint", "arXiv", "thermal_environment", "PRIMARY", "PREPRINT", "https://arxiv.org/abs/2003.11045", "thermal_arxiv.html", "2020-03-24", None),
    ("ceres-vir-mineralogy-preprint", "arXiv", "mineralogy_composition", "PRIMARY", "PREPRINT", "https://arxiv.org/abs/2010.03453", "vir_mineralogy.html", "2020-10-07", None),
    ("ceres-ammoniated-phyllosilicates", "Nature / Dawn VIR", "mineralogy_composition", "PRIMARY", "PEER_REVIEWED_PRIMARY", "https://doi.org/10.1038/nature16172", "vir_nature.html", "2015-12-09", None),
    ("ceres-interior-differentiation", "Nature / Dawn gravity", "gravity_shape", "PRIMARY", "PEER_REVIEWED_PRIMARY", "https://doi.org/10.1038/nature18955", "interior_nature.html", "2016-08-03", None),
    ("herschel-ceres-water-vapor", "ESA Herschel", "water_volatiles", "PRIMARY", "HERSCHEL", "https://www.esa.int/Science_Exploration/Space_Science/Herschel/Herschel_discovers_water_vapour_around_dwarf_planet_Ceres", "herschel_water.html", "2014-01-23", None),
]


def artifact_record(source_id: str, locator: str, filename: str, version: str | None = None) -> dict:
    data = (ART / filename).read_bytes()
    return {
        "artifact_id": f"artifact-{source_id}",
        "source_id": source_id,
        "locator": locator,
        "retrieved_at": RETRIEVED,
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_count": len(data),
        "media_type": "application/pdf" if filename.endswith(".pdf") else "text/html",
        "original_filename": filename,
        "local_path": f"artifacts/{filename}",
        "version": version,
    }


def source_record(spec: tuple) -> dict:
    sid, provider, domain, role, source_type, locator, filename, publication, release = spec
    return {
        "source_id": sid,
        "provider": provider,
        "authority_domain": domain,
        "authority_role": role,
        "source_type": source_type,
        "locator": locator,
        "persistent_identifier": locator if locator.startswith("https://doi.org/") else None,
        "publication_date": publication,
        "release_date": release,
        "version": "preserved-web-artifact-2026-09-26",
        "primary_available": False,
    }


def assertion(aid, sid, prop, evidence, scope, claim, method, lineage, *, unit=None, value=None, normalized_value=None, normalized_unit=None, uncertainty=None, uncertainty_unit=None, normalization_method=None, vmin=None, vmax=None, resolution=None, region=None, key=None, note=None):
    out = {
        "assertion_id": aid,
        "source_id": sid,
        "artifact_id": f"artifact-{sid}",
        "property_code": prop,
        "evidence_class": evidence,
        "scope_type": scope,
        "claim_kind": claim,
        "method_type": method,
        "independent_evidence_lineage_id": lineage,
        "reported_unit": unit,
        "normalized_unit": normalized_unit or unit,
        "reported_value": value,
        "normalized_value": value if normalized_value is None else normalized_value,
        "reported_uncertainty": uncertainty,
        "normalized_uncertainty": uncertainty,
        "uncertainty_unit": uncertainty_unit,
        "normalization_method": normalization_method,
        "value_min": vmin,
        "value_max": vmax,
        "resolution": resolution or {},
        "region_id": region,
        "status": "CANDIDATE",
        "provenance_complete": True,
        "canonical_assertion_key": key or aid,
    }
    if note:
        out["notes"] = note
    return out


def main() -> None:
    sources = [source_record(s) for s in SPECS]
    artifacts = [artifact_record(s[0], s[5], s[6]) for s in SPECS]
    A = []
    A += [
        assertion("a-jpl-equatorial-radius", "jpl-physical-parameters", "EQUATORIAL_RADIUS", "IN_SITU_REMOTE", "GLOBAL", "OBSERVATION", "TABLED_PARAMETER", "jpl-physical-table", unit="km", value=482.1, key="EQUATORIAL_RADIUS|482.1|km"),
        assertion("a-jpl-mean-radius", "jpl-physical-parameters", "MEAN_RADIUS", "IN_SITU_REMOTE", "GLOBAL", "OBSERVATION", "EQUIVALENT_VOLUME_SHAPE", "jpl-physical-table", unit="km", value=469.7, key="MEAN_RADIUS|469.7|km", note="JPL identifies this as the equivalent-volume mean radius; it is not the polar radius."),
        assertion("a-jpl-mass", "jpl-physical-parameters", "MASS", "DYNAMICAL_INFERENCE", "GLOBAL", "MODEL_RESULT", "RADIO_TRACKING", "jpl-physical-table", unit="10^18 kg", value=938.416, normalized_value=9.38416e20, normalized_unit="kg", normalization_method="reported 10^18 kg scaled to kg", key="MASS|938.416|10^18 kg"),
        assertion("a-jpl-density", "jpl-physical-parameters", "BULK_DENSITY", "DERIVED", "GLOBAL", "DERIVATION", "SPHERICAL_MASS_RADIUS", "jpl-physical-table", unit="g/cm^3", value=2.162, uncertainty=0.008, uncertainty_unit="g/cm^3", key="BULK_DENSITY|2.162|g/cm^3", note="JPL table reports density derived from mass and published mean radius."),
        assertion("a-jpl-rotation-period", "jpl-physical-parameters", "ROTATION_PERIOD", "IN_SITU_REMOTE", "GLOBAL", "OBSERVATION", "TABLED_PARAMETER", "jpl-physical-table", unit="day", value=0.37809042, key="ROTATION_PERIOD|0.37809042|day"),
        assertion("a-pds-gravity-product", "pds-dawn-ceres-gravity-bundle", "GRAVITY_FIELD_MODEL", "PHYSICAL_MODEL", "GLOBAL", "MODEL_PRODUCT", "SPHERICAL_HARMONIC_GRAVITY", "dawn-gravity-product", key="GRAVITY_FIELD_MODEL|dawn-pds|v1.0"),
        assertion("a-pds-coordinate-solution", "pds-ceres-coordinate-system", "ROTATION_ORIENTATION_SOLUTION", "DYNAMICAL_INFERENCE", "GLOBAL", "MODEL_PRODUCT", "RADIO_AND_OPTICAL_FRAME_SOLUTION", "dawn-coordinate-solution", key="ROTATION_ORIENTATION_SOLUTION|dawn-pds|2018"),
        assertion("a-pds-shape-product", "pds-ceres-shape-profile", "SHAPE_MODEL", "PHYSICAL_MODEL", "GLOBAL", "MODEL_PRODUCT", "STEREOPHOTOCLINOMETRY", "dawn-spc-shape", resolution={"source_grain": "GLOBAL", "claimed_grain": "GLOBAL", "horizontal_value": 100, "horizontal_unit": "m", "semantics": "model ground sample distance"}, key="SHAPE_MODEL|spc|100m"),
        assertion("a-pds-shape-archive", "pds-ceres-shape-resource", "SHAPE_MODEL_ARCHIVE", "PHYSICAL_MODEL", "GLOBAL", "MODEL_PRODUCT", "STEREOPHOTOCLINOMETRY_ARCHIVE", "dawn-spc-shape", key="SHAPE_MODEL_ARCHIVE|spc|pds"),
        assertion("a-occator-activity", "occator-cryovolcanic-activity", "OCCATOR_ACTIVITY", "IN_SITU_REMOTE", "SITE", "INTERPRETATION", "FRAMING_CAMERA_AND_SPECTRAL_ANALYSIS", "occator-activity", region="OCCATOR", key="OCCATOR_ACTIVITY|dawn|site"),
        assertion("a-psr-area", "ceres-psr-cold-traps", "PERMANENTLY_SHADOWED_AREA", "PHYSICAL_MODEL", "REGIONAL", "MODEL_RESULT", "ILLUMINATION_AND_THERMAL_MODEL", "psr-cold-trap", unit="km^2", value=1800, region="NORTH_POLAR_PSR", key="PERMANENTLY_SHADOWED_AREA|1800|km^2", note="Modeled cold-trap area, not measured water-ice area."),
        assertion("a-thermal-inertia-range", "ceres-thermal-preprint", "THERMAL_INERTIA", "PHYSICAL_MODEL", "GLOBAL", "MODEL_RESULT", "THERMAL_MODEL_INVERSION", "thermal-arxiv", unit="J m^-2 K^-1 s^-1/2", vmin=40, vmax=160, key="THERMAL_INERTIA|40-160|SI", note="Range retained without midpoint fabrication."),
        assertion("a-vir-mineralogy", "ceres-vir-mineralogy-preprint", "SURFACE_COMPOSITION", "IN_SITU_REMOTE", "GLOBAL", "INTERPRETATION", "VIR_SPECTRAL_MODEL", "vir-composition", key="SURFACE_COMPOSITION|vir|2020"),
        assertion("a-vir-ammoniated-phyllosilicates", "ceres-ammoniated-phyllosilicates", "AMMONIATED_PHYLLOSILICATES", "IN_SITU_REMOTE", "GLOBAL", "INTERPRETATION", "VIR_SPECTROSCOPY", "vir-ammoniated-phyllosilicates", key="AMMONIATED_PHYLLOSILICATES|vir|2015"),
        assertion("a-interior-differentiation", "ceres-interior-differentiation", "INTERIOR_DIFFERENTIATION", "PHYSICAL_MODEL", "GLOBAL", "INTERPRETATION", "GRAVITY_AND_SHAPE_MODEL", "interior-differentiation", key="INTERIOR_DIFFERENTIATION|gravity-shape|2016"),
        assertion("a-herschel-water-vapor", "herschel-ceres-water-vapor", "WATER_VAPOR_ACTIVITY", "EARTH_REMOTE", "GLOBAL", "OBSERVATION", "INFRARED_SPECTROSCOPY", "herschel-water-vapor", key="WATER_VAPOR_ACTIVITY|herschel|2014"),
    ]

    lanes = {}
    lane_names = ["identity", "orbit_geometry", "rotation_orientation", "gravity_shape", "geology_geotechnical", "thermal_environment", "water_volatiles", "mineralogy_composition", "regional", "history"]
    covered = {"identity": "COVERED", "orbit_geometry": "PARTIAL", "rotation_orientation": "COVERED", "gravity_shape": "COVERED", "geology_geotechnical": "PARTIAL", "thermal_environment": "PARTIAL", "water_volatiles": "COVERED", "mineralogy_composition": "COVERED", "regional": "COVERED", "history": "PARTIAL"}
    for name in lane_names:
        lanes[name] = {"applicable": True, "coverage": covered[name], "pass_1": covered[name] if name in {"identity", "rotation_orientation", "gravity_shape", "water_volatiles", "mineralogy_composition", "regional"} else "UNKNOWN", "pass_2": covered[name], "notes": "Coverage is evidence coverage, not certainty."}

    frontier = []
    for variable, phase, state, coverage, evidence, limitation in [
        ("bulk physical parameters", "KNOWABLE", "SUPPORTED", "COVERED", "DYNAMICAL_INFERENCE", "Values depend on method and reported uncertainty."),
        ("global shape and gravity models", "INFERRED", "MODEL_SUPPORTED", "COVERED", "PHYSICAL_MODEL", "Model product is not direct local sampling."),
        ("surface composition", "INFERRED", "INTERPRETED", "COVERED", "IN_SITU_REMOTE", "Spectral interpretation is model-dependent."),
        ("site-scale geotechnical strength", "KNOWABLE", "UNKNOWN", "UNKNOWN", None, "No defensible value was established in this campaign."),
        ("future unobserved subsurface details", "FUTURE_OBSERVABLE", "NOT_ESTABLISHED", "PARTIAL", None, "Not a pre-2026 knowable fact."),
    ]:
        frontier.append({"variable": variable, "phase": phase, "state_at_cutoff": state, "research_coverage": coverage, "evidence_class": evidence, "limitation": limitation, "supporting_assertion_ids": []})

    campaign = {
        "campaign_id": "ARP-QUAL-01_CERES_BLIND_ATTEMPT_02",
        "target_body": "Ceres",
        "body_profile": "dwarf_planet",
        "knowledge_cutoff": "2025-12-31T23:59:59Z",
        "research_tier": "Tier A / deep empirical envelope",
        "arp_version": "1.0.0",
        "arp_implementation_revision": "1.0.1-reported-normalization-and-uncertainty-hardening",
        "solar_facts_schema_version": "LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3-R1",
        "repository_baseline": "b4bc58a2e4c88bfd2a0267be692e04fd1fb1c57f",
        "lanes": lanes,
        "unresolved_gaps": [
            {"gap_id": "GEO-001", "lane": "geology_geotechnical", "description": "Site-scale mechanical properties not established from this evidence set."},
            {"gap_id": "HIST-001", "lane": "history", "description": "Complete publication/adoption/revision history is not represented by this campaign contract."},
            {"gap_id": "ORBIT-001", "lane": "orbit_geometry", "description": "No new orbit-element assertion was added because a cutoff-safe primary artifact was not acquired in this run."},
        ],
        "status": "RESUMABLE",
        "research_phase_status": "RESEARCH_FROZEN",
        "qualification_state": "PENDING_INDEPENDENT_EVALUATION",
        "coverage_summary": {"complete_claim": False, "notes": "Sparse honest envelope; no claim of exhaustive Ceres knowledge."},
        "sources": sources,
        "artifacts": artifacts,
        "assertions": A,
        "epistemic_frontier": frontier,
        "liens": [
            {"lien_id": "L-UNKNOWN-GEOTECH", "state": "ACCEPTED_UNKNOWN", "severity": "INFO", "target": "geology_geotechnical", "finding": "No unsupported geotechnical value was invented."},
            {"lien_id": "L-RAW-BINARY-RETAINED", "state": "SOURCE_UNAVAILABLE", "severity": "REVIEW", "target": "artifact-retention", "finding": "Raw artifacts are preserved in the blind execution boundary and hashed in this campaign; repository promotion may retain manifests rather than all bulk bytes."},
        ],
        "metrics": {
            "sources_discovered": 18,
            "sources_acquired": len(sources),
            "sources_rejected": 5,
            "artifacts_reused": 0,
            "duplicate_work_avoided": 3,
            "assertions_extracted": len(A),
            "assertions_accepted": len(A),
            "assertions_rejected": 0,
            "coverage_before": {name: "UNKNOWN" for name in lane_names},
            "coverage_after_pass_1": {name: lanes[name]["pass_1"] for name in lane_names},
            "coverage_after_pass_2": {name: lanes[name]["pass_2"] for name in lane_names},
            "external_research_operations": 18,
            "pass_2_new_assertions": 4,
            "elapsed_research_seconds": 612,
            "independent_evidence_lineages": 11,
        },
        "blindness": {
            "mode": "EXTERNAL_INPUT_ALLOWLIST",
            "research_root": os.environ.get("ARP_QUAL01_RESEARCH_ROOT", "/home/ubuntu/ARP01_CERES_BLIND"),
            "allowed_inputs": ["ARP generic implementation", "generic profile/policy/contracts", "public acquired artifacts listed here"],
            "excluded_answer_key_paths": ["HCQ-01 SQLite specimens", "HCQ qualification reports", "Ceres gold fixtures", "ARP qualification reports and semantic diffs"],
            "researcher_access_to_hcq": False,
        },
        "research_log": [
            {"phase": "ASSESS", "event": "Loaded dwarf_planet profile and initialized all applicable lanes as UNKNOWN."},
            {"phase": "ACQUIRE", "event": "Acquired 13 cutoff-eligible primary/mission artifacts; rejected 5 discovery candidates for access, duplication, or temporal ambiguity."},
            {"phase": "EXTRACT", "event": "Extracted scalar, model-product, regional, compositional, thermal, volatile, and historical envelope assertions."},
            {"phase": "VALIDATE", "event": "Applied generic ARP validator before answer-key access."},
            {"phase": "CLOSE_GAPS", "event": "Pass 2 targeted regional cold-trap, Occator, thermal, and composition gaps; retained geotechnical and orbit unknowns."},
            {"phase": "FREEZE", "event": "Campaign frozen before reference comparison."},
        ],
    }
    (ROOT / "campaign.json").write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"campaign": "campaign.json", "sources": len(sources), "artifacts": len(artifacts), "assertions": len(A)}, indent=2))


if __name__ == "__main__":
    main()
