# CURRENT PR #440: twin reactors and battery/flywheel/C-lite (2026-11-01)

Authority: protected main ce9ee081; this is a DRAFT, UNMERGED engineering candidate. Current source geometry SHA f7dc6b8c69cf56f48a55eeaa1a5daa7779fce3e06474157c960ef2f08cac95f7.

Current single-table source: SHIP_POWER_BUDGET_2026_11_01.md. Twin 50MW net D-He3 house reactors with 5MW minimum each; 3MWh / 1.5t endurance battery; 1.5MWh / 1.5t counter-rotating, contained pulse flywheel in aft electrical C-ring; C-lite 0.10t dry hardware + 0.15t wet independent monopropellant (two nominal slow recovery turns of 600s and 75kg each, not physically qualified). All 2226 densities, peak electrical power and independent control are DECLARED, not certified. Exact current 40s RCS trace and half-performance sensitivity are source stamped.

Mass: 867.531t dry; 1172.681t loaded S1 including 5t wet D-He3 and 0.15t C-lite monoprop. 55t loaded electrical allowance = 54.85t dry equipment + 0.15t monoprop. Reserve invariant at 11.284t (>5t hard floor). No new growth reserve draw. Historic full G6/G12 and certified=true do not carry forward. Metric environmental correction, reactor isolation, thermal/fluid bus, chemical nozzle torque and emergency torch-house power remain OPEN. No Navigator, Metric arrival or merge.

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
