# Slice 1 validation — 2026-09-19

Environment: Termux / Python 3.13.13 / Node v24.17.0.
Scope: private five-facility Atlas only. This is available-test qualification for
a local development commit, not production promotion or full-product acceptance.

## Executed

| Command / check | Result |
| --- | --- |
| `python -B -m pytest -p no:cacheprovider tests/test_ceres_atlas_server.py tests/test_database_data_dictionary.py -q` | **27 passed**: 25 Atlas unit/HTTP checks and 2 existing dictionary regressions. |
| `node --test tests/ceres_atlas_model.test.mjs` | **22 passed**, no skips. |
| `node --test tests/ceres_atlas_browser.test.mjs` | **7 skipped**, 0 browser tests passed: Playwright and a browser executable are unavailable. |
| `node --check` on application/model/browser-test modules | Passed. |
| Direct `python -B tests/test_database_semantic_coverage.py` | Existing failure reproduced: `TypeError: string indices must be integers, not 'str'` at line 34. Unchanged by this slice. |

The HTTP tests start a real ephemeral loopback server. They retrieve every app
resource and all five images, verify exact approved bytes, exercise HEAD, reject
foreign Host and POST requests, reject repository/database/traversal paths, and
confirm missing/corrupt/symlinked images fail while facility identities remain usable.
An independent read-only WORLD join verifies spatial/noun/media/image mappings.
Manifest drift prevents startup. Model tests cover filters, route round trips,
unknown IDs, return snapshots, provenance projection and rejection of malformed,
duplicate or unapproved records.

## Pixel smoke test — user-observed PASS, 2026-09-19

Kevin reported these observations after the slice-1 implementation:

- The facility list loads on Pixel.
- Occator detail opens correctly.
- Back to facilities preserves the list state.

Evidence source: Kevin's report in this session; this was not an agent-run or
instrumented browser test. Device/browser versions and screenshots were not supplied.
The PASS is limited to these three observed behaviors. It does not establish
all-facility, keyboard, error-path, responsive-layout or full-product acceptance.
The seven skipped automated browser tests remain explicitly **UNVERIFIED**.

Kevin subsequently authorized committing this evidence and pushing only the
11-file Ceres Atlas slice to `origin/feature/ceres-atlas-private-20260919`.
This authorizes branch delivery only, not merge, deployment, publication or
canonical database changes.

## Source preservation

Checked before and after implementation:

- `data/LOOM_2226.sqlite3`: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`
- `data/LOOM_2226_CIVSTATE.sqlite3`: `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`
- `docs/ceres/manifest.json`: `6ae473bf6b6063b17a08e876d7b0057166135d397ce56e276423d319a44ccd81`

All five PNGs match their original manifest hashes and byte lengths. Existing
Inspector, GIS, gallery, data, governance, launchers and workflows are unchanged.

## Remaining verification gaps

- Agent-run browser interaction remains unavailable. The user-observed Pixel
  smoke test above verifies only its three stated behaviors; screenshots,
  screen-reader behavior and broader visual/layout coverage remain unverified.
  All seven automated browser tests are still **SKIPPED / UNVERIFIED**.
  The browser suite covers mouse,
  keyboard, touch, 320px/393px/851px layouts, all five details, focus/scroll/history,
  refresh, unknown IDs, empty search, image retry and manifest retry when run with
  Playwright + Chromium. Skips do not establish that those browser behaviors pass.
- No protected-main `loom-gate` status was produced during implementation; there
  was no PR or promotion. The later branch-push authorization above does not
  establish a gate result. Ruby (used by the existing gate) is absent locally. The gate
  remains required for any later protected-main promotion.
- The existing semantic coverage index/checker mismatch remains `REVIEW_REQUIRED`
  under WALTER.PROVENANCE. This application does not consume that index or infer
  database metrics. A separate repair must reconcile the index schema and actual
  checker execution before asserting current semantic column coverage.
- Larger Atlas work (body dossier, richer fields, spatial interpretation, canonical
  metrics, full-product acceptance and publication) remains outside this slice.
