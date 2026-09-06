# LOOM Foundations & Consequences Program

**Status:** EXPLORATORY / NON-CANON / NON-RUNTIME  
**Active planning version:** v0.4  
**Historical planning artifacts:** retained for provenance.

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
- Avi Loeb / Galileo Project — A↔C comparator.

## Roster versus ancestry

- `MAIN_ROSTER` — preferably alive/current/active/contactable.
- `ANCESTRY` — any era; unrestricted and persistent.
- `BRIDGE` — current thinker spanning squad missions.
- `CASE_WITNESS` — claims/provenance matter without automatic scientific authority.
- `NEGATIVE_CONTROL` / `GHOST` — failed or adverse material retained because it teaches us something.

Pauli and Jung live in **Squad B ancestry**; Hynek/Fort/SPR in **Squad C ancestry**; Leibniz/Noether/Gödel/Hawking and related foundations in **Squad A ancestry**.

## Governing rules

> **Ideas may move freely; evidentiary status may not.**

> **Follow the strongest stream, not every stream.**

Three-squad/current+historical convergence is a **research-priority signal, not an evidence multiplier**.

## Active governance / planning artifacts

- `PROGRAM_CHARTER_v0.4.md` — focused active charter.
- `WORKSTREAM_MAP_v0.4.md` — active stream map and convergence routing.
- `PORTFOLIO_BACKLOG_v0.3.md` — scored active/ready/blocked/parked backlog.
- `CONVERGENCE_PRIORITY_MODEL_v1.0.md` — weighted convergence + strategic value + LOOM-WSJF.
- `SCALED_AGILE_OPERATING_MODEL_v1.0.md` — lightweight PI/WIP/dependency model.
- `SQUAD_ARCHITECTURE_v1.1.md` — current roster/ancestry/bridge/case model.
- `SQUAD_CURRENT_CONTRIBUTIONS_AND_FUTURE_CONSTRUCTION_v1.0.md` — plain-language member-by-member map of what each current squad/bridge already contributes to LOOM and what we could legitimately build from it later; includes explicit non-endorsement disclaimer and source-boundary rule.
- `CURRENT_LOOM_LINEAGE_AUDIT_v1.0.md` + supplement — canon/mechanics attribution audit.
- `research_corpus/CONTRIBUTOR_WEIGHT_REGISTER_v1.0.md` — LOOM Utility Weights for current and historical contributors.
- `research_corpus/MANIFEST_v1.3.md` — active research-corpus navigation index.
- current/ancestral squad dossiers under `research_corpus/`.
- `schemas/work_item.schema.json` and isolated `src/` / `tests/`.

Repository-wide squad/convergence discovery index:
`../../docs/LOOM_FOUNDATIONS_SQUAD_INDEX_v1.2.md`

Repository-wide attribution policy:
`../../governance/LOOM_INTELLECTUAL_ANCESTRY_AND_ATTRIBUTION_POLICY_v1.1.md`

Earlier versions remain in Git and SHALL NOT be silently overwritten or deleted.

## Five lanes

- **A. Empirical / Mathematical**
- **B. Speculative / Synthetic**
- **C. Civilizational / Fictional**
- **D. Adversarial / Wild**
- **P. Phenomenological / Anomaly**

## Current PI — Focus Reset

### FINISH
- **S1 Geometrogenesis** — T0 frozen qualification; PR #19 untouched.

### SHARPEN
- **S4 Identity & Protected Observables** — sole additional active science/discovery stream.

### BUILD
- **F2 Synthetic Identity & Personhood** — sole active fiction/world stream.

### ENABLE
- **P1 Anomaly Registry & Evidence Taxonomy** — bounded method/schema item only.

### READY / WAITING
- S3 Causality & Chronology.
- X1 Reconstruction / Observers / Effective Reality.
- F3 Xeno Epistemology & Ontology.
- F1 Schools of Physics & Metaphysics.

### HIGH-VALUE BUT BLOCKED
- S5 Matter / Information / Relational Control.
- X2 Information as Causal Structure.
- P4 Cross-Domain Correlation.
- S2 Continuum & Universality unless S1 yields a qualified positive direction.

**No fifth substantive active stream.** New work must replace, complete or formally pre-empt an active item.

## Weighted convergence

Current and historical contributors are weighted by **utility to LOOM overall**, then clustered to prevent lineage/headcount inflation. Historical convergence can be as valuable as current-roster convergence when it is independently relevant.

High convergence raises priority and source depth. It cannot:
- change scientific status;
- tune a frozen experiment;
- bypass dependencies;
- create extra WIP.

## Research-corpus convention

Preserve for every material influence:
1. source claim;
2. LOOM interpretation;
3. LOOM extension;
4. LOOM result;
5. `does_not_establish` boundary;
6. relevant criticism/counterweight.

The corpus is complete for the currently identified LOOM-relevant lineage, not every publication in every career.

## Isolation contract

This workstream SHALL NOT:
- import production Navigator/GIS/runtime modules;
- modify production runtime/data/geometry to satisfy a research hypothesis;
- alter propulsion constants, hidden topology, certification, Mc-299m/NRE calibration or locked canon without separate promotion;
- make production CI/release qualification depend on exploratory research;
- fit scientific models to desired fiction/canon outputs;
- use UAP/psi/paranormal/xeno material to calibrate M1/M2/M3 or relational response parameters.

## Local execution

```bash
python -m unittest discover -s research/foundations_consequences/tests -p "test_*.py" -v
```

No production dependency is required.
