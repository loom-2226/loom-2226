# SF-PROMOTE-02 — Ceres + 67P cross-body promotion qualification

Result: **SF_CROSS_BODY_PROMOTION_PASS_WITH_LIENS**

This is a factual/evidentiary promotion qualification only. No new Ceres or 67P research, preferred facts, Phase 4/5 state, resource judgment, or canonical promotion was performed.

## Verified inputs and output

- Live main baseline: `efb014992f19784a9d48030d0c76469bb5b4325c`
- Qualified 67P input SHA-256: `0c4da54dc8f48cd2041ce75aefcea36f5e0d3436c3ceeacf8c0a330d2f5c5e95`
- Frozen Ceres HCQ SHA-256: `0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`
- Output: `/tmp/loom-sf-promote-02/dev/solar_facts_multi_body/sf_promote_02_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_02_CERES_67P.sqlite3`
- Output SHA-256: `ed930b0453ec994712614bf0beb1a5ff8c93452db1b753884539fa510184b64f`
- Whole-database semantic digest: `2328f03f45b560c127a2c93b3aac0cf484f82e439979e16586eeaea12d845bd0`
- Pre-Ceres 67P body digest: `9e4139deb7182ce4c87176bc27e3510ffb075421e34cbca7bdb5a2a700ad9525`
- Post-Ceres 67P body digest: `9e4139deb7182ce4c87176bc27e3510ffb075421e34cbca7bdb5a2a700ad9525` — **PASS**
- Ceres body digest: `2c6ac5e1c6841122eb9b0b6ab27330eaf7f806b1ad9083e6b7c42860ee79e067`

## Counts

```json
{
  "67P": {
    "activity_facts": 2,
    "artifacts/provenance": 9,
    "assertions": 13,
    "body": 1,
    "body_model_products": 1,
    "derived_quantities": 0,
    "facts": 4,
    "frontier_gap_records": 8,
    "gravity_models": 0,
    "material_evidence": 0,
    "observations": 4,
    "orientation_models": 0,
    "preferred_facts": 0,
    "promotion_dispositions": 13,
    "region_model_products": 0,
    "regions": 0,
    "sources": 9,
    "structured_derivation_inputs": 0
  },
  "CERES": {
    "activity_facts": 2,
    "artifacts/provenance": 1,
    "assertions": 56,
    "body": 1,
    "body_model_products": 9,
    "derived_quantities": 1,
    "facts": 8,
    "frontier_gap_records": 0,
    "gravity_models": 1,
    "material_evidence": 6,
    "observations": 8,
    "orientation_models": 1,
    "preferred_facts": 0,
    "promotion_dispositions": 56,
    "region_model_products": 3,
    "regions": 5,
    "sources": 17,
    "structured_derivation_inputs": 1
  },
  "TOTAL": {
    "activity_fact": 4,
    "body": 2,
    "body_model_product": 10,
    "body_region": 5,
    "derived_input": 1,
    "derived_quantity": 1,
    "epistemic_frontier": 8,
    "fact": 12,
    "gravity_model": 1,
    "material_evidence": 6,
    "observation": 12,
    "orientation_model": 1,
    "preferred_fact": 0,
    "promotion_assertion": 69,
    "promotion_review": 69,
    "region_model_product": 3,
    "source": 26,
    "source_artifact": 10
  }
}
```

Ceres has 16 scientific source rows plus one explicit frozen-container provenance carrier; this asymmetry is preserved rather than fabricated into 67P. The Ceres HCQ schema has no native frontier table; its explicit UNKNOWN states remain in typed evidence and the raw promotion envelope. 67P retains its eight frontier records.

## Semantic and hostile qualification

- Ceres ↔ HCQ: **SEMANTICALLY_EQUIVALENT**; no semantic drift or error.
- All Ceres ledger objects have explicit `PROMOTE` dispositions (56); no evidence was silently dropped.
- Hostile review: **PASS** across body/source/region/derivation/temporal/provenance/range/uncertainty/model/interpretation/candidate/UNKNOWN boundaries.
- Replay: **PASS**; same frozen inputs reproduce deterministically.
- Insertion order: **PASS**; reverse insertion reconstruction is semantically equivalent.
- Narrator: **PASS**; body-neutral narrative emits supported predicates only.
- Preferred facts: 67P `0`, Ceres `0`, total `0`.

## Liens

1. `SCHEMA_LIEN`: the existing generic ordinary tables do not carry every HCQ field; the complete frozen row envelope is retained in the generic promotion ledger.
2. `PROVENANCE_LIEN`: Ceres has a frozen-container artifact carrier and 16 scientific sources; provenance symmetry with 67P is not invented.
3. `FRONTIER_LIEN`: Ceres HCQ expresses explicit unknowns in typed records rather than a native frontier table.

These liens do not undermine the core two-body factory, body isolation, or semantic equivalence. No Europa work was started. Europa readiness: **READY_FOR_ARP_QUAL_02_EUROPA**.
