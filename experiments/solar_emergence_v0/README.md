# Solar emergence v0 — astronomical Run 1

**Class:** `class:engineering`. **Status:** fictional, non-canon, non-production experiment. Governing plan: [`research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md`](../../research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md). Baseline main SHA: `fbc3818648cd9cdf54629281f52b5eb928b4f877`.

The first Run 1 counted 48 distinct materialized `ephemeris_states.entity_id` values and missed `SOL`. The corrective Run 1 properly audited the **49-object production Solar GIS registry**, including the Sun. That registry still preselects only 28 moons. For neutral emergence, this experiment now has a separate frozen **201-object astronomical candidate registry**. Production GIS, Navigator, SQLite, Atlas, CIVSTATE, canon and Earth are unchanged.

## Frozen authority and rule

The freeze is `2026-09-23T22:53:12Z` (24 September in Melbourne). [`source_manifest.json`](sources/astronomical_registry/source_manifest.json) records each source URL, organization, retrieval UTC, role, SHA-256, parser version and limitations. The bounded primary sources are NASA/JPL's [planetary satellite discovery table](https://ssd.jpl.nasa.gov/sats/discovery.html), [Horizons major-body ID list](https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND=%27MB%27) and SBDB identity records for Ceres and Makemake, plus [NASA's eight-planet and five-dwarf classification](https://science.nasa.gov/solar-system/planets/). The local raw JPL captures and normalized planet, moon and dwarf snapshots are frozen under `sources/astronomical_registry/`. Normal generation reads these local files and the repository world DB; it makes no network request.

Include the Sun; all eight physical planets; all five IAU-recognized dwarf planets; every JPL discovery-table satellite with both permanent IAU name and number and a unique Horizons major-body ID; Earth's Moon and named Eris/Haumea dwarf satellites identified in the JPL major-body list; the ten existing LOOM asteroids; and five existing LOOM system barycenters. The JPL discovery table supplies 168 included named moons and 292 provisional-only rows excluded. Its stated scope omits Earth's Moon and non-Pluto dwarf satellites, so the major-body list adds the Moon, Dysnomia, Hi'iaka and Namaka. Total named moons: **172**. Parent counts: Earth 1, Mars 2, Jupiter 57, Saturn 63, Uranus 27, Neptune 14, Pluto 5, Eris 1, Haumea 2. No moons are added for Ceres or Makemake. The rule does not ingest every asteroid, TNO, comet, provisional moon, spacecraft or arbitrary Horizons target. A stable Horizons ID establishes identity, **not** a qualified LOOM state or 2226 ephemeris coverage.

The full 201 are: 1 stellar reference, 8 planets, 172 moons, 5 dwarfs, 10 registered asteroids and 5 system barycenters. The first 49 map to existing LOOM identities; **152 are experiment-only**. Of these, 153 catalog objects lack a materialized `ephemeris_states` row (the 152 new objects and `SOL`). There are 37 qualified direct LOOM states and 36 bodies with the existing SQLite provider's anchor-model support. The other new bodies carry external ephemeris identities but no LOOM state or provider support. The prior 12 display-only LOOM moons remain display-only in that seam.

## Identity and opportunity

An exact one-to-one LOOM physical identity keeps its existing `body_id` (`ME`, `VE`, `EA`, `MA`, `CER` and mapped moons). A new physical body uses deterministic `NAIF_<stable JPL ID>`. `JU`, `SA`, `UR`, `NE` and `PL` retain their LOOM **system-barycenter** meanings; physical Jupiter, Saturn, Uranus, Neptune and Pluto are `NAIF_599`, `NAIF_699`, `NAIF_799`, `NAIF_899` and `NAIF_999`. Moons point to those physical parents where applicable. Each record separates experiment ID, JPL target/NAIF ID, parent, LOOM mapping and provenance. The catalog and audit retain source and state evidence without promoting external IDs into production.

`body_opportunities.json` has one row for every catalog object. Its 195 physical bodies are the only potential hosts; Sun and barycenters have no surface opportunity. `parameters.json` holds structural test priors by physical subclass. `GIANT_PLANET` has `surface_possible=false`; `TERRESTRIAL_PLANET`, `DWARF_PLANET`, `MOON` and `ASTEROID` have broad structural true flags. `orbital_possible=true` means a free-space/orbital facility may be associated with the body; it does **not** promise a stable two-body orbit at arbitrary altitude. These are not habitat, engineering, settlement or canon findings.

For 33 qualified existing LOOM physical-reference rows only, surface gravity is derived as `1000 × gm_km3_s2 / mean_radius_km²` in m/s², requiring finite positive inputs and the qualified `ENGINEERING_REFERENCE_NONCANON` / `REFERENCE_PHYSICAL_CONSTANTS_v0.1` status. New bodies receive no fabricated gravity. Radiation, thermal, solar-energy, water, volatile, bulk-material and metal potentials remain `null` for all 201. `celestial_dynamics.atmosphere_class`, `reference_orbit_radius_km`, SBDB physical/orbit values and worldbuilding census names are not treated as qualified opportunity values. The database semantic dossier and SQLite provider promotion contract govern the narrower LOOM read seam.

Eris, Haumea and Makemake enter by the five-dwarf rule. Patroclus/Menoetius and Quaoar/Orcus have JPL identities but are outside this bounded target universe and are not existing LOOM asteroids; Gonggong is likewise outside scope. Their mention in LOOM prose or census does not create registration. Named moons of Eris and Haumea enter because their parents are included recognized dwarfs; Weywot and Vanth do not because Quaoar and Orcus are outside scope.

## Reproduce and hard stop

The builder verifies the repository world DB against `manifests/release_manifest.json` and `parameters.json`, opens it with SQLite `mode=ro`, `immutable=1`, `query_only=ON`, and writes only four experiment JSON artifacts in stable ID order. The expected DB SHA-256 is `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.

From this directory:

```bash
python3 -B body_opportunities.py
python3 -B -m unittest -v test_astronomical_registry.py test_body_opportunities.py
```

Two runs with unchanged local sources and DB produce byte-identical `astronomical_registry.json`, `body_registry_audit.json`, `body_catalog.json` and `body_opportunities.json`. Run 1 stops here. No accessibility, investment, construction, facilities, migration, civilization propagation or experiment body-state engine exists.
