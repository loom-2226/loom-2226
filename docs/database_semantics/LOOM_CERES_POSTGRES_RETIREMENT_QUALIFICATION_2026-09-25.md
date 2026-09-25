# Ceres PostgreSQL retirement qualification

This `class:data` change retires the obsolete Ceres PostgreSQL projection from
the integrated development authority `loom_dev`. It does not alter Earth,
Solar, Timeline, or the Earth Narrator surface.

## Qualified preconditions

- Main authority at bootstrap: `ed6ad80ede743ab4dc527f4b6e5c5f3149773ae9`.
- Ceres snapshot: `ceres-v1-0231e5f7da744728ab5021268b6f239b`, pre-state `VALIDATED`.
- Ceres consumer identity: `520af8926fddf5bcfd32f8937dfe92b37d55b33e`;
  query SHA `4a8845a8ccc84ec83ade1aaaa734f6a850fe6bcae8608e2728f1ab65d834b46b`.
- Ceres-only rows: WORLD 26, CIV 486, MEDIA 22, field semantics 293,
  row lineage 534.
- Dedicated archive payload fingerprint: `4fc38434f93aed542384f95a8e14090d2dd8a8719dbb877003abc7ebcacb4ff9`.

The exact per-table counts and complete deterministic Earth contract are in
`EARTH_AUTHORITY_PRESERVATION_PRE_CERES_RETIREMENT.json`.

## Gates

| Gate | Result |
| --- | --- |
| Dedicated Ceres archive restore/replay | PASS; exact payload fingerprint match |
| Full pre-cleanup backup restore | PASS; Earth PRE fingerprint equals restored fingerprint |
| Disposable retirement migration | PASS; no Ceres snapshot, compatibility schema, or legacy Ceres schemas remain |
| Earth data/schema/metadata/provenance/narrator PRE→POST | EXACT PASS |
| Earth existing qualification | PASS; 47,637 demographic rows, 2,657,718 cohort rows, 16,080 economic rows, 160,800 sector rows, 643,200 asset rows, workforce 80/80 |
| Timeline qualification | PASS; snapshot `timeline-v0-1-0232bf23494f-20260925`, `VALIDATED`, 43 milestones |
| Solar regression | PASS; 8 PostgreSQL integration tests and contract tests |
| Constraints / foreign keys | PASS; zero unvalidated constraints |

## Retirement migration

Migration: `011_retire_ceres_postgres`.

The migration pins snapshot identity, consumer identity, semantic/contract
hashes, exact pre-cleanup counts, source reachability, and all Ceres-only
legacy tables. It enumerates compatibility views and dependent legacy objects;
it uses no `CASCADE`. Any unexpected retained row, dependency, or shared
control state aborts the transaction.

The legacy SQLite/recovery sources remain outside PostgreSQL and are recorded
in the durable forensic archive. Ceres is operationally retired, not silently
reinterpreted as a future authority.
