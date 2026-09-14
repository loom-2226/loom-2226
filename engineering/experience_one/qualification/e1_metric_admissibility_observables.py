#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 Geometric Admissibility observables.

This module exposes gravitational field scalars that are derivable from an
authoritative body GM and diagnostic radii. They are observations only. They do
not define metric admissibility, choose a collapse radius, or mutate
Navigator/campaign state.
"""

import json
import math
import sqlite3
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "data" / "LOOM_2226.sqlite3"

# Diagnostic anchors only. The first is the earned NAV-V1-A Neptune collapse
# radius from PR #128. The final three are the already-tested Hill/SOI family.
# None is adopted metric-domain policy.
PROFILE_RADII_KM = (
    26085.768742219727,
    100_000.0,
    1_000_000.0,
    10_000_000.0,
    27_457_396.839818828,
    57_519_511.05214582,
    86_654_926.48282048,
    115_039_022.10429163,
)


def gravitational_observables(*, mu_km3_s2: float, radius_km: float) -> dict[str, float | str]:
    mu = float(mu_km3_s2)
    radius = float(radius_km)
    if not math.isfinite(mu) or mu <= 0.0:
        raise ValueError("mu_km3_s2 must be finite and positive")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius_km must be finite and positive")
    return {
        "mu_km3_s2": mu,
        "radius_km": radius,
        "acceleration_km_s2": mu / (radius * radius),
        "tidal_scale_s2": mu / (radius * radius * radius),
        "classification": "DIAGNOSTIC_OBSERVABLES_ONLY_NOT_ADMISSIBILITY_POLICY",
    }


def radial_profile(*, mu_km3_s2: float, radii_km: tuple[float, ...]) -> list[dict[str, float | str]]:
    return [gravitational_observables(mu_km3_s2=mu_km3_s2, radius_km=r) for r in radii_km]


def authoritative_gm(db_path: Path, entity_candidates: tuple[str, ...] = ("NEPTUNE", "NEPTUNE_SYSTEM", "NE")) -> dict[str, Any]:
    path = Path(db_path).resolve()
    if not path.is_file():
        raise RuntimeError(f"LOOM celestial database not found: {path}")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        for entity_id in entity_candidates:
            row = conn.execute(
                "SELECT entity_id,gm_km3_s2,source_id,status FROM celestial_properties WHERE entity_id=? AND gm_km3_s2 IS NOT NULL",
                (entity_id,),
            ).fetchone()
            if row is not None:
                return {
                    "entity_id": row["entity_id"],
                    "gm_km3_s2": float(row["gm_km3_s2"]),
                    "source": f"celestial_properties:{row['source_id'] or ''}:{row['status']}",
                }
            row = conn.execute(
                "SELECT entity_id,gm_km3_s2,source,metadata_status FROM celestial_dynamics WHERE entity_id=? AND gm_km3_s2 IS NOT NULL",
                (entity_id,),
            ).fetchone()
            if row is not None:
                return {
                    "entity_id": row["entity_id"],
                    "gm_km3_s2": float(row["gm_km3_s2"]),
                    "source": f"celestial_dynamics:{row['source']}:{row['metadata_status']}",
                }
    finally:
        conn.close()
    raise RuntimeError(f"no authoritative GM found for candidates {entity_candidates}")


def diagnostic_report(*, collapse_radius_km: float, db_path: Path = DB_PATH) -> dict[str, Any]:
    gm = authoritative_gm(db_path)
    obs = gravitational_observables(mu_km3_s2=gm["gm_km3_s2"], radius_km=collapse_radius_km)
    profile = radial_profile(mu_km3_s2=gm["gm_km3_s2"], radii_km=PROFILE_RADII_KM)
    return {
        "schema": "LOOM_E1_METRIC_ADMISSIBILITY_OBSERVABLES_V2",
        "status": "PASS",
        "body": gm["entity_id"],
        "gm_source": gm["source"],
        "observables_at_earned_collapse": obs,
        "radial_profile": profile,
        "profile_note": "SMOOTH_NEWTONIAN_GRAVITY_DIAGNOSTIC_ONLY_NO_REGIME_BOUNDARY_INFERRED",
        "authority_note": "READ_ONLY_DIAGNOSTIC_NO_THRESHOLD_NO_METRIC_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "interpretation": "MEASUREMENT_ONLY_DO_NOT_CLASSIFY_ADMISSIBLE_OR_INADMISSIBLE",
    }


def main() -> int:
    collapse_radius_km = PROFILE_RADII_KM[0]
    print(json.dumps(diagnostic_report(collapse_radius_km=collapse_radius_km), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
