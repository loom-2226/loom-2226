# LOOM Wayfarer — AI Mesh Quarantine

**Workstream:** `workstream/wayfarer-3d`  
**Status:** NON-GOVERNING / EXPERIMENTAL

AI-generated 3D is allowed here only as visual proposal material. It must never become geometry authority by file placement, import, or aesthetic preference alone.

## Direction of travel

Authoritative / controlled:

`SQL parameters → deterministic geometry JSON → deterministic GLB`

Proposal-only:

`canon + dimensions + reference images + prompt → AI mesh/GLB → quarantine comparison`

Acceptance requires:

`AI proposal → inspect against deterministic envelope → measure → engineering review → explicit parameter/topology change → regression validation → optional canon-candidate review`

## Required provenance for each AI candidate

Create a subfolder per candidate and include a `candidate.md` recording:

- candidate ID and date;
- generator/service/model if known;
- complete prompt;
- source/reference images used;
- intended component and authoritative envelope;
- AI output filename and units/scale assumptions;
- deviations observed;
- decision: REJECT / VISUAL_REFERENCE / ENGINEERING_CANDIDATE;
- any parameter changes proposed back to LOOM.

Binary AI mesh files should normally remain local until they are deliberately selected for preservation. Do not commit huge exploratory generations by default.

## First recommended trials

1. Integrated launch-bay exterior and door mechanism, constrained to the current bay/launch envelope.
2. One of the four radiator assemblies, constrained to the existing root station and quadrature topology.

Do not ask an AI generator to redesign the entire Wayfarer before component-level acceptance works. Whole-ship generation is useful later for aesthetic comparison, but cannot be allowed to overwrite the deterministic physical architecture.
