# Luna / medium implementation handoff — Progressive Solar basemap prototype

**Read this first in a fresh implementation session.** Architecture decisions are
resolved in this packet. Implement only the bounded prototype after user authorizes
that next task. Do not repeat external research or choose another scene framework.

## Exact entry state

Repository `loom-2226/loom-2226`.
Specification branch `engineering/progressive-solar-basemap-spec`, based on main
`b22703ab7ce5586fecfeda0998d19b7d1fbbfe30`; packet in
`engineering/solar_basemap/`. Verify its remote PR/head rather than guessing the
final commit from this self-referential file.
Required implementation dependency is PR #299, open at
`f0c373a4deb5589584619b64a91ac2ac1d2ed936`. Do not merge it. Main does not yet contain
its Inspector/native ET code. A clean prototype worktree should start at this
exact SHA and import **only** the engineering/solar_basemap packet from the
specification branch. Example:

```bash
git fetch origin
git worktree add -b prototype/progressive-solar-basemap /home/ubuntu/LOOM_SOLAR_BASEMAP_PROTOTYPE f0c373a4deb5589584619b64a91ac2ac1d2ed936
cd /home/ubuntu/LOOM_SOLAR_BASEMAP_PROTOTYPE
git restore --source=origin/engineering/progressive-solar-basemap-spec -- engineering/solar_basemap
```

This is a stacked prototype dependency, not authority promotion. Verify PR299
has not changed disposition; if newer repair code is required, inspect/diff and
explicitly record the new dependency, rerun its relevant regressions. Never reset
or rewrite the existing Inspector worktree. Re-read authoritative main governance,
scoped src/engineering/any web/tools AGENTS, style guide/tokens, dependency policy.
Read README, ADR-001, AUTHORITY_PROVENANCE, PRODUCT_CONTRACT, product.schema.json,
LOD_REFINEMENT, generation-spec.json, PROTOTYPE_PLAN, ACCEPTANCE_BENCHMARKS. These are the implementation
spec, not another research assignment.

## Reuse and environment

- `src/loom_solar_postgres.py:load_authority` for read-only ledger/manifest checks.
- `src/loom_spice_ephemeris_adapter.py` registry + state service; numeric ET only.
- `src/loom_solar_time.py`; `Inspector.automatic_plan`, `trajectory`, `relative_state`
  behind an offline compiler adapter. Do not modify Inspector helpers to simplify
  publishing or bypass its source-isolation checks.
- Kernel assets `/home/ubuntu/loom_solar_assets`; Python venv
  `/home/ubuntu/loom_solar_assets/.venv/bin/python`; database `loom_dev`.
- Three.js r149 `web/three/three.min.js`, required SHA
  `8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271`.
  Setup instructions in PR299 `docs/solar_ephemeris_inspector_v0.1.md`.
- Existing Playwright `node_modules` in Inspector checkout; use NODE_PATH or local
  install consistent with its lock/dependency state. Do not silently upgrade.
- `design/loom-tokens.css`, wordmark, font; treat DRAFT values as fixed.
- Existing tests/Q8 evidence are diagnostic design donors. Do not overwrite them
  with basemap results. The attached sample corpus is decision evidence only.

## Ordered work

1. Create contract/validator and negative fixtures (A1–A6). New files are exactly
   listed in PROTOTYPE_PLAN. Commit class `class:runtime` for prototype behavior;
   schema is a derived-product contract, no SQL migration.
2. Read authority, verify native ET overlay/migration prerequisites without writing;
   compile fixed TDB `2226-01-01T00:00:00 TDB` (ET7131844800). Preserve whole 110-ID
   index including seven unresolved at baseline. No synthetic replacements.
3. Generate required curves: eight planets/Sun, Moon/Earth, Phobos/Mars,
   Deimos/Mars, Charon/Pluto. Adaptive master, independent probes, segmented nested
   simplification, immutable canonical JSON/gzip and manifest hashes. Exact
   equations and constants are in authority/refinement docs. Build twice.
4. Create static QA server on new port **8770**; no authority API. Preserve port
   8765 Inspector and all database/services. New shared client loader handles
   manifest validation, request cache, SSE/admission, error status and draw lists.
5. Add minimal Three.js QA adapter; camera continuous, no system/ref switch.
   Frozen anchor local reference geometry, Float64 camera-relative conversion,
   on-demand draws, semantic legend/catalog failures. No texture/terrain/physics.
6. Unit test selection separately, then implement deterministic browser camera
   replay and reconciliation hooks. Run Mars and Pluto sequences, cache/failure/
   frustum/edge-on tests at 412×915/DPR3 and desktop. Compare progressive vs
   monolithic same-product control with acceptance profiles.
7. Save evidence under `engineering/solar_basemap/prototype/`; final report states
   each A1–A12 result, measurements and device limitation. Commit/push to new PR,
   base PR299 branch while that dependency remains unmerged, with spec PR linked.
   Do not merge either PR. Keep all worktrees clean; generated full products go to
   `/tmp` or qualified release-artifact storage, not unreviewed data authority.

## Implement these CLI/test surfaces

The commands below are **required prototype interfaces to create**, not existing
commands or claims of passed tests:

```bash
/home/ubuntu/loom_solar_assets/.venv/bin/python -m unittest tests.test_solar_basemap_contract tests.test_solar_basemap_compile
/home/ubuntu/loom_solar_assets/.venv/bin/python tools/build_solar_basemap.py --database loom_dev --asset-root /home/ubuntu/loom_solar_assets --epoch '2226-01-01T00:00:00 TDB' --output /tmp/loom-basemap-a
/home/ubuntu/loom_solar_assets/.venv/bin/python tools/build_solar_basemap.py --database loom_dev --asset-root /home/ubuntu/loom_solar_assets --epoch '2226-01-01T00:00:00 TDB' --output /tmp/loom-basemap-b
/home/ubuntu/loom_solar_assets/.venv/bin/python tools/build_solar_basemap.py --verify-identical /tmp/loom-basemap-a /tmp/loom-basemap-b
python3 tools/serve_solar_basemap_qa.py --product-root /tmp/loom-basemap-a --port 8770
node tests/solar_basemap_selection.cjs
SOLAR_BASEMAP_URL=http://127.0.0.1:8770 SOLAR_BASEMAP_EVIDENCE=/tmp/basemap-browser node tests/solar_basemap_browser.cjs --profile pixel --delivery progressive
SOLAR_BASEMAP_URL=http://127.0.0.1:8770 SOLAR_BASEMAP_EVIDENCE=/tmp/basemap-control node tests/solar_basemap_browser.cjs --profile pixel --delivery monolithic
```

Browser runner must also support `--profile desktop`; each includes cold/warm and
throttled/unthrottled trials from ACCEPTANCE_BENCHMARKS. If dependency code is
changed (not expected), run PR299's 31-test Solar/ET regression plus relevant Q8
browser regressions. Run `git diff --check`, structural schema/packet checks,
applicable normal tests, and required loom-gate on PR. Design-system check only
if design files change (not expected).

Expected generated outputs: current pointer, immutable manifest/root/node levels,
source/sample audit resources, reproducibility report, all-feature reconciliation,
per-view pixels/screenshots, payload/network/timing/memory CSV or JSON, camera path,
negative-case results and an honest qualification report. Build IDs may differ
from this spike's ledger if current authority changes; stop to audit that change
before qualification, never silently preserve stale expected counts.

## Stop conditions and PASS/FAIL

Stop affected build/publication on authority identity/frame/time/source/coverage
mismatch, unexplained unavailability, corruption, source promotion, unresolved
sample bridged, invented geometry, or inability to reproduce. An unresolved body
with truthful status is a valid product record, not a reason to fabricate or abort
all useful context. Missing required Mars/Pluto capability means prototype FAIL.

`EMULATED_PROTOTYPE_PASS` requires A1–A12, deterministic bytes, correct pixels,
continuous automatic refinement, and comparative performance criteria, with raw
measurements retained. Inconclusive performance benefit is not PASS. Physical
Pixel is `PENDING` unless a real device is tested and evidence recorded; emulation
cannot establish handset performance. On FAIL, preserve evidence, fix bounded
implementation defects, or report architecture falsification with cause. Do not
change criteria merely to obtain green results.

Hard prohibitions: production deployment/implementation, merge #299 or any PR,
Solar authority/schema edits, new orbital model, browser propagation, synthetic
moon loops/geometry enlargement, source-gap bridging, hiding unresolved identities,
legacy Solar coordinates as authority, invented facilities, Navigator simulation,
Phase 5, or unmeasured performance optimization.
