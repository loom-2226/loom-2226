# Solar Ephemeris Inspector v0.1

Primary change class: `class:runtime`. Bounded Phase-4 qualification instrument,
authorized by Kevin, including the subsequent explicit authorization to correct
SPICE source contamination. Representation consumes empirical authority; it
does not establish new canon, membership, products, coverage, or scientific models.

## Launch locally

Requires Python, PostgreSQL `psql` access to the governed `loom_solar` ledger
through migration 019, and the already-qualified local Solar asset collection.
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
`--database`, `--asset-root`, and `--three-js` are the only configuration flags.
Libpq connection settings and credentials follow normal `psql` conventions.
The fixed query uses `REPEATABLE READ READ ONLY`, a statement timeout, and no
interpolated SQL. It works with SELECT-only credentials.

Three.js uses the existing Wayfarer classic r149 pattern, without a frontend
framework. Its MIT-licensed setup asset is local and SHA-256 pinned to
`8a5f7249903b54d30f79f708699d2fed2d6a1d0741a4cd41377d1f01bb5a2271`.
No CDN or external ephemeris request occurs at runtime. The setup download is
optional if those exact bytes are already installed. No paid/hosted service,
AI inference, telemetry, or external data transmission is introduced.

Initial evaluation hashes the local kernels (about 14 GB on this host) and can
take roughly a minute on cold storage. Later requests reuse verified assets.
Restart the inspector to reload the database snapshot or changed assets.

## Inspect

- Choose arbitrary timezone-qualified UTC input or the 2026/2226/2250 shortcuts.
  Step days, backward/forward, and play/pause evaluate exact resolver states.
  Play waits for each response; no SPICE evaluation runs per browser frame.
- Drag to rotate, Shift-drag/right-drag to pan, wheel to zoom. Fit scene frames
  the visible objects and any selected sampled path.
- Select in the catalog or click a point. Expand **Exact state + provenance +
  catalog record** for physical km/km/s, identity, identifiers, parent, epoch,
  frame, navigation grade, uncertainty, coverage, source lineage and hashes.
  Uncertainty not provided by authority remains NULL, never zero.
- Choose a reference center. Local scope includes its database-linked family
  plus the selected object. For Earth/Moon, choose Earth then select Moon: the
  current database's Moon parent is NULL and is deliberately not invented.
  Reference-center subtraction uses child and center states at identical epochs
  and frames, including velocity. The original absolute state remains intact.
- Select an object, set trajectory start/end and 2–512 nominal samples, then
  **Sample resolver**. Suggested checks: Earth over one year, Moon relative to
  Earth over a month, New Horizons or Voyager over 2026–2250, and Oumuamua over
  the same interval. No orbital periods, Kepler ellipses, or closing segments
  are inferred. Sampling density is an inspection choice, not new authority.
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
  resolved = direct + propagated. Rendered + scope-hidden = renderable.
  An unresolved reference center can reduce renderable below resolved; each
  affected record includes its presentation failure. Partial and catalog-only
  counts are catalog subsets, not additional objects.

## Authority boundary

`loom_solar_postgres.py` reads all six current Solar tables in one snapshot and
constructs the existing `SolarEphemerisRegistry`, consumed unchanged by
`SpiceEphemerisAdapter` and `HybridCelestialStateService`.

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
uses a single request thread and governed assets exclusively.

The bounded in-memory caches (8 snapshots, 16 paths, 8192 state records) are
disposable presentation data. No trajectory/state cache is written to the
database. No legacy Solar GIS code, orbit models or SQLite state is imported.

## Compatibility, checks and recovery

Existing resolver API and SpatialState fields: `UNCHANGED_COMPATIBLE`.
Solar source evaluation: `REVALIDATION_REQUIRED`, completed by the relevant
Phase-4 tests and new contamination regressions. The inspector is a new local
consumer. Existing launchers, release manifests, databases, canon, legacy GIS,
Wayfarer and other consumers have no interface/schema changes. The coarse
dependency registry was inspected; no independence claim is inferred from
unregistered inspector edges.

See [qualification evidence](qualification/SOLAR_INSPECTOR_V01_QUALIFICATION.md)
for commands, observed cases, endpoint limitations and results.
Recovery is to stop this optional server and revert the PR's code changes;
there is no database rollback or data migration. Reverting the resolver fix
would reintroduce the documented contamination defect.

Phase 5, CIVPROP/CIVSTATE, Atlas/Navigator integration, textures, decorative
belts, screenshot/export features, packaging, production infrastructure and
public deployment are outside v0.1 and were not entered. The screenshots made
during qualification are test artifacts only, not an added product feature.
