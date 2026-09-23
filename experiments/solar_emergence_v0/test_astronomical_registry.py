"""Run-1 astronomical candidate registry, distinct from production GIS."""

import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from astronomical_registry import (
    build_astronomical_registry, normalize_named_moons, parse_discovery_html,
    parse_horizons_major_bodies, read_frozen_sources,
)
from body_opportunities import generate_bytes, open_world_db

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "sources" / "astronomical_registry"
DB = ROOT / "data" / "LOOM_2226.sqlite3"
PARAMETERS = json.loads((HERE / "parameters.json").read_text())


class AstronomicalRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = read_frozen_sources(SOURCE)
        with open_world_db(DB) as conn:
            cls.registry = build_astronomical_registry(cls.sources, conn, ROOT)
        cls.by_id = {row["body_id"]: row for row in cls.registry}

    def test_eight_physical_planets_and_barycenter_distinction(self):
        planets = [r for r in self.registry if r["body_class"] == "PLANET"]
        self.assertEqual({r["display_name"] for r in planets}, {
            "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune",
        })
        self.assertEqual(len(planets), 8)
        self.assertTrue(all(r["candidate_role"] == "PHYSICAL_BODY" for r in planets))
        for physical, barycenter in (("599", "JU"), ("699", "SA"), ("799", "UR"), ("899", "NE")):
            self.assertEqual(self.by_id[f"NAIF_{physical}"]["naif_id"], physical)
            self.assertEqual(self.by_id[barycenter]["candidate_role"], "SYSTEM_BARYCENTER")
            self.assertEqual(self.by_id[barycenter]["loom_entity_id"], barycenter)
            self.assertNotEqual(self.by_id[f"NAIF_{physical}"]["body_id"], barycenter)

    def test_five_dwarfs_and_physical_pluto(self):
        dwarfs = [r for r in self.registry if r["body_class"] == "DWARF_PLANET"]
        self.assertEqual({r["display_name"] for r in dwarfs}, {
            "Ceres", "Pluto", "Eris", "Haumea", "Makemake",
        })
        self.assertEqual(len(dwarfs), 5)
        self.assertEqual(self.by_id["CER"]["display_name"], "Ceres")
        self.assertEqual(self.by_id["NAIF_999"]["display_name"], "Pluto")
        self.assertEqual(self.by_id["PL"]["candidate_role"], "SYSTEM_BARYCENTER")

    def test_normalized_planet_and_dwarf_ids_match_jpl(self):
        major = parse_horizons_major_bodies((SOURCE / "raw" / "solar_horizons_mb.txt").read_text())
        by_id = {r["naif_id"]: r for r in major}
        self.assertEqual(by_id["10"]["display_name"], "Sun")
        for number, name in (("5", "Jupiter"), ("6", "Saturn"), ("7", "Uranus"),
                             ("8", "Neptune"), ("9", "Pluto")):
            self.assertEqual(by_id[number]["display_name"], f"{name} Barycenter")
        for row in self.sources["planets"]:
            self.assertEqual(by_id[row["naif_id"]]["display_name"], row["display_name"])
        for row in self.sources["dwarf_planets"]:
            if row["display_name"] in ("Ceres", "Makemake"):
                filename = "solar_ceres_sbdb.json" if row["display_name"] == "Ceres" else "solar_makemake_sbdb.json"
                object_ = json.loads((SOURCE / "raw" / filename).read_text())["object"]
                self.assertEqual(object_["spkid"], row["naif_id"])
                self.assertIn(row["display_name"], object_["fullname"])
            else:
                self.assertTrue(by_id[row["naif_id"]]["display_name"].startswith(row["display_name"]))

    def test_named_moons_match_frozen_primary_source(self):
        raw = (SOURCE / "raw" / "solar_sats_discovery.html").read_text()
        major = (SOURCE / "raw" / "solar_horizons_mb.txt").read_text()
        rows = parse_discovery_html(raw)
        ids = parse_horizons_major_bodies(major)
        named, excluded = normalize_named_moons(rows, ids, self.sources["planets"], self.sources["dwarf_planets"])
        self.assertEqual(named, self.sources["moons"])
        self.assertEqual(excluded, self.sources["excluded_provisional_count"])
        moon_rows = [r for r in self.registry if r["body_class"] == "MOON"]
        self.assertEqual(len(moon_rows), len(named))
        self.assertEqual({r["naif_id"] for r in moon_rows}, {r["naif_id"] for r in named})
        self.assertEqual(len(moon_rows), len({r["body_id"] for r in moon_rows}))
        self.assertTrue(all(self.by_id[r["parent_body_id"]]["candidate_role"] == "PHYSICAL_BODY"
                            for r in moon_rows))

    def test_new_named_fixture_auto_included_and_provisional_excluded(self):
        html = """<table><tr><td colspan='6'>Satellites of Jupiter: 2</td></tr>
        <tr><td>CXX</td><td>Testia</td><td>S/2026 J1</td><td>2026</td></tr>
        <tr><td></td><td></td><td>S/2026 J2</td><td>2026</td></tr></table>"""
        mb = "      599  Jupiter                                   \n      59999  Testia                                    JCXX\n      59998  S/2026 J2                                S2026_J2\n"
        rows = parse_discovery_html(html)
        named, excluded = normalize_named_moons(rows, parse_horizons_major_bodies(mb),
                                                self.sources["planets"], self.sources["dwarf_planets"],
                                                include_supplements=False)
        self.assertEqual([r["display_name"] for r in named], ["Testia"])
        self.assertEqual(named[0]["naif_id"], "59999")
        self.assertEqual(excluded, 1)

    def test_identity_mapping_and_existing_small_bodies(self):
        ids = [r["body_id"] for r in self.registry]
        astronomical = [r["naif_id"] for r in self.registry if r["naif_id"] is not None]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(astronomical), len(set(astronomical)))
        self.assertEqual(sum(r["body_class"] == "ASTEROID" for r in self.registry), 10)
        self.assertEqual(sum(r["loom_entity_id"] is not None for r in self.registry), 49)
        self.assertEqual(sum(r["loom_entity_id"] is None for r in self.registry), len(ids)-49)
        self.assertEqual(self.by_id["SOL"]["candidate_role"], "REFERENCE_BODY")
        for r in self.registry:
            if r["candidate_role"] == "PHYSICAL_BODY":
                self.assertNotEqual(r["loom_entity_class"], "SYSTEM_BARYCENTER")
        self.assertEqual(sum(r["ephemeris_identity_status"] is not None and r["loom_entity_id"] is None
                             for r in self.registry), len(ids)-49)

    def test_catalog_opportunity_and_unknowns(self):
        registry_bytes, audit_bytes, catalog_bytes, opp_bytes = generate_bytes(DB, PARAMETERS, SOURCE)
        registry = json.loads(registry_bytes)["bodies"]
        audit = json.loads(audit_bytes)["bodies"]
        catalog = json.loads(catalog_bytes)["bodies"]
        opp = json.loads(opp_bytes)["opportunities"]
        self.assertEqual({r["body_id"] for r in registry}, {r["body_id"] for r in catalog})
        self.assertEqual({r["body_id"] for r in registry}, {r["body_id"] for r in audit})
        self.assertEqual({r["body_id"] for r in registry}, {r["body_id"] for r in opp})
        self.assertEqual(len(opp), len(registry))
        self.assertEqual(sum(r["candidate_role"] == "PHYSICAL_BODY" for r in opp),
                         sum(r["candidate_role"] == "PHYSICAL_BODY" for r in catalog))
        self.assertTrue(all(r["surface_gravity"] is None for r in opp
                            if r["candidate_role"] != "PHYSICAL_BODY"))
        self.assertTrue(all(r["surface_possible"] is False and r["orbital_possible"] is None
                            for r in opp if r["candidate_role"] != "PHYSICAL_BODY"))
        for field in ("radiation_environment", "thermal_environment", "solar_energy_potential",
                      "water_potential", "volatile_potential", "bulk_material_potential", "metal_potential"):
            self.assertTrue(all(r[field] is None for r in opp), field)
        giant = {r["body_id"] for r in catalog if r["physical_subclass"] == "GIANT_PLANET"}
        self.assertEqual(len(giant), 4)
        self.assertTrue(all(r["surface_possible"] is False for r in opp if r["body_id"] in giant))

    def test_offline_readonly_determinism_and_run_two_absence(self):
        before = hashlib.sha256(DB.read_bytes()).hexdigest()
        with open_world_db(DB) as conn:
            self.assertEqual(conn.execute("PRAGMA query_only").fetchone()[0], 1)
        with patch("socket.socket", side_effect=AssertionError("network access attempted")):
            first = generate_bytes(DB, PARAMETERS, SOURCE)
            self.assertEqual(first, generate_bytes(DB, PARAMETERS, SOURCE))
        self.assertEqual(hashlib.sha256(DB.read_bytes()).hexdigest(), before)
        for name, data in zip(("astronomical_registry.json", "body_registry_audit.json",
                               "body_catalog.json", "body_opportunities.json"), first):
            self.assertEqual((HERE / name).read_bytes(), data)
        self.assertFalse((HERE / "route_accessibility.py").exists())
        self.assertFalse((HERE / "accessibility.json").exists())
        for forbidden in ("accessibility", "investment", "construction", "facilities",
                          "migration", "propagation"):
            self.assertFalse(any(forbidden in key for key in PARAMETERS))
            self.assertFalse(any(forbidden in path.name for path in HERE.iterdir()
                                 if path.is_file() and path.name not in ("README.md", "WORKPLAN.md")))


if __name__ == "__main__":
    unittest.main()
