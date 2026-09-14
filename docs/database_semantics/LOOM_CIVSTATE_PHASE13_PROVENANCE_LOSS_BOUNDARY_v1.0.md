# LOOM CIVSTATE Phase-13 Provenance Loss Boundary v1.0

## Qualified finding

The exact Phase-13 CIVSTATE checkpoint has been recovered and independently verified, but the original Phase-13 materializer source has not been recovered.

Recovered checkpoint:
- file: `LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3`
- SHA-256: `5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753`
- recovered Navigator source SHA-256: `906a31616ef4895997ce6e02e389789e884240671f7fef89abc59ca370d5f4a2`
- Navigator match: exact

Historical recovery evidence also preserves the governing bridge-assumptions and contrast-report hashes, and Phase-14 records that the Phase-13 behavioral/materialization state was qualitatively validated and frozen.

## Source-search result

Production Git history contains the database introduction and later archaeology/recovery work, but no commit containing an original Phase-13 `MATERIALIZER2226` builder. Retained file-library searches likewise recover the exact checkpoint and recovery artifacts, but not the original Phase-13 builder or seed archive containing it.

This is a provenance-loss finding, not evidence that the builder never existed.

## Authority boundary

`RECOVERED_STATE != RECOVERED_GENERATOR`

Therefore:
- current runtime values remain valid as recovered state;
- equations already exactly reverse-verified remain valid runtime contracts;
- unresolved Phase-13 field generators remain unresolved;
- approximate regression may not be promoted as an original definition;
- HEL allocator v2 implementation remains blocked where it would require missing parent-pool or generator semantics;
- no display-name inference, random jitter, or synthetic uniqueness is allowed as a substitute.

## Unlock condition

This boundary may be reopened only by new primary evidence, such as:
1. the original Phase-13 materializer source;
2. a hash-validated Phase-13 seed archive containing that source;
3. equivalent direct generator evidence with provenance strong enough to reproduce the original allocation semantics.

Until then, reconstruction authority is ZERO.
