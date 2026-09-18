# Slice 1 validation — 2026-09-19

Environment: Termux / Python 3.13.13 / Node v24.17.0.
Scope: private five-facility Atlas only. This is available-test qualification for
a local development commit, not production promotion or full-product acceptance.

## Executed

| Command / check | Result |
| --- | --- |
| `python -B -m pytest -p no:cacheprovider tests/test_ceres_atlas_server.py tests/test_database_data_dictionary.py -q` | **27 passed**: 25 Atlas unit/HTTP checks and 2 existing dictionary regressions. |
| `node --test tests/ceres_atlas_model.test.mjs` | **22 passed**, no skips. |
| `node --test tests/ceres_atlas_browser.test.mjs` | **7 skipped**, 0 browser tests passed: Playwright and a browser executable are unavailable locally in Termux. Historical local result; superseded for hosted-browser coverage by the CI evidence below, not rewritten as a local PASS. |
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
The original seven locally skipped automated browser tests remain a historical
local result; the distinct hosted Chromium results are documented below.

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
Inspector, GIS, gallery, data, governance, launchers and workflows were unchanged
by the original Slice 1 implementation. The later dedicated additive CI workflow
and browser-test fixture correction are documented separately below.

## Remaining verification gaps and scope boundaries

- The original Termux browser execution remains **7 SKIPPED / UNVERIFIED LOCALLY**.
  Hosted Chromium browser coverage subsequently ran and passed; see the exact
  commit-specific CI evidence below. Screenshots, screen-reader behavior and
  full-product acceptance are not established by the hosted suite.
- No protected-main `loom-gate` status was produced during implementation; there
  was no PR or promotion. The later branch-push authorization does not
  establish a gate result. Ruby (used by the existing gate) is absent locally. The gate
  remains required for any later protected-main promotion.
- The existing semantic coverage index/checker mismatch remains `REVIEW_REQUIRED`
  under WALTER.PROVENANCE. This application does not consume that index or infer
  database metrics. A separate repair must reconcile the index schema and actual
  checker execution before asserting current semantic column coverage.
- Larger Atlas work (body dossier, richer fields, spatial interpretation, canonical
  metrics, full-product acceptance and publication) remains outside this slice.

## Dedicated browser CI authorization — 2026-09-19

Primary class: `class:governance` (verification automation only). Work item:
close the existing seven-test browser verification gap on the Ceres feature branch.
Authoritative main was reverified at `84ccdf5e88eedb492564f021a6dcc6d131a6026e`;
feature head before this change was `5bcc4b449e06b63cb0b590b980e21799097a095e`.

Repository Actions policy reports `enabled=true`, `allowed_actions=all`, and
default workflow permissions `read`. Pages reports `build_type=workflow`; the
existing `inspector-pages-deploy.yml` is manual-only with an explicit publication
confirmation. The other existing workflows use pull-request/manual events, not
this feature-branch push. No repository setting or permission change is needed.

`.github/workflows/ceres-atlas-browser.yml` is push-triggered only on
`feature/ceres-atlas-private-20260919`, additionally guarded by exact job ref.
It uses `ubuntu-24.04`, Node 24, Python 3.13, commit-pinned official setup actions,
and Playwright 1.63.0 (Apache-2.0) with its matching Chromium. Dependencies are
installed only in the disposable runner. The token has only `contents: read`;
checkout does not persist credentials. No deployment environment, Pages action,
release, artifact upload, repository write, or main-branch trigger is present.
This is a separate functional CI check, not a change to `loom-gate` or its semantics.

The existing browser suite runs with Node's TAP reporter; pipeline failures are
propagated, and `tools/check_ceres_browser_tap.py` requires exactly seven real
passes, zero failures/cancellations/skips/todos, seven result records and a complete
plan. Missing tooling cannot produce a green job. Markdown-only evidence updates
do not trigger redundant reruns. The original seven test assertions were unchanged
by the CI workflow addition.

Scope: this workflow, its result checker and checker regressions, plus this evidence
record. Application/data/schema/launcher/publication consumers remain
`UNCHANGED_COMPATIBLE`; no migration, CCR, frozen-object change or governance
exception is required. Recovery is a revert of this additive verification change.
Only this feature branch is authorized for commit/push.

Pre-push local verification for this CI change: **44 Python tests passed**
(17 TAP-checker regressions, 25 Atlas server/source checks, 2 dictionary regressions);
**22 JavaScript model tests passed**. The actual local seven-skip browser TAP output
was fed through the new CLI checker and correctly rejected with a nonzero exit.
JavaScript syntax and whitespace checks passed.

## Hosted Chromium browser CI — observed evidence, 2026-09-19

This section records completed historical results without rewriting the previous
Termux skips or first hosted failure.

1. **First hosted run — FAIL, preserved:** commit
   `80bd5bdf2366449cf5b5aa254104fc9d48a27942`, Actions run
   [35367680146](https://github.com/loom-2226/loom-2226/actions/runs/35367680146),
   completed with **6 passed, 1 failed, 0 skipped**. Playwright and Chromium
   installed successfully. Test 6, `missing image retains identity and supports
   retry without navigation loss`, timed out waiting for a visible
   `#detail-view .image-fallback`; the element remained hidden. The test installed
   its image-request interception after initial page navigation, allowing the
   first image to have loaded already. This failure remains part of the audit trail.
2. **Narrow fixture repair:** commit
   `6e22cf0e4cd568f58391f6986bb25ae4de9fcfea`,
   `test(ceres-atlas): intercept image request before initial navigation`,
   changed only `tests/ceres_atlas_browser.test.mjs` to register the simulated
   image failure before opening the page. The original failure/retry assertions
   were retained. No application code, canonical databases, manifest, deployment,
   publication or protected-main files were changed by this repair.
3. **Second hosted run — PASS, verified:** Actions run
   [35368342705](https://github.com/loom-2226/loom-2226/actions/runs/35368342705)
   checked out that exact repair commit and completed with conclusion `success`.
   The decoded browser job log explicitly records **7 tests, 7 passed, 0 failed,
   0 cancelled, 0 skipped, 0 todo**. Each of the seven named browser tests passed,
   including the previously failing missing-image recovery. The strict TAP
   checker printed `Ceres browser verification PASS: tests=7, suites=0, pass=7,
   fail=0, cancelled=0, skipped=0, todo=0`. GitHub job `browser` concluded
   `success`.

Disposition: **the scoped seven-test hosted-browser verification gap is CLOSED
for commit `6e22cf0e4cd568f58391f6986bb25ae4de9fcfea`.** This does not
retroactively make the locally skipped tests pass. It does not establish a
protected-main `loom-gate`, release qualification, full Atlas acceptance,
publication, or resolution of the unrelated semantic coverage checker defect.
This evidence-only Markdown update does not require or claim a fresh CI run.

## Prototype 08R implementation — 2026-09-19

The private Atlas now includes the complete six-domain body view (People,
Economy, Transit, Infrastructure, Institutions & Governance, and Society),
reusable facility dossiers, and typed institution dossiers connected through
facility roles. Facility, institution, and domain routes preserve query/type
filters, browser history, return focus and scroll context. The UI uses the
approved Montserrat/token styling and the unchanged official white LOOM SVG
served from the private allowlist.

The verified five-facility manifest and approved PNGs remain the only facility
identity/media source. Analytical values shown in the prototype retain the
handoff's explicit model/source caveats; no population, economic,
 infrastructure, coordinates or ownership values are inferred from the
canonical databases. The local manifest contains no Ceres body hero asset, so
that hero renders an explicit unavailable state rather than substituting an
image. Physical/JPL citation enrichment remains incomplete.

### 08R checks

| Command / check | Result |
| --- | --- |
| `node --check web/ceres-atlas/app.mjs` | Passed |
| `node --test tests/ceres_atlas_model.test.mjs` | **23 passed**, including domain/institution route coverage |
| `python -B -m pytest -p no:cacheprovider tests/test_ceres_atlas_server.py tests/test_ceres_browser_tap.py -q` | **42 passed** |
| `node --test tests/ceres_atlas_browser.test.mjs` | **7 skipped / unverified locally**: Playwright is unavailable in Termux |
| `git diff --check` | Passed |

The semantic-coverage checker discrepancy remains documented above and was not
expanded into this implementation. This is a private prototype increment, not
full Atlas acceptance, publication, deployment or protected-main qualification.
