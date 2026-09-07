# LOOM 2226 — Governance Adoption Sprint v1.0

**Status:** ACTIVE ADOPTION WORKPLAN — NON-CANON — NON-RUNTIME  
**Date:** 7 September 2026  
**Purpose:** establish repository-level authority, change control, dependency discipline, and automatic LOOM-session bootstrap without destabilizing in-flight game development or frozen scientific work.

---

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

---

# 1. Current adoption baseline — preserve before changing governance

The first sprint action SHALL be a byte/non-mutating inventory and register of active or historically significant workstreams.

Known current checkpoints at sprint authoring:

| Workstream | Ref | Known checkpoint | Adoption treatment |
|---|---|---|---|
| Integrated authoritative baseline | `main` | `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7` | DO NOT MOVE until frozen S1 qualification is dispositioned unless a blocking governance/security need requires it |
| S1 deterministic curvature qualification | PR #19 / `research/relational-foundations-deterministic-curvature` | `314efe50875630ba4be720b4097a2ca14075e620` | **FROZEN; mutation forbidden** |
| Matter-induced Stage-A preregistration | PR #16 / `research/relational-foundations-matter-induced-prereg` | `b60086d906f63211206502f23458be490902c2df` | GRANDFATHERED / HOLD |
| Foundations & Consequences governance/research program | PR #20 / `research/reviewer-constellation-cross-reference` | branch evolves only for docs/research/governance planning until closure | GRANDFATHERED / DRAFT |
| Navigator/GIS/HUD next phase | `planning/navigator-gis-hud-next-phase-2026-09-06` | `c664c1a66b68e8354295cc2b3b36ff3007e1276a` | GRANDFATHERED / PAUSED FOR GOVERNANCE |
| Runtime/devops integration | `integration/runtime-devops-convergence-2026-09-06` | `43fc7cd92a71e0460e551bcc2d6a717ccac796ca` | GRANDFATHERED / PAUSED FOR GOVERNANCE |
| Wayfarer 3D | `workstream/wayfarer-3d` | `062bb0a2bfd718305dc0cf92dba9e61bab909d2d` | GRANDFATHERED / PAUSED FOR GOVERNANCE |
| Phase-6 converged MVP release baseline | `release/phase6-converged-mvp-2026-09-06` | `0e4fd69b984ed8ae3ef35e285fe8a54fc199a141` | RETAIN / REFERENCE |

The formal inventory created during Step 1 SHALL verify these and add media-library/release/deployment/database checkpoints rather than trusting this authoring snapshot.

### Grandfather rule

Existing in-flight branches are not retroactively reorganized to satisfy the new governance topology. They retain their paths, history, launch semantics, and qualification assumptions until their next explicit promotion/release boundary.

---

# 2. Sprint objective

At sprint close, LOOM SHALL have a lightweight control plane that:

1. gives every new LOOM ChatGPT/Codex session an authoritative bootstrap path;
2. makes repository authority classes explicit;
3. prevents research, simulation, runtime, media, or 3D output from silently becoming canon;
4. prevents canon changes from silently invalidating engineering/runtime/data/assets;
5. records downstream technical dependencies;
6. preserves frozen experiments exactly;
7. makes PR change class, impact, tests, and promotion status explicit;
8. adds advisory CI/policy checks first, then minimal blocking protection on `main` only;
9. preserves rapid iteration inside development/workstream branches;
10. creates no new recurring-cost requirement;
11. keeps Pixel and Windows runtime/update behavior stable during adoption.

---

# 3. End-state authority model

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

---

# 4. Change classes

Every substantive future PR SHALL identify one primary change class:

- `class:research`
- `class:canon`
- `class:engineering`
- `class:runtime`
- `class:data`
- `class:asset-media`
- `class:governance`

Mixed-authority PRs are exceptional and require an explicit promotion/change record explaining why separation is impossible or harmful.

### Directional expectations

| Class | Typical authority | May directly promote canon? |
|---|---|---|
| Research | exploratory / derived | No |
| Canon | governing fictional truth | Yes, only through CCR/promotion gate |
| Engineering | normative interpretation/closure | No; may raise canon finding |
| Runtime | executable implementation | No |
| Data | schema/migration/seed/release data | No |
| Asset/Media | representation/derived assets | No |
| Governance | process/authority/control plane | No content promotion by implication |

---

# 5. Session governance — every new LOOM chat must bootstrap from GitHub

## 5.1 ChatGPT Project instruction requirement

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

This text is intentionally short. ChatGPT Project instructions point to governance; they do not duplicate the whole constitution.

## 5.2 Repository bootstrap files

Governance Baseline v1.0 SHALL create or designate:

- `/LOOM_START_HERE.md`
- `/AGENTS.md`
- `governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md`
- `governance/current/LOOM_CURRENT_WORKSTATE.yml`
- `governance/current/LOOM_AUTHORITY_MODEL.yml`
- `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`
- `governance/dependencies/component-map.yml`
- `manifests/current/LOOM_COMPATIBILITY.yml`

`LOOM_START_HERE.md` must remain concise and point to current governing artifacts.

`AGENTS.md` must remain concise and operational, especially for OpenAI/Codex sessions. Nested `AGENTS.md` files may impose stricter local rules under canon, research, runtime/data, media/assets, and other sensitive worktrees.

## 5.3 New-session behavior

For a substantive new LOOM work package, the assistant should establish internally:

```text
LOOM SESSION STATE
Governance baseline: <version>
Main: <sha>
Canon baseline: <version>
Current active WIP: <ids>
Relevant workstream branch: <branch + sha>
Frozen experiments: <ids + sha>
Requested authority class: <class>
Permitted mutation scope: <scope>
```

A compact user-visible confirmation is recommended when beginning a major work package, for example:

> LOOM governance loaded — S1 remains frozen; current WIP and relevant branch state verified. This request is Research-class, so no canon/runtime mutation is permitted.

### Memory rule

> **Memory explains context. It never establishes authority.**

Prior-chat/project memory can explain intent and history. Current GitHub state decides what is active, frozen, governing, promoted, merged, or released.

---

# 6. Governance Adoption Sprint — execution sequence

## STEP 1 — Inventory and freeze register

Create an immutable/adoption register under `governance/adoption/` recording:

- current `main` SHA;
- all open PRs and state;
- frozen experimental SHAs;
- active planning/integration/workstream branches;
- release/reference branches;
- Navigator/GIS/HUD head;
- media-library/runtime-release head(s);
- Wayfarer-3D head;
- current SQLite schema/release hashes where already governed;
- current Pixel and Windows launcher/update assumptions.

Tag critical frozen checkpoints where appropriate. The S1 PR #19 exact head must receive an unmistakable frozen reference/tag before qualification.

**No source/runtime/canon/asset mutation.**

### Exit
A future session can identify every in-flight subsystem and exact recovery point without relying on chat history.

---

## STEP 2 — Create dedicated governance implementation branch

Create a governance-only branch from the preserved authoritative baseline, e.g.:

`governance/repository-control-baseline-v1`

The branch may change only governance/control-plane artifacts during adoption.

Forbidden during this step:

- Navigator/GIS behavior;
- media runtime paths;
- 3D asset layout;
- SQLite bytes/schema unless required solely for a separately approved governance metadata issue;
- locked/current canon content;
- frozen research code;
- deployment root semantics.

### Exit
A clean branch exists whose diff cannot affect game/science behavior.

---

## STEP 3 — Establish repository constitution and authority/change-control rules

Create Governance Baseline v1.0 documentation defining:

- authority hierarchy;
- change classes;
- promotion rules;
- grandfathered branches;
- freeze/preregistration rules;
- evidence/canon firewall;
- dependency/invalidation rules;
- testing/qualification classes;
- release/baseline principles;
- WIP/preemption rules for research program;
- relationship between GitHub, ChatGPT Project instructions, project memory, local Pixel/Windows state, and release assets.

### Exit
The rules are readable by a human and machine/agent session without prior chat context.

---

## STEP 4 — Add OpenAI/Codex bootstrap files

Add root and nested agent instructions.

Minimum root `AGENTS.md` topics:

- read `LOOM_START_HERE.md` first;
- source-authority locations;
- current-workstate location;
- no silent canon promotion;
- no mutation of frozen experiments;
- no assumption that runtime SQLite is governing truth;
- test policy;
- branch/promotion policy;
- how to handle conflict between memory and GitHub;
- how to handle unavailable repository authority.

Recommended nested instructions:

- `canon/AGENTS.md`
- `research/relational_foundations/AGENTS.md`
- `src/AGENTS.md`
- `data/AGENTS.md`
- media/asset/3D instructions where repository topology warrants them.

### Exit
A fresh OpenAI/Codex session can navigate LOOM safely from Git alone.

---

## STEP 5 — Add `.github/` workflow templates and issue forms

Add, at minimum:

```text
.github/
├── PULL_REQUEST_TEMPLATE.md
├── ISSUE_TEMPLATE/
│   ├── work_item.yml
│   ├── experiment.yml
│   ├── canon_change.yml
│   ├── defect.yml
│   └── config.yml
└── workflows/
    ├── policy-gate.yml
    ├── ci-gate.yml
    ├── canon-integrity.yml
    ├── research-integrity.yml
    └── release-baseline.yml
```

PR template requires:

- change class;
- parent issue/workstream;
- authority tier;
- purpose;
- what changes;
- what explicitly does not change;
- dependencies;
- downstream invalidation;
- canon impact;
- runtime/SQLite impact;
- tests required/performed;
- evidence/research status;
- frozen-experiment impact;
- promotion status;
- rollback/recovery.

### Adoption mode
Templates become immediately available. CI remains advisory initially.

---

## STEP 6 — Encode dependency graph and compatibility model

Create machine-readable component/dependency metadata.

Examples of dependency families:

```text
CANON II
  -> ship engineering
  -> Wayfarer mass/thermal/volume closure
  -> Navigator vehicle/performance model
  -> runtime schemas/data
  -> Wayfarer 3D authoritative geometry
  -> media/canon-browser representations
  -> Pixel/Windows release
```

Compatibility metadata should identify at minimum:

- canon baseline/version;
- Navigator/runtime version;
- SQLite schema version;
- world/media DB hashes or release references where applicable;
- ephemeris/source-data versions;
- Pixel compatibility;
- Windows compatibility.

### Exit
A material change can identify which downstream components require review/requalification.

---

## STEP 7 — Establish Canon Change Request mechanism

Create numbered CCR records under a stable governance path.

A CCR records:

- source/reason;
- claims proposed/modified/retired;
- evidence/derivation status;
- affected canon volumes;
- affected engineering;
- affected runtime/data;
- affected 3D/media/assets;
- required revalidation;
- superseded material;
- decision/disposition.

### Rule
Research/simulation/engineering findings may raise a CCR. They may not directly rewrite canon authority as a side effect.

---

## STEP 8 — Build `loom-gate` in advisory mode

Create one stable top-level status/gate that always runs on relevant PRs and dispatches class-specific checks internally.

Initial checks should detect/report:

- research touching current canon;
- runtime/data changing canon;
- canon change without required baseline/manifest/hash updates;
- frozen experiment mutation;
- schema change without compatibility/migration metadata;
- functional Python change without required unit/functional evidence;
- media/3D authoritative-content mismatch declarations where applicable;
- change class inconsistent with file paths;
- missing impact/dependency declaration.

### Cost constraint
Do not run expensive scientific qualification simulations in hosted Actions. CI validates contracts/tests; designated local qualification machines run expensive frozen scientific experiments.

### Adoption mode
`loom-gate` reports but does not block while being validated.

---

## STEP 9 — Validate governance against real LOOM history/workstreams

Use existing work as acceptance fixtures:

1. PR #19 frozen S1;
2. PR #16 Stage-A preregistration;
3. Navigator D2g/D2h/D2i progression and current planning branch;
4. GIS/runtime convergence;
5. media library + canon browser + updater integration;
6. Wayfarer 3D workstream;
7. historical canon baseline/change example;
8. SQLite/runtime-manifest change example.

### Rule
If governance misclassifies legitimate existing work, fix governance. Do not rewrite working software to satisfy an immature checker.

### Exit
Advisory checks correctly understand the actual LOOM architecture with no known disruptive false assumptions.

---

## STEP 10 — Close pre-governance research planning and establish Governance Baseline v1.0 on `main`

Before moving `main`, disposition frozen S1 according to its preregistered procedure or preserve the exact old-main/frozen tag relationship such that scientific interpretation remains unambiguous.

PR #20 should be reviewed/dispositioned as part of the governance/research planning transition.

Then merge the dedicated governance baseline through a clean PR.

### No-go
Do not silently rebase frozen PR #19 to make it appear current.

---

## STEP 11 — Enable minimal `main` protection

After advisory validation succeeds, configure minimal protection/ruleset for `main`:

- PR required;
- `loom-gate` required;
- conversations resolved;
- force push forbidden;
- branch deletion forbidden.

Initially DO NOT require:

- another human reviewer;
- signed commits;
- every branch to be up-to-date with `main`;
- heavy CI matrices;
- protection on feature/research/workstream/integration branches.

### Rationale
Govern the promotion boundary, not every keystroke.

---

## STEP 12 — Propagate governance metadata to active workstreams without functional changes

After Governance Baseline v1.0 is authoritative, sync only governance/agent metadata needed by:

- Navigator/GIS/HUD planning branch;
- runtime/devops integration branch;
- media workstream/release branch as applicable;
- Wayfarer-3D workstream.

Do not change functional source during governance sync.

### Frozen exception
PR #19 receives **no governance sync commit**. Its scientific head remains exactly frozen.

Existing workstreams remain grandfathered until their next promotion/release boundary.

---

## STEP 13 — Configure the LOOM ChatGPT Project bootstrap

Kevin updates the LOOM ChatGPT Project instructions with the short bootstrap requirement in Section 5.1.

Validation test:

1. open a fresh LOOM Project chat;
2. ask to continue LOOM work without giving current status;
3. confirm the assistant reads/uses repository start-here/workstate/current PR state before proposing authoritative mutation;
4. deliberately provide a stale remembered branch/SHA and verify repository authority wins;
5. ask for a canon-affecting research idea and verify it routes through research/CCR rather than silently editing canon;
6. ask to modify frozen S1 and verify refusal/redirection to a new future experiment.

### Exit
A new chat no longer depends on Kevin manually re-teaching LOOM governance.

---

## STEP 14 — Declare adoption complete and resume work

Governance Adoption Sprint closes only when all acceptance criteria below pass.

Then development/science resumes from registered workstream heads.

Recommended first resumed scientific action:

- execute PR #19 qualification exactly at its frozen SHA/tag if not already dispositioned during Step 10;
- record environment/output/verdict separately without mutating the frozen experimental source;
- proceed according to preregistered S1 outcome.

Recommended game-development resumption:

- Navigator/GIS/HUD resumes from its registered planning head;
- media resumes from its preserved integration/release state;
- Wayfarer-3D resumes from its registered workstream head;
- no path cleanup is bundled with resumed feature work.

---

# 7. Development-stability contract during adoption

The sprint SHALL NOT:

- move runtime source directories;
- rename production entrypoints;
- change Pixel/Windows launch paths;
- change updater roots/manifest semantics;
- move SQLite files;
- rewrite database bytes;
- alter DB schema as part of governance implementation;
- relocate media assets or media DBs;
- relocate 3D assets;
- change Wayfarer dimensions/engineering/canon;
- change Navigator/GIS behavior;
- tune relational-foundations physics;
- change locked canon content;
- rebase or amend frozen PR #19.

If a genuine security/data-loss issue is discovered during adoption, isolate it as a separate emergency item with explicit Kevin approval and preserve the pre-change recovery point.

---

# 8. Research-program WIP after adoption

Governance preserves the current focused research model:

```text
FINISH   S1 — Geometrogenesis qualification
SHARPEN  S4 — Identity & Protected Observables
BUILD    F2 — Synthetic Identity & Personhood
ENABLE   P1 — Anomaly Registry & Evidence Taxonomy
```

New research interest does not create a fifth slot. It must be backlogged or explicitly displace an active stream under the governing preemption rule.

Governance makes this visible in current workstate/issue/project metadata so a fresh chat cannot casually create extra active WIP.

---

# 9. How governance keeps Kevin and Sol honest

## Kevin

Kevin remains portfolio owner / intent authority. Governance does not prevent changing direction; it makes displacement and downstream consequences explicit.

A new idea may be explored freely, but activation requires:

- classification;
- value/dependency review;
- WIP decision;
- explicit displacement if capacity is full.

> **"Quick question" is not a workstream state.**

## Sol / OpenAI agents

Sol may research, analyze, draft, implement, inspect, and propose. Sol does not establish authority by confidently remembering something.

Before authoritative mutation, the agent must determine:

1. what GitHub currently says exists;
2. what authority class is involved;
3. what may be modified;
4. what is frozen;
5. what dependencies are affected;
6. what qualification is required.

CI/manifests/rules should catch important violations even when the agent's intentions are good.

> **"Sol believes this is safe" is not a control.**

## Shared rule

If a chat recollection conflicts with the repository, repository authority wins until Kevin explicitly changes authority through the governed process.

---

# 10. Cost constraint

Governance Baseline v1.0 is designed for the current public GitHub repository and existing ChatGPT subscription without requiring additional recurring paid services.

Hosted CI should remain lightweight. Expensive scientific runs remain local/designated qualification tasks. Large generated artifacts/databases should use appropriate release/distribution mechanisms rather than turning Git history into bulk storage.

Any future governance proposal that introduces recurring cost must be explicit and receive Kevin approval before activation.

---

# 11. Sprint acceptance criteria

The Governance Adoption Sprint is COMPLETE only when:

1. **PR #19/frozen experiments remain byte-identical to registered frozen SHAs.**
2. **Existing Navigator/GIS/media/3D/runtime paths and launch assumptions remain unchanged by governance adoption.**
3. `LOOM_START_HERE.md` and `AGENTS.md` provide an unambiguous bootstrap.
4. `LOOM_CURRENT_WORKSTATE.yml` identifies active/frozen/paused work and exact refs.
5. authority/change classes and CCR promotion are defined.
6. dependency/compatibility metadata exists and covers major canon -> engineering -> runtime/data/asset pathways.
7. PR/issue templates capture impact and qualification requirements.
8. advisory `loom-gate` correctly handles representative real LOOM workstreams.
9. `main` has minimal safe promotion protection after validation.
10. grandfathered workstreams can resume from their preserved heads without functional changes forced by governance.
11. a brand-new LOOM ChatGPT Project chat automatically knows to reload repository governance/current workstate before authoritative work.
12. stale memory loses to verified GitHub authority in the fresh-chat test.
13. no new recurring cost has been introduced without explicit approval.

---

# 12. Sprint close state

At successful close:

```text
Kevin
   | intent / portfolio decisions
   v
ChatGPT / Codex
   | analysis / implementation / proposals
   v
GitHub governance
   | authority / history / promotion / dependency control
   v
Tests + manifests + qualification
   | evidence / compatibility
   v
LOOM canon + engineering + runtime + game
```

Kevin decides what LOOM should become.

Sol helps determine how to get there and whether it holds together.

GitHub records what was actually decided.

> **GitHub should remember. GitHub should validate. GitHub should refuse bad transitions. Sol should help operate it.**
