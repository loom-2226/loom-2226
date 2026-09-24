# Earth long-run economic baselines

**Current designation:** `EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24`. **Class:** canon + data / manifest. WPP 2024 remains empirical authority through 2100; the selected coupled successor is modeled authority for 2101–2226.

The [current economic pointer](EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json) and [current demographic pointer](EARTH_DEMOGRAPHIC_AUTHORITY_CURRENT.json) resolve the same selected `MED_CENTRAL × SYNTH_CENTRAL` authority. Use `earth_baseline_integration_2026_09_23/earth_baseline_resolver.py` to hash-verify the package, rosters, personhood categories and 80/80 workforce invariant.

The [promoted package](earth_lean_biosynthetic_successor_v0_1_2026_09_24/PROMOTION_DECISION.md) is an exact copy of the merged Research Lab candidate plus an upstream promotion manifest, intake record, validator and tests. Its full 3 × 3 sensitivity grid remains visible.

The [v3 data dictionary](earth_long_run_economic_baseline_v3_repaired_2026_09_23/DATA_DICTIONARY.md) and [machine-readable field semantics](earth_long_run_economic_baseline_v3_repaired_2026_09_23/FIELD_SEMANTICS.json) define every output field, price basis, formula, comparison limit and invalid physical-capacity interpretation. The [semantic test](earth_long_run_economic_baseline_v3_repaired_2026_09_23/test_field_semantics.py) verifies the documentation against pinned source code and actual output schemas and identities without simulation.

The [v4 economic baseline](earth_long_run_economic_baseline_v4_2026_09_24/BASELINE_MANIFEST.json), [PR #268 demographic bridge](earth_demographic_correction_v4_1_2026_09_24/CORRECTION_MANIFEST.json), v3 and v2 records remain unchanged as superseded or rollback provenance. From `earth_baseline_integration_2026_09_23/`, run `python3 -B -m unittest -v test_earth_baseline_resolver.py test_earth_v4_promotion.py test_earth_biosynthetic_canon.py` to verify the current authority without rerunning the model.
