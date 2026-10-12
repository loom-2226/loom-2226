# Route 1 optional carry cap, 2026–2029

**EXPERIMENTAL / NON-CANON / NON-RUNTIME-DEFAULT.** Off by default.

The cap is a multiple of each sponsor’s existing service price. End-of-year cash above the cap is transferred to the Earth-side `route1:earth:carry_lapse` account; sponsor, year, amount and transaction are audited. No additional services, years, or financing changes. The unlimited control is identical to Gate 2, including its fingerprint.

| Share | Cap | 2026 | 2027 | 2028 | 2029 | Funded sponsors (distinct) | Total lapsed ($B) | Conservation |
|---|---|---:|---:|---:|---:|---|---:|---|
| 10% | unlimited | 3 | 1 | 1 | 1 | CNES, CNSA, ESA, ISRO, JAXA, NASA (6) | 0.000000 | PASS |
| 10% | 0× | 3 | 0 | 0 | 1 | CNSA, ESA, ISRO, NASA (4) | 5.188041 | PASS |
| 10% | 1× | 3 | 1 | 1 | 1 | CNES, CNSA, ESA, ISRO, JAXA, NASA (6) | 3.873841 | PASS |
| 10% | 2× | 3 | 1 | 1 | 1 | CNES, CNSA, ESA, ISRO, JAXA, NASA (6) | 3.235227 | PASS |
| 25% | unlimited | 4 | 3 | 0 | 0 | CNES, CNSA, DLR, ESA, ISRO, JAXA, NASA (7) | 0.000000 | PASS |
| 25% | 0× | 4 | 0 | 0 | 0 | CNSA, ESA, ISRO, NASA (4) | 13.675102 | PASS |
| 25% | 1× | 4 | 3 | 0 | 0 | CNES, CNSA, DLR, ESA, ISRO, JAXA, NASA (7) | 12.160102 | PASS |
| 25% | 2× | 4 | 3 | 0 | 0 | CNES, CNSA, DLR, ESA, ISRO, JAXA, NASA (7) | 10.996786 | PASS |

**CNSA example (25% share, 2026):** CNSA purchases the existing **LAND** service for $150M ($0.150B). Under cap 0, its remaining $1,223.75M (rounded) lapses into the Earth-side sink; cap 1× retains at most $150M, cap 2× at most $300M. Unlimited retains the original balance.

**Reproducibility:** The off/default `None` cap uses the unmodified Gate 2 path. Tests compare its rows and fingerprint to the existing control. The other caps produce separate deterministic ledger states.
