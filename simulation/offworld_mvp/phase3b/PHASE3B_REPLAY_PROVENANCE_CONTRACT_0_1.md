# Phase 3B Replay Provenance Contract 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / BUILD-5 ENTRY GATE

Every integrated scheduled run must carry exact executable provenance.

Required run-manifest fields:

- repository identity;
- exact 40-hex Git commit;
- SHA-256 of the executable `offworld_kernel` Python source tree;
- input snapshot id(s);
- parameter-manifest id(s);
- table-manifest id(s), including explicit `NO_EXTERNAL_TABLES` when none are used;
- scheduler contract version;
- scheduler-plan fingerprint;
- initial and final state fingerprints;
- execution/event-results fingerprint;
- provenance fingerprint;
- final result fingerprint.

Archive/export execution must provide `LOOM_GIT_COMMIT` because a Git directory may not exist. A checkout may resolve `git rev-parse HEAD` directly.

The asserted commit and executable code hash are not accepted as unrelated labels. In a Git checkout, LOOM re-hashes the `offworld_kernel` Python sources directly from the asserted Git object and requires that hash to equal the executable source-tree hash (`GIT_OBJECT_VERIFIED`). In an exported archive, the current source-tree hash must match a release-attested `LOOM_EXPECTED_CODE_TREE_SHA256` (`EXPORTED_CODE_HASH_ATTESTED`).

The code-tree hash is not a substitute for the repository commit. Both are carried and their linkage is verified. The commit identifies repository state; the source-tree SHA-256 identifies the executable Python payload actually run.

All Build 5 autonomous policy implementation code shall reside under `simulation/offworld_mvp/phase3b/kernel/offworld_kernel/` (normally `offworld_kernel/policies/`) or be explicitly added to the hashed executable manifest. Policy code outside the hashed executable tree is not admissible for a qualified replay claim.

A future Build 5 underwriting run must include the underwriting table id/version/fingerprint in `table_manifest_ids`; `NO_EXTERNAL_TABLES` is valid only for runs that genuinely consume no external/versioned table.

Replay provenance establishes reproducibility identity, not empirical validity.
