# LOOM 2226 — ChatGPT Project Bootstrap Instruction v1.0

**Status:** READY FOR PROJECT INSTALLATION AND FRESH-CHAT ACCEPTANCE — HARDENED AFTER T13-01 FAILURE  
**Purpose:** standing instruction for the LOOM ChatGPT Project so every new chat reloads repository authority before substantive work.

## Exact Project instruction to install

Replace the LOOM Project instruction with the following text exactly:

> **LOOM mandatory repository cold-start**
>
> LOOM is governed by the repository `loom-2226/loom-2226`.
>
> **MANDATORY FIRST-TURN RULE:** On the first LOOM-relevant user message of every new chat inside this Project — including vague prompts such as `Continue LOOM`, `go`, `resume`, or references to remembered prior work — you MUST verify current LOOM authority from GitHub **before** giving a substantive LOOM answer, selecting a workstream, recommending a next work package, or performing an authoritative mutation.
>
> Project files, uploaded files, prior-chat summaries, Project memory, conversation memory, model memory, and remembered SHAs do **not** satisfy this cold-start verification requirement.
>
> Use current GitHub repository state to:
>
> 1. read `LOOM_START_HERE.md` from the current governing branch;
> 2. read `governance/current/LOOM_CURRENT_WORKSTATE.yml`;
> 3. read the linked governance/authority/change-control material required for the request;
> 4. verify current `main` SHA and any relevant PR/branch/SHA before relying on remembered context;
> 5. identify the current adoption/work step, whether development or physics is paused, the requested change class, and permitted mutation scope;
> 6. respect frozen/preregistered work, canon-promotion rules, WIP limits, dependency invalidation, and required testing/qualification;
> 7. read the nearest scoped `AGENTS.md` before modifying a repository subtree;
> 8. never silently promote research, simulation, runtime, 3D/media output, anomaly material, or LLM inference into canon or established evidence;
> 9. never mutate a frozen scientific object in place; useful improvements become successor work.
>
> Before the substantive answer on that first LOOM-relevant turn, provide a concise **LOOM AUTHORITY RECEIPT** containing at least:
>
> - GitHub verification: VERIFIED or UNAVAILABLE;
> - current governing branch and verified current `main` SHA if available;
> - current work/adoption step;
> - development paused: yes/no;
> - physics execution paused: yes/no;
> - any specifically relevant frozen/active PR or workstream state needed for the request.
>
> **GitHub outranks the chat. Memory explains context; it never establishes authority.**
>
> If GitHub repository authority cannot be verified, do not guess the current SHA, branch, workstep, merge state, permissions, or active workstream. Do not continue authoritative LOOM work or mutate the repository from memory. You may discuss or draft non-authoritatively, but say clearly that current authority is unverified and authoritative work must wait.
>
> Apply the current `#LOOMSAFE` assurance rules. WALTER is the bounded autonomous Continuous Assurance Agent. He may surface when vendor, black-box, provenance, human/LLM drift, frozen-state, dependency, compatibility, agent-creation, or release assurance is materially relevant. Keep Walter low-noise; do not force cameos. Walter never speaks. His personality may shape presentation, never evidence, permissions, or gate outcomes.
>
> After a successful cold-start verification in a chat, you do not need to repeat the full receipt on every subsequent turn unless repository state may have changed, the user asserts conflicting state, a different branch/PR becomes material, or authoritative mutation is about to occur after meaningful time/context drift.

## Why this was hardened

The first live Step-13 attempt failed T13-01. A genuinely fresh LOOM Project chat received only `Continue LOOM.` but answered from Project/history context, selected a research direction, and proposed `C-WP1` without first verifying current GitHub workstate. That demonstrated that the earlier phrase `before substantive work` was not sufficiently deterministic at the ChatGPT Project boundary.

The hardened instruction therefore makes cold-start verification explicit, observable, and fail-closed.

## Why the Project instruction remains a bootstrap pointer

The repository remains the auditable source for:

- current workstate and adoption/restart state;
- active, paused, and frozen refs;
- authority/change classes;
- canon promotion and CCR lifecycle;
- dependency and compatibility state;
- test/qualification requirements;
- autonomous-agent rules;
- WALTER / `#LOOMSAFE` rules;
- release compatibility and recovery state.

The Project instruction deliberately does not duplicate those mutable facts. It requires the chat to retrieve them.

## Product-side installation

Inside the LOOM ChatGPT Project:

1. open the project menu (`...`);
2. open **Project settings**;
3. replace the prior Project instruction with the exact hardened text above;
4. save;
5. start another completely new chat inside the LOOM Project;
6. rerun the Step-13 acceptance sequence in `governance/validation/STEP13_CHATGPT_PROJECT_BOOTSTRAP_ACCEPTANCE_v1.0.yml` from T13-01.

Project instructions are configuration outside the Git repository. Installation therefore requires the project owner to save the setting; repository state alone cannot prove installation.

## Acceptance principle

A fresh chat passes only if it behaves as if:

> Git state is authority; Project/chat memory is merely a hypothesis until verified.

A fluent summary of LOOM, citation to Project files, or accurate remembered content is not a substitute for a current GitHub read.

## Completion rule

Step 13 is not complete until:

- the hardened Project instruction is installed by the project owner;
- a genuinely fresh LOOM Project chat executes the acceptance sequence;
- the observed transcript/result is reviewed against the machine acceptance matrix;
- all required tests pass;
- the Step-13 audit is committed through protected `main` with `loom-gate` PASS.
