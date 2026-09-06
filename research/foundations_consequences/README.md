# LOOM Foundations & Consequences Program

**Status:** EXPLORATORY / NON-CANON / NON-RUNTIME  
**Active planning version:** v0.2  
**Historical planning artifacts:** v0.1 retained for provenance.

This directory is the isolated parallel work area for LOOM Foundations & Consequences. It runs alongside Navigator, Solar GIS, simulation/runtime engineering, canon maintenance and ship/operations development without becoming a production dependency.

## Permanent external-thinking squads

### Squad A — The Adults With Red Pens
Daniele Oriti · Bianca Dittrich · Sumati Surya · Fotini Markopoulou · Lee Smolin · Emily Adlam · Renate Loll · Seth Lloyd

Scientific/methodological murder board: emergence, continuum, causality, observables, identity and physical-information constraints.

### Squad B — The Respectably Unsupervised
Stephen Wolfram · Julian Barbour · Donald Hoffman · Bernardo Kastrup · Federico Faggin · Eric Weinstein · A. Garrett Lisi · Nassim Haramein

Radical-question engine: heterodox frameworks, metaphysical stress tests, outsider programs, failed-theory lessons and negative controls.

The name is LOOM humor, not a blanket scientific judgment. Status attaches to specific claims and sources.

### Border-Crosser — Sara Imari Walker
Attached to both squads for causal architecture, information, assembly theory and complexity metrology.

## Governing rule

> **Ideas may move freely; evidentiary status may not.**

The program can explore anything worth exploring. Scientific promotion still requires independent qualification.

## Active artifacts

- `PROGRAM_CHARTER_v0.2.md` — active program charter and squad-integrated operating model.
- `WORKSTREAM_MAP_v0.2.md` — active workplan, branch dependencies, squad ancestry and consequences.
- `SOURCE_REGISTER_v0.2.md` — fast source/role/branch lookup.
- `SQUAD_CHARTER_v1.0.md` — permanent squad membership, mandate and attribution requirements.
- `PORTFOLIO_BACKLOG_v0.1.md` — current staged backlog/WIP record; update when PI status changes.
- `research_corpus/BIBLIOGRAPHY_v1.0.md` — primary bibliography with DOI/arXiv/stable URLs.
- `research_corpus/ADULTS_WITH_RED_PENS_DOSSIER_v1.0.md` — detailed scientific-squad research notes.
- `research_corpus/RESPECTABLY_UNSUPERVISED_DOSSIER_v1.0.md` — detailed heterodox/speculative/negative-control research notes.
- `research_corpus/SARA_WALKER_BRIDGE_DOSSIER_v1.0.md` — detailed bridge corpus.
- `schemas/work_item.schema.json` — machine-readable program work-item shape.
- `src/` — isolated research-support utilities only.
- `tests/` — isolated unit tests.

Historical v0.1 charter/map/register remain in the directory and SHALL NOT be silently overwritten or deleted.

## Research-corpus convention

The repository stores detailed original summaries, branch mappings, bibliographic metadata, counterarguments, epistemic labels and stable primary-source links. It does not mirror copyrighted papers wholesale merely for convenience.

For each material external influence preserve:
1. what the source actually claims;
2. why LOOM cares;
3. what LOOM extends from it;
4. what it does **not** establish.

Repository-wide attribution policy:

`../../governance/LOOM_INTELLECTUAL_ANCESTRY_AND_ATTRIBUTION_POLICY_v1.0.md`

Global index:

`../../docs/LOOM_FOUNDATIONS_SQUAD_INDEX_v1.0.md`

## Four lanes

- **A. Empirical / Mathematical** — derivation, measurement, falsification, formal constraint.
- **B. Speculative / Synthetic** — rigorous construction/question generation without evidentiary laundering.
- **C. Civilizational / Fictional** — institutional, social, synthetic, xeno and player-facing consequences.
- **D. Adversarial / Wild** — alternatives, maverick questions, failed theories and negative controls.

## Current WIP posture

- S1 Geometrogenesis — ACTIVE / QUALIFICATION; frozen PR #19 remains untouched.
- S3A/S3B Causality & Time — PROBE / discovery.
- S4 Identity & Protected Observables — PROBE / discovery.
- F2 Synthetic Identity & Personhood — ACTIVE DESIGN.
- F3 Xeno Epistemology & Ontology — ACTIVE DESIGN.
- F1 Schools of Physics & Metaphysics — PROBE.
- Other branches staged until WIP opens.

## Isolation contract

This workstream SHALL NOT:
- import production Navigator/GIS/runtime modules;
- modify production runtime/data/geometry merely to satisfy a research hypothesis;
- alter propulsion constants, hidden topology, certification, Mc-299m/NRE calibration or current canon without separate promotion;
- make production CI/release qualification depend on exploratory research;
- fit scientific models to desired fiction/canon outputs.

It MAY:
- read declared references;
- create non-canon experiments, models, registries and scoring utilities;
- export explicitly labelled questions/constraints through reviewed artifacts;
- preserve failed work as `GHOST` material with attribution intact.

## Local execution

```bash
python -m unittest discover -s research/foundations_consequences/tests -p "test_*.py" -v
```

No production dependency is required.
