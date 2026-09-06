from __future__ import annotations

import unittest

from loom.application.contracts import SpatialState
from loom.navigation.gravity_shadow import OrdinaryTrajectorySample, compare_gravity_shadow
from loom.spatial.celestial_state import HybridCelestialStateService, ParentCentricOrbitModel
from loom.spatial.gravity import GravitySource, evaluate_gravity


class GravityShadowFunctionalTests(unittest.TestCase):
    def test_shadow_uses_time_varying_parent_and_propagated_moon_states(self):
        def direct(entity_id: str, epoch_utc: str):
            if entity_id != "PARENT":
                return None
            # Simple deterministic moving parent; not an orbital ephemeris fixture,
            # but sufficient to prove every RK4 substage asks the shared celestial
            # service for the requested epoch rather than freezing one scene state.
            sec = int(epoch_utc[17:19]) + int(epoch_utc[14:16]) * 60
            return SpatialState(
                entity_id="PARENT",
                epoch_utc=epoch_utc,
                reference_frame="J2000/ECLIPTIC",
                position_km=(100000.0, float(sec), 0.0),
                velocity_km_s=(0.0, 1.0, 0.0),
                provenance={"state_source": "FUNCTIONAL_DIRECT"},
                navigation_grade=True,
            )

        moon_model = ParentCentricOrbitModel(
            entity_id="MOON",
            parent_entity_id="PARENT",
            element_epoch_utc="2226-01-01T00:00:00Z",
            semi_major_axis_km=1000.0,
            eccentricity=0.0,
            inclination_deg=0.0,
            raan_deg=0.0,
            arg_periapsis_deg=0.0,
            mean_anomaly_deg=0.0,
            parent_mu_km3_s2=10000.0,
            model_id="FUNCTIONAL_MOON_MODEL",
            provenance={"anchor_source": "FUNCTIONAL_DIRECT_ANCHOR"},
            uncertainty={"navigation_qualification": "PROPAGATED_NOT_DIRECT"},
        )
        service = HybridCelestialStateService(direct, {"MOON": moon_model})

        def gravity(position, epoch):
            parent = service.resolve("PARENT", epoch)
            moon = service.resolve("MOON", epoch)
            self.assertFalse(moon.navigation_grade)
            sources = (
                GravitySource("PARENT", parent, 10000.0),
                GravitySource("MOON", moon, 10.0),
            )
            return evaluate_gravity(position, sources, epoch_utc=epoch)

        reference = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (0.0, 60.0, 0.0), (0.0, 1.0, 0.0)),
            OrdinaryTrajectorySample("2226-01-01T00:02:00Z", (0.0, 120.0, 0.0), (0.0, 1.0, 0.0)),
        )
        report = compare_gravity_shadow(reference, gravity, max_step_s=10.0)
        self.assertEqual(report.sample_count, 3)
        self.assertGreater(report.terminal_position_error_km, 0.0)
        self.assertGreater(report.terminal_velocity_error_km_s, 0.0)
        self.assertIn(report.samples[-1].dominant_gravity_source, {"PARENT", "MOON"})
        self.assertEqual(report.qualification["retargeting"], False)


if __name__ == "__main__":
    unittest.main()
