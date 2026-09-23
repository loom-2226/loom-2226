# Solar emergence v0 — Run 1

**Class:** `class:engineering`. **Status:** fictional, non-canon, non-production experiment. Governing plan: [`research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md`](../../research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md). Baseline main SHA: `fbc3818648cd9cdf54629281f52b5eb928b4f877`.

The only world input is repository-tracked `data/LOOM_2226.sqlite3`, SHA-256 `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`, matching `manifests/release_manifest.json` and `manifests/current/LOOM_COMPATIBILITY.yml`. The builder opens it with SQLite `mode=ro`, `immutable=1`, and `query_only=ON`; it checks the release-manifest hash before writing experimental JSON. No database or shared runtime file is written.

## Exact inclusion rule

The current repository has no separate single body-registry table. The smallest adapter over its ephemeris authority includes **every distinct `ephemeris_states.entity_id` that joins to `entities.entity_id`, with no navigation-grade or status filter**. One catalog row is emitted per ID. Missing entity registration fails generation. This preserves display-grade ephemeris bodies as candidates without promoting their state to navigation authority. `states` is not the registry: it also contains non-body entities. The current 48 ephemeris IDs match the 48 `celestial_dynamics` IDs, but dynamics is not an added eligibility gate. The 48 rows are 10 asteroids, 1 dwarf planet, 28 moons, 4 planets and 5 system barycenters. Each catalog entry records its entity identity, class, parent, source provenance and latest ephemeris row status/grade, explaining why the body was included.

## Opportunity semantics

- `body_id` and `body_class` are copied from the registered entity and ephemeris join. The catalog's source and grade fields describe stored ephemeris evidence; display-grade is not navigation-grade.
- `surface_gravity` is derived only for a body with a surface-eligible class prior and positive finite GM and mean radius in one `celestial_properties` row marked `ENGINEERING_REFERENCE_NONCANON` / `REFERENCE_PHYSICAL_CONSTANTS_v0.1`. Formula: `1000 × gm_km3_s2 / mean_radius_km²`, in m/s². The field carries its source values and formula. The reference constants are engineering inputs, not canon or a general physical suitability verdict.
- `surface_possible` and `orbital_possible` are broad **experimental body-class test priors** from `parameters.json`, not observations. The system-barycenter prior has no surface and leaves orbital possibility unresolved. No individual body receives a bonus or attractiveness score.
- Radiation, thermal, solar-energy and material/resource potentials have no qualified Run-1 input. They remain JSON `null`; null means unknown, never zero. A missing/unsupported gravity source also remains null.

The semantic dossier marks core celestial tables unresolved in general. `src/loom_sqlite_celestial_provider.py` and its promotion contract qualify the `ephemeris_states` identity/grade seam; `engineering/experience_one/qualification/e1_geometric_admissibility_inventory.py` identifies the GM/radius unit-bearing reference fields. We deliberately do not interpret `celestial_dynamics.atmosphere_class`, `reference_orbit_radius_km`, the ephemeris state as a physical capacity, or any resource/environment label from column names.

## Reproduce

From this directory:

```bash
python3 -B body_opportunities.py
python3 -B -m unittest -v test_body_opportunities.py
```

The builder writes `body_catalog.json` and `body_opportunities.json` in stable body-ID order with deterministic JSON serialization. Running it twice with unchanged inputs produces byte-identical files. Run 1 stops here: no accessibility, route, investment, construction, facility, migration or body-state propagation engine exists.
