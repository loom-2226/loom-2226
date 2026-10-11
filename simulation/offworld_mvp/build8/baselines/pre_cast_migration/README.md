# Pre-migration Build 8 outputs

Captured from `main` commit `46f9790`, after research cast PR #382 merged, before any experiment identity migration. These are exact serialized outputs, not newly authored expected outcomes.

- `network.json`: network outcomes, balances/revenue and kernel fingerprint.
- `named_sponsors.json`: six sponsor outcomes, balances and kernel fingerprint.
- `quotes.json`: executor quote/refusal outcomes.
- `screen_default.json`, `screen_sub.json`, `screen_sub_failure.json`: outcomes, years, all kernel account balances, Build 8 knowledge records, event logs, fingerprints and occupied slots.

Capture scripts run locally from `/tmp/capture_network.py` and `/tmp/capture_screen.py` on quantifactus. Remaining experiments require equivalent captures before their migration; this folder is **not** a complete baseline of every Build 8 experiment.
