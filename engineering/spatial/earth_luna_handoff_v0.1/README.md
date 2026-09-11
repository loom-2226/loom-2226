# Earth–Luna Spatial Handoff v0.1

**Status:** ENGINEERING HANDOFF / NON-CANON  
**Contract:** `LOOM_SPATIAL_TARGET_V1` metadata + existing `SpatialState` physical state  
**Consumers:** HUD, Navigator, Mara/LLM intent adapters, NPC/autonomy, traffic simulation

## What this package gives consumers

The V0.1 target layer separates **what a destination is** from **where it is at a requested epoch**.

```text
named target
    ↓
SpatialTargetCatalog
    ↓
SpatialTargetResolver.resolve_target_state(target_id, epoch_utc)
    ↓
existing celestial body state + existing body properties
    ↓
existing propagate_parent_centric() orbital physics
    ↓
SpatialState
```

No static inertial `x/y/z` is stored for an orbit or station.

## Files

- `src/loom/spatial/catalogs/earth_luna_v0.1.json` — target catalog, including standard orbit references, qualification stations and explicit unsupported/deferred target classes.
- `src/loom/spatial/targets.py` — typed catalog objects and deterministic resolver.
- `tests/test_spatial_targets.py` — unit/functional contract tests.
- `engineering/spatial/LOOM_2226_Earth_Luna_Spatial_Infrastructure_Recovery_and_Gap_v0.1.md` — recovery/gap authority record.
- `engineering/spatial/earth_luna_handoff_v0.1/manifest.json` — package/status manifest.
- `engineering/spatial/earth_luna_handoff_v0.1/example_resolved_states.json` — fixed qualification examples, explicitly not celestial/canon truth.

## Consumer operations

These are semantic operations, not direct mutation APIs.

### `LIST_TARGETS`

Call `SpatialTargetCatalog.list_targets()` and filter by `target_type` or `resolvable_only`.

### `DESCRIBE_TARGET`

Call `SpatialTargetResolver.describe_target(target_id)`.

Returns target identity, type, parent body, status, state availability, state method, navigation grade, provenance and operational metadata. It does **not** manufacture a state vector.

### `RESOLVE_TARGET_STATE`

Call:

```python
state = resolver.resolve_target_state(target_id, epoch_utc)
```

Returns existing `SpatialState`:

```text
entity_id
 epoch_utc
 reference_frame
 position_km
 velocity_km_s
 provenance
 navigation_grade
 uncertainty
 payload
```

For V0.1 standard orbits and qualification stations, state is derived through the existing parent-centric Kepler implementation and an injected authoritative central-body state/property source.

### `PLAN_RENDEZVOUS`

Semantic flow only in this slice:

```text
request target_id
  → RESOLVE_TARGET_STATE(target_id, planning_epoch)
  → Navigator / rendezvous planner
  → LOOM_MANEUVER_PLAN_V1
  → review / deterministic execution boundary
```

The target resolver does not solve rendezvous and does not mutate ship state.

### `PLAN_TRANSFER`

Semantic flow only in this slice:

```text
origin SpatialState + destination target_id + constraints
  → RESOLVE_TARGET_STATE
  → existing Navigator planning authority
  → typed plan
```

Legacy body/location-token Navigator behavior is not replaced here. A later adapter can translate target IDs into the same planner boundary after the local target/end-state contract is reviewed.

## Standard orbit policy

`REFERENCE` means a useful engineering/navigation reference, not a canon claim that the altitude is uniquely optimal or dominant in 2226.

The V0.1 catalog resolves only target classes the current two-body spatial layer can represent honestly. It deliberately marks the following unavailable rather than faking them:

- sun-synchronous-like reference requiring perturbation/precession behavior;
- true GEO requiring Earth orientation/rotation and longitude phase;
- HEO geometry before a specific reference is governed;
- Earth–Moon transfer staging before Navigator selects the architecture;
- escape/departure boundary before Navigator defines it;
- NRHO/periodic families before CR3BP/periodic-family support.

## Orbital stations

No governed named 2226 Earth/Lunar orbital station was recovered. Therefore V0.1 contains only:

- `EARTH_STATION_QUAL_01`
- `LUNA_STATION_QUAL_01`

Both are `NON_CANON` qualification fixtures used to exercise phasing, moving-target resolution and rendezvous. Operator, population, services and ownership are not invented.

## Surface ports

The V0.1 Earth ground-port and lunar surface-port arrays are intentionally empty.

Two independent gates are missing:

1. governed 2226 port coordinates/identities;
2. authoritative body orientation / body-fixed → inertial transforms.

Current `SpatialFrame` explicitly rejects rotating/body-fixed transforms. Therefore a surface request must stop at a valid orbital/pre-descent boundary and report the surface state as unavailable. Unknown is not zero; latitude/longitude is not an inertial coordinate.

## Navigator integration boundary

Do not embed this catalog in prompts or JavaScript. Navigator/HUD should receive a target ID and call the Python resolver.

V0.1 deliberately does **not** modify legacy Navigator route solving. The safe next adapter is:

```text
NavigationTargetRequest
    origin_state
    target_id
    planning_epoch
    arrival_constraints
        ↓
SpatialTargetResolver
        ↓
resolved target SpatialState
        ↓
existing Navigator / local rendezvous planner
```

For orbital stations the eventual arrival constraints must include relative position/velocity and approach/docking geometry. For surface targets Navigator must fail closed at the pre-descent/pre-ascent boundary until landing/ascent physics is earned.

## Authority rule for LLM/Mara

Mara may:

- list and describe targets;
- identify a `target_id` from player intent;
- ask the resolver for state;
- ask Navigator for a plan;
- explain the returned plan;
- request review/execution through the typed command boundary.

Mara may not:

- write coordinates;
- invent an orbit phase;
- fabricate a station/port location;
- make an unavailable surface target resolvable;
- promote a qualification fixture into canon;
- bypass Navigator or deterministic flight control.

## V0.1 playable chain

Today the honest resolved chain is:

```text
Earth body
  → Earth parking/reference orbit
  → Earth qualification station
  → cislunar transfer planning boundary
  → Lunar qualification station
  → lunar parking/reference orbit
  → PRE-DESCENT BOUNDARY
```

The requested ground-port → surface-port end-to-end chain remains intentionally incomplete until the two surface gates above are closed.
