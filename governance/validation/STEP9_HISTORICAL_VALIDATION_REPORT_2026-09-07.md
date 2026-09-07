# LOOM 2226 — Step 9 Historical Validation Report

**Date:** 7 September 2026  
**Branch:** `governance/repository-control-baseline-v1`  
**PR:** #24  
**Status:** COMPLETE — ENFORCEMENT NOT YET ENABLED

## Purpose

Validate `loom-gate` against actual LOOM work rather than an imagined ideal repository. Step 9 is specifically intended to discover governance rules that would misclassify legitimate existing work, then fix governance rather than rewriting functional history.

The historical acceptance matrix is:

`governance/validation/STEP9_HISTORICAL_FIXTURE_MATRIX_2026-09-07.yml`

## Evidence set

The review used real repository history covering:

- PR #19 — frozen deterministic-curvature scientific qualification;
- PR #16 — preregistered matter-induced Stage-A design on hold;
- PR #21 — Navigator D2g diagnostic gravity segmentation;
- PR #22 — Navigator D2h non-authoritative gravity-aware retargeting shadow;
- PR #23 — Navigator D2i thrust/remass feasibility shadow;
- PR #6 — Android/Windows GIS/Navigator source convergence;
- PR #5 — updater v0.4 progress UX;
- PR #4 — runtime world-database hash correction;
- media release commit `0aeebdb4476a6574e93dc09834242fba54f6a109`;
- Wayfarer 3D workstream commit `062bb0a2bfd718305dc0cf92dba9e61bab909d2d`;
- PR #3 — byte-preserving canon/repository lifecycle cleanup;
- PR #2 — organized genesis baseline containing canon, runtime, SQLite and release material.

Pre-governance PRs are treated as historical evidence, not retroactive paperwork violations. Their absence of `class:*` or standardized compatibility tokens does not make the work invalid. The relevant question is whether the governing concept would classify the work correctly after equivalent metadata were supplied under the new contract.

## Findings

### 1. Frozen scientific identity is safe to harden

PR #19 remains exactly:

`314efe50875630ba4be720b4097a2ca14075e620`

PR #16 remains exactly:

`b60086d906f63211206502f23458be490902c2df`

Their preregistration/freeze identities are precise, deterministic and cheaply testable. Mutation has an unambiguous remediation: do not change the frozen branch; create successor work.

**Disposition:** LG002 and LG003 are HARD-READY, pending explicit enforcement activation.

### 2. Navigator history supports boundary-aware governance, not authority-by-directory

D2g, D2h and D2i are strong examples of technically substantive work that deliberately refused authority promotion.

D2g was diagnostic only and did not change route/campaign/guidance/remass/integrator/gravity authority.

D2h explicitly stated that its controller acceleration cap was not certified Wayfarer spare-thrust or vectoring authority. It required a subsequent propulsion/remass feasibility gate.

D2i then performed that engineering feasibility shadow while still refusing to invent gimbal/vectoring or thermal certification. Missing certification left the overall status OPEN rather than being silently promoted.

These examples demonstrate that mixed engineering/runtime work must be assessed by declared authority and dependency impact, not treated as automatically dangerous merely because several technical domains are touched.

**Disposition:** LG009 remains advisory until structured dependency-impact metadata is proven. LG010 remains advisory.

### 3. GIS/runtime convergence validates test and blast-radius discipline

PR #6 added shared Android/Windows GIS/Navigator entrypoints and large source files while keeping the frozen RC6.1 core bytes unchanged behind a wrapper. It also recorded Pixel qualification and explicitly excluded database, manifest, physics and canon changes.

This is legitimate load-bearing runtime work. A future equivalent should carry a structured class and impact declaration, but a generic path alarm should not block it merely because `src/` and `deploy/` are large.

**Disposition:** no new hard path-volume rule is added. LG009 remains advisory pending structured metadata.

### 4. Release manifest co-change is not a valid hard rule

PR #4 corrected a stale SHA-256 in the release manifest after proving the downloaded and local SQLite bytes were identical. No database bytes changed.

The media release commit changed `release_manifest.json` to add the Termux media launcher and corrected artifact metadata without inherently requiring a compatibility-manifest content change.

Therefore the Step-8 version of LG008 — "release manifest changed, compatibility file did not" — would create legitimate false positives if hardened.

Step 9 changes LG008 so a release-manifest change may be satisfied by either:

- an actual `LOOM_COMPATIBILITY.yml` update; or
- an explicit standardized compatibility disposition in the PR contract.

It remains advisory until that structured metadata has enough live examples to justify blocking.

**Disposition:** LG008 = ADVISORY_REWORKED.

### 5. Canon path-only gating was wrong and has been fixed

PR #3 is the decisive fixture.

It moved five governing canon volumes into `canon/current/`. Git recorded each as a **100% rename (`R100`) with 0 additions and 0 deletions**. The source bytes were unchanged; only the new authority index added content.

The Step-8 gate looked only for a changed path beginning `canon/current/`. That would incorrectly have required a Canon Change Request for a byte-preserving lifecycle reorganization.

Step 9 replaces that model with a Git-status-aware classifier:

- exact `R100` movement into/out of `canon/current/` is a **canon authority/lifecycle movement**, not a canon-content mutation;
- any other current-canon change is treated as a **canon content/authority mutation** and enters the CCR airlock;
- an exact lifecycle move still receives LG018 advisory review because moving a file into/out of governing authority is meaningful even when bytes do not change.

This preserves the distinction between **what the canon says** and **which unchanged file is designated current authority**.

**Disposition:** LG004/LG005/LG006 become HARD-READY for non-R100 current-canon mutations. New LG018 remains advisory until authority/baseline lifecycle metadata is structured enough to harden.

### 6. Genesis baseline is grandfathered, not a future pattern

PR #2 legitimately established the repository's organized baseline in one broad promotion containing canon, runtime sources, SQLite databases and release metadata, with validation evidence.

A future PR of the same shape would be unacceptable after governance because the repository now has explicit authority classes, compatibility records and promotion gates.

Therefore PR #2 is classified as a **NONREPEATABLE_GENESIS_EVENT**. Grandfathering preserves historical legitimacy without granting an exemption template for future mixed mega-PRs.

### 7. SQLite detection is still too crude for a hard gate

Historical LOOM uses both repository-pinned SQLite release artifacts and mutable local runtime state. A path match cannot by itself determine whether a change is:

- a byte replacement;
- schema migration;
- manifest/provenance correction;
- derived snapshot;
- local mutable state that should not be committed.

Until the data-path model distinguishes these cases machine-readably, LG012 remains advisory.

**Disposition:** LG012 = ADVISORY_PENDING_PATH_MODEL.

### 8. Agent-registry hard rules survived validation

The Step-8 self-governance incident already provided a real fixture: WALTER was initially ACTIVE before the registry contained a durable approved creation review. Walter flagged it; the rule was fixed by creating the durable review rather than weakening the check.

The deterministic subset is unambiguous:

- active-agent count must match ACTIVE registry entries;
- each ACTIVE agent must reference an APPROVED durable creation review;
- an increase in ACTIVE agent count requires `class:governance`.

Whether a proposed role genuinely deserves to be a separate agent remains a human/assurance architecture judgment and is not delegated to the hard gate.

**Disposition:** LG014 and deterministic LG015 are HARD-READY. LG016 persona-authority semantics remain advisory.

### 9. Machine parse integrity is safe to harden

Required YAML controls and the current release JSON are machine objects. Failure to parse is not a matter of opinion and has a clear remediation.

**Disposition:** LG007 and LG017 are HARD-READY.

## Step-9 hard-ready set

The following rules have earned deterministic hard-gate status **conceptually**, but remain non-blocking because `loom-gate` is still in OBSERVE mode:

- LG001 — governance-era PR primary change class;
- LG002 — frozen PR #19 SHA;
- LG003 — preregistered PR #16 SHA;
- LG004 — current-canon content mutation requires `class:canon`;
- LG005 — current-canon content mutation requires exact registered CCR ID;
- LG006 — cited CCR must exist and be `APPROVED_FOR_IMPLEMENTATION`;
- LG007 — required machine-control files parse;
- LG014 — autonomous-agent registry consistency;
- LG015 — deterministic Agent Creation Gate subset;
- LG017 — release manifest parses as JSON.

No hard rule uses LLM judgment.

## Advisory/rework set

These remain WATCH-only:

- LG008 — release/compatibility coupling;
- LG009 — downstream-impact declaration;
- LG010 — mixed canon + engineering/geometry;
- LG011 — research + canon same-PR review;
- LG012 — SQLite/schema/migration/recovery semantics;
- LG013 — vendor/dependency assurance;
- LG016 — persona/authority semantic separation;
- LG018 — byte-preserving canon authority/lifecycle movement.

The reason is not that they are unimportant. The reason is that a bad hard gate is worse than a good advisory finding.

## Counterfactual negative controls

No frozen or functional branch was mutated to test failure behavior. Instead the matrix records deterministic counterfactuals derived from real state:

- moving PR #19 away from its frozen SHA must produce LG002;
- moving PR #16 away from its recorded SHA must produce LG003;
- any non-R100 current-canon mutation without a CCR must produce LG004/LG005;
- malformed required YAML must produce LG007;
- an ACTIVE agent without an approved durable creation review must produce LG015;
- malformed release JSON must produce LG017.

These controls can later become dedicated CI fixtures without touching production/frozen branches.

## Persona note

Step 9 does not activate any additional autonomous agent or bind any new persona. The general persona-binding right established in Step 8 remains intact. Future Research Qualification and Release Operator agents remain RESERVED_NOT_ACTIVE until their creation gates are separately justified and approved.

## Enforcement decision

**Enforcement remains OFF.**

`loom-gate` remains in `OBSERVE` mode. Step 9 determines which rules have earned hard-gate eligibility; it does not itself grant blocking authority.

Blocking activation occurs only in the later governance/protection sequence with explicit owner approval.

## Step-9 acceptance

PASS when all are true:

1. real historical fixtures are recorded;
2. the PR #3 canon false positive is fixed without modifying historical canon;
3. release/compatibility and downstream rules are prevented from premature hardening;
4. hard-ready rules have deterministic remediation;
5. no frozen/game/runtime/data/3D/canon functional state changes;
6. current `loom-gate` runs clean after the Step-9 revisions;
7. `main`, PR #19 and PR #16 remain at their registered frozen SHAs.

## Next permitted action

**Step 10 — Establish Governance Baseline v1.0 on `main`.**

Before merge, close the governance planning state cleanly and disposition the open Foundations PR #20 appropriately without contaminating frozen PR #19.
