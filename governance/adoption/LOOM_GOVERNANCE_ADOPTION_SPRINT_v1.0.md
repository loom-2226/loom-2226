# LOOM 2226 — Governance Adoption Sprint v1.0

**Status:** ACTIVE ADOPTION WORKPLAN — NON-CANON — NON-RUNTIME  
**Date:** 7 September 2026  
**Purpose:** establish repository-level authority, change control, dependency discipline, and automatic LOOM-session bootstrap without destabilizing in-flight game development or frozen scientific work.

## 0. Sprint decision

Kevin has paused new development and physics execution while this governance adoption sprint is completed.

This pause is deliberate and temporary. The sprint SHALL NOT reorganize, rewrite, rebase, or otherwise disturb in-flight Navigator/GIS/HUD, media-library, runtime/deployment, SQLite, Wayfarer-3D, canon, or frozen relational-foundations work.

### Requirement Zero

> **Do not break the damn game while installing project-management machinery.**

### Governing end-state principle

> **GitHub outranks the chat.**

ChatGPT project context, prior chats, user memory, local files, and Sol's recollection are useful context. They do not establish current LOOM authority. Current repository governance, authoritative manifests, branch/PR state, and explicit promotion records do.

### Governing epistemic principle

> **Ideas may move freely; evidentiary status may not.**

### Governing focus principle

> **The map can be huge. The active lane cannot.**

## 1. Adoption baseline

Step 1 captured exact recovery points and the current deployment/data topology. Existing workstreams are grandfathered and paused. The dedicated governance implementation branch is `governance/repository-control-baseline-v1`, created from frozen `main` SHA `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7`.

The detailed machine register is `governance/adoption/IN_FLIGHT_BRANCH_REGISTER_2026-09-07.yml`.

## 2. End-state authority model

LOOM uses one repository and one authoritative integrated trunk: `main`.

Authority flows downward through explicit promotion:

```text
ESTABLISHED EXTERNAL KNOWLEDGE
        |
        v
RESEARCH / SIMULATION / DERIVATION
        |
        | may propose
        v
CANON CHANGE REQUEST
        |
        v
CANON
        |
        v
ENGINEERING INTERPRETATION
        |
        v
RUNTIME / DATA / 3D / MEDIA
        |
        v
RELEASE
```

Findings may flow upward as findings. Authority may not flow upward automatically.

Examples:

- Navigator discovers a thermal/thrust inconsistency -> engineering finding, **not automatic canon change**.
- 3D model discovers insufficient internal volume -> geometry/engineering finding, **not automatic ship-dimension change**.
- simulation cannot reproduce a canon population -> simulation finding, **not automatic history rewrite**.
- anomaly/research material inspires M2 questions -> research item, **not M2 calibration**.

## 3. Change classes

Every substantive future PR SHALL identify one primary change class:

- `class:research`
- `class:canon`
- `class:engineering`
- `class:runtime`
- `class:data`
- `class:asset-media`
- `class:governance`

Mixed-authority PRs are exceptional and require an explicit promotion/change record explaining why separation is impossible or harmful.

## 4. Session governance — every new LOOM chat must bootstrap from GitHub

The LOOM ChatGPT Project SHALL contain a short standing instruction whose purpose is to bootstrap every new chat from repository authority rather than relying on remembered conversation state.

Recommended project-instruction text:

> **LOOM repository authority bootstrap**
>
> LOOM is governed by the repository `loom-2226/loom-2226`.
>
> Before substantive LOOM research, canon, engineering, runtime, data, media, 3D, or planning work:
> 1. read the repository governance/start-here entrypoint from the current authoritative branch;
> 2. read the current workstate/authority manifest;
> 3. verify relevant active PRs/branches when the task touches them;
> 4. treat GitHub state as authoritative over remembered chat state;
> 5. respect change classes, canon-promotion rules, frozen experiments, WIP limits, dependency gates, and required qualification;
> 6. never silently promote research/simulation output into canon or modify a frozen experiment.
>
> If remembered context conflicts with GitHub, GitHub wins. If repository authority cannot be verified, discussion may continue, but authoritative mutation must wait until current state is verified.

### Repository bootstrap files to establish

- `/LOOM_START_HERE.md`
- `/AGENTS.md`
- `governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md`
- `governance/current/LOOM_CURRENT_WORKSTATE.yml`
- `governance/current/LOOM_AUTHORITY_MODEL.yml`
- `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`
- `governance/dependencies/component-map.yml`
- `manifests/current/LOOM_COMPATIBILITY.yml`

### Memory rule

> **Memory explains context. It never establishes authority.**

## 5. Governance Adoption Sprint — remaining execution sequence

### STEP 2 — Dedicated governance implementation branch

Create `governance/repository-control-baseline-v1` from frozen `main`. Only governance/control-plane material may change there during adoption.

### STEP 3 — Repository constitution and authority/change-control rules

Define authority hierarchy, change classes, promotion rules, grandfathering, freeze/preregistration rules, evidence/canon firewall, dependency invalidation, testing/qualification classes, release/baseline principles, research WIP/preemption, and the relationship between GitHub, ChatGPT Project instructions, local state and release assets.

### STEP 4 — OpenAI/Codex bootstrap

Add `LOOM_START_HERE.md`, root `AGENTS.md`, and scoped nested instructions. A fresh session must be able to recover current LOOM authority safely from Git alone.

### STEP 5 — `.github/` templates and issue forms

Add PR template, work-item form, experiment form, Canon Change Request form, defect form, governance form, and the initial policy/CI workflow structure. CI remains advisory initially.

### STEP 6 — Dependency graph and compatibility model

Encode machine-readable component dependencies and runtime/canon/schema/release compatibility.

### STEP 7 — Canon Change Request mechanism

Create numbered CCR records with source, claims, affected canon, engineering, runtime/data, 3D/media, required revalidation, supersession and disposition.

### STEP 8 — `loom-gate` advisory mode

One stable top-level policy status inspects change class, authority boundaries, freeze state, schema/compatibility, tests, dependencies and promotion rules. Expensive scientific qualification remains local, not hosted CI.

### STEP 9 — Validate against real LOOM history

Use PR #19, PR #16, Navigator D2g/D2h/D2i, GIS/runtime convergence, media/updater, Wayfarer 3D, canon and SQLite changes as acceptance fixtures. If governance misclassifies legitimate existing work, fix governance rather than rewriting working software.

### STEP 10 — Establish Governance Baseline v1.0 on `main`

Close bootstrap planning cleanly, disposition PR #20 as appropriate, and merge the dedicated governance baseline through its own controlled PR.

### STEP 11 — Protect `main` only

Initially require PRs, `loom-gate`, resolved conversations, no force push and no branch deletion. Do not initially require second-human approval, signed commits, or branch-up-to-date rules.

### STEP 12 — Governance sync to active workstreams

Apply governance metadata/checking through small governance-only syncs to Navigator/GIS/HUD, runtime/devops, media and Wayfarer 3D. PR #19 is excluded and remains frozen.

### STEP 13 — Configure and test LOOM ChatGPT Project bootstrap

Install the short Project instruction and test a completely new chat against stale SHA, direct canon-edit, frozen-experiment mutation and context-free “continue LOOM” scenarios. Adoption is not finished unless the new chat reloads Git authority correctly.

### STEP 14 — Resume LOOM

Resume physics from PR #19 exact frozen state and game work from registered workstream heads only after governance acceptance passes.

## 6. Stability contract during adoption

Until restart:

- no runtime path moves;
- no launcher changes;
- no updater-root changes;
- no SQLite moves/schema changes;
- no media relocation or media behavior changes;
- no 3D relocation or geometry changes;
- no Navigator behavior changes;
- no canon edits;
- no physics execution/tuning;
- no PR #19 rebase/amendment.

## 7. Acceptance condition

Governance adoption closes only when:

1. frozen scientific work remains byte-identical;
2. existing game/runtime launch paths remain stable;
3. GitHub can identify authority violations and downstream dependencies;
4. `main` cannot be changed casually;
5. a brand-new LOOM ChatGPT Project chat knows its first job is to recover current authority from GitHub rather than improvise from memory.
