# World Authority V1.2 run transaction — architectural and qualification record

Primary change class: `class:data`.
Candidate standing: **WORLD_AUTHORITY_V1_2_RUN_TRANSACTIONS_QUALIFIED**.
Scope: independently governed World Authority store/qualification only.
Status: qualified local successor; no push, PR, main promotion, merge or tag.
Build 6E remains BLOCKED / UNQUALIFIED; it is the first runtime consumer, not owner.

## Authority and scope

Live GitHub bootstrap verified authoritative main
`c8e88f2d604a2149acce02d161bdd704932211e5`, matching frozen V1.1 tag target.
V1.1 tag object is `953e6cf076219e204185ece02f2c4fc71aa27082`.
Original V1 tag object is `3127591cd37ef834983cae3932a5bad069685091`, with target
`03c03d4448c814a5edfdfdf1e1f4024f247ecd19`. Neither tag is changed.
V1.1 PR #368 is MERGED; its qualified implementation is
`0b4b2432522ace6d40105fb1d2a0d3b98dd825d9`.
This local branch starts directly from authoritative V1.1 main; the enclosing
Git commit identifies the exact successor implementation/evidence combination.

Read authoritative start/workstate, authority model, research boundary, change
control, WALTER patrol and scoped src/data operating rules; read live V1/V1.1
store contracts, actual implementation, sealed V1.1 machine/security evidence,
and adopted Build 6E DLD §10 and implementation handoff step 5. Those artifacts
agree that WORLD/science persistence belongs to World Authority, runtime
execution belongs to the qualified causal kernel, and the consumer owns no SQL.
No canon, scientific content, frozen 6D or Build 6E file is included in this change.
Source/DDL, all SQL profiles, identities, grants and RLS remain byte-identical.
Recovery: use the unchanged frozen V1.1 store; no data migration/reversal is needed.
Existing V1/V1.1 consumers are UNCHANGED_COMPATIBLE. Build 6E remains
BLOCKED_PENDING_UPSTREAM until separate successor promotion and consumer work.

## Architectural finding and minimum contract

The DLD correctly requires a run lock/current committed-head read before preparing
admitted inputs/executing the kernel. Legacy persist_epoch obtains the same key
only when called at persistence time; its documented pre-execution caller-bound
transaction could not be opened through a bounded public API. Relaxing the DLD
would change the adopted concurrency contract; consumer SQL, a separate 6E lock,
generic callback or new lease schema would cross or unnecessarily broaden the
independent authority boundary.

The successor adds one public run_epoch(service_name, run_id) context in existing
store.py, with a private single-use session implementation. It owns the connection,
verifies exclusive runtime+admission membership (rejecting other WA roles,
superuser/BYPASSRLS), acquires the exact inherited advisory key, starts SERIALIZABLE,
pins the latest causal head, and supplies only bound replay/physical reads and
stage_epoch. No connection, SQL, cursor, role switch, generic commit or science
admission is returned. Staging copies the batch; successful context exit calls
unchanged persist_epoch and publishes status only after COMMIT. Errors before/
after staging or late persistence errors roll back/close. No kernel execution,
retry, world generation or additional state engine exists in the store.

PostgreSQL SERIALIZABLE snapshots are acquired before a blocking lock SELECT
returns. Consequently entry acquires SESSION ownership of the SAME existing
`hashtextextended('wa_run:'+run_id,0)` resource in an autocommit statement before
BEGIN, then transaction ownership inside SERIALIZABLE. It holds that resource
through persistence/commit and closes the dedicated nonpooled connection to
release session ownership. This is a snapshot bridge using the existing lock,
not a second lock namespace. A waiter therefore reads after the preceding commit;
legacy transaction-lock writers conflict on the identical key. Different runs
have no global lock. Ordinary PostgreSQL SSI may still reject a cross-run commit;
consumer must discard/reconstruct the working runtime and retry under a new scope.
No store callback executes/retries consumer code. An ambiguous commit acknowledgement
requires complete prefix/exact-match reconciliation, never an assumed rollback.

## Qualification procedure and results

Designated command (no production/default DSN):

```
.venv/bin/python tools/qualify_world_authority.py --provision-docker \
  --source /home/ubuntu/LOOM_WORLD_SCIENCE_DOC/simulation/offworld_mvp/world_science/lab_v0_1/LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3 \
  --output /tmp/loom-world-authority-v1-2-qualification-sealed --ports 55740 55741
```

Two genuinely fresh PostgreSQL **18.6** clusters were provisioned from the frozen
image digest. Both used UTF8, C collation/ctype, UTC and
standard_conforming_strings=on, pinned Python 3.12.3/psycopg 3.2.10/libpq 170005.
- `loom-wa-qual-bfd00974f6`, port 55740.
- `loom-wa-qual-9c12c36b76`, port 55741.

PASS: E01–E28 plus S01–S12 and T01–T13: **53/53 required identifiers**.
**98 test executions**: 28 ETL + 33 real-login security/onboarding/transaction tests
on EACH fresh cluster + 4 store identity regressions. Zero errors, skips or failures.
Implementation unchanged during qualification; all 19 measured files still match
the sealed hashes. Both clusters passed all inherited V1.1 onboarding behavior.
All 2,726 forensic source rows, all 256 source columns/dispositions, exact lexical/
NULL/UNKNOWN/provenance/candidate representation, target reconciliation, stable
identity vectors, deterministic export/repeat, zero baseline science admissions,
SERIALIZABLE guards, science guards, RLS and original/hash guards passed.
Migration remains MIGRATION_QUALIFIED_SCIENCE_CANDIDATE_PRESERVED; inherited metadata
onboarding guarantees remain WORLD_AUTHORITY_V1_1_METADATA_ONBOARDING_QUALIFIED.
Synthetic security admission rows occur only in isolated security databases.

| ID | Behavioral evidence on both clusters |
|---|---|
| T01 | New run has proven absent execution/head; opening remains invisible before exit. Existing head/prefix is pinned; exact repeat returns ALREADY_MATCHED. |
| T02 | PostgreSQL advisory wait observed for second same-run login; it enters with E0/hash then commits E1 referencing that exact hash. |
| T03 | Different run COMMITs while first run retains its lock/transaction. First receives SSI SerializationFailure; zero partial state is proved, fresh prefix/batch reconstruction commits. |
| T04 | Stale expected predecessor fails; counts/head remain unchanged and lock releases. |
| T05 | Propagated runtime failure before or after staging leaves no execution/artifact/envelope/snapshot. |
| T06 | Late terminal trace failure rolls back inserted runtime originals, information snapshot and actual principal-binding change. Agent view remains its previous snapshot. |
| T07 | Exact repeat of an older epoch preserves later current pointer; unequal replay fails. |
| T08 | SQL/conninfo, arbitrary table/context, cross-run rows, foreign-thread execution/exit, setters, read/double-stage after staging and session reuse are rejected. No public connection/cursor/SQL/transaction escape exists. |
| T09 | Agent, reference, governor, science/WORLD writer, auditor, runtime-only, admission-only, admin and mixed execution+WORLD principals cannot enter; no lock leaks. |
| T10 | Bound physical/replay reads compose in the same scope; safe pointer/snapshot changes become visible only after COMMIT. Real Agent login still cannot select private runtime/WORLD/info tables. |
| T11 | Actual PostgreSQL transaction/snapshot and held advisory resource persist through runtime; unstaged normal exit fails/rolls back; commit/abort release locks. |
| T12 | Existing legacy xact-lock writer blocks new session on the identical key; post-commit session pins it, old/new persist and exact repeat interoperate. |
| T13 | Caught failed read poisons scope; caller mutation after staging cannot alter payload; terminated backend produces no partial state or retained lock. |

Both T02 runs recorded predecessor
`QUAL-T02:E0 / 6d3a4721fc2d3f99c3fa675c36050c95f1cd1f8013b995d7836c95016aa04264 / ordinal 0`
and successor
`QUAL-T02:E1 / f335929510ab401cd494e8c195cedda071a43be77bbdaaabe88d632b785ad4b9 / ordinal 1`.
Both T03 runs explicitly recorded different-run overlap, initial SerializationFailure
and final fresh-scope COMMITTED; no swallowed failure is counted as a committed epoch.
`git diff --check` is clean. No functional change occurred after qualification.

The first full development run was FAIL: its T03 test proved overlap but failed to
exercise the required SSI discard/replay behavior. This actual failure is preserved
at `/tmp/loom-world-authority-v1-2-qualification-dev1/WORLD_AUTHORITY_QUALIFICATION.json`,
SHA-256 `7265d885dcd470b94fd5c1977381e2db2a9210605b95ed87d96ee8c61a73066d`.
The corrected test still proves actual concurrent execution, zero partial state,
discard/new pinned prefix/rebuilt batch and eventual successful commit; it does not
require PostgreSQL to waive SERIALIZABLE enforcement. The final entire protocol
was repeated from zero on two new clusters rather than relabeling that failure.

## Hashes and security limits

Sealed machine record:
`WORLD_AUTHORITY_V1_2_RUN_TRANSACTION_QUALIFICATION_2026-10-06.json`, SHA-256
`258cf8001ac9ac7263c688bac5e089fea5cc34bb6f24abe1fdd46401f9bddf7f`.
- store.py: `9c8a18df774807d909ef59e79a8294666f51e0b3b1e04fcda25c7a2d31af54ac`.
- security tests: `bdecacdbfcfc576a83da1388c9cffad5337114d85ee4dbabeea0292af481cc21`.
- qualifier: `280dddacc2fdb62ebb96c2d7e43ff7781a578eeadd3439066c37a26c08268c7a`.
- successor contract: `b3e9ed6bfa182c9b6e4484005d188e2bfa21de76acfc1969863082fe7740041e`.
- unchanged SQL migration: `3791cf91332f5c7d979dc2a8a590be4bacf3ba8ec932493f07edf510fb9cffe1`.
- unchanged accepted source: `72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`.

No schema/migration/grant/RLS/security-definer/Agent-view change. No source science
admission, reinterpretation or re-vetting. Legacy store content is an exact byte
prefix of successor store.py; only the new bounded scope is appended.
Private Python internals are not an adversarial-process sandbox; trusted services/
DBA retain inherited inspection powers. Operator-managed service credentials never
reach workers/Agents. Advisory coordination assumes trusted execution writers use
the governed route; malicious DBA/direct-role writers and 64-bit hash collisions
remain inherited boundary limits. Connection death releases locks; lost COMMIT
acknowledgement must be reconciled by a new complete replay/exact-match scope.
Those limits do not grant consumer SQL or weaken Agent database containment.

## Required 6E handoff correction and recommendation

Amend DLD §10/handoff step 5 to compose run_epoch instead of consumer BEGIN/SET ROLE/
lock/connection operations. Build 6E executes its original kernel inside the
session, constructs/validates its complete original/domain/admission projections,
stages once, and exposes results after clean exit/status. Its adopted retry policy
must discard mutated kernel state and rebuild from a new locked prefix; SSI is
possible for different runs despite no global lock. Existing frozen 6D, scoped
science, World Authority identity profiles and Cabeus SITE/LOCAL_SITE correction
remain intact; CONTAINS never widens scientific support. No Build 6E design or
implementation file was edited in this successor.

Recommend promotion/freeze of this exact qualified local successor after separate
authorization and required repository checks. Proposed tag:
`world-authority-v1-2-2026-10-06`, pointing to a verified future authoritative-main
merge commit. No existing tag moves and no successor tag is created here.
The evidence qualifies the World Authority transaction contract only, not Build 6E.
