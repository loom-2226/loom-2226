# Decision record (draft): Offworld civil and defense financing proxies

**Status:** PROPOSED / NON-CANON / NON-RUNTIME. No activation or baseline change authorized.

## Civil financing

- **Candidate:** `civil_envelope[c,t] = value_added[c,t] × civilian_space_share[c]`. This is a potential *civilian space* budget, **not** the amount automatically available for offworld work; the offworld allocation is tested at **10% (base)** and **30% (high)** of this envelope; neither is a verified historical offworld fraction.
- **Country shares:** USA **0.091%**, FRA **0.082%**, DEU **0.055%**, IND **0.030%**, CAN **0.043%**, KOR **0.089%** (previously reviewed OECD/government references; verify compatible budget-year and coverage before calibration). China: **low 0.030%, evidence-low 0.070%, evidence-high 0.100%**. China's published spending estimates and their civilian/military coverage remain unreconciled; these are **scenario assumptions, not verified civilian shares**. JPN, RUS, AUS, ARE: **0.030% authored placeholders**, not measured rates.
- **Civil offworld trial:** `civil_offworld[c,t] = civil_envelope[c,t] × f_civil`, with **f_civil = 0.10 and 0.30**. The high case is motivated by NASA's exploration request being roughly one-third of its civil budget, but that analogy is not a validated universal national share. Keep civil distinct from defense.
- **Control:** `0.001 × investment[c,t]` (existing 0.1%-of-investment comparison), not a civilian-budget observation.
- **Executor-capacity signal:** value added in `SHIPS_AEROSPACE + COMPUTE + PRECISION_MATERIALS`; this is industrial breadth, **not** spendable financing or guaranteed offworld-qualified throughput.
- **Sources:** Earth v4 country and country-sector outputs; OECD *Space Economy at a Glance 2026*; India Department of Space budget material. Source-year, public/private coverage, China estimates, national-versus-ESA accounting, and offworld allocation remain unresolved.

## Defense V2 (proposed; off by default)

- **Candidate defense-space envelope:** `B[c,t] = value_added[c,t] × SIPRI_military_burden[c] × military_space_share_of_defense[c]`.
- **First experiment:** `defense_draw = B × f_constant × min(1, overall_scale × country_scale × pressure_effective^steepness)`. **Run both authored constant offworld fractions, 0.05 and 0.10, in a future V2 sweep**; neither is a historical estimate. No V2 sweep is authorized until the accounting gate is resolved.
- **Later optional switch:** `f(pressure_effective) = f_base + (f_max - f_base) × pressure_effective` (illustrative 0.05→0.20). Preserve the existing squared curve; test whether this additional response is desirable before enabling.
- **Existing crisis semantics (verified in code):** `pressure_effective = min(1, base_pressure + sum(active_crisis_intensities))`; default steepness **2**. Defense uses its own Earth-boundary-to-defense-funds transfer, separate from the civil draw. Disabled means no defense call/account/transaction.
- **Sources:** SIPRI *Trends in World Military Expenditure 2025* (military burden); US Space Force FY2026 budget request approximately **$39.9–40.1B** (scope/accounting differs from SIPRI's 2025 total); `simulation/offworld_mvp/defense_capital.py`, `build8/defense_draw_trial.py`, `build8/DEFENSE_CAPITAL_DRAW.md`.
- **Authored/unverified:** Offworld fraction and any crisis-dependent rise are authored. Comparable military-space shares are unavailable for most sponsors, especially China; US Space Force share is only a cross-year, cross-definition approximation. SIPRI UAE 2025 military burden is unresolved. Do not combine defense and civil envelopes or claim either represents observed offworld spending.

## Accounting and frozen evidence

V1's ceiling is `0.01 × investment`, scaled by the crisis curve: **1% of investment is a mobilization cap, not 1% of a military-space budget**. Preserve V1's frozen defense sweeps and outputs unchanged. A V2 experiment would require its own versioned outputs; the old frozen figures do **not** get recalculated or overwritten.

**Open accounting question:** V1 validates an admitted **investment** assertion before drawing from the existing Earth-boundary account. V2 would derive its ceiling from **value added**. Determine the smallest legitimate way to admit/verify the value-added assertion and reconcile the defense boundary transfer **without modifying the Build 7 kernel or its source-integrity hash**. Do not silently relabel investment as value added or treat two independently calculated envelopes as the same stock.

## Decisions recorded (research only)

1. **Approved as research assumptions, pending source checks:** USA 0.091%, FRA 0.082%, DEU 0.055%, IND 0.030%, CAN 0.043%, KOR 0.089%; China low/evidence-low/evidence-high 0.030%/0.070%/0.100%. This is **not** source qualification or canon promotion.
2. **Civil allocation experiment:** compare **10% and 30%** of the civil envelope. The US 2026 10% case is approximately $2.16B from the previously extracted v4 value added; comparison with Route 1 (~$1.2B under the referenced settings) is an order-of-magnitude check, not calibration.
3. **Defense V2 experiment:** compare **constant 5% and 10%** offworld fractions; pressure-rising fraction remains a **later, disabled switch**. Preserve the existing crisis curve and off-by-default behavior.
4. **Blocking gate before any build:** establish a legitimate value-added assertion and Earth-boundary accounting treatment **without touching Build 7**. Leave this unresolved; no V2 implementation or sweep until it is resolved.

**No implementation, simulation rerun, qualification, or promotion authorized by this record.**
