# Exact copied-grid equivalence (TEST_ONLY)

**PASS:** For all integer flight limits from 46 through 5000 days inclusive, across sampling steps 0.25, 1, 10 and 30 days, the copied authored-limit grid reproduced the original grid exactly: **19,820/19,820 SHA-256 comparisons passed**, no tolerance. Aggregate grid comparison SHA-256 `32b5c5f6994685711e41bdf8a50a05ce0f67c29bcc4aed801a99ba1776a64483`. Authored 8000-day scenario SHA-256 `e961912cbb1780077bfff77a8663b1f492f23d1e58b425b968a52614660b0c82`.

**PASS:** Nine exact quote comparisons, using the same approved parent rule on both sides, reproduced prices and price dispositions exactly at 1400, 3000 and 5000 days for **VENUS** (inner body), **TITAN** (Saturn giant-planet moon), and **ERIS** (outer body). See `price_equivalence_parent.json` for both per-case SHA-256 values. No tolerance, no first difference.

**Explained initial discrepancy:** An initial comparison against the **uncorrected** original moon pricing output for TITAN at 1400 days differed at `status` (`UNPRICED` versus `PRICED`). This is the already identified **wrong moon-own-table prerequisite** in the original price driver, not a flight-grid difference. Repeating with the approved parent-table rule on both sides produced exact equality. The original discrepancy is preserved in `price_equivalence.json` and has not been concealed.

This establishes grid equivalence for every integer limit up to 5000 and exact sample-price equivalence at the four named dimensions (body, year, limit, source/parent rule). It does not independently establish physical ephemeris accuracy or eligibility for every other body and year.
