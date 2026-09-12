# E1.1 Ceres Presentation Diagnostic Finding v0.1

**Class:** `class:engineering / REQUIRED_FOR_E1`  
**Status:** `IMPLEMENTATION_EVIDENCE_PRESENT / PIXEL PRESENTATION REVIEW PENDING`  
**Change type:** additive diagnostic only; no production presentation replacement

## Question

After DATA, PROJECTION, and bounded SYNTHESIS have each been exercised, can the same already-qualified Ceres context be presented on Pixel so a human can understand the place, notice concrete hooks, and see obvious next questions without reading JSON or knowing LOOM's database vocabulary?

This is a **PRESENTATION** discriminator. It is not a renderer replacement, a Mara integration, or an E1.5 zero-instruction test.

## Implementation

Added:

- `engineering/experience_one/spikes/e1_1_ceres_show_then_explain_presentation.py`
- `tests/test_e1_1_ceres_show_then_explain_presentation.py`

The diagnostic consumes an existing `LOOM_CANON_CONTEXT_PROJECTION_V1` artifact and uses the existing deterministic `ORIENT` and `INTERESTING` query paths. It emits one self-contained offline HTML file intended to be opened directly on Pixel.

The page exposes:

1. **Place identity and summary** — Ceres and its existing governed summary.
2. **Political + transport context** — directly from the qualified ORIENT packet.
3. **What to notice** — up to three already-ranked INTERESTING places, with role, traffic class, strategic importance, commercial openness, governance style, and expandable provenance.
4. **Ask next** — three presentation affordances that expose useful questions without requiring database knowledge.

The prompt buttons are presentation-only. They do not invoke Mara or any service; they only display/copy the selected question locally.

## Authority boundary

- model call: **NO**
- SQLite access: **NO**
- campaign state access: **NO**
- campaign mutation: **NO**
- canon mutation: **NO**
- calculation authority: **NONE**
- state authority: **NONE**
- canon authority: **NONE**
- network dependency: **NONE**
- browser authority: pixels, layout, disclosure controls, local prompt-copy interaction only
- selection/ranking remains `PRESENTATION_DERIVED_NON_AUTHORITY`

The diagnostic is deliberately bounded to Ceres/CER and fails closed on a non-Ceres projection. It does not broaden Canon Context coverage.

## Why this is allowed while G1 remains open

PR #110 permits additive read-only endpoints/tools and diagnostics while G1 baseline capture remains open, but blocks replacing existing HUD/GIS/Atlas/world-summary presentation.

This diagnostic therefore produces a standalone evidence surface only. It does **not** modify or replace existing runtime UI.

## Technical pass criteria

The implementation is technically acceptable only if:

- the view model contains Ceres identity, summary, at least one notice card, and next-question affordances;
- the output is deterministic for fixed input;
- the HTML is self-contained and has no remote dependencies;
- source text is escaped before rendering;
- model/state/canon authority remain zero;
- campaign/canon mutation remain false;
- non-Ceres input fails closed.

These criteria can be unit-tested. They do **not** establish presentation quality.

## Pixel empirical review

After unit tests pass, generate the HTML from the actual Pixel Ceres projection and open it in Chrome.

For this bounded diagnostic, inspect four questions:

1. **Orientation:** Is it immediately obvious what place this is and what kind of place it is?
2. **Hooks:** Can the viewer identify at least two concrete things worth noticing without opening provenance/JSON?
3. **Affordance:** Is there an obvious next step/question without already knowing LOOM's data model?
4. **Noise:** Does provenance/technical detail stay subordinate rather than becoming the interface?

Record the result as one of:

- `PRESENTATION_PASS_BOUNDED`
- `PRESENTATION_NEEDS_REVISION`
- `PROJECTION_DEFECT_REVEALED`
- `MOTIVATION_DEFECT_REVEALED`

Do not classify this as E1.5 zero-instruction acceptance. A project author inspecting a prototype is not an external-user usability test.

## Interpretation

If the page is legible and the next-question affordances are obvious, the bounded PRESENTATION seam is sufficiently demonstrated to proceed without redesigning the source data or projection.

If the page is technically correct but boring or gives no reason to explore, classify the remaining issue as **MOTIVATION**, not DATA, unless a specific missing source fact is demonstrated.

If useful source facts are present in the projection but are absent from the page, classify **PRESENTATION**.

If the page reveals that the qualified packets themselves lack a needed fact, return to **PROJECTION** before authoring new lore.

## Stop condition

Do not turn this standalone HTML diagnostic into production UI by momentum. Any integration into HUD/GIS/Atlas must wait for the relevant governed baseline/integration decision and must preserve the browser authority firewall.
