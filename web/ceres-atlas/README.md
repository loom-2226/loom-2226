# Private Ceres Atlas — slice 1

**Primary class:** `class:asset-media`

**Secondary affected class:** runtime, limited to the new private serving helper.
The helper stays with the presentation because its allowlist and image verification
are required to run this slice offline without exposing the repository. No existing
production runtime component changes.

**Work item:** Ceres Atlas / private five-facility vertical slice, explicitly requested by Kevin on 2026-09-19.

**Authority tier:** derived presentation, not canon or navigation authority.

**Promotion target:** local commit on `feature/ceres-atlas-private-20260919` only; no push, Pages, deployment or release.

## Scope and authority

Bootstrap verified live main and this branch at `84ccdf5e88eedb492564f021a6dcc6d131a6026e`.
The source is `docs/ceres/manifest.json` and its five existing approved-reference PNGs.
The manifest SHA-256 is `6ae473bf6b6063b17a08e876d7b0057166135d397ce56e276423d319a44ccd81`.
The launcher pins that snapshot and verifies each image's hash and size before serving it.
Missing/corrupt images produce an unavailable-image state; they never substitute a different asset.

This work follows the current governance bootstrap, authority model, change control,
research boundary and dependency/compatibility policy. The user's explicit instruction
to keep this slice separate supersedes the Inspector-only location in
`docs/CERES_INSPECTOR_VISUALIZATION_WORKPLAN.md` for this bounded implementation.
`web/ceres-atlas/` is outside the `docs/` Pages upload tree. No publication workflow is added.

The view consumes only identity, facility type, approval and image provenance fields.
It excludes census-zone relationships and supplies no population, economic, capacity,
coordinate or other inferred measures. Database semantics are not a runtime dependency.
No canon change, CCR, governance exception, schema migration or frozen-object mutation
is involved. This is not acceptance of the larger Atlas product.

Dependency review: the existing Ceres gallery/manifest/PNG sources, Inspector/exporter,
GIS, canonical databases, Wayfarer viewer, Pixel/Windows launchers, updater and release
manifests are `UNCHANGED_COMPATIBLE`: consumed read-only where applicable and not edited.
The new presentation and its private launcher require unit + functional validation.
The coarse component map does not separately register this new application; its explicit
dependency is the pinned gallery snapshot, not an assumption of independence.
Rollback is a revert of this additive slice; no database or release recovery is needed.

## Launch offline

From the repository root, with Python 3.10+:

```sh
python -B tools/serve_ceres_atlas.py \
  --world-db data/LOOM_2226.sqlite3 \
  --media-db /storage/emulated/0/Download/LOOM_TEST/data/LOOM_2226_media.sqlite3
```

Open `http://127.0.0.1:8768/` in the Pixel's browser. Keep Termux running;
Ctrl+C stops the server. `--port 8769` selects another loopback port if needed.
No internet connection, package install or external font/CDN is needed. The launcher
opens WORLD and MEDIA SQLite in read-only immutable mode, verifies each requested
asset's stable IDs, approval state, media key, byte length and SHA-256, and serves only
the verified original image bytes. It never exposes either database to the browser and
never falls back to repository PNGs. Missing or mismatched databases/images produce the
explicit unavailable-image state. Both database paths are configurable with the shown
arguments; no device-specific path is embedded in application logic.
This is local offline use while the launcher is running, not an installed PWA.

Search by name, facility ID or type; optionally filter by facility type. Select a
card with mouse/touch or Tab then Enter/Space. Back to facilities, browser Back,
and Escape return to the list with filters, scroll and focus retained. Browser
Forward restores the detail. URLs retain filters and the selected facility across
refresh. A direct unknown facility URL offers a safe return to the list.

## Validation

```sh
python -B -m pytest -p no:cacheprovider tests/test_ceres_atlas_server.py tests/test_database_data_dictionary.py -q
node --test tests/ceres_atlas_model.test.mjs
```

Browser interaction suite (requires separately installed Playwright and Chromium):

```sh
node --test tests/ceres_atlas_browser.test.mjs
```

That suite starts/stops its own loopback server, checks mouse, touch, keyboard,
history, error recovery and narrow-screen overflow. If tooling is unavailable it
reports explicit skips, which are not browser verification. No browser package is
a runtime dependency. See `VALIDATION.md` for results and remaining gaps.

## Existing semantic coverage discrepancy

`tests/test_database_semantic_coverage.py:34` expects `tables` to be a list of
records with `database`, `table` and `schema_columns`. The committed
`docs/database_semantics/LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json` instead has a
database-name → table-name-list mapping. Direct execution raises `TypeError`;
pytest does not collect its `main()` as a test. The two dictionary-generator tests
do not validate that index contract. WALTER.PROVENANCE: `REVIEW_REQUIRED` for any
claim of current column-coverage acceptance under the semantic interpretation
contract. Repair is a separate data/documentation work item, intentionally deferred.
