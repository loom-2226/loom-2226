# Solar emergence v0 — corrective Run 1

**Class:** `class:engineering`. **Status:** fictional, non-canon, non-production experiment. Governing plan: [`research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md`](../../research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md). Baseline main SHA: `fbc3818648cd9cdf54629281f52b5eb928b4f877`.

The only world database input is repository-tracked `data/LOOM_2226.sqlite3`, SHA-256 `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`. This matches `manifests/release_manifest.json` and `manifests/current/LOOM_COMPATIBILITY.yml`. The builder opens it with SQLite `mode=ro`, `immutable=1`, and `query_only=ON`; it checks the release-manifest hash before writing experimental JSON. It does not write the database or shared runtime files.

## Registry rule and boundary

Include an `entities` row whose `entity_class` belongs to the explicit Solar scene celestial taxonomy (`STAR`, `PLANET`, `SYSTEM_BARYCENTER`, `DWARF_PLANET`, `ASTEROID`, `MOON`) and whose registration has a `source_command`, or whose class is `STAR` and provenance is `HELIOCENTRIC_ORIGIN`. Require parent identity for every non-star entry. Cross-check the resulting IDs, names, classes and parents against `src/loom_solar_gis.py`'s `EXPECTED_IDS` and seed definitions; fail generation if they disagree. This is a **bounded explicit registry backed by two agreeing sources**, because the repository has no separate single ephemeris-body registry table. Each catalog row carries entity provenance, materialization status, direct-state capability, probed propagation-model capability, and Navigator acquisition evidence where present.

The first Run 1 used `DISTINCT ephemeris_states.entity_id`, yielding 48 IDs. That table contains materialized state rows, not all registered bodies. The corrected catalog has 49: the same 48 plus `SOL`, the Sun and heliocentric reference origin. The 49 are 10 asteroids, 1 dwarf planet, 28 moons, 4 planets, 5 system barycenters and 1 star. Every stored ephemeris ID is covered. `SOL` has a qualified direct origin state in `states` but no `ephemeris_states` row or parent-centric propagation model. Registration does not itself imply navigation grade or state availability.

`body_registry_audit.json` gives per-ID source flags and evidence. Source roles are distinct: `entities` and Solar scene seed definitions register celestial identities; `ephemeris_states`, `states` and `orbit_snapshots` materialize states; `celestial_dynamics` and `celestial_properties` provide partial dynamics/physical inputs; the SQLite celestial provider determines qualified direct-state and anchor-model capability. The Solar scene has explicit acquisition commands for the 48 non-origin objects and approximate display fallback parameters for 28 moons. Its 12 moons without qualified direct states can use only that display fallback in the checked-in scene. Navigator's 11 macro targets and 34 planned acquisition requests are narrower routing/acquisition vocabulary, not a full body registry. `orbit_geometry_models`, `spatial_states` and `entity_location_models` contain infrastructure IDs. `body_zone_census` is a name-based worldbuilding census: names such as Eris, Haumea and Makemake have no corresponding registered ephemeris IDs here, so they are not silently promoted. No larger explicit LOOM ephemeris registry was found in the audited sources; the boundary remains the current Solar scene and checked-in world database, not all objects that an external ephemeris service could theoretically query.

## Opportunity semantics

- `candidate_role` separates 43 physical bodies from one stellar reference body and five system barycenters. Membership is independent of facility-host suitability.
- `surface_possible` and `orbital_possible` are broad **experimental structural body-class priors** from `parameters.json`. For `STAR` and `SYSTEM_BARYCENTER`, the surface flag is false and orbital possibility is unresolved (`null`). These flags do not assert engineering feasibility or canon importance.
- `surface_gravity` is derived only for a physical body with the surface class prior and positive finite GM and mean radius in a `celestial_properties` row marked `ENGINEERING_REFERENCE_NONCANON` / `REFERENCE_PHYSICAL_CONSTANTS_v0.1`. Formula: `1000 × gm_km3_s2 / mean_radius_km²`, in m/s². The field records input values, units, status and formula. The reference constants are engineering inputs, not canon.
- Radiation, thermal, solar-energy and material/resource potentials lack qualified Run-1 inputs. They remain JSON `null`; null means unknown, never zero. Missing or unsupported gravity also remains null.

The semantic dossier marks core celestial tables unresolved in general. The provider promotion contract qualifies the direct-state seam; `engineering/experience_one/qualification/e1_geometric_admissibility_inventory.py` identifies the GM/radius unit-bearing reference fields. We deliberately do not interpret `celestial_dynamics.atmosphere_class`, `reference_orbit_radius_km`, name-only census labels, or state coordinates as resource/environment capacity.

## Reproduce

From this directory:

```bash
python3 -B body_opportunities.py
python3 -B -m unittest -v test_body_opportunities.py
```

The builder writes `body_registry_audit.json`, `body_catalog.json` and `body_opportunities.json` in stable body-ID order with deterministic JSON serialization. Running it twice with unchanged inputs produces byte-identical files. Run 1 stops here: no accessibility, route, investment, construction, facility, migration or body-state propagation engine exists in this experiment.
