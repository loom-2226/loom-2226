# Solar Ephemeris Inspector v0.1

Primary change class: `class:runtime`; additive `class:data` schema impact in the
ET authority repair. Bounded Phase-4 qualification instrument,
authorized by Kevin, including the subsequent explicit authorization to correct
SPICE source contamination. Representation consumes empirical authority; it
does not establish new canon, membership, products, coverage, or scientific models.

## Launch locally

Requires Python, PostgreSQL `psql` access to the governed `loom_solar` ledger
through migration 020, and the already-qualified local Solar asset collection.
The inspector does not create or migrate a database or acquire ephemerides.

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-solar-ephemeris.txt
mkdir -p web/three
curl -fsSL https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js -o web/three/three.min.js
.venv/bin/python -m src.solar_inspector_server --database loom_dev --asset-root /home/ubuntu/loom_solar_assets
```

On the qualification host the existing environment can be used directly:

```sh
/home/ubuntu/loom_solar_assets/.venv/bin/python -m src.solar_inspector_server
```

Open `http://127.0.0.1:8765`. The server binds only to loopback. `--port`,
`--database`, `--asset-root`, `--three-js`, and `--max-orbit-years` are the
configuration flags. The automatic bound-object horizon cap defaults to 100
Julian years; `--max-orbit-years` accepts 1–500.
Libpq connection settings and credentials follow normal `psql` conventions.
The fixed query uses `REPEATABLE READ READ ONLY`, a statement timeout, and no
interpolated SQL. It works with SELECT-only credentials.

Three.js uses the existing Wayfarer classic r149 pattern, without a frontend
framework. Its MIT-licensed setup asset is local and SHA-256 pinned to
`8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271`.
No CDN or external ephemeris request occurs at runtime. The setup download is
optional if those exact bytes are already installed. No paid/hosted service,
AI inference, telemetry, or external data transmission is introduced.

The first scene evaluates five exact states chosen from the governed source
metadata for low declared asset cost. The remaining catalog loads in batches;
the status shows its progress. Verifying all local kernels (about 14 GB on this
host) can still take roughly a minute. Later requests reuse verified assets.
Restart the inspector to reload the database snapshot or changed assets.

## Inspect

- Enter numeric SPICE ET seconds past J2000 or an explicitly suffixed TDB
  calendar such as `2226-01-01T00:00:00 TDB`. The 2026/2226/2250 shortcuts
  use TDB. After evaluation the input displays the canonical numeric ET; the
  scene status displays its TDB calendar label. `etcal` rounds that label to
  milliseconds, so the numeric ET retains exact request identity. Step days,
  backward/forward, and play/pause add seconds to numeric ET and evaluate
  exact resolver states.
  Explicit timezone-qualified UTC is accepted as an interface projection under
  the pinned `naif0012.tls` LSK. A future UTC label is **not** a known future
  physical time definition; its resulting ET, LSK SHA-256 and projection policy
  are exposed in the response. Prefer ET or TDB for 2226/2250.
  Play waits for each response; no SPICE evaluation runs per browser frame.
- Drag to rotate, Shift-drag/right-drag or two-finger drag to pan, and pinch or
  wheel to zoom. **Focus object** frames the selected marker. **System** changes
  the reference center to the selected catalog object, switches to its local
  scope, and requests new governed relative states and paths. Its initial camera
  fit continues as local satellite states and paths arrive, enclosing all
  displayed resolved trajectory points with viewport-aware padding. Once those
  local requests settle, the camera stops refitting; any user camera gesture
  cancels a pending initial fit. When already centered, System frames that
  local family. Fit scene frames the visible objects and any selected sampled path.
- Select in the catalog or click a point. Expand **Exact state + provenance +
  catalog record** for physical km/km/s, identity, identifiers, parent, epoch,
  frame, navigation grade, uncertainty, coverage, source lineage and hashes.
  Uncertainty not provided by authority remains NULL, never zero.
- Choose a system and then a reference center. Local scope includes its
  database-linked family plus the selected object. The Earth/Moon group is an
  explicit presentation association: the current database's Moon parent is
  NULL and is not rewritten. Both Earth and Moon can be inspected relative to
  the governed Earth/Moon barycenter, or Moon relative to Earth.
  Reference-center subtraction uses child and center states at identical epochs
  and frames, including velocity. The original absolute state remains intact.
- Scope selection applies display presets. Solar enables Sun, planets and their
  paths. Local enables the selected primary and its governed physical family,
  including satellites and local paths. Whole Catalog enables all physical
  classes and their applicable paths, including spacecraft and interstellar
  objects. The explicit **Barycenters** layer is OFF in every preset; enabling
  it adds their markers and labels without changing their computational role.
  Manual layer changes persist until another scope is entered.
- Automatic bound-object paths begin at the selected T0 and attempt one future
  revolution relative to the governed primary/reference center. The server
  measures phase from successive resolver states to select a display horizon;
  it never generates an orbit or claims that measured phase as new authority.
  Open spacecraft/interstellar paths request one Julian Earth year. Bound paths
  still incomplete at the configured maximum are labeled
  `MAX_HORIZON_TRUNCATED`. Unresolved/ambiguous phase is labeled explicitly.
  The **Automatic trajectory horizons and coverage** panel lists each requested
  interval, its orbital reference, status, gap epochs and source-seam brackets.
  Missing state never becomes a display segment.
- Whole Catalog progressively requests every renderable physical-object path.
  Its label and marker LOD keeps the overview legible; automatic moon/minor
  paths appear as zoom permits. Selected paths remain visible. Cached resolver
  samples are reused at the same T0, center and body. Play requests no path per
  frame; pausing at a new T0 may request new paths.
- Labels use deterministic priority: selection, Sun/planets, local moons,
  spacecraft/dwarf planets, then other bodies. Zoom bands and a viewport label
  budget admit lower-priority labels progressively; collision resolution uses
  that order and body ID for stable ties. These are display choices only.
- Select an object, set trajectory start/end and 2–512 nominal samples, then
  **Sample resolver**. Suggested checks: Earth over one year, Moon relative to
  Earth over a month, New Horizons or Voyager over 2026–2250, and Oumuamua over
  the same interval. No Kepler ellipse or closing segment is generated. Automatic
  paths use duration-responsive nominal samples and refine curved intervals at
  resolver-evaluated midpoints, bounded at 512 samples. Manual sampling remains
  an inspection choice, not new authority.
- Direct paths are solid; propagated paths are dashed and labeled. Rings and
  expandable seam records expose before/after states and source provenance,
  including center-source transitions. Boundary-adjacent samples are added to
  the requested sample grid. Time brackets describe the sampled transition;
  they are not an invented exact physical discontinuity. Missing states split
  the geometry, even when the source on either side is unchanged.
- PHYSICAL converts km to AU for rendering and rotates axes to Y-up; it
  preserves relative distances. SCHEMATIC applies radial `log1p(100*r_AU)` only
  to display geometry and says **NOT TO SCALE · VISUAL COMPRESSION**. Markers
  are enlarged in both modes. Changing mode does not change exact state data.
- The failure panel always contains every unresolved catalog object, even if
  it is outside the current local view. Catalog = resolved + unresolved;
  resolved = direct + propagated. Scene eligible + scope/layer-hidden = renderable;
  marker/label LOD may hide some scene-eligible objects at distance.
  An unresolved reference center can reduce renderable below resolved; each
  affected record includes its presentation failure. Partial and catalog-only
  counts are catalog subsets, not additional objects.

## Authority boundary

`loom_solar_postgres.py` reads all six current Solar tables in one snapshot and
constructs `SolarEphemerisRegistry` with numeric SPICE ET bounds. It checks
every coverage row against the pinned ET overlay before startup. The Solar
resolver and `SpiceEphemerisAdapter` receive numeric ET and pass it unchanged
to `spkgeo(target, et, 'ECLIPJ2000', 10)`. The Solar state frame label is now
exactly `ECLIPJ2000`; the historical generic `J2000/ECLIPTIC` label was an
alias, not a coordinate rotation. Position remains km and velocity km/s.

Migration 020 adds `coverage_start_et` and `coverage_end_et` to the PostgreSQL
coverage table without deleting UTC labels or changing row status, membership,
source identity, or physical vectors. `tools/build_solar_et_coverage.py` read
the qualified ledger and verified each primary SPK hash and target `spkcov`
window. The static overlay records native ET windows, the selected ET interval,
the primary SPK hash and a derivation method for all 123 rows. Most intervals
use exact native endpoints. Five rows use the intersection with their narrower
historical qualification limit; the old UTC projection and pinned LSK hash are
retained as provenance. Selection compares only numeric ET. Target coverage
and selected-source segment ownership are still checked again at evaluation.

PostgreSQL owns membership, canonical names/classes, identifiers, parent and
mission metadata, source status/capability, uncertainty, source lineage and
coverage. The five existing operational manifests provide local kernel paths
and their ordered dependency closures. Shared immutable source identity
(source ID, provider, product version, filename, SHA-256 and byte count) and
active external identifiers must agree or startup fails closed. Duplicate
manifest asset recipes must agree too. Files are hash-verified by the existing
adapter before use. Retired sources without a local recipe cannot be selected.

Historical manifest display labels, acquisition timestamps and qualification
defaults are not copied over the current ledger. For example, the spacecraft
product display names differ in capitalization/spacing and older SAT441
manifest qualification defaults predate the current ledger. These are distinct
from immutable source/product version and asset identity, which are checked.

The source-isolation correction evaluates only the already-selected closure,
under a shared adapter lock, and verifies that the target SPK segment is from
the selected primary asset. Previously furnished top-level kernels are restored
on success or failure. This does not alter precedence, models or coverage.
The adapter must not run alongside unmanaged concurrent SPICE calls or depend
on manually injected, unfurnished kernel-pool variables. The local inspector
accepts concurrent HTTP requests so static resources and control responses do
not queue behind trajectory work; governed SPICE evaluations retain the shared
adapter lock and selected-source isolation.

The bounded in-memory caches (8 full and 8 compact snapshots, 16 paths, 8192
state records) are disposable presentation data. Stable ledger metadata is
projected once at startup and reused across trajectory samples. The compact
scene/path HTTP views omit repeated detail while preserving the existing full
state and trajectory endpoints for provenance inspection. No trajectory/state
cache is written to the database. No legacy Solar GIS code, orbit models or
SQLite state is imported.

## Compatibility, checks and recovery

Solar resolver and Inspector interface: `CHANGED`; numeric ET is canonical and
the authoritative frame string is `ECLIPJ2000`. Shared `SpatialState` gains an
optional `epoch_et` field; its other consumers retain their existing UTC and
generic-frame contracts. PostgreSQL coverage schema: `ADDITIVE_MIGRATION_020`;
the new code fails closed against an unmigrated ledger. The five source recipe
manifests remain unchanged; the new ET overlay is a scoped additive artifact.
Existing launchers, canon, legacy GIS and Wayfarer are not migrated by this
Inspector change. Production database promotion is separate from this PR's
disposable qualification.

See [qualification evidence](qualification/SOLAR_INSPECTOR_V01_QUALIFICATION.md)
for commands, observed cases, endpoint limitations and results.
Recovery is to stop this optional server and return to the prior code while
retaining the additive ET columns and provenance. Reverting the code would
reintroduce the prior UTC time-selection defect, so the migration and code
should be promoted together only after governed review.

Phase 5, CIVPROP/CIVSTATE, Atlas/Navigator integration, textures, decorative
belts, screenshot/export features, packaging, production infrastructure and
public deployment are outside v0.1 and were not entered. The screenshots made
during qualification are test artifacts only, not an added product feature.
