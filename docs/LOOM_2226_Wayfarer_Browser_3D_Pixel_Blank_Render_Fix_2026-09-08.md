# LOOM 2226 — Wayfarer Browser 3D Pixel Blank-Render Fix

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION
Authority: REVIEW_EVIDENCE_ONLY

Observed Pixel result: local HTML controls rendered, but the WebGL ship scene was blank. This is recorded as PIXEL OFFLINE FAIL — BLANK RENDER for browser-3D v0.1.

Root cause identified in v0.1 viewer code: view/projection matrices were constructed in WebGL column-major layout while the matrix multiplication routine used row-major indexing. The resulting MVP matrix could place all geometry outside clip space even though the UI and JavaScript controls remained operational.

v0.2 fix:
- replaces matrix multiplication with column-major indexing consistent with WebGL uniformMatrix4fv(..., false, ...);
- adds WebGL and experimental-WebGL context fallback;
- fails visibly on program-link or shader-binding errors;
- exposes WebGL version and gl.getError() code in the HUD;
- preserves the exact frozen parent and child CandidateDesign geometry and authority flags;
- remains fully offline and self-contained.

No physical engineering result, flight-dynamics authority, canon state, or production shipclass is changed by this viewer fix.

Pixel acceptance remains OPEN until the fixed artifact is opened offline on the Pixel and visibly renders the ship with working parent/child controls and touch navigation.
