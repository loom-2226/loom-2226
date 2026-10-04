# BUILD 5 FINAL FREEZE ATTESTATION

**Status:** FINAL BUILD 5 STRICT-MVP STRUCTURAL BASELINE / FROZEN
**Date:** 2026-10-05
**Qualified source branch:** `offworld-mvp-build5-integrated-qualification`
**Qualified validation head:** `a1bb26154c151cf76d7389d375eb626c64b1b8eb`
**Frozen branch:** `offworld-mvp-build5-final-2026-10-05`
**Planned release tag:** `build5-final-v1-2026-10-05`

## Decision

Build 5 is frozen as the first structurally qualified end-to-end Offworld strict-MVP
baseline.

The frozen baseline preserves the complete Build 5 history through Tests 001–014,
Compaction R1, and Integrated MVP Qualification R1.

No later runtime, schema, policy, calibration, research, progressive-elaboration, or
worldbuilding change may be back-written into this frozen branch or moved under the
Build 5 final tag.

## Qualification evidence

Controlling integrated validation record:

`simulation/offworld_mvp/build5/BUILD5_INTEGRATED_QUALIFICATION_VALIDATION_R1.md`

Full governed operator regression on the exact qualified executable/test head
`872401f6797504e7bc9b826c4e6e452a06e6680e`:

- 311 tests executed;
- 311 passed;
- 0 failures;
- 0 errors;
- runtime 782.097 s.

The later validation and freeze-attestation commits are documentation-only.

Focused current-head qualification before this freeze record:

- 5 tests executed;
- 5 passed;
- 0 failures;
- 0 errors;
- runtime 39.532 s.

## Executable identity

Frozen executable source-tree SHA-256:

`acfc3e862c0e7e063618c6d4d893525cbad2255507312d0b5b7460b96b89ffc1`

This is byte-for-byte identical to the validated Test 014 executable source tree and the
Integrated Qualification R1 executable tree.

Standing:

`GIT_OBJECT_VERIFIED`

Guiding FRD mutation across Integrated Qualification R1:

`0 lines`.

## Meaning of the freeze

This freeze means the strict-MVP architectural spine has passed structural integrated
qualification. It does **not** mean empirical, scientific, economic, mining, transport,
settlement, demographic, or long-run forecasting validation has been earned.

The frozen Build 5 baseline demonstrates bounded, deterministic and auditable coexistence
of:

- autonomous exploration and information acquisition;
- epistemically bounded Agent decisions;
- sponsor and financier behavior;
- development/construction;
- operating extraction and physical depletion;
- sale and surplus disposition;
- settlement formation;
- technology-qualified passenger transport;
- Earth reference / realized shadow accounting;
- repeated enterprise operation, recapitalization, abandonment and closure;
- conservation, replay, provenance and tamper-evident decision epochs.

The integrated NULL/SPARSE/RICH qualification is intentionally allowed to diverge after
admitted distinguishing information rather than forcing identical scripted histories.

## Frozen exclusions

The freeze does not promote or imply:

- empirical calibration;
- endogenous technology or R&D;
- detailed astrodynamics, fleets or logistics networks;
- endogenous prices or competitive market structure;
- mature colony service/reliability operations;
- detailed labour/skills, households or individual-person simulation;
- DIVERSIFYING_SETTLEMENT / HANDOFF_CANDIDATE mechanics;
- generalized bankruptcy, salvage or liquidation;
- coupled Earth/offworld macroeconomic feedback;
- canon history or a forecast of 2226.

Those remain future governed work and must derive from this baseline explicitly rather
than mutate it retroactively.

## Promotion rule

The qualified Build 5 history may now be promoted to `main` through an explicit pull
request preserving commit history. After successful merge, the mainline merge commit may
be tagged `build5-final-v1-2026-10-05` only after verifying that its executable source-tree
hash remains the frozen hash above.

The frozen branch itself shall point to the exact commit containing this attestation and
shall remain read-only by convention.
