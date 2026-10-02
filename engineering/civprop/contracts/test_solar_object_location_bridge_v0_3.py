import unittest
from pathlib import Path
from engineering.civprop.contracts.solar_object_location_bridge_v0_3 import build_solar_candidate_locations

ROOT=Path(__file__).resolve().parents[3]
NAV=ROOT/'reports/solar_civprop/NAV_READINESS_V1.json'

class SolarObjectLocationBridgeV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.pkg=build_solar_candidate_locations(NAV)
    def rows(self, body): return [x for x in self.pkg['locations'] if x['body_id']==body]
    def test_earth_moon_ids_do_not_collide_with_existing_runtime_locations(self):
        ids={x['location_id'] for x in self.pkg['locations']}
        self.assertIn('EARTH_SURFACE',ids); self.assertIn('EARTH_ORBITAL',ids)
        self.assertIn('MOON_SURFACE',ids); self.assertIn('MOON_ORBITAL',ids)
        self.assertNotIn('LUNA_SURFACE',ids)
    def test_mars_ceres_europa_are_candidates(self):
        for body in ('MARS','CERES','EUROPA'):
            rows=self.rows(body); self.assertEqual({x['placement'] for x in rows},{'ORBITAL','SURFACE'})
            self.assertTrue(all(x['candidate_status']=='NAV1_CANDIDATE' for x in rows))
    def test_nav_lien_is_preserved_not_erased(self):
        rows=self.rows('PROTEUS'); self.assertTrue(rows)
        self.assertTrue(all(x['candidate_status']=='NAV1_NOT_SUPPORTED_AT_ASSESSMENT_EPOCH' for x in rows))
    def test_catalog_only_body_is_preserved_as_nonselectable(self):
        rows=self.rows('DACTYL'); self.assertTrue(rows)
        self.assertTrue(all(x['candidate_status']=='IDENTITY_NOT_NAV0_SUPPORTED' for x in rows))
    def test_barycenters_spacecraft_and_star_not_destinations(self):
        for body in ('EARTH_MOON_BARYCENTER','SUN'):
            self.assertEqual(self.rows(body),[])
    def test_interstellar_object_remains_candidate_when_nav_supported(self):
        rows=self.rows('ATLAS3I'); self.assertTrue(rows)
        self.assertTrue(all(x['candidate_status']=='NAV1_CANDIDATE' for x in rows))
    def test_bridge_does_not_claim_access(self):
        self.assertTrue(self.pkg['semantics']['candidate_is_not_accessible'])
        self.assertTrue(self.pkg['semantics']['transport_and_actor_access_are_downstream'])

if __name__=='__main__': unittest.main()
