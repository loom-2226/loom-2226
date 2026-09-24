# Earth empirical baseline successor: dependency and change impact

**Class:** data. **Status:** candidate, not promoted. **Base Git SHA:** `fbc3818648cd9cdf54629281f52b5eb928b4f877`. The active v3 pointer and all v3 files are immutable inputs.

## Verified frozen inputs

The governed pointer designates `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23`. Its permanent manifest matches the pointer SHA-256 `f8954955671c59bda3d4ce51b734589d77395a70ae556d9df277ae209f580fdb`. All 30 baseline-manifest entries and all 46 recursively pinned run-manifest entries match their recorded byte sizes and hashes on quantifactus. The repository and local pointer bytes agree.

## Dependency graph

| Input or stage | Role | Successor impact | Reuse decision |
|---|---|---|---|
| UN WPP 2024 Medium `TPopulation1Jan` and age shares | 2026 identity/demography and 2100 tail anchors | Expand the economy universe; add tail sensitivities | Reuse exact source bytes; parse selected years only |
| WDI, IMF WEO, PWT 11, ILOSTAT and existing crosswalks | Macro, factor, labor provenance | Classify each added economy; no automatic ten-sector qualification | Reuse qualified snapshots and source registry |
| OECD 2024 current-price and previous-year-price ten-sector reducers | Signed source observations, active-sector test, IO topology | General 2026 accounting-boundary repair; added-economy topology coverage | Reuse exact source bytes; do not re-reduce unchanged OECD data |
| Qualified 2026 80-economy seed and four-asset reconstruction | Initial modeled accounts | Reconstruct qualifying active sectors and rebalance within-country accounts | Reuse as immutable control and successor input |
| 2026–2031 and 2031–2060 bridges | Pre-2060 trajectory | Must be rerun for affected countries if repaired seed enters at 2026 | Cannot reuse affected annual rows or 2060 state unchanged |
| Frozen v3 2060 state and v3 2060–2226 annual outputs | V3_CONTROL | Exact control, rollback and comparison | Reuse without computation or mutation |
| V3 long-run equations | 2060–2226 central economic model | Reuse unless upstream repaired state requires a new run | Copy only into candidate; no algorithm change by default |

## Controlled arms and decision gate

`V3_CONTROL` uses the exact 80-country frozen record. `SUCCESSOR_80` must use the same 80 IDs with a repaired 2026 seed and inherited qualified economic model. `SUCCESSOR_FULL` requires the same successor rules for an expanded **economically qualified** universe; it cannot be synthesized by filtering a full run. All 237 WPP Country/Area identities can enter the demographic envelope, but that does not establish sector, asset, factor-share or bilateral-topology evidence for every one. A full economic run is held until those layers have qualified inputs or an explicitly documented method. No absent sector or network row is zero-filled.

## Invalidation and protected state

The 2026 repair invalidates the affected 2026–2060 sector, asset and country-derived states and any later economic trajectory based on them. The demographic scenarios invalidate only post-2100 demographic and downstream economic rows for their own scenario. The WPP, OECD, WDI, PWT, ILOSTAT, v3 control, production Earth baseline pointer, Atlas, CIVSTATE, Navigator and canon remain unchanged. Candidate artifacts live separately and cannot promote themselves.
