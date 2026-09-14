from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

TEXTURE_FIELDS = (
    "mobility_intensity",
    "logistics_intensity",
    "strategic_intensity",
    "activity_pressure",
    "actor_fragmentation",
    "authority_complexity",
    "control_concentration",
    "gateway_character",
    "frontier_operational_pressure",
)


def _signature(row: dict) -> tuple:
    return tuple(round(float(row[name]), 12) for name in TEXTURE_FIELDS)


def summarize_texture_rows(rows: list[dict]) -> dict:
    signatures: dict[tuple, list[str]] = defaultdict(list)
    for row in rows:
        signatures[_signature(row)].append(row["node_subject_id"])

    duplicate_groups = [
        sorted(node_ids)
        for node_ids in signatures.values()
        if len(node_ids) > 1
    ]
    duplicate_groups.sort(key=lambda group: (-len(group), group))

    workforce_ratios = [float(row["workforce_resident_ratio"]) for row in rows]
    dominant_counts = dict(sorted(Counter(row["dominant_texture"] for row in rows).items()))

    return {
        "schema": "LOOM_CIVSTATE_HEL_TEXTURE_AUDIT_V1",
        "status": "PASS",
        "scope": "NODE:HEL-%",
        "node_count": len(rows),
        "unique_texture_signature_count": len(signatures),
        "duplicate_signature_group_count": len(duplicate_groups),
        "duplicate_signature_groups": duplicate_groups,
        "dominant_texture_counts": dominant_counts,
        "workforce_resident_ratio_min": min(workforce_ratios) if workforce_ratios else None,
        "workforce_resident_ratio_max": max(workforce_ratios) if workforce_ratios else None,
        "dominant_texture_semantics": "PERCENTILE_PROMINENCE_NOT_RAW_MAXIMUM",
        "raw_value_label_contradiction_inferred": False,
        "workforce_resident_ratio_semantics": "WORKFORCE_ASSIGNED_DIVIDED_BY_RESIDENT_POPULATION",
        "interpretation_authority": "DIAGNOSTIC_ONLY_NO_DEFECT_DECLARATION",
        "mutation_authority": "ZERO",
        "canon_change_authority": "ZERO",
        "next_action": "REVIEW_DUPLICATE_TEXTURE_SIGNATURES_AND_UPSTREAM_SOURCE_DIVERSITY_BEFORE_CHANGING_MATERIALIZER_SEMANTICS",
    }


def load_hel_texture_rows(db_path: str | Path) -> list[dict]:
    connection = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        sql = """
        SELECT
            node_subject_id,
            mobility_intensity,
            logistics_intensity,
            strategic_intensity,
            activity_pressure,
            actor_fragmentation,
            authority_complexity,
            control_concentration,
            gateway_character,
            frontier_operational_pressure,
            workforce_resident_ratio,
            dominant_texture
        FROM civ_node_texture_overlay
        WHERE node_subject_id LIKE 'NODE:HEL-%'
        ORDER BY node_subject_id
        """
        return [dict(row) for row in connection.execute(sql).fetchall()]
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only CIVSTATE HEL texture audit")
    parser.add_argument(
        "--db",
        default="data/LOOM_2226_CIVSTATE.sqlite3",
        help="Path to LOOM CIVSTATE SQLite database",
    )
    args = parser.parse_args()

    rows = load_hel_texture_rows(args.db)
    if not rows:
        raise SystemExit("No NODE:HEL-% rows found in civ_node_texture_overlay")

    print(json.dumps(summarize_texture_rows(rows), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
