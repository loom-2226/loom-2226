# LOOM 2226 — Change Control v1.0

**Status:** DRAFT — GOVERNING AFTER PR #24 MERGE  
**Parent constitution:** `governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md`

## 1. Purpose

Define how a LOOM idea, finding, defect, research result, canon proposal, engineering change, runtime/data change, asset change, governance change or exception moves from discussion into repository authority.

No chat message is itself a change record.

## 2. Required change identity

Every substantive change must identify:

- change class;
- workstream/parent issue;
- current authority tier;
- intended mutation scope;
- explicit non-scope;
- affected dependencies;
- canon impact;
- runtime/data/SQLite impact;
- asset/media/3D impact;
- tests/qualification required;
- frozen/preregistered impact;
- rollback/recovery method where relevant;
- promotion target.

## 3. Normal transition types

### 3.1 Research finding

Research may produce:

- supported direction;
- null result;
- failed/inconclusive result;
- engineering/canon inconsistency finding;
- new hypothesis;
- new instrument/method.

Research does not directly rewrite canon.

### 3.2 Canon Change Request (CCR)

Material canon change requires the formal repository lifecycle under `governance/changes/`.

Durable CCR authority is the machine-readable record plus `CCR_REGISTRY.yml`, not the chat or GitHub issue alone.

CCR IDs use `CCR-YYYY-NNNN` and are never reused.

Statuses:

- `PROPOSED`
- `UNDER_REVIEW`
- `APPROVED_FOR_IMPLEMENTATION`
- `REJECTED`
- `DEFERRED`
- `IMPLEMENTED`
- `SUPERSEDED`

`APPROVED_FOR_IMPLEMENTATION` authorizes a controlled `class:canon` PR. It does **not** itself make the content governing canon.

`IMPLEMENTED` is recorded only after the authorized change lands on authoritative `main` and required authority/baseline/hash/validation obligations are complete.

Approval changes authority disposition; it does not retroactively upgrade the source's evidentiary status.

Formal files:

- `governance/changes/README.md`
- `governance/changes/CCR_REGISTRY.yml`
- `governance/changes/CCR_SCHEMA_v1.0.yml`
- `governance/changes/CCR_TEMPLATE_v1.0.yml`

### 3.3 Engineering change

Engineering interprets/implements canon constraints and may raise upward findings.

### 3.4 Runtime/data change

Runtime/data changes implement governed behavior/state and must declare compatibility/migration impact.

### 3.5 Asset/media/3D change

Derived representation changes must state whether they are purely visual/representational or consume/update authoritative engineering parameters.

### 3.6 Governance change

Governance may change process/control semantics but must not smuggle substantive canon change through process documentation.

## 4. Frozen research change rule

If the target is frozen/preregistered:

- mutation is forbidden;
- improvement becomes successor work;
- existing SHA/design/verdict record remains unchanged;
- a new experiment must state what it changes and why.

A CCR that materially relies on an undispositioned frozen/preregistered result may be created but may not advance to `APPROVED_FOR_IMPLEMENTATION`.

## 5. Dependency invalidation

A material upstream change must classify each known downstream component as:

- `UNCHANGED_COMPATIBLE`
- `REVIEW_REQUIRED`
- `REVALIDATION_REQUIRED`
- `MIGRATION_REQUIRED`
- `BLOCKED_PENDING_UPSTREAM`
- `SUPERSEDED`

The change may not simply state 'no impact' without checking declared dependencies.

## 6. Canon promotion

A canon implementation requires:

1. exact registered CCR ID(s);
2. CCR status `APPROVED_FOR_IMPLEMENTATION`;
3. exact affected governing files identified;
4. amendment/supersession relationship explicit;
5. downstream dependencies classified against the component map;
6. baseline/authority manifest update planned;
7. hash/validation update planned;
8. compatibility update assessed;
9. required engineering/runtime follow-ons opened or explicitly deferred;
10. WALTER assurance completed at required level.

After merge to authoritative `main`, the CCR is updated to `IMPLEMENTED` with the implementation PR/commit and completed obligations.

If implementation materially exceeds the approved CCR scope, stop and return to change control rather than stretching the old approval.

## 7. Exception / override record

Material exception IDs use:

`GEX-YYYY-NNNN`

Minimum record:

- ID/date;
- rule/finding being overridden;
- requester;
- decision authority;
- rationale;
- evidence known/missing;
- risk accepted;
- scope/time limit;
- affected components;
- recovery/monitoring condition;
- closure criteria.

### Advisory findings

`WATCH` may usually proceed without formal exception if no governing rule requires action.

`REVIEW_REQUIRED` may proceed only when the relevant rule permits risk acceptance and rationale is recorded for material cases.

### HOLD

Proceed only if a governing exception path exists and is recorded.

### BLOCK

Cannot be bypassed by chat approval alone. Formal exception mechanism is required, and some blocks may be declared non-overridable by their specific rule.

## 8. WALTER independence

WALTER may create or update an assurance finding independently of Kevin/Sol intent once implementation exists.

Kevin or Sol may not edit the historical content of a WALTER finding to make it pass.

They may:

- remediate the issue;
- add evidence;
- challenge the finding with source/test support;
- record an allowed exception.

The original finding remains auditable.

For canon promotion WALTER may verify CCR existence/registration/status deterministically. During governance adoption this remains advisory; later it is a candidate hard gate.

## 9. Chat/session behavior

A chat may explore freely.

Before authoritative mutation, the session must:

- load current workstate;
- verify relevant refs;
- identify change class/scope;
- check freeze/dependency constraints;
- determine whether a change record/CCR/exception is required.

## 10. Merge/promotion boundary

The strongest controls belong at promotion boundaries rather than every local edit.

Development/workstream branches remain fast-moving within declared scope.

Promotion toward `main`, canon, released data, authoritative geometry or published baseline receives stronger assurance and validation.

## 11. Historical integrity

Change control must never erase inconvenient history.

- rejected CCRs remain rejected records;
- failed tests remain recorded failures;
- superseded files remain archived;
- frozen SHA history remains immutable;
- old release hashes remain old release hashes;
- exceptions are additive records, not rewrites;
- proposal approval does not retroactively upgrade evidentiary status;
- `APPROVED_FOR_IMPLEMENTATION` is not rewritten to pretend the canon was already governing before implementation.
