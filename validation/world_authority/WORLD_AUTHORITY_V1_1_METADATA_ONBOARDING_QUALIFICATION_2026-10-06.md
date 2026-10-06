# World Authority V1.1 metadata onboarding — qualification record

**Primary change class:** `class:data`
**Proposed successor standing:** `WORLD_AUTHORITY_V1_1_METADATA_ONBOARDING_QUALIFIED`
**Freeze state:** candidate successor branch only; no merge, release or tag.

Authority bootstrap: live `origin/main` and the frozen
`world-authority-v1-2026-10-06` tag both resolved to
`03c03d4448c814a5edfdfdf1e1f4024f247ecd19`. The implementation was made
on `data/world-authority-v1-1-metadata-onboarding` from that commit. The
accepted SQLite source remained SHA-256
`72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`.
The V1 SQL migration remained SHA-256
`3791cf91332f5c7d979dc2a8a590be4bacf3ba8ec932493f07edf510fb9cffe1`.
No role grant, RLS policy, scientific source row, Build 6D or Build 6E runtime
file changed.

The V1 schema already owns the required location, containment, unit and lexical
time rows. The store lacked a public writer for them. The successor adds only
`install_authored_site_metadata` and `install_fixture_time_support`, each bound
to an authenticated `wa_science_writer` session and existing immutable,
SERIALIZABLE exact-match machinery. The first writes exactly one authored site,
one authored local feature, two warranted `CONTAINS` edges and one
uncharacterized structural model unit. It verifies the empirical parent is a
source-snapshot location with the deterministic source identity. The second
writes only the lexical time helper for the existing independently governed
fixture-admission operation. It does not admit science. A separate governor
transaction is still mandatory; a failed governor step leaves inert metadata.

The final designated qualification ran from zero on two freshly provisioned
PostgreSQL 18.6 clusters with pinned UTF8/C/UTC settings. E01–E28 and S01–S12
passed: 40/40 required identifiers, no errors or skips. The real-login suite
ran 20 tests, including four new hostile onboarding tests: exact repeat and
candidate preservation, collision/rollback and forged-parent rejection,
time-helper separation from admission, and unauthorized principal denial.
Four store identity regressions passed. The machine report says
`implementation_unchanged_during_run=true`; it records all implementation
hashes, source hash, environment, cluster inventories and exact required IDs.
All 2,726 source rows and 256 source columns remained covered; the migrated
baseline still has zero science admissions. Synthetic admission/security rows
existed only in the disposable security database.

The sealed machine evidence is
`WORLD_AUTHORITY_V1_1_METADATA_ONBOARDING_QUALIFICATION_2026-10-06.json`,
SHA-256 `93381125a50db8c7b2df749180bf81b43fdc764a6ea3a01a662e873e443a8b54`.
It binds `store.py` SHA-256
`67716981db11f2b02b4844e0f285c4c33a74ebe2196e47228530bceda149e8b6`,
security tests SHA-256
`5d710a14fc70a608d504e465a57691585f0ac5f26be75e851fae12a18522cac0`,
and successor contract SHA-256
`2476d1a521518364bcdcacfa6d0a1e6efe75e3d668fe99085ca8beddb830f63b`.
`git diff --check` was clean. An initial attempt lacked the worktree-local
`.venv` link; another exhausted host disk because old disposable qualification
containers were still running. Both were environment failures. The final
fresh-from-zero PASS followed worktree environment setup and disposal of only
old `loom-wa-qual-*` containers; neither failure was counted as qualification.

**Build 6E DLD correction required:** The preserved Cabeus catalog row is
`location_kind=SITE`, `original_region_type=LOCAL_SITE`, not a `REGION` row.
References to a Cabeus “region” as a database type must become “empirically
identified Cabeus source location (LOCAL_SITE).” The authored child site may
be related by a separately warranted `CONTAINS` edge, but that edge does not
extend source scientific support or make the fictional feature observed.
The 6E handoff must call the two new World Authority store operations through
an independently controlled metadata/qualification route before the governor
admission and WORLD generation; it must retain the exact owner-authored
manifest bytes for audit and receive no science-writer credential in runtime.

Recommended successor tag after separate review and main promotion:
`world-authority-v1-1-2026-10-06`, pointing to a verified authoritative-main
merge commit. The frozen V1 tag remains unchanged. No successor tag is created
by this branch.
