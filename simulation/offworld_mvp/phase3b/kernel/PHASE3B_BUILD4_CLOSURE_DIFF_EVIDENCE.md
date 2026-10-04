# Build 4 Closure Diff and Freeze Evidence

**Status:** CLOSURE EVIDENCE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04

## A. Original "records only" claim

The original Build 5 gate executable/documentation head was:

`d78c7379d295b3f3cf25771f02a68e166a9ccdbb`

The first Build 4 final freeze was:

`830ca12f4f2a7a497b55dcb2705a338768956c91`

GitHub compare reports exactly three changed files between those commits:

- `simulation/offworld_mvp/phase3b/PHASE3B_BUILD5_ENTRY_GATE_DECISION_001.md`
- `simulation/offworld_mvp/phase3b/kernel/PHASE3B_BUILD4_FINAL_CLOSURE_RECORD.md`
- `simulation/offworld_mvp/phase3b/kernel/PHASE3B_KERNEL_VALIDATION_RECORD_010_BUILD5_ENTRY_GATES.md`

All three are Markdown records.

The requested VM check produced:

```
$ git diff --name-only d78c7379d295b3f3cf25771f02a68e166a9ccdbb..830ca12f4f2a7a497b55dcb2705a338768956c91 -- '*.py'
<empty>

$ git diff --name-only d78c7379d295b3f3cf25771f02a68e166a9ccdbb..830ca12f4f2a7a497b55dcb2705a338768956c91 -- 'simulation/offworld_mvp/phase3b/kernel/offworld_kernel/schema_registry.py'
<empty>
```

Therefore the statement in the original closure record that commits after `d78c737...` through the original freeze changed records only was correct.

## B. Review-driven closure correction

The original freeze is preserved as historical evidence and is not rewritten.

The review identified additional closure hardening. Those corrections were made on the active Phase 3B line and intentionally include executable changes.

The corrected Build 4 freeze is pinned by both immutable tag and commit:

- **tag:** `build4-final-v2-2026-10-04`
- **commit:** `4cb0158d71ce77affbcead68c946056baa9e817a`
- **branch mirror:** `offworld-mvp-build4-final-v2-2026-10-04`

The corrected commit was tested from a Git checkout:

- **99 tests passed**
- executable `offworld_kernel` source-tree SHA-256:
  `16b0d0247cf55b8a8b2d5f61799666f4bb89a15acedaffa883ad9bd00f998038`
- Git-object source-tree SHA-256 for the pinned commit:
  `16b0d0247cf55b8a8b2d5f61799666f4bb89a15acedaffa883ad9bd00f998038`
- commit/code linkage:
  `GIT_OBJECT_VERIFIED`

## C. Corrections included in v2 freeze

The corrected freeze additionally verifies:

- asserted Git commit against the actual executable source tree from that Git object;
- Build 5 policy code must live inside the hashed executable tree or be explicitly added to its manifest;
- ODD drift checks field names, field types, enum values, and unit contracts;
- financing reason-code register includes `CEILING`, `CONCENTRATION`, and `BELOW_RETURN`;
- required UNKNOWN underwriting inputs, beliefs, or priors force `BLOCKED_UNKNOWN`;
- underwriting validation inputs carry units, basis year, and validity years.

The corrected freeze remains PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED.
