"""Build 8 catalog-wide *state* eligibility, without route search."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from unittest import TestCase, skipUnless
import json

from .eligibility import catalog_rows
from .on_demand import OnDemandTravel

ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
# SHA-256 of compact, sorted, newline-terminated complete geometry JSON,
# independently captured from live fc949bd main before any edits, 2026-05-14.
MAIN_EIGHT_ROUTE_GEOMETRY_SHA256 = {
    "CERES->EARTH": "74247273aaed83f9b2d69bce5c8340efe8bc3183d46fb868c57ff96ff38f8eec",
    "CERES->MARS": "f3c137ef42b0a1f3074259001bc719b8ff5f80f21746926327f623637c9d6b05",
    "EARTH->CERES": "388fa934815ce457ad5f3ef49c843e82b753eeef5ca9330109ffb0647fc0e672",
    "EARTH->MARS": "4e3f7291e3a8399546ff509bde7d810a1c8b1da84d0b5c03010403e7c35f3619",
    "EARTH->MERCURY": "ac5eac62d474a73ff1cd9e2fd0be44d517de8917da5807210ad4b7fbfdea7ad4",
    "MARS->CERES": "881cc5b15112bdfe0e42a8de6b11c230f291d487f51aeec69e36dc384409f373",
    "MARS->EARTH": "1aee084876aa936218abb1061c70985cc0772ad98db5fc6306f70d84b5b21186",
    "MERCURY->EARTH": "8f03f33545e88eaeaa248ae78b3328e5cfd3b90259180bb4f54559e01fb4f3bc",
}


@skipUnless((ASSET_ROOT / "kernels/spk/de440.bsp").exists(),
            "qualified SPICE assets unavailable (offline quantifactus tests)")
class CatalogEligibilityTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = OnDemandTravel()
        cls.rows = catalog_rows()

    def check(self, body, date):
        return self.engine.endpoint(body, date)

    def test_all_110_identities_all_five_years_and_repeated_byte_identity(self):
        self.assertEqual(len(self.rows), 110)
        self.assertEqual(len(self.engine.adapter.registry.bodies), 110)
        expected = {2026:(103,5,2),2100:(103,5,2),2199:(102,6,2),
                    2200:(95,8,7),2226:(90,13,7)}
        for year, (direct, prop, missing) in expected.items():
            items = [self.check(r["body_id"], f"{year}-01-01T00:00:00Z")
                     for r in self.rows]
            counts = Counter(x["ephemeris_status"] for x in items)
            self.assertEqual(
                (counts["DIRECT"],counts["UNKNOWN_EPHEMERIS_PROPAGATED"],
                 counts["UNKNOWN_EPHEMERIS_MISSING"]), (direct,prop,missing))
            self.assertTrue(all(x["status"] is not None for x in items))
            self.assertEqual(
                json.dumps(items,sort_keys=True,separators=(",",":")),
                json.dumps([self.check(r["body_id"], f"{year}-01-01T00:00:00Z")
                            for r in self.rows],sort_keys=True,separators=(",",":")))

    def test_sun_unknown_and_no_barycenter_substitution(self):
        self.assertEqual(self.check("SUN","2226-01-01")["status"],
                         "UNSUPPORTED_SUN_ENDPOINT")
        self.assertEqual(self.check("NO_SUCH_BODY","2226-01-01")["status"],
                         "UNKNOWN_CATALOG_ENTITY")
        center = self.check("JUPITER","2226-01-01")
        bary = self.check("JUPITER_SYSTEM_BARYCENTER","2226-01-01")
        self.assertEqual(center["status"],"UNKNOWN_EPHEMERIS_PROPAGATED")
        self.assertEqual(center["alternate_barycenter"],
                         "JUPITER_SYSTEM_BARYCENTER")
        self.assertEqual(bary["status"],"DIRECT")
        self.assertNotEqual(center["source_id"],bary["source_id"])
        self.assertEqual(self.check("PLUTO","2226-01-01")["status"],
                         "UNKNOWN_EPHEMERIS_PROPAGATED")
        self.assertEqual(self.check("PLUTO_SYSTEM_BARYCENTER","2226-01-01")["status"],
                         "DIRECT")

    def test_bennu_2135_exact_direct_to_propagated_seam(self):
        self.assertEqual(self.check("BENNU","2135-09-30T23:58:49Z")["status"],"DIRECT")
        self.assertEqual(self.check("BENNU","2135-10-01T00:00:00Z")["status"],
                         "UNKNOWN_EPHEMERIS_PROPAGATED")
        self.assertEqual(self.check("BENNU","2026-01-01")["source_id"],
                         "JPL_BENNU_SB441")

    def test_missing_partial_moons_and_local_leg(self):
        for name in ("DACTYL","SELAM"):
            for year in (2026,2100,2199,2200,2226):
                self.assertEqual(self.check(name,f"{year}-01-01")["status"],
                                 "UNKNOWN_EPHEMERIS_MISSING")
        for name in ("NIX","HYDRA","KERBEROS","STYX"):
            self.assertEqual(self.check(name,"2199-01-01")["status"],
                             "UNKNOWN_LOCAL_LEG")
            self.assertEqual(self.check(name,"2200-01-01")["status"],
                             "UNKNOWN_EPHEMERIS_MISSING")
        self.assertEqual(self.check("PROTEUS","2199-01-01")["status"],
                         "UNKNOWN_LOCAL_LEG")
        self.assertEqual(self.check("PROTEUS","2200-01-01")["status"],
                         "UNKNOWN_EPHEMERIS_MISSING")
        moon=self.check("EUROPA","2026-01-01")
        self.assertEqual(moon["ephemeris_status"],"DIRECT")
        self.assertEqual(moon["status"],"UNKNOWN_LOCAL_LEG")
        self.assertFalse(moon["eligible"])
        self.assertEqual(self.check("EUROPA","2226-01-01")["status"],
                         "UNKNOWN_EPHEMERIS_PROPAGATED")

    def test_jupiter_2200_physical_moon_and_barycenter(self):
        for name in ("JUPITER","IO","EUROPA","GANYMEDE","CALLISTO"):
            before=self.check(name,"2200-01-09T23:58:49Z")
            after=self.check(name,"2200-01-10T00:00:00Z")
            self.assertEqual(before["ephemeris_status"],"DIRECT")
            self.assertEqual(after["ephemeris_status"],
                             "UNKNOWN_EPHEMERIS_PROPAGATED")
        self.assertEqual(self.check("JUPITER_SYSTEM_BARYCENTER",
                                    "2200-01-10")["status"],"DIRECT")

    def test_all_five_spacecraft_never_navigation_eligible(self):
        craft = [x for x in self.rows if x["body_class"]=="SPACECRAFT"]
        self.assertEqual(len(craft),5)
        for row in craft:
            for year in (2026,2100,2199,2200,2226):
                x=self.check(row["body_id"],f"{year}-01-01")
                self.assertEqual(x["status"],"UNKNOWN_EPHEMERIS_PROPAGATED")
                self.assertFalse(x["eligible"])

    def test_no_route_search_is_performed_by_endpoint_query(self):
        before=self.engine.solve_count
        for item in self.rows:
            self.engine.endpoint(item["body_id"],"2226-01-01")
        self.assertEqual(self.engine.solve_count,before)

    def test_original_eight_legacy_geometry_routes_byte_identical(self):
        for route, expected in sorted(MAIN_EIGHT_ROUTE_GEOMETRY_SHA256.items()):
            a,b=route.split("->")
            result=self.engine.geometry(a,b,"2026-05-14")
            encoded=(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n").encode()
            with self.subTest(route=route):
                self.assertEqual(sha256(encoded).hexdigest(),expected)
