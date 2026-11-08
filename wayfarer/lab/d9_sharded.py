#!/usr/bin/env python3
"""Execution-only shards of #471's unmodified D9 BRep operations.

A rebuild is supplied once by an upstream artifact. This module calls exactly
the existing P.make, K.audit, D.trim_liquid_forward, and T.classify operations.
No geometry, material, predicate, tolerance or identity method changes.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import shutil
import tempfile
import time
from collections import Counter
from pathlib import Path

import d9_brep as D

P, T, K = D.P, D.T, D.K
OUT = D.ROOT / "results/out/shards"


def save(name, result):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("SHARD_RESULT", path, "pass", result.get("pass"),
          "runtime_seconds", result.get("runtime_seconds"), flush=True)


def context():
    G = json.loads(D.GEO.read_text())
    I = json.loads(D.INPUT.read_text())
    C = json.loads(D.CRITERIA.read_text())
    R = json.loads(D.REF.read_text())
    rebuilt = json.loads(D.REBUILT.read_text())
    assert rebuilt["candidate_pass"] is True
    geo_sha = hashlib.sha256(D.GEO.read_bytes()).hexdigest()
    assert geo_sha == C["D9"]["approved_source_geometry_sha256"]
    assert D.SOURCE.is_file()
    assert C["D9"]["min_intersection_m3"] == 0.01
    return G, I, C, R, rebuilt, geo_sha, hashlib.sha256(D.SOURCE.read_bytes()).hexdigest()


def imported(G):
    """The exact D9 STEP mm/m unit and TopLoc placement normalisation."""
    rows = D.catalogue(G)
    with tempfile.TemporaryDirectory(prefix="loom471cad_") as td:
        dest = Path(td) / "current.step"
        with gzip.open(D.SOURCE, "rb") as rd, dest.open("wb") as wr:
            shutil.copyfileobj(rd, wr)
        step = D.import_step(dest)
        kids = list(step.children)
        assert len(kids) == 315 and len({k.label for k in kids}) == 315
        trunk = P.make(P.settled(rows["dry:core_trunk"]["shape"]))
        raw = next(k for k in kids if k.label == "dry:core_trunk")
        unit_ratio = (P.bounds(raw)[1] - P.bounds(raw)[0]) / (
            P.bounds(trunk)[1] - P.bounds(trunk)[0])
        if abs(unit_ratio - 1000) < .01:
            factor = .001
        elif abs(unit_ratio - 1) < .001:
            factor = 1.
        else:
            raise RuntimeError(f"unexpected STEP unit ratio {unit_ratio}")
        shapes = {}
        for sh in kids:
            name = D.RENAMES.get(sh.label, sh.label)
            assert name not in shapes
            if factor != 1:
                orig = sh.location.position
                pos = (float(orig.X), float(orig.Y), float(orig.Z))
                sh = sh.scale(factor)
                after = sh.location.position
                delta = tuple(a * factor - float(b)
                              for a, b in zip(pos, (after.X, after.Y, after.Z)))
                if any(abs(a) > 1e-12 for a in delta):
                    sh = sh.translate(delta)
            sh.label = name
            shapes[name] = sh
    assert set(shapes) == set(rows) - {"dry:d8_unlocated_doubler_allowance"}
    installed = {n for n, r in rows.items() if "no_render" not in r.get("tags", [])}
    assert len(installed) == 194
    assert len(set(rows) - installed) == 122
    assert installed <= set(shapes)
    return rows, shapes, sorted(installed), factor


def primary_names(shapes):
    return sorted(n for n in shapes if n.startswith("dry:") and (
        n[4:].startswith(("frame_", "longeron_", "bay_corner_")) or
        n[4:] in ("armor", "pressure_vessel", "aft_bulkhead", "thrust_cone",
                   "core_trunk", "docking_collar", "shield", "reactor", "nozzle") or
        n[4:].startswith(("tunnel_", "rcs_A"))
    ))


def single_primary(name, rows, shapes, C):
    native = P.make(P.settled(rows[name]["shape"]))
    return K.audit(
        name, native, shapes[name],
        volume_tolerance_m3=1e-5,
        bbox_tolerance_m=C["D9"]["primary_brep_unchanged_bbox_tolerance_m"],
        symmetric_tolerance_m3=C["D9"]["primary_brep_symmetric_difference_limit_m3"],
        bounds=P.bounds,
    )


def report_common(args, start, geo_sha, step_sha, factor):
    return dict(mode=args.mode, shard=args.shard, shards=args.shards,
                geometry_sha256=geo_sha, step_sha256=step_sha,
                unit_factor=factor, source_offset_m=[.03, -.26],
                runtime_seconds=round(time.monotonic() - start, 3))


def pressure(args, start, G, C, geo_sha, step_sha):
    rows, shapes, installed, factor = imported(G)
    assert "dry:pressure_vessel" in primary_names(shapes)
    print("B_PRESSURE_VALIDITY_START", flush=True)
    try:
        result = single_primary("dry:pressure_vessel", rows, shapes, C)
    except Exception as exc:
        result = dict(name="dry:pressure_vessel", pass_=False,
                      diagnostic_error=repr(exc))
        result["pass"]=result.pop("pass_")
        print("B_PRESSURE_DIAGNOSTIC_ERROR",repr(exc),flush=True)
    report = report_common(args, start, geo_sha, step_sha, factor)
    report.update(check=result, passed=result.get("pass") is True,
                  pass_=result.get("pass") is True)
    report["pass"] = report.pop("pass_")
    save("pressure.json", report)
    print("B_PRESSURE_MEASUREMENTS", json.dumps(result), flush=True)
    return 0  # Save a negative diagnosis; final E enforces acceptance.


def primary(args, start, G, C, geo_sha, step_sha):
    rows, shapes, installed, factor = imported(G)
    names = primary_names(shapes)
    assert len(names) == 43, (len(names), names)
    chosen = names[args.shard::args.shards]
    checks = []
    for name in chosen:
        print("C_PRIMARY_START", args.shard, name, flush=True)
        try:
            check = single_primary(name, rows, shapes, C)
        except Exception as exc:
            check = dict(name=name, pass_=False,
                         diagnostic_error=repr(exc))
            check["pass"] = check.pop("pass_")
        checks.append(check)
        print("C_PRIMARY_DONE", name, "pass", check.get("pass"), flush=True)
    report = report_common(args, start, geo_sha, step_sha, factor)
    report.update(total_primaries=len(names), names=chosen, checks=checks,
                  pass_=all(x.get("pass") is True for x in checks))
    report["pass"] = report.pop("pass_")
    save(f"primary-{args.shard}.json", report)
    return 0


def pair_scan(shapes, names, start_index, end_index, threshold):
    bounds = {n: P.bounds(shapes[n]) for n in names}
    hits, errors, counts = [], [], Counter()
    index = 0
    for i, a in enumerate(names):
        for b in names[i+1:]:
            if start_index <= index < end_index:
                if P.bbox_intersection_upper(bounds[a], bounds[b]) > threshold:
                    try:
                        common = shapes[a] & shapes[b]
                        if common is not None:
                            vol = float(common.volume)
                            if vol > threshold:
                                cat, why = T.classify({"a": a, "b": b})
                                assert cat in "abcd", (a, b, cat)
                                hits.append(dict(a=a, b=b, m3=round(vol, 9),
                                                 category=cat, why=why))
                                counts[cat] += 1
                    except Exception as exc:
                        errors.append(dict(a=a, b=b, error=repr(exc)))
            index += 1
    assert index == len(names) * (len(names) - 1) // 2
    return dict(part_count=len(names), pair_count=end_index-start_index,
                range_start=start_index, range_end=end_index,
                category_counts=dict(counts), collision_errors=errors,
                intersection_hits=hits, category_d_count=counts["d"],
                category_d_conflicts=sorted(
                    (x for x in hits if x["category"] == "d"),
                    key=lambda x: -x["m3"]))


def pair(args, start, G, I, C, R, geo_sha, step_sha):
    rows, shapes, names, factor = imported(G)
    assert len(names) == 194
    total = len(names)*(len(names)-1)//2
    assert total == 18721
    lo, hi = total*args.shard//args.shards, total*(args.shard+1)//args.shards
    threshold = C["D9"]["min_intersection_m3"]
    original = {n: shapes[n] for n in names}
    print("D_PAIR_PRE_START", args.shard, lo, hi, flush=True)
    before = pair_scan(original, names, lo, hi, threshold)
    assert before["pair_count"] == hi-lo
    prior_water = R["masses"]["core_R_t"]
    actual_water = I["states"]["S1"]["remass_t"]
    assert 0 < actual_water < prior_water and abs(actual_water-245.39043171108221)<1e-7
    ratio = actual_water/prior_water
    water_debits = []
    migrated = dict(original)
    for name in names:
        if name.startswith("S1:water_"):
            old = migrated[name]
            revised = D.trim_liquid_forward(old, ratio)
            migrated[name] = revised
            water_debits.append(dict(id=name, before_BRep_m3=float(old.volume),
                                     after_BRep_m3=float(revised.volume)))
    print("D_PAIR_POST_START", args.shard, lo, hi, flush=True)
    after = pair_scan(migrated, names, lo, hi, threshold)
    report = report_common(args, start, geo_sha, step_sha, factor)
    report.update(pair_total=total, names_sha256=hashlib.sha256(
        "\n".join(names).encode()).hexdigest(), source_water_R_before_t=prior_water,
        source_water_R_current_t=actual_water, water_BRep_forward_debits=water_debits,
        before=before, after=after, pass_=(
            before["category_d_count"] == after["category_d_count"] == 0 and
            not before["collision_errors"] and not after["collision_errors"]))
    report["pass"] = report.pop("pass_")
    save(f"pairs-{args.shard}.json", report)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["pressure", "primary", "pairs"])
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    args = ap.parse_args()
    if args.mode == "primary":
        assert args.shards == 4 and 0 <= args.shard < 4
    if args.mode == "pairs":
        assert args.shards == 8 and 0 <= args.shard < 8
    start = time.monotonic()
    G,I,C,R,rebuilt,geo_sha,step_sha=context()
    print("SHARD_START",args.mode,args.shard,"geometry",geo_sha,
          "step",step_sha,flush=True)
    if args.mode == "pressure":
        return pressure(args,start,G,C,geo_sha,step_sha)
    if args.mode == "primary":
        return primary(args,start,G,C,geo_sha,step_sha)
    return pair(args,start,G,I,C,R,geo_sha,step_sha)


if __name__ == "__main__":
    raise SystemExit(main())
