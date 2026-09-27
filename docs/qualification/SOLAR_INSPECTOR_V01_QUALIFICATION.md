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

## Human Q3–Q6 correction — 2026-09-27

Primary class remains `class:runtime` on PR #299. The Inspector now applies
Solar, Local System and Whole Catalog display presets. Solar starts with Sun,
planets and their resolver paths; Local System shows the primary and its
governed family; Whole Catalog enables all physical object classes and their
applicable paths. Deterministic zoom bands reduce markers, labels and path
clutter while those class layers remain enabled. Barycenters have an explicit
layer OFF by default in every
preset. The layer changes markers, labels and ordinary camera-fit inputs only;
it does not change catalog membership, selected reference centers, PostgreSQL,
SPICE, provenance or resolver calculations. Manual layer changes persist until
another scope is entered.

System navigation now keeps an initial camera fit active while the relevant
local family and its automatic path requests load. The fit uses the complete
displayed resolved path extent plus viewport-aware padding. It stops when
local rows and path requests settle; pointer, wheel and zoom actions cancel a
pending fit. Browser qualification verified Earth with its full Moon path and
Jupiter with four Galilean moon paths against the fitted camera distance, then verified
that a later manual zoom was not reset. Unresolved satellite paths remain
unresolved rather than expanding the fit with invented points.

Automatic path policy is server-side. Each request starts at selected T0. For
bound objects, the server measures phase from successive governed resolver
states relative to the local primary/reference center and requests one future
revolution where a complete phase is found. Spacecraft and interstellar
objects request one open Julian Earth year. The configurable default maximum
is 100 Julian years; a bound body that does not complete a measured revolution
within it is explicitly `MAX_HORIZON_TRUNCATED`. Unresolved or ambiguous phase
has separate status. This search determines a display horizon only; all
rendered physical samples still come from the governed resolver. Nominal sample
count responds to duration, and resolver-evaluated midpoints refine curved
intervals up to 512 samples. Automatic responses retain direct/propagated
segments, exact source seam brackets, gaps, and `closed_by_renderer: false`.

Live 2026-01-01 T0 horizon checks against the read-only `loom_dev` snapshot:
Earth 365.260 days, Moon 27.337 days, Jupiter 4,333.104 days, Io 1.769 days,
and Ceres 1,681.011 days all returned `REVOLUTION_COMPLETE`; Sedna returned
`MAX_HORIZON_TRUNCATED` at 100 years; New Horizons and Oumuamua returned
`OPEN_ONE_EARTH_YEAR` at 365.25 days. These are resolver-phase display
measurements, not promoted orbital constants.

Qualification passed: 41 scoped unit tests with three existing PostgreSQL
gated skips; 18 live Inspector tests against read-only `loom_dev`; Python and
JavaScript syntax checks; and the desktop plus 412px/3x Chromium browser run.
The browser observed 195 exact scene responses, 98/98 Whole Catalog automatic
path requests, zero path requests during Play, zero page errors and zero
external requests. It exercised Q1/Q2 navigation and decluttering, Q3
Earth/Jupiter progressive local fit and manual camera retention, Q4 barycenter
visibility toggle, Q5 scope defaults and manual override retention, and Q6
complete, open and capped horizons. Existing live trajectory checks retained
New Horizons direct/propagated seams, unresolved samples, source provenance and
open interstellar geometry. The Pixel-sized first exact scene took 3.769 s and
a Play advance 61 ms on the warm qualification host; these are observations,
not release thresholds.

No schema, SQLite, migration, canon, engineering authority, kernel asset,
source selection, resolver-state shape, legacy Solar GIS fallback, launcher or
release contract changed. The new automatic path response is an optional
Inspector endpoint; the existing manual and compact path endpoints retain
their prior request and response contracts. Recovery is to revert the PR
branch commit. Promotion still targets protected `main` through PR #299.

## HUMAN-Q7 automatic route regression — 2026-09-27

Human qualification of `bf014c7` found `GET /api/trajectory?body=EARTH&center=SUN&start=2026-09-27T00:00:00Z&view=auto`
returning HTTP 400, `{"error": "invalid epoch_utc: None"}`, while `/api/catalog`
returned valid governed JSON. The Pixel UI reported `Resolver paths unavailable`.
This is recorded as a Q6 human qualification failure, not a visual defect.

The active server process on port 8765 had started at 10:00 local time, before
the Q6 route was written at 12:46. The loaded pre-Q6 route treated `view=auto`
as a manual trajectory and passed its absent `end` query value as `None` to
`trajectory`/`_epoch`. The supplied `start` was intact. A direct call through
the current `automatic_path` with the read-only live ledger returned a complete
Earth revolution; no resolver or epoch parser defect was found. The stale
process was stopped and the current branch server started on port 8765 using
the Solar virtual environment. No default epoch, fallback path, browser
propagation or fabricated state was introduced.

A new test sends a real HTTP `view=auto` request without `end` to the current
server handler. It requires HTTP 200, the supplied T0, a complete governed
horizon, source segments and seam preservation. Browser qualification now
records non-200 automatic responses and checks that neither desktop nor Pixel
reports `Resolver paths unavailable`.

After restart, the exact human reproduction URL returned HTTP 200: Earth/Sun,
T0 `2026-09-27T00:00:00Z`, horizon `REVOLUTION_COMPLETE`, end
`2027-09-27T06:16:53.089183Z`, 38/38 resolved points, one direct segment,
zero seams and zero gaps. The first point had governed relative state and
`closed_by_renderer` remained false. A temporary system-Python launch returned
HTTP 200 with an explicitly unresolved path because that interpreter lacked
the Solar SPICE environment; it was stopped and excluded from success evidence.

The live Inspector suite passed 19/19. The Q3–Q6 scoped Inspector, spatial
authority, SPICE adapter and source-isolation run passed 42/42 in the Solar
virtual environment. An initial system-Python run had one environment error
(`spiceypy` missing); the virtual-environment rerun passed. Python compile,
JavaScript syntax and `git diff --check` passed. Desktop and 412px/3x Pixel
Chromium passed: 195 exact scene responses, 98/98 Whole Catalog automatic
paths, zero failed automatic responses, zero page errors, zero external
requests and zero path requests during Play. Both views lacked the reported
unavailable message. Seam, gap, truncation and unresolved behavior remains
explicit; prior frozen scientific and governing source objects were untouched.

## SPICE-native time authority repair v0.1 — 2026-09-27

**Root defect.** The registry selected sources by comparing Python UTC
datetimes from PostgreSQL `timestamptz` coverage labels. The adapter then
converted each requested UTC text with `spice.str2et` under the furnished
`naif0012.tls` LSK before an otherwise native `spkgeo` evaluation. Automatic
planning and trajectory sampling also used Python UTC datetime arithmetic.
Those future UTC labels cannot define an independently known 2226/2250
physical epoch under today's LSK.

**Corrected contract.** The HTTP boundary accepts numeric SPICE ET or an
explicitly suffixed TDB calendar. CSPICE `tparse` maps TDB text once to ET;
numeric ET then controls source selection, state resolution, relative-state
identity, automatic horizon search and every trajectory sample. The adapter
passes that ET directly to `spkgeo(target, et, 'ECLIPJ2000', 10)`. Browser
step/play adds seconds to the numeric ET returned by the server. `etcal` TDB
labels are display only and rounded to milliseconds; numeric ET remains in
every state/path response. Explicit UTC input is still accepted at the
interface as a **projection** through pinned LSK SHA-256
`678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b`.
Response authority identifies that policy and hash. Future UTC has no claim
of known physical mapping; the UI shortcuts use TDB.

**Data migration.** Live `loom_dev` was inspected read-only: 123 coverage rows,
121 qualified, 110 bodies. A deterministic generator verified 84 exact pinned
primary SPKs and extracted target `spkcov` ET windows. The static
`SOLAR_NATIVE_ET_COVERAGE_V1` overlay records source/body, status, historical
UTC label, native window, selected numeric ET window, SPK hash and derivation
method for every row. Migration 020 adds `coverage_start_et` and
`coverage_end_et`, matches the exact 123-row preimage and leaves historical UTC
labels, statuses, membership, source identities and kernel artifacts intact.
The migration passed in disposable `loom_solar_et_qual_299`, built by copying
the live Solar schema/data without writing to live authority. The final SQL
wraps preimage checks and schema mutation in one transaction; it was replayed
successfully on a fresh disposable `loom_dev` clone,
`loom_solar_et_tx_verify_299`. New startup
checks reject PostgreSQL/overlay disagreement. Source selection ignores the
UTC labels and compares ET; `spkcov` and selected-segment ownership still
verify the chosen physical source at evaluation.

118 rows take their ET interval directly from native SPK endpoints. Five
qualified/narrowed intervals intersect the native SPK window with their
historical qualification limit: Nereid/NEP101XL, New Horizons direct,
New Horizons propagated, Pioneer 10 propagated and Pioneer 11 propagated.
Four other historical labels differ slightly or lie outside an SPK endpoint;
the native endpoint is retained. The historical qualification guard was
projected under the pinned LSK once during artifact generation, is disclosed
in the overlay, and is fixed as numeric ET thereafter. It cannot broaden
native coverage. The New Horizons seam and any SPK-internal gaps remain
explicit; no source status or qualification scope is promoted by migration.

**Affected authority claims.** SPK bytes, source identities, NAIF target and
observer identities, native ET coverage, direct SPICE vectors at a fixed ET,
and km/km/s coordinates are unchanged. The authoritative frame label is now
the exact CSPICE `ECLIPJ2000`; the previous generic
`J2000/ECLIPTIC` label was an alias and no rotation was performed. Prior
future-calendar state/path claims and UTC-labelled coverage boundaries do not
by themselves qualify the new TDB epoch interface. Direct and derived states
at canonical 2026/2226/2250 ET, ET source boundaries, center subtraction,
automatic/manual paths and browser presentation were therefore rerun. The
previous UTC labels remain historical LSK projections, not future civil-time
authority. The five historically narrowed intervals retain their recorded
qualification provenance; any new claim that those human UTC dates have an
exact future civil meaning needs a separate scientific disposition.

Representative TDB calendar inputs map to these canonical ET seconds past
J2000: `2026-01-01T00:00:00 TDB` → `820497600.0`, `2226-01-01T00:00:00 TDB`
→ `7131844800.0`, `2250-01-01T00:00:00 TDB` → `7889227200.0`. All three
resolved Earth from DE440 with `ECLIPJ2000`; 2226/2250 also resolved tested
direct and propagated sources at identical ET for object and center. DE440
Earth native bounds `[-14200747200.0, 20514081600.0]` are inclusive; one
second outside either bound fails closed. The direct New Horizons endpoint
wins its intentional overlap; the next ET selects the propagated source.

The new 2026 TDB shortcut is ET `820497600.0` and resolves 105/110 catalog
objects. Nereid and Pioneer 10/11 are explicitly unresolved there because
their prior qualified start is ET `820497669.18392`, 69.184 seconds later.
The distinct explicit UTC projection `2026-01-01T00:00:00Z` maps to that later
ET and retains the prior 108/110 resolution count. This is a changed calendar
interpretation at a qualified boundary, not lost SPK data or a fabricated
state. At 2226 and 2250 TDB the catalog resolves 103/110, with the same seven
explicit unresolved objects as before.

**Qualification results — 2026-09-27.** The disposable
`loom_solar_et_qual_299` ledger contains 123 coverage rows, 121 qualified,
and zero NULL ET bounds after migration 020. The static overlay SHA-256 is
`ace8df81c7ddbb3657e43bd3d3ad7b5eed07ccbb3a3714df3902be7a06da7820`.
The scoped ET, Inspector, adapter, official-center and Phase-4 B–E suites ran
with `SOLAR_INSPECTOR_DB=loom_solar_et_qual_299` under the qualified
`/home/ubuntu/loom_solar_assets/.venv/bin/python`: **83 tests OK,
3 skips**. The additional Phase-4 earned-authority, source-isolation,
migration, shared SpatialState and SQLite-provider regressions were
**26 tests OK, 8 skips**. These are test skips, not failed qualifications.
The native ET contract suite reran on the freshly migrated transaction clone:
**12 tests OK, zero skips**. An earlier attempt to use the older
`loom_solar_inspector_test_20260926` database as a migration preimage failed
because that database had no `loom_solar` schema; that empty clone was removed
and the fresh live-data clone was used instead.
An initial invocation with system `python3` failed because that interpreter
lacks `spiceypy`; the qualified virtualenv rerun is the reported result.

The fresh-server Chromium desktop and 412px Pixel run passed with **196 exact
scene responses, 98 Whole Catalog paths, zero path requests during Play,
zero page errors and zero external requests**. It exercised 2026/2226/2250
TDB, an explicit UTC projection, local center/trajectory fitting, ET
step/play/pause, New Horizons seams, the open interstellar path and physical/
schematic display. Pixel initial load was **4111 ms** and Play advance
**2051 ms** on this host; these are observations, not release thresholds or
performance claims. Python compile checks, both JavaScript syntax checks and
`git diff --check` passed. `design/loom_design.py --check` passed with zero
errors and two pre-existing warnings (optional Montserrat file; undefined
operational status thresholds). No trajectory performance or cache/kernel-pool
optimization is part of this repair.
