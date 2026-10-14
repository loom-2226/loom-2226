# On-demand travel geometry experiment (Build 8, offline only)

**TEST_ONLY · NON-CANON · NON-RUNTIME · no conductor consumers.**
This is a new, review-only follow-up to merged PR #408, not a change to that
pilot's historical result. Supported routes are the inner-system directed
pairs among Earth, Mercury, Mars and Ceres listed in `on_demand.py`.
No outer-system mission range, Moon leg, low-thrust, torch, new vehicle
class, new prices, Agent integration, or new ephemeris authority is implied.

## Request and sampling

`OnDemandTravel.lookup(origin, destination, ready_date,
wait_limit_days=N, departure_limit=..., arrival_limit=...)`
checks **every calendar departure date** in the half-open interval
`[ready_date, ready_date + N days)`. The default `daily` strategy has one
departure sample at midnight UTC per calendar day and a 0.25-day
flight-duration grid over the existing 45–1400-day brackets. The caller
supplies both endpoint limits at lookup; the module chooses neither.
The 1-day minimum useful launch window is the visible authored constant
`MIN_USEFUL_LAUNCH_WINDOW_DAYS = 1.0`. No claim is made about sub-day
edges of a hard vehicle speed cutoff. One-day sampling does not prove a
continuous one-day opportunity exists.

The selectable **`distance_research`** strategy sets a trial departure
step using half the one-day minimum window, scaled by
`(inner_distance / Mercury_reference_distance)^1.5`, with a
half-day floor and one-day ceiling; this preserves every calendar day.
The trial flight-duration step uses
`0.25*(outer_distance / Earth_reference_distance)^1.5` days. Distances
come from actual qualified-source body states at each departure epoch,
not average orbital radii. The two reference values were measured from
SPICE for 2026-01-01 UTC and are visible as constants. For moons, parent
distance would be required but moons are **out of scope** here.
The distance strategy is NOT the default and has NOT earned promotion.
A larger grid step is not an infeasibility certificate.

## Geometry cache

Only the pilot's qualified direct-SPICE Izzo M=0 prograde, low-path,
heliocentric transfer family is computed. The cache key includes directed
route, exact departure epoch, flight-time grid signature and bracket,
transfer family, governing origin/destination source identifiers/hashes,
and solver version. Each retained trajectory contains its **flight days,
departure v-infinity and arrival v-infinity**. Price and vehicle speed limits
are absent from both geometry generation and keys. Changing a filter
does not regenerate geometry. The cache is in memory by default; passing
`cache_dir` optionally writes one deterministic JSON record per sampled
departure epoch, without inventing a cache service or runtime database.

To avoid persisting every solved flight duration, only the exact
three-dimensional non-dominated set is retained. A removed trajectory
must have a retained earlier-or-equal flight-time trajectory with
both endpoint speeds no greater. Therefore any pair of independent
upper bounds on endpoint speeds will retain at least one choice no
slower than the removed trajectory; so do any selection objectives
monotone nondecreasing in flight duration and both endpoint speeds.
That is the precise preservation claim. Non-monotone pricing, alternate
transfer families, and selecting a trajectory merely because its flight
duration is different are NOT preserved by that proof. A binary speed
threshold is **not** used to determine what geometry gets saved.

### Pre-write storage survey

Read-only on `quantifactus`, seven consecutive dates each, using a
0.25-day flight-duration grid and no vehicle speed filters:

| Route | Mean retained records/day | Compact JSON trajectory bytes per route-year (extrapolated) |
|---|---:|---:|
| Earth → Mercury | 172 | 5.2 MB |
| Earth → Mars | 997 | 29.8 MB |
| Mars → Ceres | 2,139 | 64.2 MB |

These are seven-day extrapolations, not annual observations. They exclude
file metadata, key and filesystem overhead. The compact key stores the
flight-duration grid's SHA-256 instead of repeating thousands of flight
times in each cache header. Storage still grows with *requested* dates,
not automatically with the 200-year LOOM horizon.

A cold/warming implementation sample (one 0.25-day-grid departure date
per route) measured the following on quantifactus, **including the compact
cache record header**. Each date required exactly 5,421 Lambert solves:

| Route | Wall elapsed | Stored bytes/date | Annual extrapolation including header |
|---|---:|---:|---:|
| Earth → Mercury | 11.57 s | 15,410 | 5.6 MB |
| Earth → Mars | 7.86 s | 85,304 | 31.1 MB |
| Mars → Ceres | 0.23 s | 183,146 | 66.8 MB |

**The timing figures include uneven first-source/kernel and compiled-solver
warm-up**, so they are not steady-state per-request predictions. The
retained per-date rows were 172 / 996 / 2,138 respectively; no speed
cap was used to choose them.

### Geometry-computation budget

A complete default daily departure date checks 5,421 flight durations
before compression. One route-year is about 1.98 million Lambert
solves. Based on PR #408's measured 3,771,036 solves / 176.28 seconds,
that is **about 93 seconds of batched solver time per requested route-year**,
excluding new overhead, caching and any engine warm-up.

One typical researched step near Earth→Mars is approximately 0.5 days
for flight duration; Mars→Ceres is about 1.3 days. The empirical speed
improvement from the radial research strategy must be measured and
compared with dense-window recall before accepting any skipped samples.

## Acceptance and limits

Focused tests must prove deterministic byte-for-byte cache replay,
all ten historical Mercury witness departure dates, absence of vehicle
limits/prices from geometry cache keys, daily request coverage, and
geometric dominance preserving speed-threshold choices. The experimental
distance rule is compared with dense daily-epoch flight-duration scans
on four slower **directed** routes, plus Mercury. These are selected
sample dates, NOT proof of 100% recall over all dates, all 200 years,
or every admissible continuous transfer interval. Any observed miss
must be reported and prevents promotion. Build 7 tests must remain green.

The current 1,400-day flight-duration maximum excludes many meaningful
outer-system missions, which remain out of scope.
