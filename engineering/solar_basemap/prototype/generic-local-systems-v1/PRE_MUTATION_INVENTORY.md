# Solar basemap generic local-system inventory v1

**Primary change class:** `class:runtime`  
**Parent:** PR #320 at `3af7eb8af68dfe68d45d0605e525acb9490c8a44`  
**Inventory state:** captured before compiler, product, schema, or client changes  
**Catalog epoch:** ET `7131844800.0`, `2226 JAN 01 00:00:00.000 TDB`  
**Frame / center / units:** ECLIPJ2000 / SUN / km

## Method and authority inputs

Candidates were grouped only from `NATURAL_SATELLITE.parent_body_id` in the
qualified 110-identity Solar catalog snapshot, plus the inherited qualified
Moon-to-Earth product relationship explicitly recorded in the current
generation contract. A parent barycenter is retained as the product anchor
when that is the governed parent ID. No nearby body or familiar primary was
inferred. The inventory is not a geometry-generation verdict: each curve still
requires successful resolver, source hash, coverage, epoch, and horizon checks.

Inputs:

- `engineering/solar_basemap/evidence/catalog_2226_snapshot.json`, authority
  ledger digest `fd0784e9fdcaea22d9e8e8b8c93b6ca5db8e6cd84ce293be1bdf4310c8db23a7`
- `manifests/solar/SOLAR_NATIVE_ET_COVERAGE_V1.json`
- Qualified baseline publication `d9d4b4082049a979eabacac0fec400122f0ed3278d33b99f76758e8d2a003a4f`
- `engineering/solar_basemap/AUTHORITY_PROVENANCE.md` and
  `engineering/solar_basemap/PRODUCT_CONTRACT.md`

## Candidate classification

| Governed anchor / parent | Members from governed relationships | Classification | Source / identity disposition |
|---|---|---|---|
| `EARTH` (inherited contract exception) | Moon | `QUALIFIED_SOURCE_AVAILABLE` | Existing product contract and validated Moon/Earth curve; catalog parent is null, so no new relationship is inferred. |
| `MARS_SYSTEM_BARYCENTER` | Phobos, Deimos | `QUALIFIED_SOURCE_AVAILABLE` | Both resolve with qualified `JPL_MAR099`; parent ID remains the node anchor for this generic successor. |
| `JUPITER_SYSTEM_BARYCENTER` | Io, Europa, Ganymede, Callisto | `QUALIFIED_SOURCE_AVAILABLE` | Four resolved members with qualified propagated Phase 4B sources covering the pinned epoch. |
| `SATURN_SYSTEM_BARYCENTER` | Mimas, Enceladus, Tethys, Dione, Rhea, Titan, Hyperion, Iapetus, Phoebe | `QUALIFIED_SOURCE_AVAILABLE` | Nine resolved members with qualified `JPL_SAT441XL_PART2` epoch coverage. |
| `URANUS_SYSTEM_BARYCENTER` | Miranda, Ariel, Umbriel, Titania, Oberon | `QUALIFIED_SOURCE_AVAILABLE` | Five resolved members with qualified `JPL_URA184_PART_3` epoch coverage. |
| `NEPTUNE_SYSTEM_BARYCENTER` | Triton, Nereid, Proteus | `QUALIFIED_SOURCE_AVAILABLE` | Triton (`JPL_NEP097`) and Nereid (`NAIF_NEP101XL_802`) resolve at T. Proteus source coverage ends at ET `6311304000`, before T; record as `MISSING_REQUIRED_SOURCE`. |
| `PLUTO_SYSTEM_BARYCENTER` | Charon | `QUALIFIED_SOURCE_AVAILABLE` | Charon and parent have qualified propagated Phase 4B sources at T. |
| `PLUTO` | Nix, Hydra, Kerberos, Styx | `MISSING_REQUIRED_SOURCE` | Governed identities and parent links exist, but all four are unresolved at T for absent qualified source coverage. |
| `IDA` | Dactyl | `UNRESOLVED_IDENTITY` | Dactyl does not have exactly one active governed identifier. |
| `DINKINESH` | Selam | `UNRESOLVED_IDENTITY` | Selam does not have exactly one active governed identifier. |

No candidate family is classified `GOVERNED_POSITION_ONLY` or
`OUT_OF_SCOPE_BY_CONTRACT` in this inventory. This does not suppress those
statuses from the product contract: the generic inventory must retain them if
future governed source rows create such cases. Proteus and Pluto's minor moons
remain visible missing coverage; their curves must not be synthesized.

## Human physical acceptance inherited

`MARS_PHYSICAL_PIXEL_PASS` is accepted for PR #320. The passed behavior covers
continuous Solar-to-Mars-to-Phobos/Deimos navigation; map pan; controlled focal
pinch; selection/focus; yaw and pitch oblique orientation; parent/local
refinement; fine Solar LOD; truthful scale; subdued Navigator-derived
cartography; and no user-facing reference-system switching. This successor
preserves that accepted client behavior. PR #320's historical qualification
record is left unchanged.

## Architecture preflight

The read-only `loom-preflight` found that the pre-successor compiler and
contract pin twelve curves by name, and that local `subtree_bound` calculations
include distant requested bodies from other systems. The generic implementation
must derive curves from the governed relationships above, explicitly qualify
omissions, and compute bounds from each node's actual content and descendants.
The initial falsification slice is Jupiter/Io plus an explicit missing-source
record for Proteus; all remaining qualified families are required after this
generic path passes deterministic source, product, and touch-path qualification.
