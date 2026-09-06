import math
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.celestial_state import (
    CANONICAL_FRAME,
    CelestialStateError,
    HybridCelestialStateService,
    ParentCentricOrbitModel,
    propagate_parent_centric,
)


EPOCH = "2226-06-15T00:00:00Z"


class CelestialStateServiceUnitTest(unittest.TestCase):
    def test_circular_orbit_propagates_quarter_period(self):
        mu = 398600.435436
        a = 384400.0
        period = 2.0 * math.pi * math.sqrt(a**3 / mu)
        model = ParentCentricOrbitModel(
            entity_id="MOON",
            parent_entity_id="EARTH",
            element_epoch_utc=EPOCH,
            semi_major_axis_km=a,
            eccentricity=0.0,
            inclination_deg=0.0,
            raan_deg=0.0,
            arg_periapsis_deg=0.0,
            mean_anomaly_deg=0.0,
            parent_mu_km3_s2=mu,
            model_id="TEST-CIRCULAR",
        )
        from datetime import datetime, timedelta, timezone
        start = datetime.fromisoformat(EPOCH.replace("Z", "+00:00"))
        target = (start + timedelta(seconds=period / 4.0)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        p, v = propagate_parent_centric(model, target)
        self.assertAlmostEqual(p[0], 0.0, delta=1e-5)
        self.assertAlmostEqual(p[1], a, delta=1e-5)
        self.assertAlmostEqual(p[2], 0.0, delta=1e-9)
        self.assertLess(v[0], 0.0)
        self.assertAlmostEqual(v[1], 0.0, delta=1e-10)

    def test_direct_state_wins_over_propagation_model(self):
        direct = SpatialState(
            entity_id="MOON",
            epoch_utc=EPOCH,
            reference_frame=CANONICAL_FRAME,
            position_km=(1.0, 2.0, 3.0),
            velocity_km_s=(4.0, 5.0, 6.0),
            provenance={"state_source": "DIRECT_TEST"},
            navigation_grade=True,
        )
        model = ParentCentricOrbitModel(
            entity_id="MOON", parent_entity_id="EARTH", element_epoch_utc=EPOCH,
            semi_major_axis_km=10.0, eccentricity=0.0, inclination_deg=0.0,
            raan_deg=0.0, arg_periapsis_deg=0.0, mean_anomaly_deg=0.0,
            parent_mu_km3_s2=1.0, model_id="SHOULD-NOT-BE-USED",
        )
        svc = HybridCelestialStateService(lambda eid, epoch: direct if eid == "MOON" else None, {"MOON": model})
        self.assertIs(svc.resolve("MOON", EPOCH), direct)

    def test_missing_body_fails_closed(self):
        svc = HybridCelestialStateService(lambda eid, epoch: None, {})
        with self.assertRaises(CelestialStateError):
            svc.resolve("UNKNOWN", EPOCH)


class CelestialStateServiceFunctionalTest(unittest.TestCase):
    def test_propagated_moon_is_heliocentric_and_retains_provenance(self):
        earth = SpatialState(
            entity_id="EARTH",
            epoch_utc=EPOCH,
            reference_frame=CANONICAL_FRAME,
            position_km=(100000000.0, 20000000.0, -5000000.0),
            velocity_km_s=(-4.0, 28.0, 1.0),
            provenance={"state_source": "DIRECT_JPL_TEST"},
            navigation_grade=True,
        )
        model = ParentCentricOrbitModel(
            entity_id="MOON",
            parent_entity_id="EARTH",
            element_epoch_utc=EPOCH,
            semi_major_axis_km=384400.0,
            eccentricity=0.0549,
            inclination_deg=5.145,
            raan_deg=125.08,
            arg_periapsis_deg=318.15,
            mean_anomaly_deg=115.3654,
            parent_mu_km3_s2=398600.435436,
            model_id="MOON-TEST-OSCULATING",
            provenance={"source": "TEST_ELEMENTS"},
            uncertainty={"position_1sigma_km": 25.0},
        )
        svc = HybridCelestialStateService(
            lambda eid, epoch: earth if eid == "EARTH" else None,
            {"MOON": model},
        )
        moon = svc.resolve("MOON", EPOCH)
        self.assertEqual(moon.reference_frame, CANONICAL_FRAME)
        self.assertFalse(moon.navigation_grade)
        self.assertEqual(moon.provenance["state_source"], "PROPAGATED_PARENT_CENTRIC_KEPLER")
        self.assertEqual(moon.provenance["parent_state_source"], "DIRECT_JPL_TEST")
        self.assertEqual(moon.payload["parent_entity_id"], "EARTH")
        separation = math.sqrt(sum((moon.position_km[i] - earth.position_km[i])**2 for i in range(3)))
        self.assertGreater(separation, 300000.0)
        self.assertLess(separation, 450000.0)


if __name__ == "__main__":
    unittest.main()
