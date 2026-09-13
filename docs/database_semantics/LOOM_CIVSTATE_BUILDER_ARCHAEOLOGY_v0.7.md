# LOOM CIVSTATE Builder Archaeology v0.7

**Runtime database:** `LOOM_2226_CIVSTATE.sqlite3`  
**SHA-256:** `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`

## Finding

The remaining governance/place/social/texture generator gaps are not ordinary schema-recovery problems. The authoritative runtime database identifies a Phase-13 materializer run, but the production repository history does not preserve the original Phase-13 builder source.

## Runtime provenance

### `DERIV:MATERIALIZER2226`

- Epistemic class: `MODEL_DOWNSCALED`
- Run: `RUN:MATERIALIZER2226_V0.1`
- Method: `Conserved 2226 materialization from macro, census, infrastructure role and bridge assumptions`
- Source detail: `Navigator + Phase2 macro envelope`
- Confidence: `0.62`
- Notes: `High-resolution gameplay materialization; not unique historical prediction`

### `DERIV:GAMEPLAY2226`

- Epistemic class: `GAMEPLAY_ESTIMATE`
- Run: `RUN:MATERIALIZER2226_V0.1`
- Method: `Governance/social/influence parameters constrained by role, remoteness, authority and historical assumptions`
- Source detail: `Navigator authority/economic/transport profiles + bridge assumptions`
- Confidence: `0.48`
- Notes: `LLM behavioral scaffolding and contrast testing`

### `RUN:MATERIALIZER2226_V0.1`

- Model: `LOOM 2226 CIVSTATE materializer`
- Version: `0.1`
- Status: `PHASE13_CONTRAST_PROTOTYPE`
- Boundary year: `2226`
- Source detail: `Phase 2 macro envelope + Navigator census/infrastructure + governing bridge assumptions`
- Assumptions JSON: `{"offearth_va_share": 0.15, "earth_bio_population": 6553512340, "country_economics": "coarse influence priors pending qualified 2190 NDJSON"}`

## Git-history boundary

Git history for `data/LOOM_2226_CIVSTATE.sqlite3` contains one introduction of the database:
`3cd852c15e153ff52064983ee4c71e56cb30e104` (`Add files via upload`, 2026-09-03).

The pre-governance archive tree contains the SQLite database and runtime consumers, but no recovered standalone Phase-13 materializer source. Therefore production Git history currently cannot supply the missing field-level Phase-13 equations.

This is a provenance finding, not evidence that the builder never existed.

## Recovered pre-Git historical artifacts

File-library recovery found three Phase-13-era artifacts that predate the production Git database upload:

1. `LOOM_2226_CIVSTATE_Bridging_Assumptions_v1.0.md`
   - status: GOVERNING MATERIALIZATION CANON;
   - contains A01-A20;
   - A11-A14 govern governance/control/history;
   - A15-A18 govern migration/synthetic geography/scarcity/social pressure;
   - A20 requires lower-resolution allocations to conserve to parent totals.

2. `LOOM_2226_CIVSTATE_Phase13_Contrast_Report_v0.1.md`
   - records Phase-13 output for anchor facilities;
   - exposes governance strata, Place DNA, influence edges and LLM scaffolds;
   - confirms these values existed before Phase 14 and were intended as behaviorally significant gameplay parameters.

3. `LOOM_2226_CIVSTATE_Phase14_Anchor_Validation_and_Backfill_v0.1.md`
   - explicitly names `LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3` as the working checkpoint;
   - states Phase-13 behavioural/materialization parameterization was qualitatively validated and frozen;
   - records the Phase-13 seed archive hashes:
     - SQLite `5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753`
     - bridging assumptions `744c968d8c896625eee7dd2f84dcbcb978ccec14d01d59003089972a390530d7`
     - contrast report `4f38ae2e600a30e33a9b3cd1ac34c41a63239348910ff0335808ec1471f64bb7`

These are historical recovery evidence, not current Git authority. They should be imported into governed repository provenance before being treated as first-class source material.

## Phase-14 clarification

Recovered Phase-14 builder artifacts show that later country operating-profile anchors were explicitly authored score tuples, not inferred from a universal quantitative formula. Generated political-breadth rows added later use separately documented composites.

This means `civ_country_operating_profile` is intentionally mixed-origin:
- authored anchor profiles for selected countries;
- generated breadth scaffolds for broader coverage.

A single universal field-generation formula must not be invented for the whole table.

## Remaining exact-generator gap

Still not recovered from an original source builder:

- `civ_node_texture_overlay.mobility_intensity`
- `civ_node_texture_overlay.logistics_intensity`
- `civ_node_texture_overlay.activity_pressure`
- `civ_node_texture_overlay.frontier_operational_pressure`
- `civ_economic_state.productivity_index`
- field-level Phase-13 equations for much of `civ_governance_profile`
- field-level Phase-13 equations for several `civ_place_dna` priors
- field-level Phase-13 equations for several `civ_social_state` scores

The equations already reverse-verified exactly in v0.5/v0.6 remain valid runtime contracts. Approximate regressions remain prohibited as definitions.

## Next recovery target

Search specifically for the **Phase-13 seed archive or original materializer source** associated with:
- `LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3`
- `RUN:MATERIALIZER2226_V0.1`
- the three preserved Phase-13 hashes above.

If recovered, hash-validate it against the Phase-14 handoff before promoting any formulas into the production data dictionary.
