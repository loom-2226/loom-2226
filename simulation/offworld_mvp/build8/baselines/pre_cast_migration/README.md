# Pre-migration Build 8 outputs

Captured from `main` commit `46f9790`, after research cast PR #382 merged, before any experiment identity migration. These are exact serialized outputs, not newly authored expected outcomes.

- `network.json`: network outcomes, balances/revenue and kernel fingerprint.
- `named_sponsors.json`: six sponsor outcomes, balances and kernel fingerprint.
- `quotes.json`: executor quote/refusal outcomes.
- `screen_default.json`, `screen_sub.json`, `screen_sub_failure.json`: outcomes, years, all kernel account balances, Build 8 knowledge records, event logs, fingerprints and occupied slots.

Capture script is committed as `capture.py`. From repository root with the existing Build 8 Python path configured, run `python3 -m simulation.offworld_mvp.build8.baselines.pre_cast_migration.capture` to verify exact bytes, or `python3 -m unittest simulation.offworld_mvp.build8.test_master_cast_snapshots` for the regression check. `--write` is an explicit baseline-regeneration option, not part of tests. Remaining experiments require equivalent captures before their migration; this folder is **not** a complete baseline of every Build 8 experiment.

Migration coverage as of PR #383: `executor_quotes.py` and `named_sponsor_trial.py` resolve selected names through cast; `sponsor_executor_network_trial.py` now resolves its 20 sponsors and 16 selected executors through cast, takes executor home from cast and checks authored capability selections against cast evidence. The 20-sponsor funding participation, preferences, preferred relationships, costs and motives remain authored in that experiment. The three screened-delivery snapshots are **comparison-only**, not migrated. Snapshot comparisons cover these six named captures, not every Build 8 experiment.

Opt-in demonstrations after PR #384: alternate screened BUILD CASC and LAND Astrobotic use the **same authored** SCALE 0.25, BUILD cost 2.00, markup 25%, LAND cost 3.00, markup 20%, 2-year durations, and one slot per category-year; no contractor price evidence is inferred. `subcontract_choice.py` is a separate request allocator, not wired into existing trials; its quotes 0.25/0.30 and one-slot capacity are authored examples. Existing `b8_source:USA` may be negative (-10.020169202983437) under both baseline and alternate runs; this is an existing mobilization source-account behavior, not newly introduced by alternative subcontract identities. Kernel invariants still pass; do not describe every account as nonnegative.

## Frozen legacy transaction references (2026-10-11)

Captured **once on 2026-10-11 UTC** from live GitHub `main` commit
`e20ad340709cc5f49f949bc9df396e46509cd3af`, using the unchanged
`run_screened` implementations and only after each corresponding original
JSON snapshot matched exactly. New files (the original snapshots were not edited):

- `screen_default_transactions.json` (18 transfers)
- `screen_sub_transactions.json` (20 transfers)
- `screen_sub_failure_transactions.json` (20 transfers)

Each record retains the generated ID, year, source/destination, exact decimal
amount, purpose, supplier/asset locations and parent references. Yearly replay
compares the frozen economic transfer multiset independently of ID and order;
ID and parent-reference differences must be reported separately. **Do not
regenerate these references from future live code in acceptance tests.**
