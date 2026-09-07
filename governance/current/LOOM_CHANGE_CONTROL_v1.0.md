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

Required for material canon change.

CCR statuses:

- `PROPOSED`
- `UNDER_REVIEW`
- `APPROVED_FOR_IMPLEMENTATION`
- `REJECTED`
- `DEFERRED`
- `SUPERSEDED`
- `IMPLEMENTED`

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

A canon promotion requires:

1. CCR approved;
2. exact affected governing files identified;
3. amendment/supersession relationship explicit;
4. downstream dependencies classified;
5. baseline/authority manifest update planned;
6. hash/validation update planned;
7. required engineering/runtime follow-ons opened or explicitly deferred;
8. WALTER assurance completed at required level.

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
- exceptions are additive records, not rewrites.
