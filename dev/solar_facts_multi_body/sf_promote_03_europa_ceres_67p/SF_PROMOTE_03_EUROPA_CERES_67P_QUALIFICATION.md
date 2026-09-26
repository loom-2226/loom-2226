# SF-PROMOTE-03 — Europa + Ceres + 67P qualification

**ARP Europa research:** `ARP_QUAL_02_EUROPA_PASS_WITH_LIENS`
**Three-body Solar Facts promotion:** `SF_THREE_BODY_PROMOTION_PASS_WITH_LIENS`

Research Lab PR #86 passed `lab-gate` and merged at `eb433d36b76752ae3fc66bbe3fd730b341ddb837`. Gate A was frozen at campaign SHA-256 `5f6f4dc829746da05eb3eb25bf56ef6f57ec2085225ccb88d9d74eb587d67730` with cutoff `2025-12-31T23:59:59Z`. Blindness excluded pre-existing identity/ephemeris and legacy presentation data from research; the existing `loom_solar.body:EUROPA` identity was bound after Gate A. No Ceres/67P science or model memory supplied Europa facts.

## Research and coverage

ARP `1.0.0` discovered 32 sources, acquired 24 sources/artifacts, rejected 8, and recorded 12 independent lineages. It extracted and accepted 17 candidate assertions; no assertion was rejected at admission. All 26 coverage questions were dispositioned in both passes: 11 SUPPORTED, 12 PARTIAL, 2 SOURCE_NOT_FOUND, 1 UNKNOWN. Pass 2 reviewed 9 targeted questions. Coverage is disposition, not completeness. Hostile research review passed 25 attacks. The full Research Lab suite passed 180 tests plus 5 subtests; 8 project tests passed.

Important boundaries: magnetic measurements support but do not directly observe an ocean; the 2025 Juno shell result remains a footprint-scoped idealized model interval (19–39 km), not a global thickness; plume candidates, nondetections and limits remain instrument/epoch scoped; NaCl remains a regional surface spectral interpretation; radiation and geotechnical information remain incomplete; no downstream engineering/resource judgments were introduced.

## Baseline and promoted database

SF-PROMOTE-02 input SHA-256 `ed930b0453ec994712614bf0beb1a5ff8c93452db1b753884539fa510184b64f`; whole semantic digest `2328f03f45b560c127a2c93b3aac0cf484f82e439979e16586eeaea12d845bd0`. Frozen pre-Europa body digests: 67P `9e4139deb7182ce4c87176bc27e3510ffb075421e34cbca7bdb5a2a700ad9525`; Ceres `2c6ac5e1c6841122eb9b0b6ab27330eaf7f806b1ad9083e6b7c42860ee79e067`.

Final database: `LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3`
SHA-256: `f25681e27ec3beb320c4983f4a59436f8471e8322208157039be0d21ecea6f53`
Whole semantic digest: `382f7871cdfc42526eddcc84bd17fcfdd1a6a78cafa129c5feb21546cdfa8581`
67P digest after: `9e4139deb7182ce4c87176bc27e3510ffb075421e34cbca7bdb5a2a700ad9525`
Ceres digest after: `2c6ac5e1c6841122eb9b0b6ab27330eaf7f806b1ad9083e6b7c42860ee79e067`
Europa digest: `730378a6094082f8afbe23b41b213989e2552520801074d3387beb5d67c8b07d`

Existing-body non-interference passed exactly for 67P and Ceres. SQLite integrity and foreign keys pass. Preferred facts: 67P=0, Ceres=0, Europa=0, total=0. Europa campaign has 17 explicit reviews: PROMOTE=11, HOLD=1, SCHEMA_LIEN=5. Every candidate assertion remains in the promotion ledger with raw JSON/hash and provenance references. No schema change was made.

Body counts (fact / observation / material / model / activity): 67P 4 / 4 / 0 / 0 / 2; Ceres 8 / 8 / 3 / 1 / 0; Europa 2 / 10 / 1 / 2 / 3. Six Europa frontier records remain unresolved. Body-neutral retrieval, provenance, regional/material/model/activity/frontier/history queries and shared-GM lineage separation passed. Narrator output preserves candidate/unknown language and adds no predicates. Fourteen adversarial promotion mutations and 25 Gate A hostile attacks were refused.

## Replay, limitations, and liens

Two fresh builds were byte-identical; reverse SQL row insertion preserved whole-database and all three body digests. Alternate ordering of entire body insertion was not run because Ceres/67P were not rebuilt; their frozen database was used unchanged. Nonblocking research liens: thermal primary analysis unavailable, calibrated Europa radiation analysis unavailable, complete shell-model comparison open, limited independent specialist review, and identity-blindness exclusion documented. Promotion retains five schema liens. External raw artifacts remain in the Research Lab at the recorded immutable commit and were hash/size checked during build.
