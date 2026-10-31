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
