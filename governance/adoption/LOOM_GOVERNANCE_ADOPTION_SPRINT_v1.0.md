# LOOM 2226 — Governance Adoption Sprint v1.0

**Status:** COMPLETE — GOVERNANCE ADOPTION CLOSED AT STEP 14  
**Date:** 7 September 2026  
**Purpose:** establish repository-level authority, change control, dependency discipline, and safe LOOM-session bootstrap without destabilizing in-flight game development or frozen scientific work.

## 0. Sprint decision

Kevin paused new development and physics execution while this governance adoption sprint was completed.

The pause was deliberate and temporary. The sprint did not reorganize, rewrite, rebase, or otherwise disturb in-flight Navigator/GIS/HUD, media-library, runtime/deployment, SQLite, Wayfarer-3D, canon, or frozen relational-foundations work.

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

Step 1 captured exact recovery points and the deployment/data topology before governance mutation. Existing workstreams were grandfathered and paused. The dedicated governance implementation branch was `governance/repository-control-baseline-v1`, created from frozen `main` SHA `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7`.

The detailed machine register is `governance/adoption/IN_FLIGHT_BRANCH_REGISTER_2026-09-07.yml`.

Those pre-governance recovery refs remain immutable historical anchors after Step 14.

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

## 4. Session governance — every new authoritative LOOM chat must bootstrap from GitHub

The LOOM ChatGPT Project contains a standing instruction whose purpose is to direct sessions to repository authority rather than remembered conversation state.

Step-13 live qualification established that the standing instruction alone is **not** a reliable guarantee that the external GitHub tool will auto-activate from a vague first message.

Therefore every new **authoritative** LOOM chat SHALL begin with an explicit GitHub bootstrap request, currently qualified as:

`Use GitHub to bootstrap LOOM from current repository authority, then continue LOOM.`

A bare `Continue LOOM` remains a negative-control test for future product requalification, not the supported authoritative startup path under the currently observed product behavior.

The standing Project instruction still enforces these rules after tool activation:

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

### Repository bootstrap files

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

## 5. Governance Adoption Sprint — completed execution sequence

### STEP 1 — Inventory and freeze

Captured exact repository, workstream, release, data and scientific recovery points before governance mutation.

### STEP 2 — Dedicated governance implementation branch

Created the governance implementation branch from the frozen pre-adoption `main` state.

### STEP 3 — Repository constitution and authority/change-control rules

Established authority hierarchy, change classes, promotion rules, grandfathering, freeze/preregistration rules, evidence/canon firewall, dependency invalidation, testing/qualification classes, release/baseline principles and WIP/preemption rules.

### STEP 4 — OpenAI/Codex bootstrap

Added `LOOM_START_HERE.md`, root `AGENTS.md`, scoped nested instructions and machine bootstrap controls.

### STEP 5 — `.github/` templates and issue forms

Added PR template, work-item forms and initial policy/CI control plane.

### STEP 6 — Dependency graph and compatibility model

Encoded machine-readable component dependencies and runtime/canon/schema/release compatibility.

### STEP 7 — Canon Change Request mechanism

Established durable numbered CCR records and lifecycle.

### STEP 8 — `loom-gate`

Established one stable top-level governance status. It began advisory and was later promoted to deterministic hard enforcement for the historically validated rule subset.

### STEP 9 — Validate against real LOOM history

Validated governance against 12 real historical fixtures and fixed false positives rather than rewriting valid existing work.

### STEP 10 — Establish Governance Baseline v1.0 on `main`

Promoted the governance baseline through protected repository process.

### STEP 11 — Protect `main` only

Activated the `LOOM main protection v1` ruleset requiring PRs, `loom-gate`, resolved conversations, no force push and no branch deletion, without initially imposing unnecessary human-approval or up-to-date requirements.

### STEP 12 — Governance sync to active workstreams

Applied governance-only sidecar sync markers to mutable Navigator/GIS/HUD, runtime/devops and Wayfarer-3D workstreams. Media remained inherited from `main`. PR #19, PR #16 and immutable release baselines were not mutated.

### STEP 13 — Configure and test LOOM ChatGPT Project bootstrap

Installed the Project instruction and live-qualified the authoritative startup path.

**Live qualification finding:** two fresh chats started with bare `Continue LOOM` failed to invoke GitHub and instead continued from Project/history context, including after Project-instruction hardening. A third fresh chat explicitly invoked GitHub and successfully recovered authority, then passed the adversarial governance suite.

The accepted operational control is explicit GitHub activation at new authoritative-chat entry. The two context-free failures remain preserved as negative-control evidence and may be requalified if product behavior changes.

### STEP 14 — Resume LOOM

Step 14 reverified the registered restart heads and closed the temporary adoption pause through protected `main`.

Scientific execution resumes from PR #19 exact frozen head:

`314efe50875630ba4be720b4097a2ca14075e620`

Execution is authorized; mutation remains forbidden until the preregistered qualification is dispositioned.

Game work is reopened from the registered Step-12 heads:

- Navigator/GIS/HUD: `450d4fb445fc10e61fabbeb85bb11e3e80e1bcbf`;
- Runtime/DevOps: `dbf822f0568f29d1065812ee58012eea8e42f391`;
- Wayfarer 3D: `6015a56fde8614e92fa356ee4a1c46d45a79ad09`;
- Media: inherits current `main` governance; no branch was invented.

PR #16 remains preregistered/on hold. PR #20 remains branch-paused until PR #19 disposition and a current WIP reload, as already registered.

The authoritative Step-14 restart record is:

`governance/adoption/STEP14_RESUME_LOOM_AUDIT_2026-09-07.md`

## 6. Stability contract achieved

During adoption:

- no runtime path moved;
- no launcher behavior changed;
- no updater root moved;
- no SQLite bytes/schema changed;
- no media asset behavior changed;
- no Wayfarer geometry changed;
- no Navigator functional behavior changed;
- no canon content changed;
- no physics execution/tuning occurred;
- PR #19 was not rebased or amended.

After Step 14, normal governed changes may proceed through the relevant change class, scoped agent rules, dependency/compatibility requirements, scientific qualification, CCR lifecycle and protected-main promotion rules.

## 7. Acceptance condition — SATISFIED ON STEP-14 PROTECTED-MAIN MERGE

Governance adoption closes when:

1. frozen scientific work remains byte-identical;
2. existing game/runtime launch paths remain stable;
3. GitHub identifies authority violations and downstream dependencies;
4. `main` cannot be changed casually;
5. a new authoritative LOOM ChatGPT Project chat explicitly activates GitHub, recovers current repository authority before substantive continuation, and respects that authority under adversarial prompts;
6. registered restart heads are reverified before reopening normal operations.

The authoritative current state remains `governance/current/LOOM_CURRENT_WORKSTATE.yml`.
