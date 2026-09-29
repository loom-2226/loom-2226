# Function-domain stretch evidence — 2226 one-year characterization

Persistent qualification evidence for the Chebyshev-only adaptive Solar state-function compiler.

- Start ET: `7131844800.0` (2226-01-01 TDB baseline used by the run)
- Resolved catalog objects: 103
- Diagnostic spans: 1, 2, 4, 8, 16, 32, 64, 128, 256, 365 days
- Results: 1030 total; 1029 PASS; 1 FAIL; 0 coverage stops
- Runtime: 6973.033079147339 s
- 365-day result: 102/103 PASS; 77 PASS bodies required one Chebyshev segment
- Sole failure: IO at 365 days. Recursive qualification reached an interval whose candidate error was 28.9821 km against a 25 km tolerance. IO passed the 256-day diagnostic with 512 segments.

This is empirical sampled qualification evidence, not a formal all-interval mathematical error proof and not qualification for 2226–2250 or 1950–2500. The run characterizes natural function-domain complexity and supports dynamics-driven segmentation rather than fixed calendar chunks.

`results.jsonl` is the canonical row-level evidence. `results.csv` is a convenience projection. `run.log` preserves stdout. `SHA256SUMS.json` hashes the archived evidence files. The runner is preserved at `tools/loom_function_domain_stretch.py`.
