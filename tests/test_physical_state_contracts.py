from __future__ import annotations

import unittest

from loom.application.contracts import ContractError, SpatialState
from loom.physical_state_contracts import (
    BoundaryStateSemantics,
    CONTRACT_VERSION,
    PropulsionBoundaryState,
    TerminalMatchClass,
    TerminalStateQualification,
    TerminalStateResidual,
)


class PhysicalStateContractTests(unittest.TestCase):
    def _state(
        self,
        *,
        position=(1000.0, 2000.0, 3000.0),
        velocity=(1.0, 2.0, 3.0),
        epoch="2226-08-22T12:00:00Z",
        frame="MARS_CENTERED_J2000",
    ) -> SpatialState:
        return SpatialState(
            entity_id="WAYFARER",
            epoch_utc=epoch,
            reference_frame=frame,
            position_km=position,
            velocity_km_s=velocity,
            provenance={"source": "test"},
            navigation_grade=False,
        )

    def test_contract_version_and_boundary_preserve_explicit_state(self) -> None:
        state = self._state()
        boundary = PropulsionBoundaryState(
            transition_id="COLLAPSE-1",
            semantics=BoundaryStateSemantics.NATURAL,
            incoming_regime="metric",
            outgoing_regime="ordinary",
            spatial_state=state,
            campaign_revision=10,
            solution_id="SOL-1",
            propagator_id="U-M-TEST",
            calibration_id="CAL-1",
        )
        self.assertEqual(CONTRACT_VERSION, "LOOM_F_PB_STATE_CONTINUITY_V1")
        self.assertIs(boundary.spatial_state, state)
        self.assertEqual(boundary.incoming_regime, "METRIC")
        self.assertEqual(boundary.outgoing_regime, "ORDINARY")
        self.assertEqual(boundary.semantics, BoundaryStateSemantics.NATURAL)

    def test_terminal_residual_is_full_vector_difference(self) -> None:
        natural = self._state(position=(10.0, 20.0, 30.0), velocity=(1.0, 2.0, 3.0))
        desired = self._state(position=(11.5, 18.0, 35.0), velocity=(0.5, 2.25, 4.0))
        residual = TerminalStateResidual(natural_state=natural, desired_state=desired)
        self.assertEqual(residual.delta_position_km, (1.5, -2.0, 5.0))
        self.assertEqual(residual.delta_velocity_km_s, (-0.5, 0.25, 1.0))

    def test_residual_refuses_hidden_frame_or_epoch_conversion(self) -> None:
        natural = self._state()
        with self.assertRaises(ContractError):
            TerminalStateResidual(
                natural_state=natural,
                desired_state=self._state(frame="CERES_CENTERED_J2000"),
            )
        with self.assertRaises(ContractError):
            TerminalStateResidual(
                natural_state=natural,
                desired_state=self._state(epoch="2226-08-22T12:00:01Z"),
            )

    def test_correctable_match_requires_explicit_exchange(self) -> None:
        residual = TerminalStateResidual(
            natural_state=self._state(),
            desired_state=self._state(velocity=(1.0, 2.0, 3.1)),
        )
        with self.assertRaises(ContractError):
            TerminalStateQualification(
                match_class=TerminalMatchClass.CORRECTABLE_MATCH,
                residual=residual,
                physical_certification_status="PASS",
                traffic_authorization_status="AUTHORIZED",
            )
        qualified = TerminalStateQualification(
            match_class=TerminalMatchClass.CORRECTABLE_MATCH,
            residual=residual,
            physical_certification_status="PASS",
            traffic_authorization_status="AUTHORIZED",
            correction_exchange="TORCH",
        )
        self.assertEqual(qualified.correction_exchange, "TORCH")

    def test_physical_and_traffic_status_are_independent(self) -> None:
        residual = TerminalStateResidual(
            natural_state=self._state(),
            desired_state=self._state(),
        )
        qualified = TerminalStateQualification(
            match_class=TerminalMatchClass.NATURAL_MATCH,
            residual=residual,
            physical_certification_status="PASS",
            traffic_authorization_status="PROHIBITED",
        )
        self.assertEqual(qualified.physical_certification_status, "PASS")
        self.assertEqual(qualified.traffic_authorization_status, "PROHIBITED")
        self.assertEqual(qualified.match_class, TerminalMatchClass.NATURAL_MATCH)


if __name__ == "__main__":
    unittest.main()
