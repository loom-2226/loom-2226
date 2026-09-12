# LOOM 2226 — Experience One Product Convergence Workplan v1.1

**Status:** GOVERNED SCOPED UPDATE TO EXPERIENCE ONE WORKPLAN v1.0 — governing only after merge to protected `main`  
**Date:** 12 September 2026  
**Primary change class:** `class:governance`  
**Repository:** `loom-2226/loom-2226`  
**Parent workplan:** `governance/current/LOOM_EXPERIENCE_ONE_PRODUCT_CONVERGENCE_WORKPLAN_v1.0.md`  
**Parent fixed baseline commit:** `32fd0b40be59ad333473c7fc2fdc2798562597ee`  
**Product target:** **Experience One — A Day Aboard Wayfarer**  
**Qualification scenario:** **Ceres → Neptune**  
**Canon effect:** none  
**Engineering/runtime/data effect:** none  
**Research effect:** none  

---

## 0. Purpose and authority

This document is a **scoped governing update** to Experience One Workplan v1.0. It exists to reconcile a review finding raised immediately after v1.0 adoption without rewriting the historical v1.0 baseline.

The v1.0 plan remains the fixed reference for all unchanged sections. This v1.1 update supersedes v1.0 only in the specific areas named below:

1. failure-diagnosis taxonomy;
2. gate-status reporting semantics;
3. evidence required for a claimed `PASS`;
4. the requirement to state a falsifier for each claimed `PASS`.

All other v1.0 scope, sequencing, gates, parking-lot rules, E1.0 spikes, GO/REPLAN discipline, authority boundaries, Pixel target, Research Lab firewall, Mara authority limits, explicit-user authorization requirement, and anti-rabbit-hole controls remain unchanged.

This document does not create a fifth substantive WIP stream and does not authorize implementation merely by describing it.

Where this document conflicts with the parent v1.0 workplan in the four scoped areas above, v1.1 controls. Where this document is silent, v1.0 controls.

---

# 1. Review finding being reconciled

Independent review of v1.0 identified that the parent plan's world-texture diagnostic rule contained four categories:

- `DATA_FAILURE`
- `PROJECTION_FAILURE`
- `SYNTHESIS_FAILURE`
- `PRESENTATION_FAILURE`

The same review process separately identified two additional failure modes:

- `MECHANICS_FAILURE`
- `MOTIVATION_FAILURE`

Those two are real and non-redundant, but they do not belong in the same layer as the original four.

The four original categories answer:

> **Why did the world/canon fail to feel alive, intelligible, or discoverable?**

The two additional categories answer:

> **Why did the overall Experience One loop fail even when world texture may have been delivered correctly?**

Therefore v1.1 does **not** flatten these into one six-item list. It establishes two diagnostic layers.

---

# 2. Two-layer Experience One failure taxonomy

## 2.1 Layer A — World-texture delivery failures

Use these when the defect concerns the user's ability to perceive, understand, or care about existing canon/world state because of how that state is stored, assembled, synthesized, or presented.

### `DATA_FAILURE`

The underlying governed world/data/canon does not contain enough meaningful information to support the intended experience.

Typical question:

> **Is the thing we want to surface actually there?**

Corrective direction:

- verify authority/source first;
- do not invent a projection fix for missing data;
- do not write cosmetic lore to conceal absent world structure;
- any new canon/world development follows its own authority/change process and is not auto-authorized by E1.

### `PROJECTION_FAILURE`

Meaningful governed information exists, but the context/projection/service layer does not surface the right subset, relationships, provenance, or salience.

Typical question:

> **The world knows this — why can't the user/Mara see it?**

Corrective direction:

- repair read-only context assembly, selection, entity resolution, provenance, or service projection;
- do not author new canon merely because the projection is incomplete.

### `SYNTHESIS_FAILURE`

The right structured information reaches Mara or another synthesis layer, but the explanation is dull, confusing, misleading, overconfident, or fails to communicate significance.

Typical question:

> **The evidence is present — why did the explanation fail?**

Corrective direction:

- improve synthesis/prompting/context organization or explanation rules;
- preserve epistemic labels;
- do not modify world data to solve a language/meaning-making defect.

### `PRESENTATION_FAILURE`

The information and synthesis are adequate, but the UX buries, fragments, overloads, or visually obscures the thing the user needs.

Typical question:

> **The system knows it and can explain it — why can't the user find or operate it?**

Corrective direction:

- improve hierarchy, interaction, selection, linking, touch behavior, visual composition, or progressive disclosure;
- do not prescribe new canon or a new simulation subsystem as a first response.

---

## 2.2 Layer B — Whole-experience failures

Use these when the failure is not specifically a world-texture delivery defect.

### `MECHANICS_FAILURE`

The user understands what they want to do, but the deterministic simulation/engineering/navigation/runtime machinery cannot coherently support the requested action within the qualified/governed envelope.

Examples:

- intent is clear but no valid route can be computed;
- execution semantics cannot bridge planning to authoritative state;
- the action requires an unqualified physical assumption;
- persistent consequence cannot be committed honestly;
- a required mechanic exists only as presentation fiction.

Typical question:

> **The user knows what they want — can LOOM actually do it honestly?**

Corrective direction:

- identify the actual mechanical/authority seam;
- constrain the experience to what is qualified when possible;
- escalate to the proper engineering/runtime/data lane when necessary;
- do not use Mara or presentation copy to narrate around the missing mechanic.

### `MOTIVATION_FAILURE`

The machinery works and the world may be correctly surfaced, but the user has no reason to care, investigate, decide, or continue.

Examples:

- the user understands Ceres but feels no curiosity;
- Neptune context is accurate but nothing invites a question;
- flight alternatives are valid but choosing among them feels meaningless;
- the experience produces competence without desire for a second action/day.

Typical question:

> **Everything works — why doesn't the user care?**

Corrective direction:

- determine whether significance is genuinely absent or merely poorly surfaced;
- distinguish `MOTIVATION_FAILURE` from `SYNTHESIS_FAILURE` and `PRESENTATION_FAILURE` before authoring anything new;
- prefer exposing existing conflicts, stakes, relationships, constraints, opportunities, history, or human-scale texture already latent in LOOM;
- do not manufacture a fake quest merely to force forward motion.

---

# 3. Diagnostic precedence and ambiguity rule

A symptom may admit more than one plausible cause. Do not classify from surface behavior alone.

Use this order:

1. verify whether the relevant authoritative data/state exists;
2. verify whether the projection contains it;
3. verify whether the synthesis communicates it correctly;
4. verify whether presentation exposes it effectively;
5. verify whether mechanics can support the user's intended action;
6. only then classify residual lack of engagement as motivation failure.

This order prevents `MOTIVATION_FAILURE` from becoming a vague bucket for defects that actually belong to data, projection, synthesis, presentation, or mechanics.

When evidence does not discriminate between causes, report:

`DIAGNOSIS_UNRESOLVED`

and list the minimum discriminator test required.

---

# 4. Gate-status reporting semantics

The v1.0 gate-state vocabulary remains:

- `NOT_STARTED`
- `IN_PROGRESS`
- `PASS`
- `FAIL`
- `BLOCKED`
- `REPLAN`

v1.1 adds an **evidence-maturity modifier** so that planning/documentation cannot be mistaken for implementation progress.

Allowed modifiers are:

- `DOCUMENTED_ONLY`
- `IMPLEMENTATION_EVIDENCE_PENDING`
- `IMPLEMENTATION_EVIDENCE_PRESENT`
- `EMPIRICALLY_TESTED`

A gate report should therefore look like:

```text
G1 — NOT_STARTED
Evidence maturity: DOCUMENTED_ONLY
Reason: regression-fixture requirement is governed, but no E1 baseline fixture artifact has yet been verified.
```

or:

```text
G9 — IN_PROGRESS
Evidence maturity: IMPLEMENTATION_EVIDENCE_PRESENT
Reason: two candidate routes exist in source/output, but deterministic ranking reproducibility has not yet been tested.
```

## 4.1 Governing interpretation for the initial v1.0 adoption state

The existence of the workplan itself does not place G0, G1, or G2 `IN_PROGRESS` automatically.

Until branch/fixture/test/implementation evidence demonstrates active work against a gate, report the gate state according to the actual implementation state and use the evidence modifier to distinguish planning from execution.

For example, immediately after adoption it is acceptable to report:

```text
G0 — NOT_STARTED or IN_PROGRESS, depending on verified implementation activity
Evidence maturity: DOCUMENTED_ONLY / IMPLEMENTATION_EVIDENCE_PENDING
```

The reviewer must state what concrete evidence justifies `IN_PROGRESS` if that state is used.

Do not award progress credit merely because requirements have been written down.

---

# 5. PASS evidence rule

No Experience One gate may be marked `PASS` from design intent, prose, architecture diagrams, TODO completion, code presence alone, or model assertion.

A `PASS` claim must include:

1. **Gate ID and exact pass statement**;
2. **evidence class** using the standing vocabulary where applicable:
   - `OBSERVED_IN_SOURCE`
   - `TESTED`
   - `DOCUMENTED`
   - `INFERRED`
   - `REQUIRES_EMPIRICAL_TEST`
   - `UNKNOWN`;
3. **exact evidence reference** — branch, PR, commit SHA, test/fixture/run identity, or authoritative data reference as appropriate;
4. **target configuration** — especially Pixel/device/runtime/epoch/ship/solver/version when relevant;
5. **known limits/tolerances**;
6. **falsifier** — the minimum observation or repeat test that would invalidate the claimed `PASS`.

A gate whose strongest evidence remains only `DOCUMENTED`, `INFERRED`, `REQUIRES_EMPIRICAL_TEST`, or `UNKNOWN` may not be `PASS` unless the gate itself is explicitly documentary by definition.

---

# 6. Falsifier requirement

Every claimed `PASS` must include one concise falsifier.

Examples:

### Ranked-route determinism

```text
G9 — PASS
Evidence: TESTED at <exact ref/run>
Claim: fixed state/epoch/ship/destination/constraints/solver version reproduces candidate ordering within declared tolerances.
Falsifier: an identical-input rerun produces materially different candidate membership or ordering outside the declared tolerance.
```

### Persistence

```text
G13 — PASS
Evidence: TESTED at <exact ref/run>
Claim: post-flight authoritative state survives process/app restart and identifies Neptune plus committed journey provenance.
Falsifier: restart restores pre-flight location, loses the committed journey, or requires browser/session memory to reconstruct the result.
```

### Mara epistemic discipline

```text
G5 — PASS
Evidence: TESTED hostile suite at <exact ref/run>
Claim: Mara preserves authority/uncertainty/provenance boundaries under the declared adversarial cases.
Falsifier: a declared hostile case causes Mara to replace authoritative tool state, invent unavailable canon, expose inaccessible truth, or present unresolved state as certain.
```

The falsifier is not a demand for philosophical certainty. It is a discipline against milestone labels becoming unfalsifiable confidence statements.

---

# 7. Product-diagnostic matrix update

The v1.0 diagnostic matrix remains useful but should now be read through the two-layer taxonomy.

Additional required rows/concepts are:

| Symptom | Primary candidate class | First discriminator |
|---|---|---|
| User knows what they want to do but LOOM cannot support it honestly | `MECHANICS_FAILURE` | Trace deterministic/authority path; identify missing qualified capability or persistence seam |
| Everything works but the user expresses no curiosity, stake, or desire to continue | `MOTIVATION_FAILURE` | First rule out data/projection/synthesis/presentation defects; then inspect whether meaningful stakes/opportunities are actually perceptible |
| Mara explanation is factually grounded but lifeless/confusing | `SYNTHESIS_FAILURE` | Inspect structured inputs versus produced explanation |
| Mara explanation is good but user never notices the relevant entity/action | `PRESENTATION_FAILURE` | Inspect salience, hierarchy, linking, touch flow, and progressive disclosure |
| User asks for action but the UI/model implies success despite an unsolved mechanic | `MECHANICS_FAILURE` plus epistemic violation | Fail closed; expose unresolved mechanic; no narrative substitution |

A single observation may produce more than one candidate class. Record the discriminator rather than prematurely choosing the most convenient fix.

---

# 8. Review cadence and delta discipline

Independent reviewers should review Experience One after **meaningful state movement**, not simply on a clock.

Useful triggers include:

- an E1.0 spike branch/PR appears;
- a spike receives an exit classification;
- an active upstream lane materially changes in a way that affects E1;
- a gate is claimed complete;
- a Mara/model/tool integration branch appears;
- execution continuity is claimed to exist;
- a task begins drifting into the POST_E1 parking lot;
- a regression invalidates a previously passed gate.

Each review should report:

- current E1 phase;
- gate-state deltas since the previous review;
- evidence-maturity deltas;
- strongest new evidence;
- regressions/new risks;
- WALTER findings;
- POST_E1 scope drift;
- biggest remaining seam;
- smallest next action that closes it;
- falsifier for every newly claimed `PASS`.

No-change reviews should say **NO MATERIAL STATE CHANGE** rather than manufacturing progress commentary.

---

# 9. WALTER / #LOOMSAFE scoped findings

This v1.1 update formalizes the following watch items without creating new deterministic `loom-gate` rules:

1. **Documentation-as-progress drift** — a governed requirement is reported as implementation progress without evidence.
2. **PASS-without-falsifier drift** — a gate is treated as permanently achieved without a stated condition that could disprove it.
3. **Motivation laundering** — missing world texture, synthesis, presentation, or mechanics is mislabeled as a generic motivation problem and patched with hand-authored story.
4. **Mechanics laundering** — Mara/presentation language implies an action is possible or completed where deterministic machinery cannot support it.
5. **Taxonomy overreach** — the failure classes become architecture mandates rather than diagnostic labels.

These are review/assurance rules unless and until separately promoted into validated deterministic governance controls.

---

# 10. Does not establish

This v1.1 update does **not** establish:

- that G0–G2 have begun;
- that any E1.0 spike has run;
- that ranked route alternatives are feasible;
- that execution continuity exists;
- that Mara/model/tool plumbing exists;
- that any Experience One gate has passed;
- that Ceres or Neptune motivation is sufficient;
- that additional canon must be written;
- that any specific renderer, model provider, framework, or architecture is required;
- that Research Lab outputs are promoted;
- that any runtime, engineering, data, canon, or scientific state has changed.

---

# 11. Current working rule

Read v1.0 and this v1.1 update together.

The working product discipline is:

> **Diagnose the layer that failed. Do not fix the wrong layer because it is easier or more fun.**

And the review discipline is:

> **A PASS is a falsifiable evidence claim, not a milestone sticker.**

Everything else in Experience One remains governed by v1.0 unless explicitly superseded here.
