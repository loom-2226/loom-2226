# LOOM WORLD AUTHORITY V1 qualification record

**Standing:** `MIGRATION_QUALIFIED_SCIENCE_CANDIDATE_PRESERVED`
**Change class:** `class:data`
**Qualification date:** 2026-10-06

The complete World Authority V1 migration qualification passed from zero on two newly provisioned PostgreSQL 18.6 clusters. E01–E28 and S01–S12 passed (40/40 required identifiers), with no errors or skips. The suite also passed 16 real-login security/store behavior tests and four store identity regressions. The machine-readable report records the exact tested implementation file hashes, pinned environment, both database inventories, complete test IDs, and successful repeat, failure/rollback, security and reproducibility results.

The accepted World Science SQLite source was independently reopened read-only and compared against the PostgreSQL forensic archive. All 2,726 source rows, all 256 source columns, and 50,078 source cells were preserved and matched, including source keys, NULL, lexical text, storage classes, BLOB bytes, and IEEE-754 values. The source SHA-256 is `72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`; the source file was unchanged after qualification.

Migration did not perform scientific admission. The migrated source retained 880 candidate assertions and 35 candidate material-evidence records; zero scientific admissions were created. The four UNKNOWN assertion explanatory texts remain available in the forensic raw layer under their documented normalized disposition. No filtering, deduplication, scientific re-review, value repair, or standing change occurred.

The final machine-readable report is [WORLD_AUTHORITY_V1_QUALIFICATION_2026-10-06.json](WORLD_AUTHORITY_V1_QUALIFICATION_2026-10-06.json), SHA-256 `daf3ce1317658860de9171f2b580d78e600bd4fa68d9411c2b16329d3a213932`. Its direct-source completeness result is [WORLD_AUTHORITY_V1_SOURCE_COMPLETENESS_2026-10-06.json](WORLD_AUTHORITY_V1_SOURCE_COMPLETENESS_2026-10-06.json). The complete external evidence bundle, including deterministic exports, is archived at `/home/ubuntu/LOOM-output/WORLD_AUTHORITY_V1_FINAL_QUALIFICATION_2026-10-06/` and has a `SHA256SUMS.txt` inventory.

This record qualifies World Authority V1 only. It does not authorize Build 6E or scientific admission.
