# LOOM 2226 — Convergence Priority & Scaled-Agile Portfolio Model v1.0

**Status:** ACTIVE PORTFOLIO GOVERNANCE — NON-CANON — NON-RUNTIME  
**Date:** 7 September 2026

## 1. Purpose

LOOM now has enough attractive rabbit holes that the main risk is no longer idea scarcity. It is **portfolio sprawl**.

This model exists to keep attention on the highest-value individual workstreams while deliberately rewarding unusually strong convergence among:

- current Squad A / B / C members;
- bridge members;
- historical ancestral lineages;
- independent methodological modes;
- LOOM science, canon, simulation, fiction and gameplay needs.

The model borrows the useful parts of SAFe/WSJF — explicit economic prioritization, WIP limits, program increments, dependency gates and enablers — without turning a small LOOM team into bureaucracy cosplay.

> **Convergence increases priority. It does not increase truth.**

## 2. Two-stage portfolio decision

Every proposed stream is evaluated in two separate stages.

### Stage A — Strategic Value Score (SVS)
Determines whether the stream deserves scarce LOOM attention at all.

`SVS = BLV + 1.5(CV) + RROE`

Where:

- `BLV` = Base LOOM Value, 0–20;
- `CV` = Convergence Value, 0–20;
- `RROE` = Risk Reduction / Opportunity Enablement, 0–10.

Maximum SVS = 60.

**Convergence is deliberately overweighted by 1.5×.** The purpose is to notice questions that independently recur across serious science, radical reframing, phenomenology and intellectual history.

### Stage B — LOOM-WSJF
Used only among streams already in the same strategic tier and not blocked by dependencies.

`LOOM-WSJF = (SVS + TC) / Job Size`

Where:

- `TC` = Time Criticality / Dependency Unlock, 0–10;
- `Job Size` = Fibonacci-like 1, 2, 3, 5, 8, 13.

A tiny low-value task cannot jump ahead of a major strategic stream merely because it is tiny. **SVS tier comes first; WSJF sequences work inside the tier.**

## 3. Base LOOM Value — BLV (0–20)

Score each category 0–4.

1. **Scientific / miracle-reduction leverage** — could this constrain, derive, falsify or cleanly isolate M1/M2/M3 or the physics before them?
2. **Canon coherence leverage** — could this clarify a major unresolved canon boundary across more than one document/domain?
3. **World / fiction yield** — does it produce institutions, history, culture, conflict, philosophy or xeno depth?
4. **Gameplay / simulation leverage** — can it improve mechanics, epistemic simulation, operations, Navigator-facing concepts or player inference?
5. **Architectural reuse** — does the work create methods/data structures/epistemic tools reusable across LOOM?

`BLV = sum(5 categories)`

A stream with `BLV < 12` normally remains SEED/PROBE no matter how fashionable or convergent it looks.

## 4. Convergence Value — CV (0–20)

Convergence is evaluated across **independent intellectual lineages**, not raw headcount.

### 4.1 Current-member component — 0–8

For the live/current rosters and bridges:

- identify each materially relevant contributor;
- apply their LOOM Utility Weight from `CONTRIBUTOR_WEIGHT_REGISTER_v1.0.md`;
- group contributors into independent lineage/method clusters;
- within one cluster, the highest-weight contributor counts fully, the second at 35%, later members at 15% each;
- cap each cluster at 7 weighted points;
- normalize the branch total to 0–8.

This prevents eight related people from becoming eight independent votes.

### 4.2 Historical-lineage component — 0–8

Apply the same logic to ancestral figures/programs.

Historical convergence is intentionally worth **as much as current-roster convergence** when the lineage is genuinely independent and materially relevant. Recency is not a proxy for intellectual importance.

### 4.3 Cross-squad component — 0–2

- +0.75 for each additional independently contributing squad beyond the first;
- +0.5 for a bridge member who contributes a genuinely non-redundant formulation;
- maximum 2.

### 4.4 Method-mode diversity — 0–2

Award up to 2 points when a question independently appears through different modes such as:

- formal/mathematical;
- computational;
- phenomenological;
- instrument/measurement;
- philosophical/conceptual;
- adversarial/skeptical;
- historical/cultural.

The modes must supply different information, not merely different rhetoric.

### 4.5 Independence rule

Before awarding convergence, ask:

> Could these contributors reasonably have inherited the same claim from one another or from the same source tradition?

If yes, cluster them.

Examples:

- Pauli → Jung → Primas → Atmanspacher is a rich lineage, but not four independent empirical observations.
- Fort → Hynek → Vallée contains historical influence and methodological evolution; it is not three independent proofs of a phenomenon.
- Surya causal sets and Loll CDT count as more independent than two papers within the same causal-set program.

## 5. Contributor weights are LOOM utility, not credibility

The 1–5 weights in the contributor register answer:

> **How much can this person's relevant body of work help LOOM overall?**

They do **not** answer:

- how smart the person is;
- whether their controversial claims are true;
- whether they are mainstream;
- whether LOOM agrees with them.

A high-weight negative-control thinker can increase priority by exposing a dangerous failure mode.

## 6. Risk Reduction / Opportunity Enablement — RROE (0–10)

High scores go to work that:

- can kill an attractive but wrong direction cheaply;
- unlocks several downstream branches;
- defines an evidence or identity schema used elsewhere;
- prevents canon contamination;
- prevents expensive post-hoc model fitting;
- supplies a reusable benchmark/null model.

This is why P1 Anomaly Registry can outrank more glamorous anomaly interpretation work even though it is not itself the interesting mystery.

## 7. Time Criticality / Dependency Unlock — TC (0–10)

Examples:

- 10: currently blocks the active execution stream or a production/canon decision;
- 7–9: unlocks the next PI objective;
- 4–6: useful this PI but not blocking;
- 1–3: can safely wait;
- 0: purely opportunistic.

## 8. Strategic tiers

### T0 — PROTECT / FINISH
A branch already in qualification or a binding dependency whose interruption would destroy experimental integrity or create rework.

T0 can override raw SVS ordering.

### T1 — HIGHEST VALUE
Normally `SVS >= 48`, with BLV >=12 and no unresolved hard dependency.

Maximum **two T1 discovery/design streams in addition to one T0 execution stream**.

### T2 — READY / IMPORTANT
Normally `SVS 40–47` or a T1 stream blocked on another result.

Keep ready, source-deepened and bounded. Do not actively elaborate unless WIP opens.

### T3 — PARKED / SEED
Normally `SVS <40`, or stronger score but low readiness / high dependency.

Preserve; do not feed it continuously.

### CONVERGENCE HOTSPOT
Any stream with `CV >=17` is flagged even if blocked.

A hotspot earns a short convergence memo and backlog visibility. It does **not** automatically become active execution.

## 9. WIP guardrails

At any time Foundations & Consequences may have:

1. **ONE T0 scientific execution/qualification stream.**
2. **ONE T1 scientific/discovery stream.**
3. **ONE T1 fiction/world/simulation stream.**
4. **ONE time-boxed enabling-method item** such as schema/provenance work.

Everything else is READY, PROBE-CORPUS, BLOCKED or PARKED.

This is intentionally tighter than v0.2.

### The Kevin/Sol anti-rabbit-hole rule

A new shiny branch may enter active WIP only by:

- replacing an existing active item;
- satisfying a completed-item release;
- or meeting a documented convergence-hotspot trigger **and** displacing a lower-SVS active stream.

It may not simply become "also active."

## 10. Program Increment model

LOOM uses lightweight Program Increments.

A PI contains:

- one T0 anchor objective;
- up to two T1 objectives;
- one enabler objective;
- explicit exit criteria;
- a list of READY items that are deliberately **not being worked**.

A PI closes when its anchor objective reaches a verdict/milestone, not when every interesting side investigation is exhausted.

At PI close:

1. rescore changed streams;
2. update convergence map;
3. inspect new squad/ancestry work;
4. retire/GHOST dead ideas;
5. select the next limited WIP set.

## 11. Mandatory overlays that do not consume a separate WIP slot

### D1 Red Team
Every positive scientific result gets a null/alternative/kill pass.

### Attribution
Every materially inherited idea retains source ancestry.

### Epistemic firewall
No fiction, anomaly or philosophical fit becomes evidence through repetition.

### Convergence watch
New corpus additions may update CV without activating the branch.

## 12. Current highest convergence zones

The current corpus identifies these broad hotspots:

1. **S4 / X1 — Identity, protected observables, reconstruction and effective reality.**
   - Red Pens: Adlam, Lloyd, Dittrich/Oriti, relational-observable ancestry.
   - Unsupervised: Whitehead, Bohm, Maturana/Varela, Pauli/Jung→Primas/Atmanspacher, Wolfram/Hoffman/Kastrup question pressure.
   - Freaks: continuity/anomalous-memory phenomenology as taxonomy pressure only.
   - LOOM-wide consequence: M1 definition, synthetics, GM/player epistemology, xeno interpretation.

2. **S3 — Causality, chronology and the status of time.**
   - Red Pens: Surya, Loll, Smolin, Adlam; Gödel/Hawking/Penrose/Wheeler-DeWitt ancestry.
   - Unsupervised: Barbour, Wolfram; Bergson/Whitehead/Prigogine ancestry.
   - Freaks: subjective-time/chronology reports as phenomenological question generators only.
   - LOOM-wide consequence: possible M3 separation and safer transport ontology.

3. **X2 / S5 — Information, causal architecture and control.**
   - Red Pens: Lloyd/Bell/Noether/resource-accounting line.
   - Bridge: Sara Walker.
   - Unsupervised ancestry: Schrödinger, Bateson, Maturana/Varela, Prigogine, Faggin questions.
   - Freaks/ancestry: Rhine/PEAR/Radin plus Hyman/French as contested experiment/negative-control corpus.
   - LOOM-wide consequence: M2 boundary, synthetics, life, xeno systems.

4. **P1/P3 — Evidence objects and instrumented anomalies.**
   - Freaks: Hynek/Sturrock/Vallée/Haines/Strand/Nolan/French/Truzzi lineages.
   - Red-Pen bridge pressure: standard instrumentation/null-model discipline; Loeb/Galileo comparator.
   - LOOM-wide consequence: Strangeness Problem, TAAC/TAAM, gameplay evidence model, xeno forensics.

5. **F2/F3 — Synthetic identity and xeno epistemology.**
   - Strong cross-stream rather than purely scientific convergence.
   - These are where science/speculation/phenomenology can create major world/game value without being mistaken for physical proof.

## 13. Governing principle

> **Follow the strongest stream, not every stream. Follow convergence when independent traditions keep finding the same question. Then make the Red Pens earn the answer.**
