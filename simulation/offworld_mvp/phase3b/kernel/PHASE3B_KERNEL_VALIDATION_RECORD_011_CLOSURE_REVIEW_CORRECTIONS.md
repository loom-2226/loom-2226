# Phase 3B Kernel Validation Record 011 — Build 4 Closure Review Corrections

**Status:** PASS FOR CLOSURE-REVIEW CORRECTIONS / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Tested executable/documentation head:** `3bb888e9275d8cf7824629d849f7404d08a11e00`
**Prior final freeze:** `830ca12f4f2a7a497b55dcb2705a338768956c91`

## 1. Purpose

Address the hostile review received after the first Build 4 freeze without rewriting that historical freeze.

The review requested:

1. immutable tag + SHA pinning and evidence for the original records-only closure claim;
2. verification that asserted Git commit and executable source hash correspond;
3. assurance that future policy code is inside the hashed executable tree;
4. stronger ODD drift protection for field types, enum values, and unit semantics;
5. financing reason codes for CEILING, CONCENTRATION, and BELOW_RETURN;
6. BLOCKED_UNKNOWN behavior for missing beliefs/priors as well as table inputs;
7. explicit time indexing and units for underwriting price/cost inputs;
8. confirmation that scheduler-valid A1–A9 property runs had already occurred.

## 2. Regression result

The corrected executable/documentation head was tested on `quantifactus` from a Git checkout.

**99 tests executed; 99 passed.**

The checkout test suite includes direct Git-object/source-tree linkage verification.

## 3. Original records-only claim

The original tested G5 head was:

`d78c7379d295b3f3cf25771f02a68e166a9ccdbb`.

The original freeze was:

`830ca12f4f2a7a497b55dcb2705a338768956c91`.

GitHub compare shows exactly three changed files, all Markdown records.

The requested VM commands produced empty output for:

```
git diff --name-only d78c7379d295b3f3cf25771f02a68e166a9ccdbb..830ca12f4f2a7a497b55dcb2705a338768956c91 -- '*.py'

git diff --name-only d78c7379d295b3f3cf25771f02a68e166a9ccdbb..830ca12f4f2a7a497b55dcb2705a338768956c91 -- 'simulation/offworld_mvp/phase3b/kernel/offworld_kernel/schema_registry.py'
```

Detailed evidence is preserved in:

`PHASE3B_BUILD4_CLOSURE_DIFF_EVIDENCE.md`.

## 4. Commit/code linkage

Replay provenance now verifies the asserted commit against the executable source tree.

In a Git checkout, LOOM reconstructs the `offworld_kernel` Python tree from the asserted Git object and requires its canonical SHA-256 to match the executable tree.

At the corrected tested head:

- executable source-tree SHA-256:
  `16b0d0247cf55b8a8b2d5f61799666f4bb89a15acedaffa883ad9bd00f998038`;
- Git-object source-tree SHA-256:
  `16b0d0247cf55b8a8b2d5f61799666f4bb89a15acedaffa883ad9bd00f998038`;
- linkage:
  `GIT_OBJECT_VERIFIED`.

For exported archives, an explicit release-attested expected code hash is required and must match the current executable tree.

## 5. Hashed policy-code boundary

The executable hash recursively covers all Python under:

`simulation/offworld_mvp/phase3b/kernel/offworld_kernel/`.

Build 5 autonomous policy code is required to live inside that tree, normally under:

`offworld_kernel/policies/`.

Policy implementation outside the hashed executable tree is not admissible for a replay-qualified run unless explicitly added to the executable manifest.

## 6. ODD drift strengthening

The machine-readable ODD registry is now version:

`ODD_SCHEMA_REGISTRY_0_2`.

The regression comparison covers:

- dataclass field names;
- dataclass field types;
- registered enum values;
- declared semantic unit contracts.

Therefore a semantic type, enum, or unit change can fail drift checking even when the field name remains unchanged.

## 7. Financing reason codes and UNKNOWN dependencies

The reason-code register now explicitly includes:

- `BELOW_RETURN`;
- `CEILING`;
- `CONCENTRATION`;
- `BLOCKED_REQUIRED_INPUT_UNKNOWN`.

A Build 5 financing request now declares exact required:

- underwriting keys;
- belief keys;
- prior keys.

For Test 001 the required belief and prior key is:

`resource_exists`.

The protocol computes required unknown dependencies from the immutable DecisionSnapshot. Missing required underwriting inputs, beliefs, or priors force `BLOCKED_UNKNOWN`. They may not be hidden under REJECT or DEFER.

## 8. Underwriting time indexing

Underwriting inputs now carry:

- explicit unit;
- mandatory basis year;
- mandatory valid-from year;
- mandatory valid-to year.

The validation table is explicitly scoped to:

`SIM_YEAR 1`.

It is not a timeless price/cost table.

Decision-snapshot admission rejects an underwriting input outside its declared validity year.

## 9. A1–A9 property entry check

This had already been completed before the review.

Validation Record 009 established:

- 20 deterministic seeded sequences;
- 80 scheduler-valid transitions per sequence;
- 1,600 scheduler-valid generated transitions;
- A1 through A9 checked after every transition;
- 14,400 individual identity evaluations.

The generated transition set covered disbursement, WIP spend, commissioning, depreciation, extraction, revenue, surplus decomposition, and commitment lapse.

The complete property suite remains green in this correction pass.

## 10. Standing

These corrections strengthen Build 4 closure verification. They do not authorize autonomous behavior and do not create empirical validity.

Build 4 remains:

- PRE-CONTRACT;
- SINGLE-AUTHORITY;
- NOT_EMPIRICALLY_VALIDATED.
