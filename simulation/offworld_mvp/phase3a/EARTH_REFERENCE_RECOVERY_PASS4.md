# Phase 3A Earth Reference Recovery - Pass 4

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Branch:** `offworld-mvp-phase3`

## 1. Result

Pass 4 closes the two near-term numerical replay obligations left open by Pass 3 and sharpens the 2060 transition problem.

The important result is that the recovered recurrence rules are not merely descriptive prose. For the checked Australia transitions, the immediate boundary values and recovered formulas independently reproduce the stored next-year macro values to floating-point precision.

## 2. Exact replay: Australia 2026 -> 2027

Recovered 2026 boundary:

- value added Y_2026 = 1,728,703,629,851.8467
- investment I_2026 = 412,288,545,182.134
- WEO real-GDP growth for 2027 = 0.01698

Recovered near-term rules:

`Y_2027 = Y_2026 * (1 + g_WEO_2027)`

`I_2027 = I_2026 * (1 + g_WEO_2027)`

Independent arithmetic gives:

- calculated Y_2027 = 1,758,057,017,486.731
- stored Y_2027 = 1,758,057,017,486.731
- calculated I_2027 = 419,289,204,679.3266
- stored I_2027 = 419,289,204,679.32666

The difference is floating-point representation only.

The stored 2027 row also reports:

- capital = 8,257,519,782,056.423
- population = 27,351,104
- employment = 13,926,064.96581015
- country TFP multiplier = 0.9905782846324604
- asset-rebuilt TFP multiplier = 1.004276141389238
- replacement coverage ratio = 1.0

The country output and investment replay is therefore **ESTABLISHED**. Full asset-by-asset capital replay remains a separate lower-level proof obligation.

## 3. Exact replay: Australia 2031 -> 2032

Recovered 2031 boundary:

- Y_2031 = 1,912,235,611,725.3037
- I_2031 = 456,060,150,964.83673

Recovered structural rule:

`sI_2031 = I_2031 / Y_2031`

which gives:

`sI_2031 = 0.23849579422556566`

The stored 2032 endogenous output is:

`Y_2032 = 1,959,191,893,631.7979`

Applying the recovered investment rule:

`I_2032 = sI_2031 * Y_2032`

gives:

- calculated I_2032 = 467,259,026,712.0056
- stored I_2032 = 467,259,026,712.0055

Again the difference is floating-point representation only.

The stored 2032 row additionally reports:

- capital = 9,022,569,921,802.639
- real value-added growth = 0.024555698899534573
- replacement requirement = 306,972,206,122.5103
- replacement funded = 306,972,206,122.5103
- expansion investment = 160,286,820,589.49518
- replacement coverage = 1.0

Replacement plus expansion reconciles to total investment:

`306,972,206,122.5103 + 160,286,820,589.49518 = 467,259,026,712.0055`

The country investment recurrence and replacement/expansion accounting are therefore **ESTABLISHED** for this replay.

## 4. 2060 boundary finding

The structural-stage artifact inspected for Australia reports at 2060:

- value added = 3,402,430,152,234.1226
- investment = 811,465,281,454.0891
- capital = 15,278,049,696,370.824
- investment/output ratio = 0.2384957942255656

The current PostgreSQL reference projection reports instead:

- 2060 value added = 3,403,050,164,285.8843
- 2060 investment = 811,613,151,720.8035
- 2060 capital = 15,279,355,131,849.312
- 2061 value added = 3,469,680,592,943.0083
- 2061 investment = 834,934,914,029.7188
- 2061 capital = 15,564,939,117,026.521

Therefore the earlier structural-stage artifact is **not byte-for-byte identical to the promoted/current 2060 PostgreSQL boundary**.

This is not repaired or hand-waved away. It establishes that a later repair/promotion changed the 2060 boundary before the current PostgreSQL projection was built.

Consequently, an exact 2060 -> 2061 replay must use the promoted v4/current 2060 checkpoint and its immediate asset/depreciation state, not the earlier stage artifact.

## 5. Status of replay obligations

| Obligation | Status |
|---|---|
| 2026 -> 2027 country value added | ESTABLISHED |
| 2026 -> 2027 country investment | ESTABLISHED |
| 2031 -> 2032 investment envelope | ESTABLISHED |
| 2032 replacement + expansion reconciliation | ESTABLISHED |
| 2026 -> 2027 complete asset capital replay | NOT YET ESTABLISHED |
| 2031 -> 2032 complete sector/output replay | NOT YET ESTABLISHED |
| promoted 2060 -> 2061 transition | NOT YET ESTABLISHED |
| reason/lineage for stage-2060 versus promoted-2060 difference | NOT YET ESTABLISHED |

## 6. New anomaly / lineage requirement

The 2060 mismatch is now a formal recovery item:

**EARTH-REC-2060-001**

> The earlier recovered 2031-2060 structural artifact and the current promoted PostgreSQL projection contain different Australia 2060 macro values. The current reference must not be reconstructed from the stale stage boundary without tracing the intervening repair/promotion lineage.

This is exactly why Phase 3A is recovering the model rather than trusting whichever NDJSON file happens to have an encouraging filename.

## 7. Consequence for MVP interface

Nothing in this pass changes the earlier rule that national investment is not actor cash.

What improves is confidence that the Earth interface can expose not merely a number but a temporal-regime-aware assertion whose derivation can be replayed.

For MVP consumption, the interface should eventually expose at minimum:

- reference value;
- unit/basis;
- temporal regime;
- derivation identifier;
- source/promoted snapshot identity;
- fallback/imputation marker;
- uncertainty state;
- replay/verification status.

A consumer must not be able to accidentally mix an earlier stage artifact with the promoted reference series.

## 8. Next recovery target

Pass 5 shall trace the promoted v4 repair lineage into the current 2060 checkpoint, identify the exact source of the boundary delta, recover the immediate promoted 2060 asset/depreciation state, and replay 2060 -> 2061.

After that, Phase 3A can assess whether the remaining lower-level field and price-basis liens block freezing the narrow MVP Earth reference contract or can remain explicitly bounded non-MVP liens.
