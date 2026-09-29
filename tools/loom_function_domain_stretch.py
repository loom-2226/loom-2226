import csv
import json
import math
import os
import time
from pathlib import Path

from src.loom_solar_inspector import Inspector
from src.loom_solar_function_compile import compile_adaptive
from src.loom_solar_state_runtime import PiecewiseStateFunction
from src.loom_solar_temporal_publish import DAY, center_for, tolerance


OUT = Path("/tmp/loom_function_domain_stretch")
OUT.mkdir(parents=True, exist_ok=True)

JSONL = OUT / "results.jsonl"
CSV = OUT / "results.csv"
SUMMARY = OUT / "summary.json"

I = Inspector.connect(
    "loom_dev",
    "/home/ubuntu/loom_solar_assets",
)

start = I.time.parse("2226-01-01T00:00:00 TDB")

spans_days = [
    1, 2, 4, 8, 16,
    32, 64, 128, 256, 365
]

fractions = [
    0.031,
    0.117,
    0.239,
    0.417,
    0.583,
    0.731,
    0.913,
    0.977,
]


def persist(row):
    """Persist one result immediately."""

    with JSONL.open("a") as f:
        f.write(
            json.dumps(
                row,
                sort_keys=True,
            )
            + "\n"
        )
        f.flush()
        os.fsync(f.fileno())

    new_csv = not CSV.exists()

    with CSV.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "body_id",
                "center_id",
                "span_days",
                "status",
                "segments",
                "avg_days_per_function",
                "tolerance_km",
                "worst_error_km",
                "elapsed_s",
                "reason",
            ],
        )

        if new_csv:
            writer.writeheader()

        writer.writerow(
            {
                key: row.get(key)
                for key in writer.fieldnames
            }
        )

        f.flush()
        os.fsync(f.fileno())


# Resume support.
completed = set()

if JSONL.exists():
    for line in JSONL.read_text().splitlines():
        if not line.strip():
            continue

        row = json.loads(line)

        completed.add(
            (
                row["body_id"],
                row["span_days"],
            )
        )


resolved = []

for body in sorted(I.bodies):
    center = center_for(I, body)

    r = I.at(
        body,
        start,
        center,
    )

    if r.get("resolution") == "RESOLVED":
        resolved.append(body)


print(
    "LOOM FUNCTION DOMAIN STRETCH TEST",
    flush=True,
)
print(
    f"Resolved objects: {len(resolved)}",
    flush=True,
)
print(
    f"Output: {OUT}",
    flush=True,
)
print(
    f"Already completed: {len(completed)}",
    flush=True,
)
print("=" * 100, flush=True)


run_started = time.time()

for number, body in enumerate(resolved, 1):

    center = center_for(I, body)
    tol = tolerance(I, body)

    print(
        f"\n[{number:3d}/{len(resolved):3d}] "
        f"{body}",
        flush=True,
    )

    stop_body = False

    for days in spans_days:

        key = (body, days)

        if key in completed:
            print(
                f"    {days:4d} d  "
                f"SKIP  already persisted",
                flush=True,
            )
            continue

        if stop_body:
            break

        end = start + days * DAY
        begun = time.time()

        row = {
            "body_id": body,
            "center_id": center,
            "span_days": days,
            "status": None,
            "segments": None,
            "avg_days_per_function": None,
            "tolerance_km": tol,
            "worst_error_km": None,
            "elapsed_s": None,
            "reason": None,
        }

        try:
            rend = I.at(
                body,
                end,
                center,
            )

            if rend.get("resolution") != "RESOLVED":

                row["status"] = "COVERAGE_STOP"
                row["reason"] = (
                    rend.get("reason")
                    or "governed state unresolved"
                )
                row["elapsed_s"] = (
                    time.time() - begun
                )

                persist(row)

                print(
                    f"    {days:4d} d  "
                    f"COVERAGE_STOP  "
                    f"{row['reason']}",
                    flush=True,
                )

                stop_body = True
                continue

            compiled = compile_adaptive(
                I,
                body,
                center,
                start,
                end,
                tol,
            )

            representations = {
                segment["representation"]
                for segment
                in compiled["segments"]
            }

            if representations != {
                "CHEBYSHEV_STATE_SEGMENT"
            }:
                raise RuntimeError(
                    "unexpected representations "
                    f"{representations}"
                )

            f = PiecewiseStateFunction(
                compiled
            )

            worst = 0.0

            for fraction in fractions:

                t = (
                    start
                    + fraction
                    * (end - start)
                )

                predicted = f.state(t)

                truth = I.at(
                    body,
                    t,
                    center,
                )

                if (
                    truth.get("resolution")
                    != "RESOLVED"
                ):
                    raise RuntimeError(
                        "governed truth unresolved "
                        "inside interval at "
                        f"fraction {fraction}"
                    )

                actual = truth[
                    "relative"
                ]["position_km"]

                error = math.dist(
                    predicted.position_km,
                    actual,
                )

                worst = max(
                    worst,
                    error,
                )

            if worst > tol:
                raise RuntimeError(
                    f"independent error "
                    f"{worst:.6f} km "
                    f"> tolerance "
                    f"{tol:.6f} km"
                )

            segments = len(
                compiled["segments"]
            )

            row.update(
                {
                    "status": "PASS",
                    "segments": segments,
                    "avg_days_per_function":
                        days / segments,
                    "worst_error_km": worst,
                    "elapsed_s":
                        time.time() - begun,
                }
            )

            persist(row)

            print(
                f"    {days:4d} d  "
                f"PASS  "
                f"segments={segments:4d}  "
                f"avg={days/segments:9.3f} d  "
                f"worst={worst:12.6f} km  "
                f"t={row['elapsed_s']:7.2f}s",
                flush=True,
            )

        except Exception as exc:

            row.update(
                {
                    "status": "FAIL",
                    "elapsed_s":
                        time.time() - begun,
                    "reason": str(exc),
                }
            )

            persist(row)

            print(
                f"    {days:4d} d  "
                f"FAIL  "
                f"{exc}",
                flush=True,
            )

            stop_body = True


# Build persistent final summary from JSONL.

rows = [
    json.loads(line)
    for line
    in JSONL.read_text().splitlines()
    if line.strip()
]

summary = {
    "schema":
        "loom.solar-function-domain-stretch/0.1",
    "start_et": start,
    "resolved_objects": len(resolved),
    "spans_days": spans_days,
    "result_count": len(rows),
    "pass_count": sum(
        r["status"] == "PASS"
        for r in rows
    ),
    "failure_count": sum(
        r["status"] == "FAIL"
        for r in rows
    ),
    "coverage_stop_count": sum(
        r["status"] == "COVERAGE_STOP"
        for r in rows
    ),
    "runtime_s": time.time() - run_started,
}

tmp = SUMMARY.with_suffix(".json.tmp")

tmp.write_text(
    json.dumps(
        summary,
        indent=2,
        sort_keys=True,
    )
)

os.replace(
    tmp,
    SUMMARY,
)

print()
print("=" * 100)
print("FUNCTION DOMAIN STRETCH TEST COMPLETE")
print(
    json.dumps(
        summary,
        indent=2,
        sort_keys=True,
    )
)
print()
print(f"JSONL:   {JSONL}")
print(f"CSV:     {CSV}")
print(f"SUMMARY: {SUMMARY}")
