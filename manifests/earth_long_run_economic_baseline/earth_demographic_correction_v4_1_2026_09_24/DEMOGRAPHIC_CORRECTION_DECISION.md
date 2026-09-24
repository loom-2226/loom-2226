# Earth v4 demographic correction decision — 2026-09-24

**Primary change class:** `class:data`
**Target:** `EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24` demographic integration only
**Economic baseline:** unchanged
**Canon:** unchanged
**Selected demographic scope:** Earth biological population by WPP Country/Area at 2226 only

## Decision

Keep the promoted v4 economic baseline intact. Do not rewrite its historical
candidate or promoted artifacts. Add a bounded demographic authority supplement
for consumers that need a 2226 country population endpoint.

The selected Earth biological parent is the current governing canon value:

`8,312,538,895.185726` biological residents on Earth in 2226.

The selected country allocation is a **canon-constrained allocation bridge**,
not a new cohort-component simulation and not an empirical forecast.
## Why this correction is necessary

The v4 candidate's post-2100 demographic sensitivity extends each country's
median 2091-2100 WPP log-population growth rate with an exponentially decaying
half-life. That artifact remains useful as sensitivity provenance, but it has no
fertility, age-specific mortality, cohort aging, longevity-medicine diffusion,
or migration mechanism after 2100.

PR #267 therefore correctly made that sensitivity non-selected. This correction
supplies the missing selected **2226 endpoint** without pretending to solve the
still-open annual cohort history.

The governing Solar census already fixes total biological humanity and Earth's
share. Re-estimating the total here would improperly move a canon boundary in a
data-integration change.
## Recovered allocation evidence

The production CIVSTATE database preserves
`FREEZE:DEMOGRAPHIC_V2_1` / `DEMOGRAPHIC_ALLOCATION_V2_1`.

Its 2226 country audit has 81 rows: the same 80 named economies used by v4 plus
one `ROW` accounting residual. The rows exactly reconcile to that historical
allocator's frozen Earth parent. Its preserved limitation is explicit:
aggregate allocator, no explicit migration term, no dense recovered intermediate
trajectory, and a geometric-mean endpoint-development proxy.

The allocator is therefore used here only for **relative 2226 allocation shape**.
Its obsolete 6.553512340B parent is not reused as Earth authority.
## Selected allocation rule

1. Preserve the frozen v2.1 2226 shares for the 80 named economies.
2. Renormalize those shares and the v2.1 `ROW` residual to the current canon
   Earth biological parent.
3. Disaggregate that renormalized `ROW` residual across the other 157 WPP
   Country/Area identities using UN WPP 2024 Medium 2100 Jan-1 population share.
4. Reconcile all 237 rows exactly to the canon Earth parent.

This introduces **zero fitted or free parameters**.

UN WPP remains empirical/projected demographic authority through 2100.
The 2226 allocation is a LOOM data-layer bridge beyond that boundary.
## Medical/longevity lineage

Recovered v0.2-v0.4 demographic work explicitly modeled future medicine,
rejuvenation access, fertility timing, and long-lived cohorts. That lineage is
preserved and remains relevant to future cohort reconstruction.

This correction does **not** claim that the current exact canon total was
regenerated from those historical medical parameters. Current canon explicitly
keeps exact fertility, median-age, and extreme-longevity-tail details
model-sensitive unless separately promoted.

Accordingly, medical/longevity assumptions remain provenance and future
cohort-model inputs; they are not silently converted into selected exact
country-age distributions here.
## Authority and dependency effects

- v4 qualified 80-economy value-added/capital/investment outputs: **UNCHANGED**
- WPP identity and demographic authority through 2100: **UNCHANGED**
- v4 post-2100 half-life sensitivity: **RETAINED AS NON-SELECTED PROVENANCE**
- 2226 Earth biological parent: **INHERITED FROM CURRENT CANON**
- 2226 country population endpoint: **SELECTED BY THIS SUPPLEMENT**
- 2101-2225 annual country population trajectory: **NOT SELECTED**
- age/sex cohort detail after 2100: **NOT SELECTED**
- Solar census and off-Earth population: **UNCHANGED**
- CIVSTATE/SQLite/Postgres materialization: **NOT MUTATED BY THIS CHANGE**

Any future cohort-component successor may supersede this bridge after separate
qualification, but it must preserve governing canon totals unless canon itself
changes through governed process.
## Acceptance gates

The supplement must fail closed unless all of the following hold:

- v4 coverage remains 80 economic economies / 237 demographic areas / 157
  demographic-only areas;
- the recovered v2.1 named roster equals the v4 economic-80 roster exactly;
- the v2.1 source rows reconcile to their own frozen parent;
- the WPP 2100 source hash remains the registered source hash;
- all 237 selected populations are positive;
- the selected rows sum to the exact canon Earth biological parent;
- no v4 economic selected output is modified;
- the old half-life artifact remains explicitly non-selected;
- no annual post-2100 trajectory is implied by the endpoint bridge.
