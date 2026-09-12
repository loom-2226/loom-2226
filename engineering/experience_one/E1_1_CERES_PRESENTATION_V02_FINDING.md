# E1.1 — Ceres Presentation v0.2 Finding

Status: IMPLEMENTATION EVIDENCE PRESENT / PIXEL VISUAL RETEST PENDING
Class: class:engineering / REQUIRED_FOR_E1

## Diagnosis from v0.1 Pixel screenshots

The v0.1 page established that Pixel ergonomics, hierarchy, cards, touch sizing, and tucked-away provenance are viable. It did not close PRESENTATION.

Observed defect: governed world data was surfaced too directly as ontology/database prose. The lede required decoding; machine labels and raw strategic/openness values dominated the place cards; the first exploration affordance arrived only after several phone screens.

Classification: PRESENTATION defect. Do not add lore or alter DATA/PROJECTION/SYNTHESIS to compensate.

## v0.2 bounded change

`e1_1_ceres_show_then_explain_presentation_v02.py`:

- consumes the existing qualified deterministic Ceres projection;
- consumes the already-qualified grounded Mara orientation synthesis artifact;
- performs no model call and no SQLite query;
- uses the grounded synthesis only as human-facing EXPLAIN copy;
- retains deterministic ORIENT/INTERESTING packets as SHOW/INSPECT source;
- humanizes machine enum labels for display;
- moves raw strategic/openness values behind `Details`;
- adds a top-level Mara exploration affordance before the notice cards;
- adds a contextual `Ask Mara about this` affordance to every card;
- keeps provenance subordinate and expandable;
- remains Ceres-only, read-only, offline, non-mutating, and non-replacement.

This is still a presentation diagnostic, not production UI architecture.

## Pixel retest

Generate v0.2 from the same projection and the empirically qualified v0.2 Mara synthesis artifact. Inspect on Pixel.

Pass requires human review that:

1. Ceres is understandable within seconds without decoding source-field prose;
2. at least two location hooks are perceptible as world objects rather than schema rows;
3. an exploration action is obvious near the top and on each card;
4. provenance/details remain available but subordinate;
5. the page remains readable/touchable on Pixel;
6. no new lore, authority, model call, network dependency, or mutation has been introduced.

A structural/unit PASS is not sufficient for PRESENTATION closure.

## Stop condition

If v0.2 remains clean but uninteresting, do not continue polishing layout by momentum. Reclassify the remaining seam as MOTIVATION and test whether the existing facts provide compelling hooks before adding new canon.
