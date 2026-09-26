# SOLAR-BASELINE-01R qualification

**Verdict:** `SOLAR_BASELINE_01R_PASS_WITH_LIENS`

Reconciliation uses deterministic decimal and property-scoped unit rules, preserves all input candidate assertions, records pairwise relationships in an additive ledger, and performs no preferred-fact selection. Runtime is offline after the frozen NAIF identity reference and B01 artifacts are available.

The frozen B01 input contains 788 assertions, 748 body/property groups and 40 pair comparisons. It produced {'CONFLICT': 6, 'DISTINCT_BUT_COMPATIBLE': 5, 'EXACT_EQUIVALENT': 2, 'LIMIT_COMPATIBLE': 1, 'LIMIT_CONFLICT': 1, 'NOT_COMPARABLE': 3, 'PRECISION_EQUIVALENT': 22}. Coverage increased from 661 to 671 supported lanes after one identity family was resolved. Three SF-PROMOTE-03 canary digests and zero preferred facts remain unchanged.

The held Moon GM record has a reported/normalized representation mismatch and remains not comparable. Distinct source lineage labels are not treated as proof of independent evidence. Three binary-system source mappings remain held because their external IDs identify barycenters; Kleopatra's ID resolves by exact NAIF name and documented legacy/extended alias.

No Tier-1 data was ingested. The first recommended Tier-1 study is IAU/WGCCRE orientation products for broad, structured model coverage; exact lane gain must be verified before acquisition. Reports, machine-readable outputs, and the immutable input freeze accompany this report.
