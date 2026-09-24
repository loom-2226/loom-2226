"""Build the bounded 2226 demographic correction for Earth baseline v4.

Primary class: data. This does not rerun the qualified 80-economy simulation.
It selects one 2226 demographic endpoint by reconciling the recovered frozen
country allocator to current canon Earth population and WPP coverage.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V4 = ROOT / "manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24"
V4_CAND = ROOT / "manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24"
V3 = ROOT / "manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23"
CANON = ROOT / "canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md"
CIVSTATE = ROOT / "data/LOOM_2226_CIVSTATE.sqlite3"
OUT_JSON = HERE / "EARTH_2226_DEMOGRAPHIC_AUTHORITY.json"
OUT_CSV = HERE / "EARTH_2226_COUNTRY_POPULATION.csv"
OUT_MANIFEST = HERE / "CORRECTION_MANIFEST.json"
DECISION = HERE / "DEMOGRAPHIC_CORRECTION_DECISION.md"
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canon_earth_population() -> float:
    text = CANON.read_text(encoding="utf-8")
    match = re.search(r"\| Earth \| (8312538895\.\d+) \|", text)
    if not match:
        raise RuntimeError("exact canon Earth biological population not found")
    values = {float(x) for x in re.findall(r"\| Earth \| (8312538895\.\d+) \|", text)}
    if len(values) != 1:
        raise RuntimeError(f"ambiguous canon Earth population values: {values}")
    return values.pop()


def load_v21() -> tuple[dict[str, float], dict]:
    con = sqlite3.connect(f"file:{CIVSTATE}?mode=ro", uri=True)
    try:
        audit_rows = con.execute(
            "select iso3, final_population, method from civ_country_demographic_v2_1_audit "
            "where year=2226"
        ).fetchall()
        rows = {iso: population for iso, population, _ in audit_rows}
        methods = {method for _, _, method in audit_rows}
        freeze = con.execute(
            "select freeze_id, model_id, status, frozen_earth_parent_2226, "
            "country_rows_per_year, audit_rows, limitations, decision_basis "
            "from civ_demographic_model_freeze where freeze_id='FREEZE:DEMOGRAPHIC_V2_1'"
        ).fetchone()
    finally:
        con.close()
    if len(audit_rows) != 81 or len(rows) != 81 or "ROW" not in rows or freeze is None:
        raise RuntimeError("recovered v2.1 demographic allocator is incomplete")
    if methods != {"LAGGED_DEVELOPMENT_GEOMEAN_CONVERGENCE_V2_1"}:
        raise RuntimeError(f"unexpected v2.1 method set: {methods}")
    if any(value <= 0 for value in rows.values()):
        raise RuntimeError("recovered v2.1 demographic allocator contains nonpositive population")
    meta = {
        "freeze_id": freeze[0], "model_id": freeze[1], "status": freeze[2],
        "frozen_earth_parent_2226": freeze[3],
        "country_rows_per_year": freeze[4], "audit_rows": freeze[5],
        "limitations": freeze[6], "decision_basis": freeze[7],
    }
    if (meta["freeze_id"] != "FREEZE:DEMOGRAPHIC_V2_1" or
            meta["model_id"] != "DEMOGRAPHIC_ALLOCATION_V2_1" or
            meta["status"] != "FROZEN_GAMEPLAY_DEMOGRAPHIC_ALLOCATOR" or
            meta["country_rows_per_year"] != 81 or meta["audit_rows"] != 162):
        raise RuntimeError("recovered v2.1 freeze identity is not the expected production allocator")
    if abs(sum(rows.values()) - meta["frozen_earth_parent_2226"]) > 1e-3:
        raise RuntimeError("v2.1 allocation does not reconcile to its frozen parent")
    return rows, meta


def load_wpp_2100(v3_manifest: dict, demographic: set[str]) -> tuple[dict[str, float], dict[str, str], Path]:
    source = v3_manifest["sources"]["wpp_total"]
    path = Path(source["path"])
    if sha256(path) != source["sha256"]:
        raise RuntimeError("WPP total source hash mismatch")
    pop, names = {}, {}
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["Variant"] != "Medium" or row["LocTypeName"] != "Country/Area" or row["Time"] != "2100":
                continue
            iso = row["ISO3_code"]
            if iso in demographic:
                pop[iso] = float(row["TPopulation1Jan"]) * 1000.0
                names[iso] = row["Location"]
    if set(pop) != demographic:
        raise RuntimeError(f"WPP 2100 coverage mismatch: {len(pop)} != {len(demographic)}")
    return pop, names, path


def build() -> dict:
    scope = load_json(V4 / "PROMOTION_SCOPE.json")
    economic = set(scope["economic_qualification"]["iso3"])
    demographic = set(scope["identity_demography"]["iso3"])
    demographic_only = set(scope["demographic_only"]["iso3"])
    if len(economic) != 80 or len(demographic) != 237 or len(demographic_only) != 157:
        raise RuntimeError("unexpected v4 coverage partition")
    v21, v21_meta = load_v21()
    if set(v21) - {"ROW"} != economic:
        raise RuntimeError("v2.1 named-country universe differs from v4 economic 80")

    v3_manifest = load_json(V3 / "RUN_MANIFEST.json")
    pop2100, names, wpp_path = load_wpp_2100(v3_manifest, demographic)
    canon_parent = canon_earth_population()
    old_parent = v21_meta["frozen_earth_parent_2226"]
    scale = canon_parent / old_parent

    output = {iso: v21[iso] * scale for iso in economic}
    residual = v21["ROW"] * scale
    residual_wpp = sum(pop2100[iso] for iso in demographic_only)
    for iso in demographic_only:
        output[iso] = residual * pop2100[iso] / residual_wpp

    if set(output) != demographic:
        raise RuntimeError("selected country allocation coverage mismatch")
    if abs(sum(output.values()) - canon_parent) > 1e-3:
        raise RuntimeError("selected country allocation does not reconcile to canon")

    diagnostic = load_json(V4_CAND / "DEMOGRAPHIC_SENSITIVITY.json")
    old_central = diagnostic["scenarios"]["CENTRAL"]["country_population_2226"]
    ranked = sorted(output, key=lambda iso: (-output[iso], iso))
    rows = []
    for iso in sorted(output):
        rows.append({
            "iso3": iso,
            "name": names[iso],
            "allocation_class": "RECOVERED_V2_1_NAMED_80_RENORMALIZED" if iso in economic else "WPP_2100_SHARE_OF_RECOVERED_V2_1_ROW_RESIDUAL",
            "wpp_population_2100": pop2100[iso],
            "population_2226": output[iso],
            "earth_share_2226": output[iso] / canon_parent,
            "superseded_v4_diagnostic_central_population_2226": old_central[iso],
        })
    artifact = {
        "schema": "loom-earth-v4-demographic-authority-correction-v1",
        "status": "SELECTED_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION",
        "change_class": "data",
        "scope": "2226 Earth biological population endpoint only; 237 WPP Country/Area identities",
        "authority": {
            "canon_earth_biological_population_2226": canon_parent,
            "canon_source": repo_path(CANON),
            "canon_source_sha256": sha256(CANON),
            "wpp_authority_through_year": 2100,
            "cohort_detail_status": "NOT_REPROMOTED_BY_THIS_CORRECTION",
            "medical_longevity_lineage_status": "PRESERVED_AS_PROVENANCE; EXACT_AGE_FERTILITY_LONGEVITY_DETAIL_REMAINS_MODEL_SENSITIVE",
        },
        "method": {
            "id": "CANON_PARENT_X_RECOVERED_V2_1_COUNTRY_SHAPE_WITH_WPP_ROW_DISAGGREGATION",
            "recovered_allocator_source": repo_path(CIVSTATE),
            "recovered_allocator_source_sha256": sha256(CIVSTATE),
            "recovered_allocator": v21_meta,
            "renormalization_factor": scale,
            "named_80_rule": "preserve frozen v2.1 2226 country shares and renormalize to canon Earth parent",
            "demographic_only_157_rule": "allocate recovered v2.1 ROW residual by UN WPP 2024 Medium 2100 Jan-1 population share",
            "wpp_source": str(wpp_path),
            "wpp_source_sha256": sha256(wpp_path),
            "free_parameters_added": 0,
        },
        "boundaries": {
            "not_a_cohort_component_rerun": True,
            "no_selected_2101_2225_annual_trajectory": True,
            "does_not_change_qualified_80_economy_outputs": True,
            "does_not_change_canon": True,
            "does_not_select_v4_half_life_sensitivity": True,
            "replaces_for_2226_country_population_use": "v4 diagnostic half-life sensitivity only",
        },
        "checks": {
            "country_area_count": len(output),
            "economic_80_count": len(economic),
            "demographic_only_count": len(demographic_only),
            "selected_population_sum": sum(output.values()),
            "canon_parent_difference": sum(output.values()) - canon_parent,
            "minimum_country_population": min(output.values()),
            "maximum_country_population": max(output.values()),
        },
        "top_20_population_2226": [
            {"rank": n, "iso3": iso, "name": names[iso], "population": output[iso]}
            for n, iso in enumerate(ranked[:20], 1)
        ],
        "countries": rows,
    }
    return artifact


def write_outputs(artifact: dict) -> None:
    OUT_JSON.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        fields = ["iso3", "name", "allocation_class", "wpp_population_2100", "population_2226",
                  "earth_share_2226", "superseded_v4_diagnostic_central_population_2226"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(artifact["countries"])


def write_manifest() -> None:
    files = {}
    for path in (OUT_JSON, OUT_CSV, DECISION, Path(__file__).resolve()):
        files[path.name] = {
            "path": repo_path(path),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
    manifest = {
        "schema": "loom-earth-v4-demographic-correction-manifest-v1",
        "status": "ACTIVE_DATA_INTEGRATION_SUPPLEMENT",
        "target_baseline": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
        "selected_year": 2226,
        "files": files,
    }
    OUT_MANIFEST.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    result = build()
    write_outputs(result)
    write_manifest()
    print("status", result["status"])
    print("countries", result["checks"]["country_area_count"])
    print("population", result["checks"]["selected_population_sum"])
    print("top10", " ".join(row["iso3"] for row in result["top_20_population_2226"][:10]))
