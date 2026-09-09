from __future__ import annotations

import dataclasses
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "src" / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from vehicle_dynamics_contract import (  # noqa: E402
    CONTRACT_AUTHORITY,
    OPEN,
    TORCH_CARD_AUTHORITY,
    VehicleDynamicsContractError,
    build_vehicle_dynamics_contract,
    build_wayfarer_contract_family,
    family_differentiation_report,
    translational_signature,
    validate_vehicle_dynamics_contract,
)
from generative_candidate_compiler import compile_wayfarer_survivor_family  # noqa: E402


class VehicleDynamicsContractTests(unittest.TestCase):
    def test_candidate_family_binds_dynamics_to_same_design_and_glb(self):
        artifacts = compile_wayfarer_survivor_family()
        contracts = build_wayfarer_contract_family()
        self.assertEqual(len(artifacts), len(contracts))
        by_id = {row.candidate_id: row for row in artifacts}
        for contract in contracts:
            source = by_id[contract.candidate_id]
            self.assertEqual(contract.design_state_hash, source.governed_package_hash)
            self.assertEqual(contract.semantic_glb_sha256, source.glb_sha256)
            self.assertEqual(contract.authority_status, CONTRACT_AUTHORITY)
            self.assertFalse(contract.flight_dynamics_authority)

    def test_working_torch_cards_are_explicit_derived_inputs_not_flight_authority(self):
        artifact = compile_wayfarer_survivor_family()[0]
        contract = build_vehicle_dynamics_contract(artifact)
        self.assertEqual([row.mode for row in contract.torch_cards], ["ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"])
        self.assertTrue(all(row.authority_status == TORCH_CARD_AUTHORITY for row in contract.torch_cards))
        self.assertAlmostEqual(contract.torch_cards[-1].acceleration_g, 7.5)
        self.assertAlmostEqual(contract.torch_cards[-1].exhaust_velocity_km_s, 300.0)
        self.assertGreater(contract.torch_cards[-1].mass_flow_kg_s_at_contract_mass, 0.0)

    def test_unqualified_dynamics_fields_remain_open(self):
        contract = build_wayfarer_contract_family()[0]
        self.assertEqual(contract.inertia_tensor_status, OPEN)
        self.assertEqual(contract.attitude_control_status, OPEN)
        self.assertEqual(contract.thermal_duration_status, OPEN)
        self.assertEqual(contract.plume_geometry_status, OPEN)
        self.assertEqual(contract.metric_transport_contract_status, OPEN)
        self.assertEqual(contract.loom_transport_contract_status, OPEN)
        with self.assertRaises(VehicleDynamicsContractError):
            validate_vehicle_dynamics_contract(dataclasses.replace(contract, inertia_tensor_status="QUALIFIED"))

    def test_current_family_is_visually_distinct_but_not_yet_translationally_distinct(self):
        report = family_differentiation_report()
        self.assertGreaterEqual(report["candidate_count"], 2)
        self.assertGreaterEqual(report["distinct_design_state_count"], 2)
        self.assertGreaterEqual(report["distinct_semantic_glb_count"], 2)
        self.assertEqual(report["distinct_translational_signature_count"], 1)
        self.assertFalse(report["translational_mission_behavior_differentiated"])
        self.assertIn("FIXED_WET_MASS_REMASS_AND_TORCH_CARDS", report["reason_if_not_differentiated"])

    def test_contract_and_signature_are_deterministic(self):
        a = build_wayfarer_contract_family()
        b = build_wayfarer_contract_family()
        self.assertEqual([row.contract_hash for row in a], [row.contract_hash for row in b])
        self.assertEqual([translational_signature(row) for row in a], [translational_signature(row) for row in b])


if __name__ == "__main__":
    unittest.main()
