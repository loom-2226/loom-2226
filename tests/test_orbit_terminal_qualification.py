from __future__ import annotations

import math
import unittest

from loom.application.contracts import SpatialState
from loom.orbit_terminal_qualification import (
    ORBIT_TERMINAL_QUALIFICATION_VERSION,
    OrbitTerminalQualificationError,
    TerminalMatchTolerance,
    validate_terminal_match_against_orbit_consequence,
)
from loom.physical_state_contracts import (
    TerminalMatchClass,
    TerminalStateQualification,
    TerminalStateResidual,
)
from loom.spatial.orbit_consequence import (
    CentralBodyOrbitContext,
    OrbitClass,
    derive_orbital_consequence,
)


class OrbitTerminalQualificationTests(unittest.TestCase):
    MU = 398600.435507
    RADIUS = 7000.0
    FRAME = "EA_CENTERED_J2000"
    EPOCH = "2226-08-22T12:00:00Z"

    def _state(self, velocity, *, position=(RADIUS, 0.0, 0.0)) -> SpatialState:
        return SpatialState(
            entity_id="WAYFARER",
            epoch_utc=self.EPOCH,
            reference_frame=self.FRAME,
            position_km=position,
            velocity_km_s=velocity,
            provenance={"source": "hostile_test"},
            navigation_grade=False,
        )

    def _context(self, *, surface=6378.1) -> CentralBodyOrbitContext:
        return CentralBodyOrbitContext(
            central_body_id="EA",
            reference_frame=self.FRAME,
            mu_km3_s2=self.MU,
            reference_surface_radius_km=surface,
            provenance={"source": "explicit_test_constant"},
        )

    def _qualification(self, natural, desired, match_class) -> TerminalStateQualification:
        return TerminalStateQualification(
            match_class=match_class,
            residual=TerminalStateResidual(natural_state=natural, desired_state=desired),
            physical_certification_status="PASS",
            traffic_authorization_status="AUTHORIZED",
            correction_exchange="TORCH" if match_class == TerminalMatchClass.CORRECTABLE_MATCH else None,
        )

    def test_version_and_exact_circular_natural_match_pass(self) -> None:
        speed = math.sqrt(self.MU / self.RADIUS)
        natural = self._state((0.0, speed, 0.0))
        desired = natural
        consequence = derive_orbital_consequence(natural, self._context())
        qualification = self._qualification(natural, desired, TerminalMatchClass.NATURAL_MATCH)
        result = validate_terminal_match_against_orbit_consequence(
            qualification,
            consequence,
            tolerance=TerminalMatchTolerance(0.0, 0.0),
            accepted_natural_orbit_classes=(OrbitClass.CIRCULAR,),
        )
        self.assertEqual(ORBIT_TERMINAL_QUALIFICATION_VERSION, "LOOM_F_PB_ORBIT_TERMINAL_QUALIFICATION_V1")
        self.assertTrue(result.natural_match_physically_consistent)
        self.assertEqual(result.actual_orbit_class, OrbitClass.CIRCULAR)

    def test_hyperbolic_collapse_cannot_be_called_natural_circular_match(self) -> None:
        escape = math.sqrt(2.0 * self.MU / self.RADIUS)
        circular = math.sqrt(self.MU / self.RADIUS)
        natural = self._state((0.0, escape * 1.05, 0.0))
        desired = self._state((0.0, circular, 0.0))
        consequence = derive_orbital_consequence(natural, self._context())
        self.assertEqual(consequence.orbit_class, OrbitClass.HYPERBOLIC)
        qualification = self._qualification(natural, desired, TerminalMatchClass.NATURAL_MATCH)
        with self.assertRaises(OrbitTerminalQualificationError):
            validate_terminal_match_against_orbit_consequence(
                qualification,
                consequence,
                tolerance=TerminalMatchTolerance(0.1, 0.001),
                accepted_natural_orbit_classes=(OrbitClass.CIRCULAR,),
            )

    def test_surface_intersecting_collapse_cannot_be_called_safe_natural_match(self) -> None:
        # Tangential sub-circular velocity at 7000 km produces an ellipse whose
        # periapsis falls below the explicit reference surface.
        circular = math.sqrt(self.MU / self.RADIUS)
        natural = self._state((0.0, circular * 0.70, 0.0))
        consequence = derive_orbital_consequence(natural, self._context())
        self.assertEqual(consequence.orbit_class, OrbitClass.ELLIPTIC)
        self.assertTrue(consequence.intersects_reference_surface)
        qualification = self._qualification(natural, natural, TerminalMatchClass.NATURAL_MATCH)
        with self.assertRaises(OrbitTerminalQualificationError):
            validate_terminal_match_against_orbit_consequence(
                qualification,
                consequence,
                tolerance=TerminalMatchTolerance(0.0, 0.0),
                accepted_natural_orbit_classes=(OrbitClass.ELLIPTIC,),
            )

    def test_correctable_match_is_not_upgraded_or_erased(self) -> None:
        escape = math.sqrt(2.0 * self.MU / self.RADIUS)
        circular = math.sqrt(self.MU / self.RADIUS)
        natural = self._state((0.0, escape * 1.01, 0.0))
        desired = self._state((0.0, circular, 0.0))
        consequence = derive_orbital_consequence(natural, self._context())
        qualification = self._qualification(natural, desired, TerminalMatchClass.CORRECTABLE_MATCH)
        result = validate_terminal_match_against_orbit_consequence(
            qualification,
            consequence,
            tolerance=TerminalMatchTolerance(0.1, 0.001),
            accepted_natural_orbit_classes=(OrbitClass.CIRCULAR,),
        )
        self.assertEqual(result.claimed_match_class, TerminalMatchClass.CORRECTABLE_MATCH)
        self.assertFalse(result.natural_match_physically_consistent)
        self.assertGreater(result.residual_velocity_km_s, 0.0)

    def test_consequence_from_different_state_is_rejected(self) -> None:
        speed = math.sqrt(self.MU / self.RADIUS)
        natural = self._state((0.0, speed, 0.0))
        copied = self._state((0.0, speed, 0.0))
        consequence = derive_orbital_consequence(copied, self._context())
        qualification = self._qualification(natural, natural, TerminalMatchClass.NATURAL_MATCH)
        with self.assertRaises(OrbitTerminalQualificationError):
            validate_terminal_match_against_orbit_consequence(
                qualification,
                consequence,
                tolerance=TerminalMatchTolerance(0.0, 0.0),
                accepted_natural_orbit_classes=(OrbitClass.CIRCULAR,),
            )


if __name__ == "__main__":
    unittest.main()
