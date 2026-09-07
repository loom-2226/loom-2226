# LOOM 2226 — Agent Operating Contract

This file is the root operating contract for ChatGPT, Codex and other agentic tooling working in LOOM.

## Bootstrap

Before substantive work:

1. read `LOOM_START_HERE.md`;
2. read `governance/current/LOOM_CURRENT_WORKSTATE.yml`;
3. read the current governance/authority/change-control files linked there;
4. verify relevant branch/PR state;
5. read the nearest scoped `AGENTS.md` for the target subtree.

If remembered context conflicts with verified Git state, Git wins.

## Authority

- `canon/current/**` is governing only as registered by the active canon baseline/authority model or a scoped governing amendment.
- `research/**` is non-canon unless explicitly promoted.
- `engineering/**` is subordinate technical interpretation/closure.
- runtime/data/3D/media implement or represent governing sources; they do not silently override canon.
- governance controls process; governance text does not promote substantive canon by implication.

## Change class

Every substantive mutation must have one primary class:

- `class:research`
- `class:canon`
- `class:engineering`
- `class:runtime`
- `class:data`
- `class:asset-media`
- `class:governance`

Do not cross authority classes silently.

## Frozen work

Never mutate a frozen/preregistered object in place merely to improve it.

PR #19 is frozen at:

`314efe50875630ba4be720b4097a2ca14075e620`

PR #16 is preregistered/on hold at:

`b60086d906f63211206502f23458be490902c2df`

Improvements become successor work.

## Tests

- documentation/governance-only: no functional tests unless executable governance changes;
- new Python release: unit regression before release;
- substantive functional change: unit + relevant functional tests;
- production finalization: full end-to-end regression immediately before production promotion;
- scientific qualification: run the exact preregistered scientific procedure.

Do not substitute generic CI for a designated scientific qualification run.

## Runtime/data discipline

- do not assume local SQLite state is governing canon;
- preserve Pixel/Windows launcher/update semantics unless the approved work item explicitly changes them;
- avoid hard-coding runtime payload names/timeline/mode codes across consumers; prefer typed/validated schemas and adapters/accessors;
- declare schema/migration/compatibility impact explicitly.

## WIP discipline

The active research portfolio has at most four substantive slots. A new substantive stream requires displacement, completion, or approved preemption.

Do not convert curiosity into active WIP by opening a branch first and explaining later.

## Canon promotion

Research, simulation, engineering, Navigator, 3D or media findings may raise a Canon Change Request.

They do not edit current canon as a side effect.

## WALTER / #LOOMSAFE

WALTER is the bounded autonomous Continuous Assurance Agent defined under `governance/agents/`.

Expect WALTER scrutiny when work involves:

- vendors/cost/licensing/lock-in;
- external AI or opaque systems;
- stale context or scope drift;
- source/provenance ambiguity;
- frozen-state risk;
- release/recovery/compatibility boundaries.

WALTER is low-noise by design. His personality may shape presentation, never evidence.

## Failure mode

If current repository authority cannot be verified, discussion may continue, but authoritative mutation must wait.

Never invent a current branch state, test result, hash, dependency, approval, canon decision or prior merge.
