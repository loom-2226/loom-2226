# Solar authority reconciliation 1950–2500 — Stage 2 catalog reconciliation

Status: evidence only; HUMAN REVIEW GATE. No authority mutation, download, propagation, or source promotion has occurred.

This stage reconciles all 110 governed Solar bodies against the read-only PostgreSQL authority ledger and the Stage 1 physical SPK inventory.

## Current governed result

- Catalog bodies: 110.
- Full governed coverage of the 2226-01-01 TDB through 2251-01-01 TDB gate: 103.
- Governed partial game-interval coverage: 5 — Hydra, Kerberos, Nix, Proteus, Styx.
- No governed qualified coverage: 2 — Dactyl and Selam.
- Full governed coverage of the broader 1950-01-01 through 2500-12-31 TDB program target: 17.
- 108 bodies have at least one local physical SPK candidate by active NAIF target identity; this does NOT mean those files are governed or qualified.

Coverage is evaluated as the union of qualified governed intervals, preserving source seams and explicit gaps. A body does not require one source to span the whole interval.

## Important Pluto boundary

Pluto and Charon already have governed direct PLU060 coverage followed by governed LOOM/JPL-NASA-derived propagation. Hydra, Nix, Kerberos, and Styx do not: their current governed coverage remains PLU060-only and ends in 2199. The newer independent six-body PLU060 reproduction/continuation experiment is preserved elsewhere as experimental evidence and is deliberately NOT promoted here.

## Epistemic boundary

Physical local target presence never fills a governed gap. Unknown or rejected candidate kernels remain candidates. The 1950–2500 envelope is a program target, not a completed coverage claim.

HARD STOP: review this evidence before any external acquisition, qualification/promotion, new propagation, or authority-ledger mutation.
