# Pre-migration Build 8 outputs

Captured from `main` commit `46f9790`, after research cast PR #382 merged, before any experiment identity migration. These are exact serialized outputs, not newly authored expected outcomes.

- `network.json`: network outcomes, balances/revenue and kernel fingerprint.
- `named_sponsors.json`: six sponsor outcomes, balances and kernel fingerprint.
- `quotes.json`: executor quote/refusal outcomes.
- `screen_default.json`, `screen_sub.json`, `screen_sub_failure.json`: outcomes, years, all kernel account balances, Build 8 knowledge records, event logs, fingerprints and occupied slots.

Capture script is committed as `capture.py`. From repository root with the existing Build 8 Python path configured, run `python3 -m simulation.offworld_mvp.build8.baselines.pre_cast_migration.capture` to verify exact bytes, or `python3 -m unittest simulation.offworld_mvp.build8.test_master_cast_snapshots` for the regression check. `--write` is an explicit baseline-regeneration option, not part of tests. Remaining experiments require equivalent captures before their migration; this folder is **not** a complete baseline of every Build 8 experiment.
