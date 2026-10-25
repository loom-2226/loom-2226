# Architecture packet validation — 2026-09-28

Scope: specification and disposable decision experiments only. This is **not**
a basemap prototype qualification, Inspector requalification or physical-device PASS.

| Check | Result |
|---|---|
| Main governance/root/engineering authority bootstrap | PASS at b22703ab7ce5586fecfeda0998d19b7d1fbbfe30 |
| PR299 dependency | OPEN at f0c373a4deb5589584619b64a91ac2ac1d2ed936; existing loom-gate SUCCESS |
| Live PostgreSQL repeatable-read recheck | PASS; ledger hash equals API/evidence fd0784e9…; see ledger_reverification.json |
| `bench/measure.py` live read-only acquisition/format/simplification experiment | PASS after correcting archived Atlas payload parser; measurements.json + sample_corpus.json |
| Existing-client Pixel-sized browser measurements | 3 archive + 3 Inspector contexts, zero page errors; timings/limits preserved in browser_measurements.json |
| `python3 engineering/solar_basemap/bench/validate.py` | 7 tests PASS: schema/negative shapes, geometry format hashes, simplification math, segments/ET, live/root identity, links and chosen policy consistency |
| `node --check engineering/solar_basemap/bench/browser.cjs` | PASS |
| `python3 -m py_compile engineering/solar_basemap/bench/measure.py` | PASS |
| `git diff --check` | PASS |
| Physical Pixel | NOT RUN; no device attached; Chromium/SwiftShader approximation only |
| Prototype A1–A12 | NOT IMPLEMENTED / NOT RUN; handed off as falsifiable requirements |

The initial measurement attempt failed parsing the historical archive's Atlas
payload because it uses JSON rather than the other payloads' metadata+binary
layout. Corrected the experiment decoder; no source/archive bytes changed.
Its already-completed API calls warmed caches, so recorded successful timings
are labeled warm. One archive browser run had a 2558ms animation interval; retained,
not erased or represented as smooth performance. No speculative basemap result
was added to Inspector qualification evidence.

No production functional source, migration, kernel, source precedence, authority
coverage, release manifest, launcher or design token changed. No authority was
promoted, no frozen research modified, no service restarted, and no PR merged.
Architecture packet CI is the PR's live `loom-gate` status; it is reported after
push and is not substituted for future prototype tests.
