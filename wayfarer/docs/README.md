# CURRENT research/engineering branch: Wayfarer ship-power budget (2026-11-01)

**Base protected main:** `ce9ee081`; previously accepted full Option C geometry `7f620c53` (PR #439 merged). This new **unmerged engineering candidate** moves 5t of D–He3 HOUSE fuel into **wet consumable mass**, plus 0.5t of DRY containment charged to reserve, and therefore has a NEW source geometry: `49cc20e70f5ad2b39280fa460cec07874a1053ca2a6fed48dda38ca4527d7c6b`.

[**Current source-backed 10-state power and heat ledger**](SHIP_POWER_BUDGET_2026_11_01.md) is the active new document for this power task. Dedicated 80MW net D–He3 house reactor; relational plant and Metric bank are **not generators**. Main torch is **PULSED** (all operating modes) and emergency house-power use of the pulsed torch is **not** a continuous standby source. Emergency ~519MW×40s RCS belongs to a charged flywheel; routine 120s from the house reactor is currently a declared throttling-law approximation, not an observed nozzle trace.

**New geometry evidence:** targeted G1/G3/G4 PASS/PASS/PASS-DECLARED, 78/78 actual fresh FQ1–FQ4 (new folder `lab/flight_qual/fq_house_power_20261101/`). The earlier 7f620c53 G6/G12 source-stamped evidence and `certified=true` acceptance **DO NOT TRANSFER TO THIS HASH**. Physical reactor, flywheel, tank containment, coolant loops, crew radiation at new source hash and visual state remain unqualified. Metric arrival HOLD; Navigator EXCLUDED; no new simulator.

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
