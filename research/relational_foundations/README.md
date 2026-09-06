# LOOM 2226 — Relational Foundations Research Index

**Status:** NON-CANON / NON-RUNTIME RESEARCH  
**Purpose:** Index the relational-foundations workstream, its source authority, recovered historical work, execution discipline, and isolated research tooling.

## Authority boundary

This directory does not override current canon, governance, Navigator, GIS, runtime, or production deployment authority.

Governing canon remains under `canon/current/` and `governance/current/`. The current technical research source remains `research/technical_papers/LOOM_2226_Technical_Paper_Series_Complete_v1.0.pdf`. The ranked project research queue remains `research/rabbit_holes/LOOM_2226_Rabbit_Hole_Priority_Table_v1.3.md`.

## Current relational-foundations documents

- `../rabbit_holes/LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md` — governing work plan for this research lane.
- `HISTORICAL_RECONSTRUCTION_v0.1.md` — reconstruction of the earlier AUIF / RQO-1 work and its known failure state.
- `RQO1_RECOVERY_PROTOCOL_v0.1.md` — protocol for reproducing the earlier experiment before new model design.
- `RQO1_HISTORICAL_SOURCE_NOTE_v0.1.md` — source-grounded recovery note for the surviving 28 Aug 2026 RQO-1 implementation/protocol.
- `TERMUX_DEVOPS_WORKFLOW_v0.1.md` — Android/Termux execution and GitHub workflow, isolated from production Navigator/GIS runtime.

## Command surface

From the repository root:

```bash
python -m research.relational_foundations.src.cli status
python -m research.relational_foundations.src.cli validate
python -m research.relational_foundations.src.cli deps
python -m research.relational_foundations.src.cli test
python -m research.relational_foundations.src.cli smoke
python -m research.relational_foundations.src.cli controls
python -m research.relational_foundations.src.cli rqo1-smoke
```

On Termux use the tracked launcher through `bash`; this avoids changing its executable bit and dirtying the Git worktree:

```bash
bash research/relational_foundations/ops/loomrf status
bash research/relational_foundations/ops/loomrf validate
bash research/relational_foundations/ops/loomrf deps
bash research/relational_foundations/ops/loomrf test
bash research/relational_foundations/ops/loomrf controls
bash research/relational_foundations/ops/loomrf rqo1-smoke
```

The numerical RQO-1 stack is research-local in `requirements-rqo1.txt`. Do not install it into the Navigator/GIS production environment.

`smoke` remains infrastructure-only. `rqo1-smoke` is a **protocol-class reconstruction**, not a claim to reproduce the exact historical two-cell run: the surviving protocol specifies approximately N=40, two cells, and 30 steps, but does not identify those exact two cells. The reconstruction declares its substitute cells in output instead of inventing history.

`controls` qualifies the measurement layer against obvious graph classes before candidate dynamics are trusted.

Default research output remains separate from production runtime state:

- Termux/Android: `/storage/emulated/0/Documents/LOOM_RESEARCH/relational_foundations`
- Desktop: `~/Documents/LOOM_RESEARCH/relational_foundations`

Override with `LOOM_RF_OUTPUT` when needed.

## Recovered historical status

The project previously attempted a coordinate-free relational graph model. The meaningful prior negative result was the AUIF-era observation that generic finite-degree relational graphs tended toward expander-like, nonlocal structure rather than manifold-like locality. Short-cycle terms could improve locality but risk hard-coding the desired answer. A later RQO-1 implementation used random-regular baselines, degree-preserving Metropolis rewiring, Ollivier-Ricci curvature, triangle terms, spectral dimension, volume-growth dimension, and a provisional broad-phase gate. Its documented small smoke execution was not a scientifically decisive run.

The present workstream therefore begins with reproduction and diagnostic qualification, not invention.

## Source-preservation rule

Where an exact historical artifact is recovered later, preserve it byte-for-byte under an `archive/` or `recovered/` subdirectory before adapting it. Do not silently rewrite a historical result into a cleaner modern version.

## Non-interference rule

Research code and outputs must remain under `research/relational_foundations/`. It must not modify production release manifests, runtime SQLite files, Navigator/GIS launchers, or the production Python dependency set. The workstream may reuse repository discipline and DevOps patterns, but not production authority or mutable runtime state.
