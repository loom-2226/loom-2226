# World Authority V1.2 — run-scoped execution transaction

Primary class: `class:data`. Additive successor to frozen World Authority V1.1
at main `c8e88f2d604a2149acce02d161bdd704932211e5`. World Authority remains
independently governed; Build 6E is FIRST_RUNTIME_CONSUMER_NOT_OWNER and remains
BLOCKED / UNQUALIFIED until its separate implementation/qualification. This
contract does not implement or promote Build 6E. Frozen V1/V1.1 tags and records
remain historical evidence. The V1 schema/identity profile stays V1.

## Finding and alternatives

The adopted Build 6E DLD §10 requires a run lock and committed-head read before
Agent input preparation and runtime execution, held through atomic persistence.
V1/V1.1 persist_epoch checks SERIALIZABLE isolation and obtains precisely that
run lock, but only during persistence; its caller-bound-before-kernel precondition
had no bounded public implementation. That requirement is legitimate: the durable
causal/physical prefix defines the working runtime state and authorized inputs.
Post-execution stale-head rejection preserves database integrity but alone does
not satisfy the adopted pre-execution boundary.

Alternatives: (1) relax the DLD to optimistic post-execution rejection, rejected
because it changes the adopted concurrency contract; (2) Build 6E SQL/connection
or a separate lock, rejected by independent authority ownership; (3) generic
transaction callback/connection yield, rejected by the bounded interface rule;
(4) a new schema/lease table/scheduler, unnecessary because the existing advisory
key, immutable projections and persist_epoch already implement the semantics.
Chosen: one connection-owning context in store.py composed with the unchanged
V1 persistence validator. No new database records, role grants, DDL or migration.

## Exact public surface

```
with run_epoch(service_name: str, run_id: str) as epoch:
    head = epoch.head             # (envelope_id, envelope_hash, event_ordinal) | None
    prefix = epoch.read_replay_prefix(
        input_snapshot_ref=..., code_contract=..., code_tree_sha256=...)
    physical = epoch.load_bound_world(
        binding_key, context='REALIZED', effective_time=...)
    # trusted consumer prepares admissions/safe snapshot and runs its original kernel
    epoch.stage_epoch(epoch_id, expected_previous_head, fixed_column_rows,
                      terminal_artifact_refs)
# clean exit calls legacy persist_epoch, validates, COMMITs, then closes connection
assert epoch.status in ('COMMITTED', 'ALREADY_MATCHED')
# only now may the consumer expose its completed result
```

The two reads are optional and fixed to this run; their inherited identity,
context, effective-time and original-byte validation remain mandatory. A proven
absent execution yields `None` from the prefix read; an existing execution with
unequal requested code/input identity fails. `head=None` means there is no
committed causal envelope, not that stock/belief/time is zero or known. An
existing execution can have no head in inherited structural fixtures; this is
not silently reclassified as a qualified runtime genesis. New-run binding and
actual opening originals still first commit together in the complete epoch batch.
No independent genesis writer or physical reducer is introduced. Existing-run
physical histories are read through load_bound_world in this same snapshot.

The returned object has no public connection, SQL, cursor, arbitrary callback,
role switch, table-select, scientific-admission, generic commit or rollback route.
Service names accept only letters/digits/underscore/hyphen, not conninfo/options.
World Authority opens the connection from an operator-managed libpq service
configuration, does not accept a caller connection or connection factory, and
never pools it. The operator supplies secrets; the runtime worker/Agent gets no
service configuration, credential, session or hidden WORLD projection.

The only mutation submission is the already closed wa_run/wa_info epoch batch.
Staging copies it and freezes the session's input/read surface; it does not write
or commit. Runtime/admission projections and safe-pointer changes occur together
at context exit through unchanged persist_epoch. A duplicate stage/read after
stage, session reuse, foreign-thread access or failed read cannot initiate another
transition. A swallowed read failure poisons the scope and clean exit fails.
An exception anywhere in the scope, including after staging, discards the batch.
Normal exit without a staged complete epoch fails rather than returning an
apparently successful uncommitted result. `status` is unavailable until COMMIT.

## Authorization and epistemic boundary

Entry verifies the authenticated session user has BOTH wa_runtime_writer and
wa_admission_writer memberships, and is not superuser/BYPASSRLS. Other World
Authority service memberships, including owner, science writer/governor, WORLD
writer, reference reader, auditor, Agent reader and Agent view owner, are rejected.
Run writers are trusted execution services under the inherited authority model,
not untrusted Agents; V1 does not provide tenant/per-run credential ACLs and V1.2
does not invent them. The chosen run_id is immutable within the scope. All reads
and batch rows bind to it; unequal run/world/epoch/provenance remains fail-closed.
Separate governed science/reference/WORLD bootstrap routes remain independent,
with explicit immutable science cutoffs. No scientific admission operation is
available here. Runtime information/admission receipts are part of the single
epoch batch; this does not grant science-governor rights or alter source standing.

Agent containment remains PostgreSQL grants/RLS and login-bound safe views.
Python reflection/private-memory access by a compromised trusted process is not
an Agent sandbox; the consumer must never pass this session to a worker. The
bounded API eliminates accidental SQL/connection escape, not DBA/service compromise.
No new hidden state becomes readable by an Agent login.

## Lock, snapshot, transaction and failure semantics

The exact inherited key is `hashtextextended('wa_run:' + run_id, 0)`; no UUID,
random draw, wall time, new lock table or Build 6E lock enters authority. Entry:
1. open a dedicated autocommit connection and verify exclusive service authority;
2. acquire a SESSION advisory lock on that same key in an autocommit statement;
3. after that statement completes, BEGIN ISOLATION LEVEL SERIALIZABLE;
4. SET LOCAL ROLE wa_runtime_writer and acquire transaction ownership of the same
   advisory key; read/pin the ordered latest causal head;
5. retain this connection, transaction and key through fixed reads, consumer
   runtime and stage/legacy persistence; COMMIT then CLOSE.

The session ownership is a necessary snapshot bridge, not an alternate lock:
PostgreSQL takes a SERIALIZABLE statement's snapshot before waiting inside
pg_advisory_xact_lock. Beginning SERIALIZABLE and only then blocking can retain
a snapshot predating the preceding writer's commit. The autocommit wait occurs
before the SERIALIZABLE snapshot is established, and conflicts with both legacy
transaction locks and V1.2 session locks on the identical resource. Transaction
ownership is retained for inherited semantics; session ownership is released only
by close after commit/rollback. Entry failure, scope error, read/persistence error,
connection loss and process death release the resource. There is no shared pool
which could retain a session lock. Lock timeouts, if configured, are operator
connection settings; no consumer-supplied SQL or timeout knobs are added.

New-run expected_previous_head is None. For a new epoch on an existing run it
must equal the pinned head's first two cells; unchanged persist_epoch rejects
stale/unequal predecessors and non-increasing ordinals. Exact repeat may target
an earlier already-committed epoch: its predecessor is checked against history,
all immutable originals/projections/envelope/trace membership must match, and
current principal bindings are never rewound. It returns ALREADY_MATCHED only
after commit. An unequal replay fails; no partial repair/upsert is added.

Same-run cooperating writers serialize on the same resource; a waiting V1.2
writer pins the preceding completed head after entry. Different runs use separate
keys and can execute while another run holds its lock. Inherited 64-bit hash
collisions and PostgreSQL SERIALIZABLE predicate conflicts can still block/abort;
these are existing database limits, not a global lock. The store never retries a
runtime itself. On serialization/deadlock/connection/lost acknowledgement, consumer
discards mutated working state, reads/replays the complete durable prefix through
a new session, and applies its adopted bounded retry policy. An ambiguous COMMIT
acknowledgement cannot be advertised as rollback: either the complete epoch exists
or none does. New session exact-match replay resolves it. Trusted DBA/direct-role
writers bypassing this protocol are outside cooperating-writer assumptions; roles
are not weakened and the regression still exercises their SQL guards.

## Provenance, compatibility and 6E amendment

No causal transition is synthesized merely for lock acquisition. Committed
original bytes, heads, trace edges, source standing, authorization, time fields,
FK/type/UNKNOWN distinctions and deterministic identities retain V1 semantics.
The public legacy persist_epoch and all other V1/V1.1 operations remain unchanged.
The store imports no Offworld module. Four historical identity vectors and all
E01–E28/S01–S12 plus V1.1 onboarding tests remain mandatory.

Build 6E DLD §10 and handoff step 5 must name this run_epoch composition and
stage-before-exit/status-after-exit ordering instead of asking Build 6E to BEGIN,
SET ROLE, acquire a lock or own a raw connection. Do not alter their semantic
sequence, causal scope, frozen 6D behavior, source science or Cabeus SITE/LOCAL_SITE
correction. The existing-run bound physical read and replay read use the session;
first opening rows remain in the first atomic batch. The consumer keeps original
kernel conservation/trace/admission/serializer validation. No Build 6E artifact is
modified or qualified by this successor workstream.

## Qualification and recovery

Focused real-login T01–T13 cover new/existing pinned heads and atomic opening;
same-run blocked waiter/fresh post-commit head; different-run overlap; stale-head
rejection; runtime errors before/after staging; late persistence rollback across
runtime/information/ACL; old-epoch exact repeat/current pointer/collision; SQL/run/
role/session escape; exclusive credential denial; run-bound replay/physical reads
and safe-view visibility; exact lock/transaction lifetime; legacy interoperability;
poisoned scopes, staged-copy immutability and server termination. Complete inherited
qualification executes on two fresh pinned PostgreSQL 18.6 UTF8/C/UTC clusters,
with original source/DDL/dependency hashes, all 2726 forensic rows, all 256 column
dispositions, zero baseline science admissions and deterministic export/repeat.
A failed test/environment iteration is not PASS; no tests are weakened or skipped.
