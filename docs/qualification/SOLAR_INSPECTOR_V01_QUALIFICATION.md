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

Automatic scene paths use the same `/api/trajectory` resolver. Planetary scope
samples planets and natural satellites; Whole Catalog progressively samples all
visible planets, satellites, asteroid classes, dwarf planets, centaurs,
trans-Neptunian objects, comets and interstellar objects. Spacecraft retain the
explicit selected-trajectory control. The scene reports sampling progress.
Calendar-stable inspection windows reuse sampled paths during Play; selected
trajectories and their source seams remain separate. The browser caches path
geometry and limits the automatic path cache to 256 entries. These are
presentation choices only, not new physics or source authority.

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
npm ci
PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright" npx playwright install chromium
PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright" npm run test:solar-inspector-browser
```

Result: PASS for the original run, 13 exact-state responses checked, zero page
exceptions, zero external requests. Exercised 2026/2226/2250 and arbitrary UTC,
rotate/pan/zoom, canvas and catalog selection, Earth/Moon, Jupiter, Pluto,
Ida/Dactyl, step/play/pause, physical/schematic state immutability, New Horizons
seam, open interstellar trajectory, and 390px layout. Screenshots were inspected
locally. The follow-up browser evidence is recorded below.

Follow-up path/performance run: PASS, 17 exact-state responses, zero page
exceptions and external requests. The browser requested all 93 renderable
planet, satellite and minor-body paths in Whole Catalog through
`/api/trajectory`; no automatic path request occurred during Play. Selected
Earth/Sun, Moon/Earth, Ceres/Sun and 67P/Sun paths changed the rendered canvas.
On this qualification host, the 412px mobile page reached its first exact
snapshot in 469 ms and a Play advance took 63 ms. These are observations, not
release performance thresholds. The mobile viewport at 3x pixel ratio had no
horizontal overflow or page exception. The 13 live inspector Python tests also
passed unchanged after the presentation follow-up.

The repository's pre-existing absent Montserrat file causes a local font 404;
the documented system fallback works. No missing runtime scripts or page errors.

### Mobile review and progressive data-path follow-up

The original mobile view waited for a full 110-body response before drawing a
useful scene. A fresh-process full snapshot took 58.8 s on this host, of which
57.6 s was pinned SPICE asset verification. JSON serialization took about
5 ms; the full response was 320,689 bytes. The governing kernel hashes remain
checked and source isolation remains fail closed. The adapter was not given a
browser-side substitute or a bypass for verification.

The revised UI first requests governed catalog identity, then five exact
resolver states selected by the already-governed source metadata's declared
kernel-byte cost. It progressively merges the remaining rows in 12-body
batches. Manual epoch and center changes use the same preview. A process-start
Pixel-sized Chromium run observed first useful paint at 1.748 s, 17/110 rows
at 2.160 s, 53/110 at 3.620 s, 89/110 at 15.834 s, and 110/110 at 64.191 s.
The ten compact scene responses totaled 59,208 bytes. OS file cache state was
different between the original and revised process-start measurements, so the
times are observations rather than a controlled cold-storage speedup claim.
The full verification cost remains; it is moved behind a useful scene.

Whole Catalog requests all 93 renderable planet, moon and minor-body paths,
not merely the selected object. They appear as resolver responses arrive. In
the process-start run, all paths completed in 40.601 s and transported
1,077,297 bytes. The earlier warm-server run completed in 10.126 s and
transported 8,769,177 bytes; those completion times are not directly comparable
because the earlier process had already warmed its asset and resolver caches.
The compact path response retains exact sampled relative geometry, segment
authority, gaps and source keys; explicit selected trajectories retain the
full provenance/seam records. Automatic minor-body arcs now use a one-year
window and 24 nominal samples, with longer exact traces available on demand.

Avoidable repeated work was reduced by projecting stable ledger identity and
coverage metadata once at inspector startup, and omitting those repeated
records from scene/path transport. `read_ledger` remains one read-only
repeatable PostgreSQL snapshot; no schema, migration, authority precedence,
manifest or kernel asset changed. Browser path caches are bounded and carry no
state authority. Threaded HTTP handling keeps static/control requests
responsive while the existing shared SPICE evaluation lock enforces selected
source isolation.

For Navigator scale, retain separate governed identity, exact state, compact
scene and full provenance contracts. Key any reusable evaluated state or path
by ledger/manifest/source identity, epoch, frame and reference center, and
invalidate it when authority changes. Preverification or managed asset warming
could shorten first use only if it retains current hash and source-closure
checks. Batch/stream exact resolver work by source closure behind that boundary;
use visible-extent and time-window queries to bound demand. Progressive
geometry may reduce samples or transport detail, but every physical sample
must still come from the governed resolver, with gaps and seams exposed.

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

## Completion review — 2026-09-27

Current `main` was refreshed to `a7b21f82067294be3e27e1715864f0932a13a8f5`.
The intervening Solar data promotions do not change this PR's Inspector source
files. The existing PR remains #299, `class:runtime`.

The combined Inspector and Solar regression run passed: 88 tests, 11 existing
PostgreSQL integration-gated skips. The live Inspector portion passed all 15
tests against the read-only `loom_dev` snapshot. The prior disposable-database
integration qualification of the 11 gated cases remains recorded above; no
schema or migration was changed in this follow-up.

A fresh Inspector process passed the desktop and 412px/3x Chromium browser run:
93/93 Whole Catalog resolver paths, zero path requests during Play, zero page
errors and zero external requests. The warm-server phone view reached its first
exact scene in 2.128 s and a Play advance in 64 ms. These measurements are
host observations, not release thresholds. A separate phone browser check held
back background batches, selected Mars outside the five-row preview, and
verified that exact detail insertion reconciles the preview to 6/110 with
matching resolved/rendered counts. Invalid catalog epochs returned HTTP 400.

Final Python/JavaScript compile checks, `git diff --check`, and design validation
passed. Design validation retained only its two pre-existing warnings for the
optional font and undefined operational status thresholds. The local mobile
capture was visually inspected; touch controls, scene focus and readable
state overlays were present without horizontal overflow.

## Human Q1/Q2 correction — 2026-09-27

On the open `class:runtime` Inspector PR #299, **System** now changes the
reference center to the selected governed catalog object and switches to local
scope before requesting a new exact scene. Earth selection therefore enters
the Earth-centered Earth/Moon view; automatic Moon paths are requested with
`center=EARTH`. When the selected object is already the reference center,
System frames its local family. No resolver, database, schema, source precedence,
Pixel/Windows launcher, canon, or asset authority changed.

Whole Catalog label visibility now follows a deterministic camera-distance
band, class priority, viewport budget, collision check and body-ID tie break.
At Solar overview distance, selection and major planets take precedence. Local
moons, spacecraft, dwarf planets and other minor labels appear progressively
as zoom permits. Nonselected minor and Solar-overview moon paths are withheld
from the display until close zoom, while all supported Whole Catalog paths are
still sampled through the governed resolver and reused from the bounded cache.
Selected paths remain visible. These LOD bands are representational only.

Qualification on the existing read-only `loom_dev` snapshot: Inspector unit
suite 15 tests passed, including three existing database-gated skips; JavaScript
syntax checks and `git diff --check` passed. Desktop and 412px/3x Chromium
browser qualification passed with 195 exact scene responses, 93/93 Whole Catalog
resolver paths, zero path requests during Play, zero page errors and zero
external requests. The browser checked selected Earth -> System -> Earth center
and local scope, Moon@Earth path requests, selected minor priority and Solar
overview decluttering. The warm-server phone first exact scene was 2.063 s and
Play advance 65 ms; these are host observations, not release thresholds.
