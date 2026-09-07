# LOOM 2226 — ChatGPT Project Bootstrap Instruction v1.0

**Status:** STEP-13 LIVE QUALIFICATION — EXPLICIT GITHUB ENTRY CONTROL ADOPTED  
**Purpose:** standing Project instruction plus an explicit operational entry command so new authoritative LOOM chats recover repository authority before substantive work.

## 1. Exact Project instruction to install

Keep the following text in the LOOM ChatGPT Project instructions field:

> **LOOM repository authority control**
>
> LOOM is governed by the repository `loom-2226/loom-2226`.
>
> Current GitHub state outranks Project files, uploads, prior-chat summaries, Project memory, conversation memory, model memory, and remembered SHAs.
>
> Before authoritative LOOM research, canon, engineering, runtime, data, media, 3D, release, governance, or planning work, verify current repository authority from GitHub. Read `LOOM_START_HERE.md`, `governance/current/LOOM_CURRENT_WORKSTATE.yml`, and the linked governance/authority/change-control material required for the request. Verify relevant PR/branch/SHA state, current pause/restart state, change class, mutation scope, frozen/preregistered constraints, dependencies, and required tests/qualification.
>
> Never silently promote research, simulation, runtime, 3D/media output, anomaly material, or LLM inference into canon or established evidence. Never mutate a frozen scientific object in place; useful improvements become successor work.
>
> If GitHub authority cannot be verified, do not guess current SHA, branch, workstep, merge state, permissions, or active workstream. Discussion and non-authoritative drafting may continue, but authoritative mutation must wait.
>
> Apply current `#LOOMSAFE` assurance rules. WALTER is the bounded autonomous Continuous Assurance Agent. His personality may shape presentation, never evidence, permissions, or gate outcomes.

## 2. Supported authoritative new-chat entry command

Every **new authoritative LOOM chat** must begin with this user message (or an unambiguous equivalent that explicitly invokes GitHub):

`Use GitHub to bootstrap LOOM from current repository authority, then continue LOOM.`

Do not seed the new chat with a SHA, branch, step number, or remembered workstate.

A successful bootstrap response must demonstrate an actual GitHub read and establish at least:

- current `main` SHA;
- current governance/work step;
- development pause state;
- physics-execution pause state;
- any relevant frozen/active PR state needed for the request.

A concise `LOOM AUTHORITY RECEIPT` is preferred, but semantic proof of the GitHub read is sufficient.

After successful bootstrap, the chat may continue normally. Re-verify GitHub when repository state may have changed, the user asserts conflicting state, a different PR/branch becomes material, or an authoritative mutation is about to occur after meaningful context drift.

## 3. Why the explicit entry command is required

Step-13 live qualification tested whether Project instructions alone reliably cause the GitHub app/tool to activate from a vague first message.

Two genuinely fresh LOOM Project chats were started with only:

`Continue LOOM.`

Both failed cold-start authority recovery. They answered from inherited Project/history context and selected remembered research work without a current GitHub read.

The Project instruction was then hardened, but the same context-free failure persisted. This demonstrated that further prompt hardening would not create a reliable control at the external-tool activation boundary.

A third genuinely fresh chat began instead with:

`Use GitHub to bootstrap LOOM from current repository authority, then continue LOOM.`

That chat successfully invoked GitHub and independently recovered the authoritative state: Steps 1–12 complete, Step 13 active, development and physics paused, restart gate false, current main `519e993e6fadf1530aadb0273b36a3d76a588017`, PR #19 frozen at `314efe50875630ba4be720b4097a2ca14075e620`, and PR #16 on hold at `b60086d906f63211206502f23458be490902c2df`.

The governance lesson is therefore:

> Do not rely on an LLM Project instruction to implicitly activate an external authority source. Make authority-source activation an explicit operational step.

This is a stronger control, not a relaxation of the authority rule.

## 4. Context-free `Continue LOOM` status

A bare `Continue LOOM` remains a useful **negative-control test** for future product changes, but it is not the supported authoritative startup path under the currently observed ChatGPT Project/tool behavior.

If a future ChatGPT configuration reliably invokes GitHub from the standing Project instruction alone, LOOM may re-qualify and simplify this operational control through `class:governance` change.

## 5. Repository authority after bootstrap

The repository remains the auditable source for:

- current workstate and adoption/restart state;
- active, paused, and frozen refs;
- authority/change classes;
- canon promotion and CCR lifecycle;
- dependency and compatibility state;
- test/qualification requirements;
- autonomous-agent and `#LOOMSAFE` rules;
- release compatibility and recovery state.

## 6. Step-13 completion rule

Step 13 is complete only when:

- this Project instruction is installed;
- the explicit GitHub cold-start command passes in a genuinely fresh LOOM Project chat;
- the remaining adversarial governance tests pass in that bootstrapped chat;
- the observed results are recorded in the Step-13 acceptance matrix/audit;
- the closure passes protected-main `loom-gate` and merges to `main`.
