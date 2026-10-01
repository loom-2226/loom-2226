# Solar authority reconciliation 1950–2500 — Stage 1 physical inventory

Status: evidence only. No authority mutation. No source promotion. No downloads. No propagation.

This inventory enumerates every local `.bsp` / `.spk` under `/home/ubuntu/loom_solar_assets`, records SHA-256, byte count, SPK target/center/frame/type metadata and native segment coverage, and cross-links exact hashes to the governed PostgreSQL ephemeris-source ledger or acquisition manifest where available.

## Result

- 101 local SPK/BSP files were inventoried; filesystem and inventory path sets match exactly.
- 85 governed ephemeris-source rows carry hashes, representing 84 unique governed hashes; every governed hashed source is present locally.
- Two byte-identical duplicate groups exist: JUP365 and PLU060 candidate copies.
- 12 local files remain `UNKNOWN_UNVERIFIED` by exact hash. Their names or apparent contents are not sufficient to promote them.
- `kernels/spk/phase4e/testp10.bsp` is a 5,096-byte SPK container with zero segments. It is retained in the physical inventory and is not usable state authority.
- Several unknown Neptune products are already discussed in repository qualification evidence as candidate/rejected material. This inventory does not override those decisions.
- Stale/superseded-looking Horizons products are likewise retained as physical files without authority inference.

## Epistemic boundary

A local SPK is evidence of local bytes, not of governed authority. Target presence is not qualification. Filename/provider resemblance is not provenance. Stage 2 must use governed identity/source precedence and exact coverage; this inventory may expose candidates or gaps but cannot promote either.

The checkpoint JSONL is an execution-recovery artifact. `local_spk_inventory.json` is the finalized inventory; `stage1_audit.json` records reconciliation gates.
