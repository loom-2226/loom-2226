from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

from design_requirements import (  # noqa: E402
    LinearDerivationRule,
    RequirementsError,
    canonical_json,
    compile_requirements,
)
from ship_requirements import (  # noqa: E402
    ShipMissionRequest,
    direct_requirements_from_ship_request,
    doctrine_profile,
)


class DesignRequirementsCompilerTests(unittest.TestCase):
    def setUp(self):
        self.doctrine = doctrine_profile(
            "TEST_INTERPLANETARY_FREIGHTER",
            objective_priority=(
                "MINIMIZE_COST_PER_TONNE_KM",
                "MINIMIZE_DRY_MASS",
                "MINIMIZE_TURNAROUND_TIME",
            ),
            required_capabilities=("CARGO_TRANSFER", "DOCKING"),
            provenance="TEST_DOCTRINE_v0.1",
        )

    def test_ship_request_is_direct_and_does_not_invent_downstream_physics(self):
        direct = direct_requirements_from_ship_request(
            ShipMissionRequest(cargo_mass_t=1800, cargo_volume_m3=3200, passengers=12, crew=8)
        )
        compiled = compile_requirements(
            direct,
            doctrine=self.doctrine,
            expected_outputs=(
                "ship.required_habitable_volume",
                "ship.required_life_support_power",
                "ship.required_radiator_area",
            ),
        )
        ids = {row.requirement_id for row in compiled.direct_requirements}
        self.assertEqual(
            ids,
            {"ship.cargo_mass", "ship.cargo_volume", "ship.passengers", "ship.crew"},
        )
        self.assertEqual(len(compiled.derived_requirements), 0)
        self.assertEqual(
            {row.output_requirement_id for row in compiled.open_derivations},
            {
                "ship.required_habitable_volume",
                "ship.required_life_support_power",
                "ship.required_radiator_area",
            },
        )

    def test_explicit_provenanced_rule_can_derive_requirement(self):
        direct = direct_requirements_from_ship_request(ShipMissionRequest(passengers=200))
        rule = LinearDerivationRule(
            rule_id="TEST_HAB_VOLUME_PER_PASSENGER",
            input_requirement_id="ship.passengers",
            output_requirement_id="ship.required_habitable_volume",
            coefficient=20.0,
            offset=0.0,
            output_unit="m3",
            output_relation="MIN",
            authority_status="QUALIFICATION_ONLY",
            provenance="TEST_ENGINEERING_RULE_v0.1",
        )
        compiled = compile_requirements(direct, doctrine=self.doctrine, rules=(rule,))
        self.assertEqual(len(compiled.derived_requirements), 1)
        row = compiled.derived_requirements[0]
        self.assertEqual(row.requirement_id, "ship.required_habitable_volume")
        self.assertEqual(row.value, 4000.0)
        self.assertIn("TEST_ENGINEERING_RULE_v0.1", row.provenance)
        self.assertIn("derived_from=ship.passengers", row.provenance)

    def test_open_rule_is_never_used(self):
        direct = direct_requirements_from_ship_request(ShipMissionRequest(passengers=200))
        rule = LinearDerivationRule(
            rule_id="OPEN_HAB_RULE",
            input_requirement_id="ship.passengers",
            output_requirement_id="ship.required_habitable_volume",
            coefficient=20.0,
            offset=0.0,
            output_unit="m3",
            output_relation="MIN",
            authority_status="OPEN",
            provenance="UNQUALIFIED_ESTIMATE",
        )
        compiled = compile_requirements(direct, doctrine=self.doctrine, rules=(rule,))
        self.assertEqual(len(compiled.derived_requirements), 0)
        self.assertEqual(compiled.open_derivations[0].reason, "RULE_OPEN_NOT_ADMITTED:OPEN_HAB_RULE")

    def test_rules_can_chain_deterministically(self):
        direct = direct_requirements_from_ship_request(ShipMissionRequest(passengers=10))
        rules = (
            LinearDerivationRule(
                "R2",
                "ship.required_habitable_volume",
                "ship.required_environmental_power",
                0.1,
                0.0,
                "MW",
                "MIN",
                "QUALIFICATION_ONLY",
                "TEST_R2",
            ),
            LinearDerivationRule(
                "R1",
                "ship.passengers",
                "ship.required_habitable_volume",
                20.0,
                0.0,
                "m3",
                "MIN",
                "QUALIFICATION_ONLY",
                "TEST_R1",
            ),
        )
        compiled = compile_requirements(direct, doctrine=self.doctrine, rules=rules)
        values = {row.requirement_id: row.value for row in compiled.derived_requirements}
        self.assertEqual(values["ship.required_habitable_volume"], 200.0)
        self.assertEqual(values["ship.required_environmental_power"], 20.0)

    def test_same_inputs_are_byte_deterministic(self):
        direct = direct_requirements_from_ship_request(
            ShipMissionRequest(cargo_mass_t=1800, crew=8, endurance_days=120)
        )
        a = compile_requirements(direct, doctrine=self.doctrine)
        b = compile_requirements(tuple(reversed(direct)), doctrine=self.doctrine)
        self.assertEqual(a.input_hash, b.input_hash)
        self.assertEqual(canonical_json(a), canonical_json(b))
        json.loads(canonical_json(a))

    def test_doctrine_is_preserved_as_priority_not_hidden_scalar_weight(self):
        direct = direct_requirements_from_ship_request(ShipMissionRequest(cargo_mass_t=1000))
        compiled = compile_requirements(direct, doctrine=self.doctrine)
        self.assertEqual(
            compiled.doctrine.objective_priority,
            (
                "MINIMIZE_COST_PER_TONNE_KM",
                "MINIMIZE_DRY_MASS",
                "MINIMIZE_TURNAROUND_TIME",
            ),
        )

    def test_invalid_negative_or_duplicate_input_fails_closed(self):
        with self.assertRaises(RequirementsError):
            direct_requirements_from_ship_request(ShipMissionRequest(cargo_mass_t=-1))

        direct = direct_requirements_from_ship_request(ShipMissionRequest(cargo_mass_t=1000))
        with self.assertRaises(RequirementsError):
            compile_requirements(direct + direct, doctrine=self.doctrine)

    def test_boolean_is_not_accepted_as_count(self):
        with self.assertRaises(RequirementsError):
            direct_requirements_from_ship_request(ShipMissionRequest(passengers=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
