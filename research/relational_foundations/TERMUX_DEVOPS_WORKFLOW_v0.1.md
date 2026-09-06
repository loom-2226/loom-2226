# LOOM 2226 — Relational Foundations Termux / DevOps Workflow v0.1

**Date:** 6 September 2026  
**Status:** RESEARCH EXECUTION WORKFLOW — NON-CANON / NON-RUNTIME  
**Goal:** Reuse LOOM's GitHub/Termux delivery discipline without coupling this research lane to Navigator, GIS, campaign state, or the production release manifest.

## 1. Existing LOOM delivery pattern being reused

The production deployment framework already uses a disciplined pattern: fetch from a selected Git ref, validate expected files/hashes, preserve mutable state, install atomically where practical, expose status/validate/update behavior, and fail closed on bad source/hash conditions. Android launchers are kept platform-specific under `deploy/android/`.

Relational-foundations work will reuse those **principles**, but not join the production runtime payload.

## 2. Isolation decision

Do **not** add research files to the production `deploy/loom_update.py` release manifest or the installed Navigator/GIS runtime root.

Preferred Android research root:

`/storage/emulated/0/Documents/LOOM_RESEARCH/relational_foundations`

Preferred Termux working clone:

`~/src/loom-2226`

The Git clone is the source workspace. The shared-storage research root is for configs, results, reports and exported artifacts that should remain easy to inspect from Android file apps.

Production defaults such as `/storage/emulated/0/Documents/LOOM` remain untouched.

## 3. Git / branch discipline

Implementation work uses branches named:

`research/relational-foundations-<short-purpose>`

Rules:

- branch from current `main`;
- touch only `research/relational_foundations/` and, where necessary, relational research planning/index files;
- no edits to Navigator/GIS/runtime code or current canon/governance;
- unit + functional research tests before push;
- use a PR for substantive model changes;
- merge only after the research-local test suite passes and changed-file review confirms the isolation boundary.

Documentation-only recovery commits may land directly on `main` when they do not modify runtime behavior, consistent with current project practice.

## 4. Termux toolchain

Target minimal stack:

- `git`
- `python`
- `pip`
- standard build tooling only where a research dependency requires it
- a research-local virtual environment

Do not install or modify production Navigator/GIS packages merely to satisfy a research dependency.

Recommended environment location:

`~/venvs/loom-relational`

Recommended dependency file:

`research/relational_foundations/requirements-lock.txt`

If a dependency is difficult to build on Android, keep Android as orchestration/status/review and run the heavy experiment on desktop rather than distorting the model to suit the phone.

## 5. Command surface to build

Research should eventually expose one small command surface, analogous in spirit to the deployment framework but research-local:

```text
loomrf status
loomrf update
loomrf validate
loomrf test
loomrf smoke
loomrf run <config>
loomrf report <run-id>
```

Intended meanings:

- `status` — show git ref/SHA, environment, last run and dirty state;
- `update` — fetch/pull the selected research branch/ref only when working tree is safe;
- `validate` — check package files, dependency lock, config schema and output root;
- `test` — run research unit + functional tests;
- `smoke` — reproduce the small RQO-1 compatibility run;
- `run` — execute a frozen config and write immutable run output;
- `report` — summarize an existing run without changing it.

The command wrapper should live under `research/relational_foundations/ops/`, not `deploy/android/`, to avoid implying production runtime authority.

## 6. Run artifact structure

Shared-storage output should be append-only by run ID:

```text
LOOM_RESEARCH/
  relational_foundations/
    runs/
      <run-id>/
        config.json
        provenance.json
        metrics.csv
        summary.json
        stdout.log
        plots/
```

A run ID should encode or record:

- UTC timestamp;
- git SHA;
- config hash;
- seed or seed-set identifier.

No run overwrites another run. Re-analysis creates a new report artifact referencing the original run.

## 7. Validation / fail-closed behavior

A scientific run must refuse to start if any required condition fails:

- dirty source tree unless explicitly allowed for local development;
- missing or invalid frozen config;
- dependency-lock mismatch;
- unknown experiment-contract version;
- unwritable output root;
- collision with an existing run ID;
- missing provenance fields.

A failed run must not emit a normal PASS/FAIL science verdict.

## 8. Phone/desktop sync model

GitHub remains source authority for code/docs/config templates.

Phone and desktop each use their own local clone and research environment. Changes flow through Git commits/push/pull, not by manually copying Python files between devices.

Large generated run outputs should not automatically enter Git. Promote only compact, reviewable artifacts such as:

- frozen configs;
- machine-readable summary tables;
- final reports;
- hashes/provenance;
- selected plots when useful.

Raw bulk outputs can remain local or be packaged separately if later needed.

## 9. Test policy

Before any research Python release/push:

- run unit tests;
- for substantive behavior changes, run unit + functional tests;
- run the deterministic smoke experiment where relevant.

Do **not** run full Navigator/GIS end-to-end regression for research-only changes. If a research change can affect Navigator/GIS, the architecture has already failed and the change should be split/redesigned.

## 10. First implementation sequence

1. recover or reconstruct the RQO-1 Python artifact under `recovered/`;
2. create a clean research package and compatibility wrapper without changing historical logic;
3. add dependency lock and environment capture;
4. add unit tests for graph invariants and diagnostics;
5. add deterministic smoke test;
6. add `loomrf status/validate/test/smoke`;
7. validate on desktop first;
8. validate the same smoke path under Termux;
9. only then add `loomrf run` and the proper increasing-N experiment grid;
10. publish the RF-WP0 reproduction report and STOP / REVISE / CONTINUE verdict.

## 11. Explicit non-goals

This workflow will not:

- launch Navigator or GIS;
- mutate production SQLite databases;
- install research dependencies into the production runtime environment;
- change the production release manifest;
- use Navigator routes as physics calibration;
- promote a research result into canon automatically.

The purpose is to gain the convenience and provenance discipline of the existing GitHub/Termux workflow without creating another dependency inside the main LOOM runtime.
