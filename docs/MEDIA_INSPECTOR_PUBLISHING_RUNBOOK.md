# LOOM 2226 — Media + Canon Inspector publishing and republishing runbook

**Recorded:** 2026-09-18. **Change class:** `class:asset-media` (documentation of existing publication; no canon promotion). **Repository:** `loom-2226/loom-2226`. **Live URL:** https://loom-2226.github.io/loom-2226/inspector/ . **Related deployment:** PR #242, squash merge `e34d54525fe1d46bb25cf2531d151dbc2c6ecf54`. The initial live browser screenshot showed the Inspector rendering 182 assets, thumbnails, search, two filters and Inspect buttons; this is a UI smoke observation, not proof of every interactive path.

## 1. Authority and architecture

GitHub `main` is authoritative for the source and governance; the browser is a derived, read-only public presentation, **not** a canonical database or authority for facts. Begin any future work with `LOOM_START_HERE.md`, current governance and `AGENTS.md`; read scoped `AGENTS.md` if present. Use a feature branch, PR with primary change class `class:asset-media`, declared dependency/compatibility impact, relevant tests and successful `loom-gate` before protected-main merge. Never change frozen PR #19/#16, canon or engineering as a side effect of publishing media. Publication is not canon promotion.

Data flow:

```text
main:data/LOOM_2226.sqlite3 (WORLD, tracked)
    + immutable GitHub release: LOOM_2226_media.sqlite3 (media bytes)
    -> src/loom_media_library.py load_catalog()/entities()/ancestry()
    -> tools/build_inspector_pages.py (read-only allowlist + blob export)
    -> docs/inspector/catalog.json + images/<sha256>.<ext> + index.html
    -> GitHub Actions uploads ALL docs/ as one Pages artifact
    -> GitHub Pages /loom-2226/inspector/ (Ceres /ceres/ preserved)
```

The generated catalogue and images are **build outputs**, not the authoritative source; the workflow generates them on its runner. Do not commit the ~300 MB export into Git or duplicate the ~474 MB release. The media release is downloaded afresh each run and verified before use. Pages source must remain **GitHub Actions**, not `Deploy from a branch`. The deploy workflow packages **all `docs/`**, not just `docs/inspector/`, to retain the existing Ceres gallery.

## 2. Exact tracked components

| Path or resource | Role |
| --- | --- |
| `docs/inspector/index.html` | Static responsive UI, fetches `catalog.json`, search, celestial/object filters, image cards and record/ancestry Inspect panel. |
| `tools/build_inspector_pages.py` | Read-only exporter; imports `src/loom_media_library.py`, selects approved/current entries, reads original and thumbnail blobs, writes allowlisted JSON and content-addressed images. |
| `src/loom_media_library.py` | Catalog, entity and ancestry adapters; changes here can affect export and require regression. |
| `data/LOOM_2226.sqlite3` | WORLD input from checked-out commit. |
| `.github/workflows/inspector-pages-preview.yml` | PR/manual preview build; uploads `inspector-pages-preview` Actions artifact for 7 days; **does not publish**. |
| `.github/workflows/inspector-pages-deploy.yml` | Manually dispatched publication workflow with `confirm_publication` boolean; runs on `main`, regenerates export, uploads entire `docs/`, deploys Pages. |
| `docs/ceres/index.html` and other `docs/**` | Existing Pages content that must survive every deployment. |
| Release `v0.1.0-runtime-baseline` asset `LOOM_2226_media.sqlite3` | Existing immutable media source, not re-uploaded for this publication. |

Release URL: `https://github.com/loom-2226/loom-2226/releases/download/v0.1.0-runtime-baseline/LOOM_2226_media.sqlite3` . Expected SHA-256: `286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038`. Recorded release size: 473,837,568 bytes. Both workflows pin the URL and hash; a replacement release **requires an intentional reviewed update to both workflows and tests**. A hash mismatch must stop publication, never be waived casually.

## 3. Actual exported catalogue schema (as implemented 2026-09-18)

Top-level JSON object (`docs/inspector/catalog.json`, generated, not tracked):

| Key | Meaning |
| --- | --- |
| `status` | Literal `APPROVED_FOR_PUBLICATION`; UI refuses other values. **This is set by exporter, not independent evidence of rights clearance.** |
| `source` | Literal `WORLD + existing media release; read-only derived export`. |
| `approved_current_assets` | Number of exported entries; 182 in current version. |
| `sql_inspection` | Literal `NOT_EXPORTED`. |
| `assets` | Array of exported asset objects. |

Every asset object contains these 16 allowlisted fields copied from the catalog adapter (missing values become JSON null): `asset_id`, `knowledge_entity_id`, `asset_role`, `review_status`, `media_key`, `width_px`, `height_px`, `is_current`, `canonical_name`, `noun_class`, `spatial_entity_id`, `name`, `object_type`, `parent`, `celestial_object`, `celestial_id`. The exporter adds `ancestry` (array of objects with `name`, `entity_id`, `entity_class`), `original`, `original_bytes`, `thumbnail`, and `thumbnail_bytes`: **21 top-level fields per asset**. Image paths are relative `images/<SHA256-of-blob>.<png|jpg|webp>`; byte lengths are original blob lengths. Identical blobs share a filename; count referenced files rather than assuming unique file count. Supported MIME types: `image/png`, `image/jpeg`, `image/webp`; other types fail. Source SQL reads `media_assets` columns `mime_type`, `original_blob`, `thumbnail_mime_type`, `thumbnail_blob` by `media_key` and opens both databases read-only. The complete source database schema is **not** documented by this export and must not be inferred from these four selected columns.

Selection rule: `review_status == 'APPROVED_REFERENCE'` AND `is_current == 1`, with exactly **182 rows and 182 distinct `asset_id`** required by current exporter. Each must have nonempty original and thumbnail blobs and allowed MIME. No arbitrary SQL rows, WORLD tables, SQLite files or CIVSTATE data are copied into Pages. The UI searches JSON text across records, filters by `celestial_object` and `object_type`, opens original images, and displays an escaped JSON/ancestry detail panel. `Canon Inspector` is the UI title; it does **not** provide live canon/SQL inspection or authority.

**Schema evolution:** 182 is a deliberate current invariant, not a universal constant. When approved assets change, revise the count in exporter, preview and deploy workflow together after reviewing changed entries and public fields; verify unique IDs, bytes, references, UI and release compatibility. Never merely weaken the assertion to make a build pass. If adding fields, review their public disclosure and update this schema contract. If changing `src/loom_media_library.py` or underlying SQLite schema, document compatibility/migration and run relevant unit + functional tests.

## 4. Reproduce a preview locally

From a clean repository checkout with Python and the correct release asset available:

```bash
curl --fail --location --retry 3 --output /tmp/LOOM_2226_media.sqlite3 'https://github.com/loom-2226/loom-2226/releases/download/v0.1.0-runtime-baseline/LOOM_2226_media.sqlite3'
echo '286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038  /tmp/LOOM_2226_media.sqlite3' | sha256sum --check
python tools/build_inspector_pages.py --world data/LOOM_2226.sqlite3 --media /tmp/LOOM_2226_media.sqlite3 --output docs/inspector
```

These commands are the workflow's Linux runner procedure; on Pixel/Termux use a suitable local file path and available SHA-256 checker, without assuming `/tmp` or `sha256sum` exists. The exporter uses `mode=ro` SQLite connections; do not run write/migration commands against source databases as part of publishing. A local `docs/inspector/` export may contain large untracked files: do not stage `catalog.json` or `images/` into Git accidentally.

## 5. Update, review, merge and republish (operator checklist)

1. Bootstrap from live `main`, verify current SHA, workstate and governance, existing workflow/Pages configuration, media release and active PRs. Decide whether this is **UI-only**, **metadata/export**, or **new/changed media**. New media requires updating the authoritative media source/release through its own governed process; editing generated Pages output alone will be overwritten on next deploy.
2. Create a branch from current `main`. Modify only intended source files. For UI changes edit `docs/inspector/index.html`; for allowlist/selection/schema edit `tools/build_inspector_pages.py` and, when needed, `src/loom_media_library.py`. For new release, update both workflow release URLs and SHA-256 only after source/release verification. Preserve `docs/ceres/` and unrelated `docs/` content.
3. Review publication rights and metadata fields, including ancestry and names, before making new records public. `APPROVED_REFERENCE` is an internal selection status; `APPROVED_FOR_PUBLICATION` is currently a generated flag, not a substitute for human publication approval. Record explicit approval in the PR. Keep CIVSTATE, SQL rows and private material excluded unless separately governed and implemented.
4. Run relevant unit and functional tests for substantive changes. Open PR with exact primary class `class:asset-media`, scope, source/release provenance, dependency/compatibility impact, publication authorization, evidence and rollback plan. Preview workflow triggers for changes under `docs/inspector/**`, `tools/build_inspector_pages.py` or its own YAML. **If changing only `src/loom_media_library.py` or the deploy YAML, manually run preview or expand its path triggers**: they are not currently listed. Preview success only produces a temporary artifact, not a live site.
5. Inspect preview `catalog.json` and ZIP: 182 unique approved/current IDs (or newly reviewed count), top-level and asset field allowlists, no SQL/CIVSTATE/database, expected image MIME, all referenced originals/thumbs present, SHA-256 filenames and recorded byte lengths correct, no path traversal, and UI search/filter/Inspect on a browser. The initial preview was inspected with 366 ZIP entries, 182 records and 364 image references; this is historical evidence, not an evergreen assertion about future builds.
6. Require green `loom-gate` for the **current PR head**, resolve discussions, then merge to protected `main` through normal PR procedure. The initial PR was #242, merged at `e34d54525fe1d46bb25cf2531d151dbc2c6ecf54`. A past successful check does not cover a later commit.
7. Confirm Settings → Pages → Build and deployment → Source = **GitHub Actions**. Do **not** click GitHub's suggested Jekyll or Static HTML Configure buttons; the custom workflow already exists.
8. Open https://github.com/loom-2226/loom-2226/actions/workflows/inspector-pages-deploy.yml ; choose **Run workflow**, branch `main`, tick `confirm_publication`, submit **once**. It requires `contents:read`, `pages:write`, `id-token:write`, uses `github-pages` environment and concurrency group `loom-pages` with no cancellation. The job downloads/verifies release, checks Ceres, regenerates Inspector, validates catalogue/IDs/image existence, configures Pages, uploads all `docs/` and deploys. Wait for the run to be **green**; yellow means in progress, red means failure.
9. Verify live https://loom-2226.github.io/loom-2226/inspector/ and https://loom-2226.github.io/loom-2226/ceres/ . Confirm expected asset count, thumbnails/originals, search, both filters, Inspect/ancestry, mobile and desktop layout, and that no databases/CIVSTATE are served. Record deployment run URL, deployed commit, release SHA, asset count, time and smoke results in the PR/release record. A green Actions job alone is not browser acceptance.

**Important current workflow limits:** Deployment is manual, not automatic on merge. The deploy workflow checks existence of files and IDs but does not independently hash every generated image or perform browser end-to-end tests; add those tests in a future PR if desired. Its hardcoded 182 count will intentionally fail on catalog expansion until reviewed and updated. The Pages artifact includes all `docs/`; keep generated private/unreviewed material out of that tree.

## 6. Failure and rollback

- **No Run workflow control:** use repository Actions workflow page (not Settings → Pages); verify the YAML exists on default branch and Actions permissions. The GitHub mobile app/web UI may differ.
- **Release download/hash failure:** check release URL, availability, asset and expected SHA; do not bypass integrity check or upload another large release just to make it pass.
- **182/count/duplicate failure:** inspect catalog changes, approvals, `is_current`, IDs and source release compatibility; update expectations only after explicit review.
- **Missing blob/MIME/image failure:** correct authoritative media data/release, then rebuild; never silently skip broken assets.
- **Pages permission/environment/source failure:** verify Pages source GitHub Actions, workflow permissions and `github-pages` environment; inspect failing job logs. A source switch may require owner access.
- **Blank/partial page:** inspect `catalog.json` fetch/status, image relative paths, browser console/network, Pages run and deployment URL; test Ceres independently. Do not infer deployment success from a screenshot of the Pages Settings page alone.
- **Rollback:** identify last known-good `main` source and its matching immutable media release/hash, revert offending source change through a governed PR if needed, then manually rerun the deployment workflow with explicit authorization. Because the workflow checks out `main`, rerunning without reverting will redeploy the same current source; an older Actions artifact alone is not an automatic rollback mechanism. Preserve Ceres by continuing to deploy entire `docs/`.

## 7. Historical publication trace and boundaries

Initial development PR: https://github.com/loom-2226/loom-2226/pull/242 . Preview run `35217392456` succeeded; inspected preview artifact `10495768897` was temporary. A later preview and `loom-gate` succeeded on PR head `ac4b6746f1614c2bcd30f5f82e5d582e6082a02d`; squash merge was `e34d54525fe1d46bb25cf2531d151dbc2c6ecf54`. Repository owner changed Pages source to GitHub Actions and manually launched `Publish LOOM Pages with Media Inspector` on `main`; the initial live mobile screenshot displayed the site and 182 assets. **Exact first successful deployment run ID was not captured in this document; retrieve it from GitHub Actions history rather than inventing it.** No duplicate media release was made for this Inspector publication. This runbook records current implementation, not a claim that all future schema and release changes are automatically safe.
