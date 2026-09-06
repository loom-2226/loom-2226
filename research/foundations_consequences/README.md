# LOOM Foundations & Consequences Program

Status: EXPLORATORY / NON-CANON / NON-RUNTIME

This directory is the parallel work area for the LOOM Foundations & Consequences program. It is intentionally isolated from Navigator, Solar GIS, production runtime, current canon, and certified engineering code.

## Purpose

The program runs four porous but epistemically labelled lanes in parallel:

- A. Empirical / Mathematical — what can be earned by derivation, measurement, falsification or formal constraint.
- B. Speculative / Synthetic — what can be rigorously constructed or explored without pretending it is established physics.
- C. Civilizational / Fictional — what follows when people, institutions, synthetics and cultures live with unresolved science and operational technology.
- D. Adversarial / Wild — alternative frameworks, maverick questions, failed theories and negative controls that may expose hidden assumptions.

The governing rule is: **ideas may move freely; evidentiary status may not.** Fiction may generate scientific questions, and speculative work may suggest candidate mathematics, but neither may be promoted into evidence without independent qualification.

## Program artifacts

- `PROGRAM_CHARTER_v0.1.md` — mission, principles, operating model and consequences.
- `WORKSTREAM_MAP_v0.1.md` — parent workstream, branches, dependencies and expected LOOM value.
- `PORTFOLIO_BACKLOG_v0.1.md` — sequenced epics, current WIP limits and graduation states.
- `SOURCE_REGISTER_v0.1.md` — referenced thinkers, works and intended use.
- `schemas/work_item.schema.json` — canonical machine-readable shape for program work items.
- `src/` — isolated research-support utilities only.
- `tests/` — isolated unit tests for the research-support utilities.

## Isolation contract

This workstream SHALL NOT:

- import production Navigator/GIS/runtime modules;
- modify `src/`, `web/`, `deploy/`, production `data/`, production `geometry/`, or current canon/governance;
- alter current propulsion constants, hidden topology, ship certification, Mc-299m/NRE calibration, or runtime mechanics;
- make production CI or release qualification depend on this research area;
- fit scientific models to desired fiction or current canon outputs.

It MAY:

- read declared research/reference material;
- create non-canon models, notes, registries, scoring utilities and experiment metadata;
- export questions or constraints to other LOOM workstreams through reviewed artifacts;
- preserve retired or disproved ideas as `GHOST` items for historical/worldbuilding value.

## Local execution

Research-support code is designed to run independently:

```bash
python -m unittest discover -s research/foundations_consequences/tests -p "test_*.py" -v
```

No production dependency is required.