# Earth long-run baseline resolution integration — 23 September 2026

**Result:** the local current-baseline pointer resolves to the qualified national-GFCF, alpha=0.60 successor. No active LOOM application or model consumer was found that hard-codes the former Earth long-run baseline. Accordingly, no existing consumer, historical run, canonical file, or production repository was edited. The new read-only `earth_baseline_resolver.py` is the integration entry point for consumers of the current result; it reads only `../EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json` to choose a run and never falls back silently.

## Consumer inventory and changes

| Scope inspected | Active direct Earth-baseline consumers found | Change |
| --- | ---: | --- |
| Local LOOM application and tooling: `LOOM_DEV/src`, `tools`, `web`, `tests`, `manifests`, `data`; `LOOM-output`, `pixel-loom-legacy`, `/opt/loom`, `ceres-pg-dev` | 0 | None |
| Live `loom-2226/loom-2226` main and `loom-2226/loom-research-lab` main file trees; organization code searches for the prior directory, old baseline name and endpoint filename | 0 Earth propagation consumers or exact reference matches | None; no Git mutation |
| Earth recovery research tree | Historical comparison/qualification scripts only | Left intact to preserve exact experiment provenance |
| New integration entry point | 1 read-only endpoint loader | `earth_baseline_resolver.py` verifies the designated manifest and all registered files before loading |

Remaining direct versioned references are intentional historical evidence: `earth_baseline_2226_2026_09_23/` is the immutable v1 rollback record; `earth_repair_successor_2026_09_22/`, `alpha_ceiling_round1_2026_09_23/`, `earth_dynamic_successor_2026_09_23/` and their scripts/manifests pin the baselines they actually studied; `investment_rate_source_round1_2026_09_23/` pins its alpha=0.60 comparator and qualified own outputs. Repointing those comparison scripts would rewrite the meaning of archived tests. No current LOOM runtime consumer was found outside this Earth workspace, so this integration does not claim a production or canon adoption.

The local `LOOM_DEV` checkout is older than the verified live main ref; live GitHub searches were checked separately for the exact former-baseline references. These checks cannot prove that an unindexed external private deployment has no consumer.

## Verification

Run `python3 -B -m unittest -v test_earth_baseline_resolver.py` here. **5/5 PASS**. The tests verify the pointer designates `v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1`, compare SHA-256 and byte size for all **59** files registered by its run manifest, load 80 endpoint countries for 2226, reject a missing active manifest or a bad registered artifact hash without fallback, and use the same resolver with a temporary **pointer-only** change to verify all **75** v1 rollback files and load its distinct endpoint. The real pointer and both baseline trees are unchanged. No economic simulation was run.

The pointer, active designation manifest, selected endpoint and complete 2226 checkpoint remain hash-pinned. The resolver rejects stale or corrupt files rather than substituting the previous baseline. Rollback requires only changing the current pointer to the preserved v1 manifest and its recorded SHA-256; no consumer code change is required. The current designation remains an exploratory 80-economy scenario, not an empirical forecast.


## 24 September 2026 — demographic endpoint supplement

PR #267 first removed the v4 aggregate half-life demographic sensitivity from
selected authority. The additive
`earth_demographic_correction_v4_1_2026_09_24/` supplement now supplies a
selected 2226 Earth country-population endpoint while leaving the promoted v4
economic run and its immutable records unchanged.

The supplement inherits the exact current canon Earth biological parent
(8,312,538,895.185726), preserves the frozen demographic-v2.1 country-allocation
shape for the same 80 named economies used by v4, and disaggregates the recovered
v2.1 `ROW` residual across the other 157 WPP Country/Area identities by their
WPP 2024 Medium 2100 Jan-1 population shares. It adds no fitted/free parameter.
All 237 rows reconcile to the canon parent.

This is an endpoint allocation bridge, not a cohort-component rerun. WPP remains
authority through 2100; no annual 2101-2225 demographic trajectory is selected.
Historical medical/longevity cohort work is retained as provenance, while exact
post-2100 age, fertility and longevity detail remains model-sensitive.

The resolver hash-verifies the supplement manifest and its generated JSON/CSV,
decision record and builder, verifies the current canon/CIVSTATE/WPP source
hashes, and fails closed if the selected endpoint no longer reconciles. The old
v4 half-life sensitivity remains available only as non-selected comparison
provenance.
