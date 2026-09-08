from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

from design_requirements import RequirementsError  # noqa: E402
from ship_design_request import compile_ship_design_request  # noqa: E402


BASE_PAYLOAD = {
    "schema": "LOOM_2226_SHIP_DESIGN_REQUEST",
    "schema_version": "0.1",
    "ship_class": {
        "id": "TEST_FREIGHTER",
        "objective_priority": [
            "MINIMIZE_COST_PER_TONNE_KM",
            "MINIMIZE_DRY_MASS",
        ],
        "required_capabilities": ["CARGO_TRANSFER", "DOCKING"],
        "authority_status": "QUALIFICATION_ONLY",
        "provenance": "TEST_CLASS_v0.1",
    },
    "functional_requirements": {
        "cargo_mass_t": 1800,
        "cargo_volume_m3": 3200,
        "passengers": 12,
        "crew": 8,
        "endurance_days": 120,
        "normal_acceleration_g": 0.08,
        "docking_ports": 2,
        "planetary_landing_required": False,
    },
    "requirements_provenance": "TEST_MISSION_REQUEST_v0.1",
    "expected_derived_requirements": [
        "ship.required_habitable_volume",
        "ship.required_life_support_power",
        "ship.required_radiator_area",
    ],
    "derivation_rules": [],
}


class ShipDesignRequestTests(unittest.TestCase):
    def test_file_model_preserves_class_and_direct_functional_requirements(self):
        compiled = compile_ship_design_request(BASE_PAYLOAD)
        self.assertEqual(compiled.doctrine.doctrine_id, "TEST_FREIGHTER")
        direct = {row.requirement_id: row.value for row in compiled.direct_requirements}
        self.assertEqual(direct["ship.cargo_mass"], 1800.0)
        self.assertEqual(direct["ship.cargo_volume"], 3200.0)
        self.assertEqual(direct["ship.passengers"], 12.0)
        self.assertEqual(direct["ship.crew"], 8.0)
        self.assertEqual(direct["ship.docking_ports"], 2.0)
        self.assertEqual(direct["ship.planetary_landing_required"], 0.0)

    def test_expected_engineering_outputs_remain_open_without_rules(self):
        compiled = compile_ship_design_request(BASE_PAYLOAD)
        self.assertEqual(len(compiled.derived_requirements), 0)
        open_rows = {row.output_requirement_id: row.reason for row in compiled.open_derivations}
        self.assertEqual(
            open_rows,
            {
                "ship.required_habitable_volume": "NO_ADMITTED_DERIVATION_RULE",
                "ship.required_life_support_power": "NO_ADMITTED_DERIVATION_RULE",
                "ship.required_radiator_area": "NO_ADMITTED_DERIVATION_RULE",
            },
        )

    def test_explicit_rule_from_request_can_compile(self):
        payload = json.loads(json.dumps(BASE_PAYLOAD))
        payload["derivation_rules"] = [
            {
                "rule_id": "TEST_CREW_SERVICE_VOLUME",
                "input_requirement_id": "ship.crew",
                "output_requirement_id": "ship.test_service_volume",
                "coefficient": 10.0,
                "offset": 0.0,
                "output_unit": "m3",
                "output_relation": "MIN",
                "authority_status": "QUALIFICATION_ONLY",
                "provenance": "TEST_ONLY_RULE",
            }
        ]
        compiled = compile_ship_design_request(payload)
        derived = {row.requirement_id: row.value for row in compiled.derived_requirements}
        self.assertEqual(derived["ship.test_service_volume"], 80.0)

    def test_unknown_functional_field_fails_closed(self):
        payload = json.loads(json.dumps(BASE_PAYLOAD))
        payload["functional_requirements"]["magic_space_factor"] = 4
        with self.assertRaises(RequirementsError):
            compile_ship_design_request(payload)

    def test_cli_compiles_json_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "request.json"
            path.write_text(json.dumps(BASE_PAYLOAD), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SYNTHESIS / "ship_design_request.py"), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        parsed = json.loads(proc.stdout)
        self.assertEqual(parsed["doctrine"]["doctrine_id"], "TEST_FREIGHTER")
        self.assertEqual(len(parsed["derived_requirements"]), 0)
        self.assertEqual(len(parsed["open_derivations"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
