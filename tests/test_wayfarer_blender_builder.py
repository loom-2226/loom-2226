import importlib.util
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wayfarer_blender_builder", ROOT / "src" / "wayfarer_blender_builder.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BUILDER)


def fixture_payload():
    return {
        "components": [
            {
                "id": "pressure_hull",
                "kind": "cylinder_x",
                "center_m": [7.0, 0.0, 0.0],
                "dimensions": {"length_m": 14.0, "diameter_m": 8.6},
                "status": "DESIGN_BASELINE",
                "source": "pressure_hull.diameter_m",
                "group": "habitat",
            },
            {
                "id": "planetary_launch",
                "kind": "box",
                "center_m": [21.75, 0.0, 5.15],
                "dimensions": {"x_m": 10.5, "y_m": 3.9, "z_m": 3.1},
                "status": "DESIGN_BASELINE",
                "source": "launch.*",
                "group": "launch",
            },
            {
                "id": "radiator_1",
                "kind": "radiator_placeholder",
                "center_m": [35.5, 4.5, 0.0],
                "dimensions": {"root_length_m": 5.0, "panel_chord_m": 5.0, "azimuth_deg": 0.0},
                "status": "OPEN",
                "source": "radiator physical panel geometry OPEN",
                "group": "radiators",
            },
            {
                "id": "docking_collar",
                "kind": "collar_z",
                "center_m": [16.0, 0.0, -4.5],
                "dimensions": {"diameter_m": 1.6, "depth_m": 0.7},
                "status": "OPEN",
                "source": "docking diameter OPEN",
                "group": "docking",
            },
        ]
    }


class WayfarerBlenderBuilderTests(unittest.TestCase):
    def test_plan_is_importable_without_blender(self):
        self.assertIsNone(BUILDER.bpy)
        plan = BUILDER.build_plan(fixture_payload(), "DOCKED", "STOWED", False)
        self.assertEqual([p["id"] for p in plan], ["pressure_hull", "planetary_launch", "radiator_1"])

    def test_launch_absent_and_open_visibility(self):
        plan = BUILDER.build_plan(fixture_payload(), "ABSENT", "STOWED", True)
        ids = [p["id"] for p in plan]
        self.assertNotIn("planetary_launch", ids)
        self.assertIn("docking_collar", ids)

    def test_deployed_radiator_transform(self):
        plan = BUILDER.build_plan(fixture_payload(), "DOCKED", "DEPLOYED", False)
        radiator = next(p for p in plan if p["id"] == "radiator_1")
        self.assertEqual(radiator["primitive"]["size_m"], [5.0, 5.0, 0.12])
        self.assertAlmostEqual(radiator["center_m"][1], 12.5)
        self.assertAlmostEqual(radiator["center_m"][2], 0.0)

    def test_cylinder_x_rotation(self):
        plan = BUILDER.build_plan(fixture_payload(), "DOCKED", "STOWED", False)
        hull = next(p for p in plan if p["id"] == "pressure_hull")
        self.assertAlmostEqual(hull["rotation_euler_rad"][1], math.pi / 2.0)


if __name__ == "__main__":
    unittest.main()
