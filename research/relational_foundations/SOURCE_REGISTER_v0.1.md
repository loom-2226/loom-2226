# LOOM 2226 — Relational Foundations Source Register v0.1

**Date:** 6 September 2026  
**Status:** PROVENANCE / RECOVERY REGISTER — NON-CANON

## Current repository sources

| Source | Location | Role |
|---|---|---|
| Technical Paper Series v1.0 | `research/technical_papers/LOOM_2226_Technical_Paper_Series_Complete_v1.0.pdf` | Existing physics/research baseline; does not make relational foundations canon. |
| Rabbit-Hole Priority Table v1.3 | `research/rabbit_holes/LOOM_2226_Rabbit_Hole_Priority_Table_v1.3.md` | Ranked research queue; RH-024 carries the M1/M2 parent-theory seam. |
| Relational Foundations Independent Work Plan v0.1 | `research/rabbit_holes/LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md` | Current bounded research work plan. |
| Historical Reconstruction v0.1 | `research/relational_foundations/HISTORICAL_RECONSTRUCTION_v0.1.md` | Reconstructs the earlier AUIF/RQO-1 work from surviving project records. |
| RQO-1 Recovery Protocol v0.1 | `research/relational_foundations/RQO1_RECOVERY_PROTOCOL_v0.1.md` | Defines reproduction before reinvention. |
| RQO-1 Historical Source Note v0.1 | `research/relational_foundations/RQO1_HISTORICAL_SOURCE_NOTE_v0.1.md` | Records mechanics recovered from surviving File Library source artifacts. |
| RQO-1 Source Audit v0.1 | `research/relational_foundations/RQO1_SOURCE_AUDIT_v0.1.md` | Records sign, diagnostic, RNG and fixed-gate audit findings without rewriting history. |
| Termux / DevOps Workflow v0.1 | `research/relational_foundations/TERMUX_DEVOPS_WORKFLOW_v0.1.md` | Isolated GitHub/Termux execution plan. |

## Governing authority references

Current canon and authority remain in `canon/current/` and `governance/current/`, including the v2.4 three-volume canon, Earth/Solar Atlas v3.2 and Core Mechanics v0.5. These are reference constraints, not outputs of this research program.

## Recovered historical sources outside Git

### Relational Foundations Research Hypotheses v0.2

A File Library artifact titled `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf` survives from 28 August 2026. Its substance includes the RQO-1 relation-first/non-expander gate, locality/dimension criteria, relational-clock caution, and the rule against using high-strangeness anecdotes as calibration evidence.

**Current state:** recovered in File Library, but not yet preserved byte-for-byte under Git. Do not manufacture a replacement and label it as the original.

### RQO-1 implementation and protocol

The actual surviving 28 August 2026 source artifacts are:

- `rqo1_experiment.py`
- `RQO-1_protocol.md`

They were recovered through the project File Library and establish the mechanics recorded in `RQO1_HISTORICAL_SOURCE_NOTE_v0.1.md`: random-regular graphs, degree-preserving Metropolis rewiring, sampled Ollivier–Ricci curvature, triangle coupling, spectral/volume-growth diagnostics and the provisional `1.3 * log(N)` gate.

**Current state:** source content recovered in File Library. Git contains `src/rqo1_reconstruction.py`, a labeled reconstruction/adaptation, **not** a byte-for-byte archival copy of the File Library Python object. The exact two parameter cells used in the old N≈40/two-cell/30-step smoke are still not established by surviving protocol text and must not be invented.

### AUIF v1 microscopic experiment artifact

Project history preserves the earlier negative conclusion that generic finite-degree relational graphs were expander-like/nonlocal and that locality-promoting short-cycle terms risked hard-coding the answer.

**Current state:** no separate earlier AUIF executable artifact has been recovered in Git. R3 has now reproduced the null expander failure independently across increasing N using the recovered RQO-1 mechanics.

## Recovery policy

For every newly recovered historical artifact:

1. save exact bytes before editing;
2. calculate SHA-256;
3. record original filename/date/source when known;
4. place exact exported artifacts under `research/relational_foundations/recovered/` when byte-preservation becomes available;
5. keep reconstructed/adapted versions separately labeled;
6. never silently replace provenance material with a cleaned-up rewrite;
7. never describe an experimental correction as historical behavior.
