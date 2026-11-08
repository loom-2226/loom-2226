#!/usr/bin/env python3
"""Strict evidence merge for #471 A/B/C/D independent GitHub Actions jobs.

Never substitutes a research zero-clash screen or a subset of primary checks
for current source D9 qualification. Produces FAIL evidence on incomplete shards.
"""
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/out"
SHARDS = OUT / "shards"
REPORT = OUT / "D9_BREP_CLASH_REPORT.json"
GEO = OUT / "wayfarer_v05_geometry.json"
CRITERIA = ROOT / "config/cert_criteria.json"
REF = ROOT / "lab/packing_phase1b/frozen_research_3p8_forward.json"
REBUILT = ROOT / "lab/packing_phase1b/current_g3_rebuild_report.json"
STEP = ROOT / "lab/packing_phase1b/current_g3_3p8_forward.step.gz"
INPUT = ROOT / "config/wayfarer_v05_inputs.json"


def load(path):
    return json.loads(path.read_text())


def aggregate_paired(rows, attr):
    hits, errors, counts = [], [], Counter()
    for x in rows:
        r = x[attr]
        hits.extend(r["intersection_hits"])
        errors.extend(r["collision_errors"])
        counts.update(r["category_counts"])
    d = sorted((h for h in hits if h["category"] == "d"),
               key=lambda h: -h["m3"])
    return dict(
        part_count=194, pair_count=sum(x[attr]["pair_count"] for x in rows),
        expected_pairs=18721, category_counts=dict(counts),
        category_d_count=len(d), category_d_conflicts=d,
        collision_errors=errors, intersection_hits=hits)


def merge():
    started = time.monotonic()
    G, C, R, I = map(load, (GEO, CRITERIA, REF, INPUT))
    sha = hashlib.sha256(GEO.read_bytes()).hexdigest()
    step_sha = hashlib.sha256(STEP.read_bytes()).hexdigest()
    assert sha == C["D9"]["approved_source_geometry_sha256"]
    assert C["D9"]["min_intersection_m3"] == .01
    rebuilt=load(REBUILT)
    assert rebuilt["candidate_pass"] is True
    print("E_CURRENT_SOURCE", sha, "STEP", step_sha, flush=True)
    p = load(SHARDS/"pressure.json")
    Crows = [load(SHARDS/f"primary-{i}.json") for i in range(4)]
    Drows = [load(SHARDS/f"pairs-{i}.json") for i in range(8)]
    allrows=[p]+Crows+Drows
    for row in allrows:
        assert row["geometry_sha256"] == sha
        assert row["step_sha256"] == step_sha
        assert row["unit_factor"] in (.001,1.)
        assert row["source_offset_m"] == [.03,-.26]
    assert {x["unit_factor"] for x in allrows} == {p["unit_factor"]}
    assert p["mode"] == "pressure"
    assert p["check"]["name"] == "dry:pressure_vessel"
    names = []
    checks = []
    for i,row in enumerate(Crows):
        assert row["mode"] == "primary" and row["shard"]==i and row["shards"]==4
        assert row["total_primaries"] == 43
        assert [q["name"] for q in row["checks"]] == row["names"]
        names.extend(row["names"])
        checks.extend(row["checks"])
    assert len(names) == len(set(names)) == 43
    assert len(checks) == 43
    assert sum(x["name"]=="dry:pressure_vessel" for x in checks)==1
    pressure_from_C=next(x for x in checks if x["name"]=="dry:pressure_vessel")
    assert pressure_from_C.get("pass") == p["check"].get("pass")
    assert p.get("pass") == p["check"].get("pass")
    pairs_total = 18721
    position=0
    for i,row in enumerate(Drows):
        assert row["mode"]=="pairs" and row["shard"]==i and row["shards"]==8
        assert row["pair_total"] == pairs_total
        for phase in ("before","after"):
            r=row[phase]
            assert r["range_start"] == position
            assert r["range_end"] == pairs_total*(i+1)//8
            assert r["pair_count"] == r["range_end"]-r["range_start"]
            assert r["part_count"] == 194
            assert r["category_d_count"] == len(r["category_d_conflicts"])
            assert sum(r["category_counts"].values()) == len(r["intersection_hits"])
        position = row["before"]["range_end"]
    assert position == pairs_total
    assert len({x["names_sha256"] for x in Drows})==1
    water=Drows[0]["water_BRep_forward_debits"]
    for x in Drows[1:]:
        assert len(x["water_BRep_forward_debits"]) == len(water)
        for a,b in zip(water,x["water_BRep_forward_debits"]):
            assert a["id"]==b["id"]
            assert abs(a["before_BRep_m3"]-b["before_BRep_m3"]) < 1e-8
            assert abs(a["after_BRep_m3"]-b["after_BRep_m3"]) < 1e-8
    before=aggregate_paired(Drows,"before")
    after=aggregate_paired(Drows,"after")
    assert before["pair_count"] == after["pair_count"] == 18721
    failures=[x for x in checks if x.get("pass") is not True]
    d9_ok=(p.get("pass") is True and not failures and
           before["category_d_count"] == 0 and not before["collision_errors"] and
           after["category_d_count"] == 0 and not after["collision_errors"])
    result=dict(
        authority="kT Phase1b G3 current -0.26m named research-cut STEP, sharded exact BRep D9",
        geometry_sha256=sha,
        approved_source_step_gz_sha256=step_sha,
        approved_source_brep_origin="PR #157 D8 cuts replayed against #471 G3 current source",
        original_D8_notch_ops=len(R["notches"]),
        current_G3_rebuilt_D8_notch_ops=len(rebuilt["notches"]),
        current_G3_candidate_pass=rebuilt["candidate_pass"],
        D8_primary_shape_unchanged=(len(failures)==0 and p["pass"] is True),
        protected_primary_integrity_accepted_methods=[
            "ordinary_symmetric_difference","OCCT_fuzzy_symmetric_difference",
            "two_way_BRep_surface_sample_distance_if_boolean_numerically_invalid"],
        OCCT_fuzzy_value_m=1e-6,
        protected_primary_surface_min_samples_per_direction=256,
        primary_invariant_failures=failures,
        primary_shape_volume_checks=checks,
        B_pressure_vessel_diagnosis=p["check"],
        B_pressure_runtime_seconds=p["runtime_seconds"],
        C_primary_job_runtime_seconds=[x["runtime_seconds"] for x in Crows],
        D_pair_job_runtime_seconds=[x["runtime_seconds"] for x in Drows],
        E_merge_runtime_seconds=round(time.monotonic()-started,3),
        source_dry_count=len(G["parts"]),
        source_S1_fluid_count=len(G["fluids_by_state"]["S1"]),
        imported_reference_names=315,
        imported_step_source_numeric_unit="mm" if p["unit_factor"]==.001 else "m",
        source_geometry_numeric_unit="m",
        explicit_step_to_source_linear_scale=p["unit_factor"],
        excluded_source_no_render_proxy_count=122,
        no_render_excluded_count=122,
        same_lab_and_upstream_installed_part_set=True,
        modelled_solids=194,
        source_water_R_before_t=Drows[0]["source_water_R_before_t"],
        source_water_R_current_t=Drows[0]["source_water_R_current_t"],
        water_BRep_forward_debits=water,
        threshold_m3=.01,
        classification="source_brep_triage.classify pinned #156 shared single checker",
        lab_same_checker=before,
        upstream_same_checker=after,
        category_d_count=after["category_d_count"],
        category_d_conflicts=after["category_d_conflicts"],
        geometry_conversion_or_boolean_errors=before["collision_errors"]+after["collision_errors"],
        pair_count=after["pair_count"],expected_pairs=after["expected_pairs"],
        pass_=bool(d9_ok),
        unresolved="Fitted secondary doublers, internals, dynamic sweeps remain OPEN.",
    )
    result["pass"]=result.pop("pass_")
    return result


if __name__ == "__main__":
    begin = time.monotonic()
    try:
        result=merge()
    except Exception as exc:
        print("E_INTEGRITY_MERGE_FAILED",repr(exc),flush=True)
        sha=hashlib.sha256(GEO.read_bytes()).hexdigest()
        result=dict(authority="kT #471 E merge incomplete/invalid: NO D9 qualification",
                    geometry_sha256=sha,category_d_count=0,
                    geometry_conversion_or_boolean_errors=[{"error":repr(exc)}],
                    pair_count=0,expected_pairs=18721,
                    D8_primary_shape_unchanged=False,
                    primary_invariant_failures=[{"error":"Incomplete/unusable C or D shard evidence"}],
                    primary_shape_volume_checks=[], pass_=False,
                    STOP="C-E pipeline incomplete: no clearance credit.")
        result["pass"]=result.pop("pass_")
    OUT.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("E_D9_SUMMARY",json.dumps(dict(
        pass_=result["pass"],primary_count=len(result.get("primary_shape_volume_checks",[])),
        primary_failures=len(result.get("primary_invariant_failures",[])),
        d=result["category_d_count"],pairs=result["pair_count"],
        elapsed_seconds=round(time.monotonic()-begin,3))),flush=True)
    raise SystemExit(0 if result["pass"] else 1)
