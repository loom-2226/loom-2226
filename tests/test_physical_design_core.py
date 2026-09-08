from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "qualification" / "synthesis" / "physical_design_core.py"
spec = importlib.util.spec_from_file_location("physical_design_core", CORE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load core from {CORE_PATH}")
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


class PhysicalDesignCoreTests(unittest.TestCase):
    def test_mass_com_and_partial_inertia_derive_from_candidate(self):
        ctype = core.PhysicalComponentType(
            "box", 12.0, core.BoxGeometry(2.0, 4.0, 6.0), "QUALIFICATION_ONLY", "fixture"
        )
        candidate = core.CandidateDesign(
            candidate_id="c",
            seed=1,
            component_types=(ctype,),
            component_instances=(
                core.PhysicalComponentInstance("body", "box", core.Transform((2.0, 0.0, 0.0))),
            ),
            point_masses=(
                core.PointMassContribution("unresolved", 8.0, (7.0, 0.0, 0.0), "OPEN", "fixture"),
            ),
        )
        mass, com, pa, centroidal, aggregate, unresolved = core.evaluate_mass_inertia(candidate)
        self.assertEqual(mass, 20.0)
        self.assertEqual(com, (4.0, 0.0, 0.0))
        self.assertAlmostEqual(unresolved, 0.4)
        self.assertGreater(centroidal[0][0], 0.0)
        self.assertGreater(pa[1][1], 0.0)
        self.assertGreater(aggregate[1][1], pa[1][1])

    def test_cylinder_box_collision_is_geometric_not_name_based(self):
        cyl = core.CylinderXGeometry(10.0, 2.0)
        box = core.BoxGeometry(4.0, 2.0, 2.0)
        a = core.PhysicalComponentInstance("a", "cyl", core.Transform((5.0, 0.0, 0.0)))
        b = core.PhysicalComponentInstance("b", "box", core.Transform((5.0, 0.0, 0.5)))
        c = core.PhysicalComponentInstance("c", "box", core.Transform((5.0, 0.0, 3.0)))
        self.assertTrue(core.bodies_collide(a, cyl, b, box))
        self.assertFalse(core.bodies_collide(a, cyl, c, box))

    def test_negative_nan_or_zero_geometry_fails_closed(self):
        with self.assertRaises(core.PhysicalDesignError):
            core.validate_geometry(core.BoxGeometry(float("nan"), 1.0, 1.0))
        with self.assertRaises(core.PhysicalDesignError):
            core.validate_geometry(core.CylinderXGeometry(0.0, 1.0))
        with self.assertRaises(core.PhysicalDesignError):
            core.centroidal_tensor(-1.0, core.BoxGeometry(1.0, 1.0, 1.0))

    def test_non_identity_body_orientation_fails_closed_in_s1_evaluator(self):
        angle = math.pi / 4.0
        q = (math.cos(angle / 2.0), 0.0, 0.0, math.sin(angle / 2.0))
        with self.assertRaises(core.PhysicalDesignError):
            core.validate_transform(core.Transform((0.0, 0.0, 0.0), q))


if __name__ == "__main__":
    unittest.main(verbosity=2)
