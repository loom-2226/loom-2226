from __future__ import annotations

import math
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.orbit_consequence import (
    CentralBodyOrbitContext,
    ORBIT_CONSEQUENCE_VERSION,
    OrbitClass,
    OrbitConsequenceError,
    derive_orbital_consequence,
)


class OrbitConsequenceTests(unittest.TestCase):
    def _state(self, *, position=(100.0, 0.0, 0.0), velocity=(0.0, 10.0, 0.0), frame="TEST_BODY_CENTERED_INERTIAL") -> SpatialState:
        return SpatialState(
            entity_id="WAYFARER",
            epoch_utc="2226-08-22T12:00:00Z",
            reference_frame=frame,
            position_km=position,
            velocity_km_s=velocity,
            provenance={"source": "terminal-collapse-test"},
            navigation_grade=False,
        )

    def _context(self, **kwargs) -> CentralBodyOrbitContext:
        values = {
            "central_body_id": "TEST_BODY",
            "reference_frame": "TEST_BODY_CENTERED_INERTIAL",
            "mu_km3_s2": 10000.0,
            "reference_surface_radius_km": 50.0,
            "atmosphere_interface_radius_km": 60.0,
            "provenance": {"source": "test-GM"},
        }
        values.update(kwargs)
        return CentralBodyOrbitContext(**values)

    def test_version_and_exact_circular_consequence(self) -> None:
        result = derive_orbital_consequence(self._state(), self._context())
        self.assertEqual(ORBIT_CONSEQUENCE_VERSION, "LOOM_F_PB_ORBIT_CONSEQUENCE_V1")
        self.assertEqual(result.orbit_class, OrbitClass.CIRCULAR)
        self.assertAlmostEqual(result.radius_km, 100.0, places=12)
        self.assertAlmostEqual(result.speed_km_s, 10.0, places=12)
        self.assertAlmostEqual(result.specific_energy_km2_s2, -50.0, places=12)
        self.assertAlmostEqual(result.angular_momentum_magnitude_km2_s, 1000.0, places=12)
        self.assertLess(result.eccentricity, 1e-12)
        self.assertAlmostEqual(result.semi_major_axis_km, 100.0, places=12)
        self.assertAlmostEqual(result.periapsis_radius_km, 100.0, places=12)
        self.assertAlmostEqual(result.apoapsis_radius_km, 100.0, places=12)
        self.assertFalse(result.intersects_reference_surface)
        self.assertFalse(result.intersects_atmosphere_interface)

    def test_hyperbolic_state_is_not_called_capture(self) -> None:
        result = derive_orbital_consequence(
            self._state(velocity=(0.0, 15.0, 0.0)),
            self._context(),
        )
        self.assertEqual(result.orbit_class, OrbitClass.HYPERBOLIC)
        self.assertGreater(result.specific_energy_km2_s2, 0.0)
        self.assertGreater(result.eccentricity, 1.0)
        self.assertIsNone(result.apoapsis_radius_km)

    def test_periapsis_exposes_surface_and_atmosphere_intersection(self) -> None:
        result = derive_orbital_consequence(
            self._state(velocity=(0.0, 6.0, 0.0)),
            self._context(reference_surface_radius_km=50.0, atmosphere_interface_radius_km=70.0),
        )
        self.assertEqual(result.orbit_class, OrbitClass.ELLIPTIC)
        self.assertLess(result.periapsis_radius_km, 50.0)
        self.assertTrue(result.intersects_reference_surface)
        self.assertTrue(result.intersects_atmosphere_interface)

    def test_radial_terminal_state_is_explicit_not_silently_regularized(self) -> None:
        result = derive_orbital_consequence(
            self._state(velocity=(-5.0, 0.0, 0.0)),
            self._context(),
        )
        self.assertEqual(result.orbit_class, OrbitClass.RADIAL)
        self.assertEqual(result.angular_momentum_magnitude_km2_s, 0.0)
        self.assertEqual(result.periapsis_radius_km, 0.0)
        self.assertTrue(result.intersects_reference_surface)

    def test_hidden_frame_conversion_is_rejected(self) -> None:
        with self.assertRaises(OrbitConsequenceError):
            derive_orbital_consequence(
                self._state(frame="OTHER_FRAME"),
                self._context(),
            )

    def test_context_never_infers_gm_or_radius(self) -> None:
        context = CentralBodyOrbitContext(
            central_body_id="TEST_BODY",
            reference_frame="TEST_BODY_CENTERED_INERTIAL",
            mu_km3_s2=10000.0,
        )
        result = derive_orbital_consequence(self._state(), context)
        self.assertIsNone(result.intersects_reference_surface)
        self.assertIsNone(result.intersects_atmosphere_interface)


if __name__ == "__main__":
    unittest.main()
