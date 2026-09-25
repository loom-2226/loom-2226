# SF-PROMOTE-01 — 67P promotion qualification

Result: **SF_PROMOTION_PASS_WITH_LIENS**

The frozen ARP-QUAL-01B structured campaign was promoted deterministically into a reusable multi-body Solar Facts candidate database. No new 67P research was performed.

## Frozen inputs

- Campaign SHA-256: `2f5637c36fa657017f6668b42a7f05f356ebdd0d4db8953be51a0bffca0f38fa`
- HCQ Ceres SHA before/after: `0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`
- Body identity: `COMET_67P`, referenced from `loom_solar.body`; no identity duplicate created.

## Output

- Database: `LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3`
- Database SHA-256: `0c4da54dc8f48cd2041ce75aefcea36f5e0d3436c3ceeacf8c0a330d2f5c5e95`
- Schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_MULTI_BODY_v0.3-R1`
- Semantic digest: `a9433ce68ce74a426540359e8e41b78627263f185436c376c8ee5a7a6da6643a`
- Table counts: `{"activity_fact": 2, "body": 1, "body_model_product": 1, "epistemic_frontier": 8, "fact": 4, "fact_input": 1, "material_evidence": 0, "observation": 4, "preferred_fact": 0, "promotion_assertion": 13, "promotion_review": 13, "region_model_product": 0, "source": 9, "source_artifact": 9}`
- Dispositions: PROMOTE=13; HOLD=0; REJECT=0; SCHEMA_LIEN=0; DUPLICATE=0; OUT_OF_SCOPE=0.

## Preservation and semantics

All 13 assertions remain in `promotion_assertion` with canonical raw JSON, raw SHA-256, source/artifact references, claim kind, evidence class, scope, resolution, temporal context, uncertainty, normalization and independent lineage. Four scalar facts (GM, MASS, BULK_DENSITY, POROSITY), four observations, two activity records, and one shape model product are represented in ordinary Solar Facts tables. Material evidence is zero: the frozen assertions describe surface/coma composition and are not converted into a material inventory.

BULK_DENSITY has one structured lineage edge to the unambiguous MASS input; no unsupported volume fact was invented. Porosity remains a 72–74% range with no midpoint. Thermal evidence retains a 15 m/pixel footprint and time context without a temperature scalar. Coma volatile observations remain coma observations; activity and production remain models. Frontier UNKNOWN/SOURCE_NOT_FOUND states are stored in `epistemic_frontier`, not as physical zeros or absent-world claims.

## Provenance

Nine source records and nine artifact records are retained. Raw bytes are not duplicated in SQLite; the frozen campaign artifact hashes and byte counts are retained. The repository promotion worktree initially lacked the raw files, so the exact already-acquired artifacts were restored from the prior qualification worktree and hash-verified by the existing 67P transfer suite.

## Hostile qualification

Passed checks for coma→nucleus, surface→interior, local/global, global model→local measurement, time-bounded→timeless, model→observation, interpretation→direct, range midpoint, UNKNOWN→zero, missing source→absence, duplicate lineage, invalid disposition, preferred fact, Phase-4 and downstream judgment contamination.

Narrator and downstream-read-only query checks pass. No Phase-4 tables or state vectors are written. No preferred facts, canonical/current promotion, engineering/resource/economic/habitation/transport/CIVPROP state is written.

## Liens / limitations

- `SCHEMA_LIEN`: v0.3-R1 does not natively carry every ARP field in ordinary fact tables; the generic promotion ledger preserves the complete assertion envelope.
- `PROVENANCE_LIEN`: raw artifact bytes remain externalized by repository policy; immutable hashes/byte counts and source/artifact relation are native.
- Orbit is not promoted: the frozen campaign explicitly has `SOURCE_NOT_FOUND` for the orbit evidence question and this is not evidence that 67P lacks known orbital geometry.
- No new Ceres migration was performed.

## Authority firewall

All promoted scientific facts remain `CANDIDATE`; `preferred_fact=0`. No new scientific discovery, canonical 67P authority, Phase-4/5 state, or downstream judgment was introduced.
