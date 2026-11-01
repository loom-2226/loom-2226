# CURRENT PR #440: twin-reactor power, enlarged pulse flywheel and C-lite (2026-11-01)

**MERGE-APPROVED ENGINEERING CANDIDATE (kT 2026-11-01); PRE-MERGE EVIDENCE.** Main at bootstrap ce9ee081. Exact source SHA256: 4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331. No Navigator, Metric arrival, or full hardware qualification.

[**Current source-backed ship-power ledger**](SHIP_POWER_BUDGET_2026_11_01.md): 2×50MW net D–He3 reactors in separately located aft C-ring (A) and forward service-ring (B) component envelopes, 5MW minimum per running unit. 3MWh / 1.5t battery for quiet and reactor-failure endurance. 1.8MWh / 1.8t counter-rotating contained flywheel at declared 1kWh/kg and 150kW/kg (270MW peak) in aft C-ring. C-lite 0.10t dry + 0.15t wet independent slow attitude capability, torque and actual propulsion UNQUALIFIED.

Docked states use declared 2MW maximum external shore power, reactors OFF. During pulsed main torch burn ONLY, magnet/cryocooler electric 47.52MW is internally sourced from the torch; the assumed 63.36MW raw energy diversion (75% conversion) is named in the ledger and must be physically earned, including thrust and thermal effects. Main torch is never credited as a standalone house-power generator. Failure doctrine: surviving reactor B → battery → independent C-lite attitude (chemical, not electricity). Separate refuge battery retained.

All storage, reactor and conversion capabilities above are non-canon 2226 engineering declarations. 55t loaded electrical allocation and engineering growth reserve unchanged, wet C-lite fuel separately accounted. The current-source 40s / degraded 60s traces and half-performance sensitivity close numerically. G1–G12 all PASS/PASS-DECLARED (including 32 current-hash render assets and the power cutaway (four installed systems plus D–He3 and C-lite source-derived mass/CG envelopes)). FQ1–FQ4 78/78 PASS NUMERICAL. **certified=true** after kT acceptance of the 2MW shore interface, burn-only 63.36→47.52MW torch tap and power-bay visualization on unchanged geometry; **G12 12/12** after adding D–He3 and C-lite wet/dry mass-and-CG placement labels. Conventional lab acceptance only, not hardware flightworthiness. No prior geometry-hash G6/G12 result or `certified=true` is inherited.

The remaining pages below include superseded historic source-hash and branch-status narratives. Keep them as evidence only; do not mistake them for the latest branch state.

---

# CURRENT Option C, 2026-11-01 source 447c05ccb7a3031823e0713ee6010eaa200dbb4c1635b8a5c747b7cd98dae6a6

**Option C chosen by kT; geometry checks and FQ1–FQ4 pass; mechanical/pressure/damage qualifications remain kT HOLD.** [Current close-out, mass table, acceptance](CROWN_SHELL_OPTION_C_CLOSEOUT_2026_11_01.md). Earlier snapshots below are historical, not current.

# I4 completeness repair, final source 702cca4ef985f754b066e4289f3cc63a4d13c87608b40a75fc9520cf67d0cfb3

See [I4 completeness recovery](I4_COMPLETENESS_RECOVERY_2026_11_01.md) for f07354f item mapping, restored 37 panes, NAV platform, hatches, optical viewer, G7/G6 and FQ1-FQ4 latest new geometry. **certified=false**, draft PR #439; previous docs retain historical evidence.

# Wayfarer current AOI-2226 Option A review

NEW geometry SHA256: faf75e0da8a58c850c72d3e6941f5af94cadb06dcf8dfbaa510fac56b77327af. 37 protective outer panes, TWO independently pressure-capable ~7m ceramic domes, 3.023m3 optogel between; failure independence and current visual evidence remain kT HOLD. See [Option A report](AOI_2226_CROWN_OPTION_A_2026_11_01.md).

# Wayfarer engineering source: 2026-11-01 I4 carry-over under review

ALL bodies. ALL sponsors. 2026-2226.

**Engineering source, not canon, hardware flightworthiness or runtime deployment.**

**NEW I4/crown geometry SHA256:** faf75e0da8a58c850c72d3e6941f5af94cadb06dcf8dfbaa510fac56b77327af

**Certification on this NEW geometry:** G1-G12 PASS/PASS-DECLARED, but certified=false until kT accepts the new 7m ceramic pressure-dome milestone and visually reviews new-hash images. The old certified=true record applies only to archived 5d73 geometry.

Five folders: config (source inputs and kT decisions), lab (builder, certification and flight tests, PR #433 lab / PR #436 cards), render (views, deckplans, I4 GLB), results (geometry and generated certification), docs (qualification basis and history).

Run from wayfarer/lab: python3 build_v05.py; python3 certify.py. The SHA must remain exact. New-hash G1-G12 checks pass or pass-declared, but the new declarations are not all kT accepted; do not claim certified=true from the earlier hash. The Rev7 test fixtures under lab/flight/fixtures/rev7 are historical, non-governing and not a second authoritative ship design.

**Metric arrival HOLD, Navigator EXCLUDED, RCS heating power source OPEN.** No new Metric or Navigator qualification implied.

See PHASE2_SINGLE_HOME_2026_11_01.md and KT_DECLARED_CONVENTIONAL_LAB_ACCEPTANCE_2026_11_01.md.

Full flight lab (including canonical Metric HOLD safeguards): python wayfarer/lab/flight/run_lab_regression.py; 61 tests, no exclusions. The tests do not clear Metric arrival HOLD.

**New current-source report:** [I4 carry-over and crown Option B](L1_I4_CARRYOVER_CROWN_OPTION_B_2026_11_01.md).
