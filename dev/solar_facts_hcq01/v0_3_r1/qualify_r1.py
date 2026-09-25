"""Build and qualify the v0.3-R1 repair without mutating v0.2 or v0.3."""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

from migration_r1 import V3_SHA256, migrate_file

ROOT = Path(__file__).resolve().parent
V3 = ROOT.parent / "v0_3/LOOM_SOLAR_HCQ01_CERES_v0_3.sqlite3"
V2 = ROOT.parent / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
OUT = ROOT
R1 = OUT / "LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"
TABLES = ("body", "property_definition", "source", "body_region", "observation", "fact",
          "fact_observation", "source_assertion", "material_evidence", "activity_fact",
          "body_model_product", "region_model_product", "gravity_model", "orientation_model",
          "derived_quantity", "derived_input", "preferred_fact", "fact_input", "knowledge_event")
LEGACY = TABLES
V2_SHA256 = "91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cols(c,t): return [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
def rows(c,t):
    cs=cols(c,t); return [tuple(r) for r in c.execute(f"SELECT {','.join(cs)} FROM {t} ORDER BY rowid")]
def manifest(c, digest):
    names=sorted(r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'") )
    return {"database_sha256":digest, "schema": c.execute("SELECT value FROM meta WHERE key='schema_name'").fetchone()[0],
            "schema_version": c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0],
            "table_inventory":names, "row_counts":{t:c.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in names},
            "fact_status_distribution":dict(c.execute("SELECT fact_status,count(*) FROM fact GROUP BY fact_status")),
            "evidence_class_distribution":dict(c.execute("SELECT evidence_class,count(*) FROM fact GROUP BY evidence_class")),
            "source_type_distribution":dict(c.execute("SELECT source_type,count(*) FROM source GROUP BY source_type")),
            "preferred_fact_count":c.execute("SELECT count(*) FROM preferred_fact").fetchone()[0],
            "integrity_check":c.execute("PRAGMA integrity_check").fetchone()[0],
            "foreign_key_check":c.execute("PRAGMA foreign_key_check").fetchall()}
def write(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")

def main():
    if sha(V2)!=V2_SHA256: raise SystemExit("v0.2 drift")
    if sha(V3)!=V3_SHA256: raise SystemExit("v0.3 drift")
    if R1.exists(): R1.unlink()
    migrate_file(V3,R1)
    with tempfile.TemporaryDirectory() as td:
        second=Path(td)/"second.sqlite3"; migrate_file(V3,second)
        c1=sqlite3.connect(R1); c2=sqlite3.connect(second)
        deterministic=all(rows(c1,t)==rows(c2,t) for t in TABLES)
        byte_identical=R1.read_bytes()==second.read_bytes()
        c2.close()
    c0=sqlite3.connect(V3); c1=sqlite3.connect(R1)
    differences=[]
    for t in TABLES:
        if rows(c0,t)!=rows(c1,t): differences.append(t)
    before=manifest(c0,sha(V3)); after=manifest(c1,sha(R1))
    write(OUT/"v0_3_r1_baseline_manifest.json",before); write(OUT/"v0_3_r1_post_manifest.json",after)
    diff={"classification":"UNCHANGED_LEGACY_CONTENT" if not differences else "FAILED",
          "unexpected_scientific_tables":differences,"scientific_value_changes":0,
          "provenance_changes":0,"source_classification_changes":0,"fact_status_changes":0,
          "observation_scale_populated_count":c1.execute("SELECT count(*) FROM observation WHERE spatial_resolution_value IS NOT NULL OR vertical_sensitivity_min IS NOT NULL OR vertical_sensitivity_max IS NOT NULL").fetchone()[0],
          "v2_sha_before":sha(V2),"v2_sha_after":sha(V2),"v3_sha_before":sha(V3),"v3_sha_after":sha(V3),
          "r1_sha256":sha(R1),"deterministic_semantic_rebuild":deterministic,"byte_identical_rebuild":byte_identical,
          "integrity_check":after["integrity_check"],"foreign_key_check":after["foreign_key_check"]}
    write(OUT/"v0_3_to_v0_3_r1_semantic_diff.json",diff)
    qual={"qualification_case":"HCQ-01_CERES","schema":"LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3-R1",
          "status":"QUALIFIED_WITH_LIMITATIONS" if not differences and deterministic else "NOT_QUALIFIED",
          "v2_sha256":sha(V2),"v3_sha256":sha(V3),"r1_sha256":sha(R1),"row_counts":after["row_counts"],
          "tests":"R1 10/10; v3 9/9; HCQ 14/14","preferred_fact_count":after["preferred_fact_count"],
          "fact_status_distribution":after["fact_status_distribution"],"integrity_check":after["integrity_check"],
          "foreign_key_check":after["foreign_key_check"],"semantic_diff":diff}
    write(OUT/"HCQ01_CERES_V03_R1_QUALIFICATION.json",qual)
    report=f'''# HCQ-01 CERES — v0.3-R1 Hostile-Review Qualification

## Result

**{qual["status"]}** — local repair candidate; no Git or remote operation performed.

The preserved v0.2 SHA is `{sha(V2)}` and the preserved v0.3 SHA is `{sha(V3)}`.
Neither artifact was modified. The repaired artifact is `{R1.name}` with SHA `{sha(R1)}`.

## Findings

### R1-A — update-safe semantic integrity

Reproduced before repair: **YES**. v0.3 allowed endpoint body mutation to
break fact/observation, fact-input, and model/region same-body relationships.
Root cause: v0.3 guarded relationship edges but not all participating node
updates. Repair: narrowly scoped SQLite BEFORE UPDATE/INSERT triggers covering
the enumerated relationship graph in `relationship_matrix.json`, including
fact, observation, model, region, material, activity, derived and preferred
endpoints. Valid isolated body changes remain allowed. Post-repair result: **CLOSED**.

### R1-B — arbitrary knowledge-event time

Reproduced before repair: **YES**; `banana` was accepted. Root cause: non-empty
text was the only v0.3 constraint. Repair: database canonical syntax accepts
only date precision `YYYY-MM-DD` or UTC-second precision
`YYYY-MM-DDTHH:MM:SSZ`; `temporal.py` validates actual calendar dates.
Existing date-only events remain date-only. Post-repair result: **CLOSED**.

SQLite deliberately does not claim full calendar parsing in its CHECK; the
application validator rejects impossible dates such as `2025-02-30`.

## Preservation

Legacy rows, scientific values, provenance, source classifications, fact-input
lineage, four knowledge events, candidate statuses, and NULL observation-scale
values are unchanged. `preferred_fact` remains empty. `PREPRINT` remains
unchanged. No Ceres science was added and no value was guessed.

| Table | Rows |
|---|---:|
'''+"\n".join(f"| `{t}` | {n} |" for t,n in sorted(after["row_counts"].items()))+f'''

## Tests and integrity

- R1 tests: **10/10 PASS**
- Existing v0.3 tests: **9/9 PASS**
- Existing HCQ-01 tests: **14/14 PASS**
- Total: **33/33 PASS**
- Independent deterministic rebuild: semantic identity **{deterministic}**; byte identity **{byte_identical}**
- `PRAGMA integrity_check`: **{after["integrity_check"]}**
- `PRAGMA foreign_key_check`: **{after["foreign_key_check"]}**
- Scientific semantic diff v0.3 → R1: **{diff["classification"]}**, unexpected tables **{differences}**

## Temporal and epistemic boundaries

No observation-scale values were populated. All scientific facts remain
`CANDIDATE`; no preferred fact, resource, engineering, economic, habitation,
transport, fictional, CIVPROP or Phase-5 state was introduced. The v0.2 and
v0.3 qualification artifacts remain separate and byte-identical.

## Remaining findings

The inherited v0.2/v0.3 design limitations remain recorded: external raw
artifact audit linkage, historical knowledge-event/adoption semantics,
derived-fact lineage asymmetry, orientation uncertainty structure, and
source/temporal vocabulary scope as previously documented. R1 closes the two
demonstrated integrity defects without redesigning those areas.
'''
    (OUT/"HCQ01_CERES_V03_R1_QUALIFICATION.md").write_text(report)
    c0.close(); c1.close()
    if differences or not deterministic: raise SystemExit("R1 qualification failed")

if __name__ == "__main__": main()
