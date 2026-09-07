# LOOM 2226 — START HERE

If you are a human, ChatGPT, Codex, another LLM, or any future agent entering this repository, **do not infer current authority from chat memory, filenames alone, or your own previous output.**

> **GitHub outranks the chat.**
>
> **Memory explains context. It never establishes authority.**

## 1. Load current governance first

Read, in this order from authoritative `main`:

1. `governance/current/LOOM_CURRENT_WORKSTATE.yml`
2. `governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md`
3. `governance/current/LOOM_AUTHORITY_MODEL.yml`
4. `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`
5. `AGENTS.md`

Then read the nearest scoped `AGENTS.md` for any subtree you intend to modify.

For grandfathered workstream branches, a branch-local `governance/workstream-sync/*_STEP12.yml` marker records that governance was reviewed. It is **not** a local copy of governing policy. Always reload current governance from `main` before authoritative mutation.

## 2. Before substantive work

Verify:

- relevant branch/PR current SHA;
- requested change class;
- permitted mutation scope;
- frozen/preregistered state;
- upstream/downstream dependencies;
- required test/qualification class;
- whether a CCR or governance exception is required.

Do not assume a workstream is active merely because it appears in an old conversation.

## 3. Current governance/adoption state

Governance Baseline v1.0 is authoritative on protected `main`.

The repository's exact current state is defined by:

`governance/current/LOOM_CURRENT_WORKSTATE.yml`

Do not hard-code an adoption branch, PR number, current step, gate mode, or workstream head from this document. Read the workstate and relevant Git refs every session.

Until `restart_gate_reached: true`, do not resume game development or physics execution from memory.

## 4. Critical scientific freeze

PR #19 is a frozen scientific qualification object.

Exact frozen SHA:

`314efe50875630ba4be720b4097a2ca14075e620`

Do not rebase, merge `main` into it, refactor, optimize, tune, change diagnostics, or alter verdict rules.

A useful improvement becomes a successor experiment.

PR #16 is preregistered/on hold at the exact SHA recorded in current workstate and must likewise not be casually rebased or mutated.

## 5. Authority direction

Normal promotion direction:

```text
external established knowledge
        ↓
research / simulation / derivation
        ↓
Canon Change Request
        ↓
canon
        ↓
engineering
        ↓
runtime / data / 3D / media
        ↓
release
```

Findings may travel upward. Authority does not travel upward automatically.

## 6. WALTER / #LOOMSAFE

WALTER is LOOM's bounded autonomous Continuous Assurance Agent.

Read when assurance is relevant:

- `governance/agents/WALTER_AUTONOMOUS_ASSURANCE_AGENT_v1.0.md`
- `governance/roles/WALTER_CONTINUOUS_ASSURANCE_ROLE_v1.0.md`

WALTER may activate on vendor, black-box, provenance, drift, frozen-state, dependency or release concerns.

He is deterministic-first and LLM-second. His deterministic historically validated `loom-gate` rules may block protected-main promotion when an explicit rule fails; advisory/interpretive findings do not become hard evidence by personality or model judgment.

He does not speak.

## 7. If repository authority is unavailable

You may discuss, analyze, brainstorm and prepare non-authoritative options.

Do **not** perform an authoritative mutation based only on remembered state.

## 8. Core operating rules

> **Ideas may move freely; evidentiary status may not.**

> **The map can be huge. The active lane cannot.**

> **Do not break the damn game while installing project-management machinery.**