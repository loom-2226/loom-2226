# LOOM 2226 — Earth–Luna Spatial Infrastructure Recovery & Gap v0.1

**Date:** 2026-09-12  
**Status:** ENGINEERING RECOVERY / NON-CANON  
**Primary change class:** `class:runtime` (this document records the engineering basis)  
**Workstream:** child lane of the active HUD / Navigator workstream; no new top-level autonomous or research stream  
**Base:** `feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11` at `17286037c429f4acbf26ee1a544a9a147c8b063a`

## 1. Recovery result

| Recovered object / rule | Disposition | Reason |
|---|---|---|
| `SpatialState` in `src/loom/application/contracts.py` | **REUSE** | Already the typed cross-application physical-state contract. |
| `HybridCelestialStateService` / `ParentCentricOrbitModel` / `propagate_parent_centric` | **REUSE** | Existing deterministic parent-centric Kepler propagation with provenance and fail-closed semantics. |
| `SQLiteCelestialCatalog` | **REUSE** | Existing read-only bridge to nav-grade celestial states and authoritative parent GM. |
| `SpatialRuntime` | **REUSE** | Existing deterministic inertial frame-graph traversal. |
| `SpatialFrame` rotating/body-fixed support | **EXTEND LATER** | Current implementation explicitly forbids non-inertial/body-fixed transforms until an orientation model is authorized. |
| `LegacySequenceHEphemerisProvider` | **REUSE / ADAPTER BOUNDARY** | Preserves Navigator ephemeris authority; do not create a second ephemeris solver. |
| Earth/Moon IDs `EA` / `LU` in the direct Horizons acquisition tool | **REUSE** | Existing live HUD qualification lineage uses these identifiers. |
| J2000/ECLIPTIC canonical celestial frame | **REUSE** | Existing spatial service standard. |
| HUD Earth orbital diagnostics | **HISTORICAL/DIAGNOSTIC ONLY** | Useful qualification logic, but target resolution must not duplicate HUD-local orbital physics. |
| Earth–Moon HUD flight-command contracts | **REUSE AT HANDOFF ONLY** | Infrastructure supplies target state; deterministic flight-control remains a separate authority. |
| Canon Atlas Earth–Luna transport hierarchy | **REUSE** | Supports dense cislunar infrastructure qualitatively and requires PORT / ROADSTEAD / TRAFFIC BOUNDARY / CERTIFICATION VOLUME to remain distinct. |
| Named Earth orbital stations | **UNKNOWN / NOT RECOVERED** | No governed named station recovered from current repository search. |
| Named lunar orbital stations | **UNKNOWN / NOT RECOVERED** | No governed named station recovered from current repository search. |
| 2226 Earth ground-port coordinates | **UNKNOWN / NOT RECOVERED** | No governed 2226 latitude/longitude catalog recovered. Contemporary survival cannot be assumed. |
| 2226 lunar surface-port coordinates | **UNKNOWN / NOT RECOVERED** | No governed surface-port coordinate catalog recovered. |
| Body-fixed → inertial transform | **CONFLICT if faked / GAP if absent** | Existing frame code intentionally rejects rotating frames. Surface targets must fail closed for inertial state until orientation is implemented. |
| Static Lagrange/NRHO point model | **UNAVAILABLE** | No CR3BP/periodic-family resolver recovered; do not label these as static orbital states. |

## 2. Authority boundaries preserved

1. Python owns physical target state and target resolution.
2. HUD, GIS, Mara/LLM and NPC clients consume the same resolved state.
3. No client receives permission to manufacture coordinates, state vectors, remass, feasibility or arrival state.
4. Existing celestial ephemeris and gravity-property sources remain authoritative inputs.
5. No Earth/Moon GM is duplicated in the new target layer.
6. No canon file or CIVSTATE database is mutated by this slice.

## 3. Gap analysis

### Already earned

- typed physical state (`SpatialState`);
- Earth/Moon stable identifiers (`EA`, `LU`);
- `J2000/ECLIPTIC` state convention;
- exact/direct celestial-state lookup and propagated satellite fallback;
- parent-centric two-body Kepler propagation;
- read-only GM retrieval from existing celestial catalogs;
- deterministic inertial frame translation;
- live Earth–Moon qualification ephemeris acquisition/interpolation;
- rendezvous/flight HUD qualification and shared command architecture.

### Missing for this lane

- target metadata contract above `SpatialState`;
- standard-orbit catalog;
- orbital-station catalog;
- target resolver joining named target → physical state at epoch;
- governed 2226 Earth and lunar port records;
- body-orientation/body-fixed transform service;
- periodic-family/CR3BP resolver for NRHO/Lagrange families;
- Navigator adapter accepting target IDs instead of only legacy body/location tokens;
- traffic/docking state, which is deliberately deferred.

## 4. Smallest honest Earth–Luna sandbox set

The first executable slice is intentionally orbital-first:

```text
EA (Earth body state)
  ↓
EARTH_LEO_400_REFERENCE
  ↓
EARTH_STATION_QUAL_01       [NON-CANON qualification fixture]
  ↓
LU (Moon body state / Earth-relative ephemeris)
  ↓
LUNA_LLO_100_REFERENCE
  ↓
LUNA_STATION_QUAL_01        [NON-CANON qualification fixture]
```

The two station objects are **qualification fixtures**, not fictional canon. They exist only to exercise phasing, rendezvous, approach and the shared resolver before governed station names/operators/roles are promoted.

Surface endpoints are represented by contract capability, but **no 2226 port coordinates are fabricated**. Until both a governed port catalog and body-fixed orientation model exist, `GROUND_PORT` and `SURFACE_PORT` inertial resolution returns an explicit unavailable error. Navigator should terminate surface requests at a physically valid orbital/pre-descent boundary in this state.

## 5. Initial standard-orbit policy

The runtime may carry engineering-reference orbit targets without promoting them to canon. Each record declares:

- target/status/provenance;
- central body;
- representation;
- element epoch and phase rule;
- altitude or periapsis/apoapsis where applicable;
- inclination/eccentricity/orientation fields;
- navigation and operational roles.

The V0.1 executable catalog should remain small and useful. NRHO, halo and Lagrange-family records are excluded from resolvable targets until a periodic-family/CR3BP model exists.

## 6. Implementation seam

Introduce a presentation-agnostic `LOOM_SPATIAL_TARGET_V1` metadata contract and `SpatialTargetResolver` under `src/loom/spatial/`.

The resolver will:

1. look up a named target;
2. obtain the central-body state at the requested epoch from the existing celestial-state service;
3. obtain body radius and GM through injected authoritative property accessors;
4. construct a `ParentCentricOrbitModel` for standard-orbit/station targets;
5. call the existing `propagate_parent_centric()` implementation;
6. compose relative state with the central-body inertial state;
7. return the existing `SpatialState` with target provenance preserved.

Surface targets fail closed until a body-fixed resolver is supplied. No alternate orbital propagator is introduced.

## 7. Test gate

Required V0.1 tests:

- circular Earth reference orbit;
- circular lunar reference orbit;
- station phase/state remains on its declared orbit;
- station velocity is non-zero and physically consistent;
- resolver determinism for fixed epoch/input;
- provenance survives resolution;
- unknown/missing target data fails closed;
- no station defaults to body center;
- ground/surface port resolution fails closed without body orientation;
- manual/LLM/NPC/System consumers receive identical target state;
- no new Earth/Moon GM constants are introduced.

Full production E2E remains outside this child slice; exact-head unit/functional regression is required before declaring the slice complete.
