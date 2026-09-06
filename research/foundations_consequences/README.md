# LOOM Foundations & Consequences Program

**Status:** EXPLORATORY / NON-CANON / NON-RUNTIME  
**Active planning version:** v0.3  
**Historical planning artifacts:** v0.1–v0.2 retained for provenance.

This directory is the isolated parallel work area for LOOM Foundations & Consequences. It runs alongside Navigator, Solar GIS, simulation/runtime engineering, canon maintenance and ship/operations development without becoming a production dependency.

## Permanent external-thinking squads

### Squad A — The Adults With Red Pens
Daniele Oriti · Bianca Dittrich · Sumati Surya · Fotini Markopoulou · Lee Smolin · Emily Adlam · Renate Loll · Seth Lloyd

Scientific/methodological murder board: emergence, continuum, causality, observables, identity and physical-information constraints.

### Squad B — The Respectably Unsupervised
Stephen Wolfram · Julian Barbour · Donald Hoffman · Bernardo Kastrup · Federico Faggin · Eric Weinstein · A. Garrett Lisi · Nassim Haramein

Radical-question engine: heterodox frameworks, metaphysical stress tests, outsider programs, failed-theory lessons and negative controls.

### Squad C — The Freaks With Clipboards
Jacques Vallée · Garry Nolan · Colm Kelleher · Jeffrey J. Kripal · Diana Walsh Pasulka · Etzel Cardeña · Christopher French · Dean Radin · Erling P. Strand · Bob Lazar (`CASE_WITNESS` / Contested Primary-Witness Seat)

Formal subtitle: **LOOM Anomalous Phenomenology & High-Strangeness Review Squad**. Preserve reports, measurements, witness/sensor provenance and ordinary explanations before selecting an ontology.

The names are LOOM humor, not blanket judgments. Status attaches to specific claims and sources.

### Bridges
- Sara Imari Walker — A↔B.
- Harald Atmanspacher — B↔C.
- Avi Loeb / Galileo Project — A↔C comparator, not yet permanent main roster.

## Roster versus ancestry

- `MAIN_ROSTER` — preferably alive/current/active/contactable.
- `ANCESTRY` — any era; unrestricted and persistent.
- `BRIDGE` — current thinker spanning squad missions.
- `CASE_WITNESS` — claims/provenance matter without automatic scientific authority.
- `NEGATIVE_CONTROL` / `GHOST` — failed or adverse material retained because it teaches us something.

Pauli and Jung therefore live in **Squad B ancestry**, not the current roster. Hynek, Fort, early SPR and related historical investigators live in **Squad C ancestry**. Leibniz, Noether, Gödel, Hawking and other foundational figures live in **Squad A ancestry**.

## Governing rule

> **Ideas may move freely; evidentiary status may not.**

Three-squad convergence is a **research-priority signal, not an evidence multiplier**.

## Active artifacts

- `PROGRAM_CHARTER_v0.3.md` — current five-lane program charter.
- `WORKSTREAM_MAP_v0.3.md` — active branch/squad/lineage map.
- `PORTFOLIO_BACKLOG_v0.2.md` — current WIP and sequencing.
- `SQUAD_ARCHITECTURE_v1.1.md` — governing roster/ancestry/bridge/case model.
- `CURRENT_LOOM_LINEAGE_AUDIT_v1.0.md` — canon/mechanics attribution audit.
- `CURRENT_LOOM_LINEAGE_AUDIT_SUPPLEMENT_v1.0.md` — Rabbit Hole, Ship Operations and further audit findings.
- `research_corpus/MANIFEST_v1.1.md` — current research-corpus index.
- `research_corpus/ADULTS_WITH_RED_PENS_DOSSIER_v1.0.md`
- `research_corpus/RESPECTABLY_UNSUPERVISED_DOSSIER_v1.0.md`
- `research_corpus/FREAKS_WITH_CLIPBOARDS_DOSSIER_v1.0.md`
- `research_corpus/ANCESTRY_ADULTS_WITH_RED_PENS_v1.0.md`
- `research_corpus/ANCESTRY_RESPECTABLY_UNSUPERVISED_v1.0.md`
- `research_corpus/ANCESTRY_FREAKS_WITH_CLIPBOARDS_v1.0.md`
- `research_corpus/SARA_WALKER_BRIDGE_DOSSIER_v1.0.md`
- `schemas/work_item.schema.json` — machine-readable program work-item shape.
- `src/` / `tests/` — isolated research-support code and tests.

Repository-wide discovery index:
`../../docs/LOOM_FOUNDATIONS_SQUAD_INDEX_v1.1.md`

Repository-wide attribution policy:
`../../governance/LOOM_INTELLECTUAL_ANCESTRY_AND_ATTRIBUTION_POLICY_v1.1.md`

Earlier versions remain in Git and SHALL NOT be silently overwritten or deleted.

## Five lanes

- **A. Empirical / Mathematical** — derivation, measurement, falsification, formal constraint.
- **B. Speculative / Synthetic** — rigorous construction/question generation without evidentiary laundering.
- **C. Civilizational / Fictional** — institutional, social, synthetic, xeno and player-facing consequences.
- **D. Adversarial / Wild** — alternatives, maverick questions, failed theories and negative controls.
- **P. Phenomenological / Anomaly** — reports, measurements, experiences and residuals before ontology.

## Current WIP posture

- S1 Geometrogenesis — ACTIVE / QUALIFICATION; frozen PR #19 untouched.
- S3 Causality & Chronology — PROBE.
- S4 Identity & Protected Observables — PROBE.
- F2 Synthetic Identity & Personhood — ACTIVE DESIGN.
- F3 Xeno Epistemology & Ontology — ACTIVE DESIGN.
- F1 Schools of Physics & Metaphysics — PROBE.
- P1 Anomaly Registry & Evidence Taxonomy — documentation/method PROBE.
- P2/P3 — corpus probes only.
- P4 Cross-Domain Correlation — blocked until P1 independence/selection/null-model rules mature.

## Research-corpus convention

The repository stores detailed original summaries, branch mappings, bibliographic metadata, counterarguments, epistemic labels and stable primary-source links. It does not mirror copyrighted papers wholesale merely for convenience.

For each material external influence preserve:
1. what the source actually claims;
2. why LOOM cares;
3. what LOOM extends from it;
4. what LOOM itself later establishes;
5. what the source does **not** establish where confusion is plausible.

The corpus is **complete for the currently identified LOOM-relevant lineage**, not a claim to contain every work in each thinker's career. Deepen a branch's bibliography before formal qualification or outreach.

## Isolation contract

This workstream SHALL NOT:
- import production Navigator/GIS/runtime modules;
- modify production runtime/data/geometry merely to satisfy a research hypothesis;
- alter propulsion constants, hidden topology, certification, Mc-299m/NRE calibration or locked canon without separate promotion;
- make production CI/release qualification depend on exploratory research;
- fit scientific models to desired fiction/canon outputs;
- use UAP/psi/paranormal/xeno anecdotes to calibrate M1, M2 or relational response parameters.

It MAY:
- read declared references;
- create non-canon experiments, models, registries and scoring utilities;
- export explicitly labelled questions/constraints through reviewed artifacts;
- preserve failed work as `GHOST` material with attribution intact;
- queue source-level provenance improvements for the next normal canon/document revision.

## Local execution

```bash
python -m unittest discover -s research/foundations_consequences/tests -p "test_*.py" -v
```

No production dependency is required.