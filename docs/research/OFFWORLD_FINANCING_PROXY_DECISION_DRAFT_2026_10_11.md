# Decision record (draft): Offworld civil and defense financing proxies

**Status:** PROPOSED / NON-CANON / NON-RUNTIME. No activation or baseline change authorized.

## Civil financing

- **Candidate:** `civil_envelope[c,t] = value_added[c,t] × civilian_space_share[c]`. This is a potential *civilian space* budget, **not** the amount automatically available for offworld work; an offworld allocation decision remains open.
- **Country shares:** USA **0.091%**, FRA **0.082%**, DEU **0.055%**, IND **0.030%**, CAN **0.043%**, KOR **0.089%** (previously reviewed OECD/government references; verify compatible budget-year and coverage before calibration). China: **low 0.030%, evidence-low 0.070%, evidence-high 0.100%**. China's published spending estimates and their civilian/military coverage remain unreconciled; these are **scenario assumptions, not verified civilian shares**. JPN, RUS, AUS, ARE: **0.030% authored placeholders**, not measured rates.
- **Control:** `0.001 × investment[c,t]` (existing 0.1%-of-investment comparison), not a civilian-budget observation.
- **Executor-capacity signal:** value added in `SHIPS_AEROSPACE + COMPUTE + PRECISION_MATERIALS`; this is industrial breadth, **not** spendable financing or guaranteed offworld-qualified throughput.
- **Sources:** Earth v4 country and country-sector outputs; OECD *Space Economy at a Glance 2026*; India Department of Space budget material. Source-year, public/private coverage, China estimates, national-versus-ESA accounting, and offworld allocation remain unresolved.

## Defense V2 (proposed; off by default)

- **Candidate defense-space envelope:** `B[c,t] = value_added[c,t] × SIPRI_military_burden[c] × military_space_share_of_defense[c]`.
- **First experiment:** `defense_draw = B × f_constant × min(1, overall_scale × country_scale × pressure_effective^steepness)`. **Author** a constant offworld fraction (e.g. 0.05 or 0.10) and compare; do not assume a historical fraction.
- **Later optional switch:** `f(pressure_effective) = f_base + (f_max - f_base) × pressure_effective` (illustrative 0.05→0.20). Preserve the existing squared curve; test whether this additional response is desirable before enabling.
- **Existing crisis semantics (verified in code):** `pressure_effective = min(1, base_pressure + sum(active_crisis_intensities))`; default steepness **2**. Defense uses its own Earth-boundary-to-defense-funds transfer, separate from the civil draw. Disabled means no defense call/account/transaction.
- **Sources:** SIPRI *Trends in World Military Expenditure 2025* (military burden); US Space Force FY2026 budget request approximately **$39.9–40.1B** (scope/accounting differs from SIPRI's 2025 total); `simulation/offworld_mvp/defense_capital.py`, `build8/defense_draw_trial.py`, `build8/DEFENSE_CAPITAL_DRAW.md`.
- **Authored/unverified:** Offworld fraction and any crisis-dependent rise are authored. Comparable military-space shares are unavailable for most sponsors, especially China; US Space Force share is only a cross-year, cross-definition approximation. SIPRI UAE 2025 military burden is unresolved. Do not combine defense and civil envelopes or claim either represents observed offworld spending.

## Accounting and frozen evidence

V1's ceiling is `0.01 × investment`, scaled by the crisis curve: **1% of investment is a mobilization cap, not 1% of a military-space budget**. Preserve V1's frozen defense sweeps and outputs unchanged. A V2 experiment would require its own versioned outputs; the old frozen figures do **not** get recalculated or overwritten.

**Open accounting question:** V1 validates an admitted **investment** assertion before drawing from the existing Earth-boundary account. V2 would derive its ceiling from **value added**. Determine the smallest legitimate way to admit/verify the value-added assertion and reconcile the defense boundary transfer **without modifying the Build 7 kernel or its source-integrity hash**. Do not silently relabel investment as value added or treat two independently calculated envelopes as the same stock.

## Decisions requested

1. Approve the six reference civil shares and the three China cases **as research assumptions**, pending source reconciliation?
2. Choose a civilian **offworld allocation fraction** (or retain the full civil envelope as a non-spendable ceiling only)?
3. Choose a constant defense offworld fraction for the first V2 sweep (**5% vs 10%**) and whether a pressure-rising fraction merits a later switch?
4. Resolve the value-added boundary assertion/accounting question before any implementation; keep V1 frozen and defense **off by default**.

**No implementation, simulation rerun, qualification, or promotion authorized by this record.**
