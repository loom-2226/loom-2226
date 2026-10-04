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

The code-tree hash is not a substitute for the repository commit. Both are carried: the commit identifies the repository state; the source-tree SHA-256 identifies the executable Python payload actually run.

A future Build 5 underwriting run must include the underwriting table id/version/fingerprint in `table_manifest_ids`; `NO_EXTERNAL_TABLES` is valid only for runs that genuinely consume no external/versioned table.

Replay provenance establishes reproducibility identity, not empirical validity.
