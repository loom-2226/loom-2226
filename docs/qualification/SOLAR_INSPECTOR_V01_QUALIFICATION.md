# Solar Ephemeris Inspector v0.1 qualification

Date: 2026-09-26. Primary class: `class:runtime`.
Base/current main verified before delivery:
`3752b018e1029d75db18410e61a336dc90efdf2d`.
Environment: quantifactus, Python 3.12, spiceypy 8.2.0, local pinned Solar assets,
PostgreSQL `loom_dev` read-only startup snapshot, Three.js 0.149.0, Chromium via
Playwright. No live database writes or scientific manifest modifications.

## Result

PASS for the bounded inspector acceptance criteria. The existing evaluator now
obeys its selected source regardless of prior governed requests. Membership,
PostgreSQL schema, source-precedence policy, accepted products/models, coverage
declarations and qualification thresholds are unchanged. No existing test was
weakened. The UI is a local qualification instrument, not a production release.

### Source-contamination correction

Before the fix, revisiting New Horizons at `2033-01-01T06:00:00Z` after a 2250
request evaluated the propagated SPK while declaring `NAIF_NH_OD164` direct
authority. Its position differed by `0.00005358639890095786 km` from the initial
request. Neptune at 2026 changed by `0.1759105993067449 km` after another adapter
resolved Proteus, still declaring NEP097 while evaluating NEP098's segment.

The cause was accumulated process-global SPICE kernels plus per-instance
"already loaded" bookkeeping. The correction isolates evaluation to the
registry-selected ordered closure, checks actual target-segment ownership,
serializes governed evaluations, and restores the furnished pool on success
and failure. New regressions prove exact replay, actual segment/provenance
agreement, cross-adapter isolation, pool restoration, and concurrent requests.
No source-selection policy or scientific input is changed.

### Live catalog reconciliation

These are observations, not hard-coded UI expectations. Ledger snapshot SHA-256
prefix in the browser run: `70ed97cf27de`.

| UTC epoch | Catalog | Resolved/renderable | Direct | Propagated | Unresolved |
|---|---:|---:|---:|---:|---:|
| 2026-01-01T00:00:00Z | 110 | 108 | 106 | 2 | 2 |
| 2226-01-01T00:00:00Z | 110 | 103 | 90 | 13 | 7 |
| 2250-01-01T00:00:00Z | 110 | 103 | 90 | 13 | 7 |
| 2250-12-31T23:59:59Z | 110 | 103 | 90 | 13 | 7 |

Dactyl and Selam remain catalog-only at all checkpoints. At the later epochs,
Proteus, Nix, Hydra, Kerberos and Styx also remain explicitly unresolved outside
their qualified coverage. Catalog-only count is 2 and partial-catalog count is
5; both are subsets. All unresolved records retain identity, parent/status,
known coverage and error reasons without fabricated coordinates.

Local-state checks: Earth/Moon, Mars/Phobos, Jupiter/Io, Saturn/Titan,
Neptune/Triton, Pluto/Charon. Ida/Dactyl and Dinkinesh/Selam were checked as
unresolved asteroid companion systems; no qualified satellite state was invented.
The current Moon parent is NULL, so local presentation can include the selected
Moon without rewriting or inferring authoritative parent metadata.

### Trajectories

Every vertex comes from `service.resolve`, including the independently sampled
reference-center subtraction. No analytic orbit or browser propagator exists.

2026–2250 checks with 16 nominal samples plus coverage-adjacent samples:

| Object | Actual samples | Source seams | Unavailable samples |
|---|---:|---:|---:|
| New Horizons | 26 | 1 | 2 |
| Voyager 1 | 23 | 1 | 0 |
| 1I/Oumuamua | 16 | 0 | 0 |

Additional live HTTP checks used 96 resolver samples each, with one segment
and no gaps: Earth relative to Sun over 2026–2027; Moon relative to Earth over
January 2026; Io relative to Jupiter over January 1–3; Charon relative to Pluto
over January 1–8. Observed radial ranges in km were respectively
147100520.51–152086970.09, 360352.37–405427.17, 420020.76–423502.44, and
19592.62–19598.91. These are inspection observations, not new qualification
thresholds. Paths are never forcibly closed.

**Exposed endpoint limitation:** New Horizons fails closed at
`2033-01-01T11:58:50.999999Z` and `2033-01-01T11:58:51Z`: the declared direct
source is selected but its actual SPK lacks target coverage at those samples.
The propagated source resolves immediately after the declared boundary. The
inspector retains both failures, breaks the path, and reports the surrounding
source seam with a time bracket and gap indices. It does not round away the
gap, fall back to another source, or change any coverage declaration. Coverage
endpoint review is separate authority work, not required to expose this result.

## Tests and checks

Solar regression command, unchanged existing suites plus new source isolation:

```sh
/home/ubuntu/loom_solar_assets/.venv/bin/python -m unittest -q \
  tests.test_solar_source_isolation tests.test_spatial_state_authority \
  tests.test_spice_ephemeris_adapter tests.test_official_planet_center_ephemeris \
  tests.test_solar_phase4_earned_authority tests.test_solar_phase4b \
  tests.test_solar_phase4c tests.test_solar_phase4d tests.test_solar_phase4e \
  tests.test_solar_phase4e_residual_closure tests.test_solar_ephemeris_migration
```

Result: 73 tests, 62 passed and 11 PostgreSQL environment-gated skips. All 11
were subsequently run unchanged and passed with `SOLAR_PG_INTEGRATION=1` and
`SOLAR_PG_TEST_DB=loom_solar_inspector_test_20260926` in a newly created
disposable database: migration (6), earned authority (2), Phase 4B (1), 4C (1),
4D (1). The normal user lacks CREATEDB, so local administrator access created
only this disposable test database; no live schema was altered.

```sh
SOLAR_INSPECTOR_DB=loom_dev /home/ubuntu/loom_solar_assets/.venv/bin/python \
  -m unittest -v tests.test_solar_inspector
```

Result: all 13 passed, including live PostgreSQL reconciliation, four epochs,
local systems, open paths, seams/gaps, identifier/source/hash mismatch rejection,
frame/units, arbitrary epochs, shared resolver sampling and unresolved retention.
During development, the new path test's assumption of no endpoint gaps failed;
it was corrected to require explicit unresolved records and disjoint geometry,
as required by the inspector contract. Historical Solar tests were untouched.

```sh
NODE_PATH=/tmp/ceres-atlas-browser-test-20260921/node_modules \
PLAYWRIGHT_BROWSERS_PATH=/tmp/ceres-playwright-browsers \
node tests/solar_inspector_browser.cjs
```

Result: PASS, 13 exact-state responses checked, zero page exceptions, zero
external requests. Exercised 2026/2226/2250 and arbitrary UTC, rotate/pan/zoom,
canvas and catalog selection, Earth/Moon, Jupiter, Pluto, Ida/Dactyl, step/play/
pause, physical/schematic state immutability, New Horizons seam, open
interstellar trajectory, and 390px layout. Screenshots were inspected locally.
The repository's pre-existing absent Montserrat file causes a local font 404;
the documented system fallback works. No missing runtime scripts or page errors.

`git diff --check`, Python compile checks and JavaScript syntax checks passed.
`python3 design/loom_design.py --check` passed: 251 tokens, 74 contrast checks,
zero errors, two existing warnings (missing optional font; undefined operational
status thresholds). Inspector uses certainty/selection styles, not invented
operational status thresholds. Design tokens were not modified.

## Scope and delivery boundary

No unrelated WIP was touched. No Phase 5, CIVPROP/CIVSTATE, canon change,
Atlas/Navigator integration, scientific model/product change, public deployment
or production infrastructure work. No generated scene cache is authority.
The existing design tokens remain DRAFT. Deferred: font packaging, decorative
context, textures and other explicitly excluded features. The bounded deliverable
is the local inspector and PR; merging is not part of this authorization.
