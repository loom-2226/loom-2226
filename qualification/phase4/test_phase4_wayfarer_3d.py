from __future__ import annotations
import sqlite3, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
P3=HERE.parent/"phase3"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(P3))

from minimal_3d import build_scene, scene_bounds
from shipclasses_resolver import compute_mass_properties

SCHEMA=P3/"LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED=P3/"LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
P3G=P3/"LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"
P4G=HERE/"LOOM_2226_SHIPCLASSES_WAYFARER_PHASE4_GEOMETRY_v0.1.sql"

def db():
    c=sqlite3.connect(":memory:"); c.row_factory=sqlite3.Row
    for p in (SCHEMA,SEED,P3G,P4G): c.executescript(p.read_text(encoding="utf-8"))
    return c

def prim(scene,pid):
    return next(p for p in scene["primitives"] if p["primitive_id"]==pid)

class Phase4Wayfarer3DTests(unittest.TestCase):
    def test_overall_and_main_body_reference(self):
        s=build_scene(db(),{"launch_state":"DOCKED","radiator_state":"STOWED"})
        b=scene_bounds(s)
        self.assertAlmostEqual(b["min_m"][0],0.0,places=12)
        self.assertAlmostEqual(b["max_m"][0],57.0,places=12)
        r=prim(s,"p_reference_envelope")
        self.assertEqual(r["dimensions"],{"length_m":57.0,"diameter_m":9.0})
        self.assertEqual(r["authority_status"],"CANON")
        self.assertNotIn("RENDER",r["physical_roles"])

    def test_four_tanks_and_major_regions(self):
        s=build_scene(db(),{"launch_state":"DOCKED","radiator_state":"STOWED"})
        tanks=[p for p in s["primitives"] if p["primitive_id"].startswith("p_tank_")]
        self.assertEqual(len(tanks),4)
        self.assertTrue(all(p["dimensions"]=={"length_m":14.0,"diameter_m":3.0} for p in tanks))
        self.assertEqual(prim(s,"p_relational_region")["pose_B"]["translation_m"],[26.0,0.0,0.0])
        self.assertEqual(prim(s,"p_shadow_shield")["pose_B"]["translation_m"],[40.5,0.0,0.0])
        self.assertEqual(prim(s,"p_reactor")["pose_B"]["translation_m"],[46.5,0.0,0.0])
        self.assertEqual(prim(s,"p_nozzle")["pose_B"]["translation_m"],[53.5,0.0,0.0])

    def test_launch_and_docking_side_semantics(self):
        s=build_scene(db(),{"launch_state":"DOCKED","radiator_state":"STOWED"})
        self.assertGreater(prim(s,"g_planetary_launch")["pose_B"]["translation_m"][2],0.0)
        d=prim(s,"p_docking_marker")
        self.assertLess(d["pose_B"]["translation_m"][2],0.0)
        self.assertEqual(d["dimensions"]["side"],"-Z")
        self.assertEqual(d["authority_status"],"OPEN")

    def test_radiator_geometry_stays_open_not_fabricated(self):
        s=build_scene(db(),{"launch_state":"DOCKED","radiator_state":"DEPLOYED"})
        roots=[p for p in s["primitives"] if p["primitive_id"].startswith("p_radiator_root_")]
        self.assertEqual(len(roots),4)
        for p in roots:
            self.assertEqual(p["authority_status"],"OPEN")
            self.assertEqual(p["dimensions"]["root_x_start_m"],33.0)
            self.assertEqual(p["dimensions"]["root_x_end_m"],38.0)
            self.assertNotIn("RENDER",p["physical_roles"])

    def test_launch_absent_affects_mass_and_scene(self):
        c=db()
        m=compute_mass_properties(c,{"launch_state":"ABSENT","radiator_state":"STOWED"})
        s=build_scene(c,{"launch_state":"ABSENT","radiator_state":"STOWED"})
        self.assertAlmostEqual(m["mass_kg"],1125500.0,places=6)
        self.assertFalse(any(p["primitive_id"]=="g_planetary_launch" for p in s["primitives"]))

    def test_critical_same_source_transform_changes_mass_and_render(self):
        c=db()
        before_m=compute_mass_properties(c,{"launch_state":"DOCKED","radiator_state":"STOWED"})
        before_s=build_scene(c,{"launch_state":"DOCKED","radiator_state":"STOWED"})
        z0=prim(before_s,"g_planetary_launch")["pose_B"]["translation_m"][2]
        c.execute("UPDATE component_transform SET tz_m=6.25 WHERE component_id='planetary_launch'")
        after_m=compute_mass_properties(c,{"launch_state":"DOCKED","radiator_state":"STOWED"})
        after_s=build_scene(c,{"launch_state":"DOCKED","radiator_state":"STOWED"})
        z1=prim(after_s,"g_planetary_launch")["pose_B"]["translation_m"][2]
        self.assertAlmostEqual(z0,5.2,places=12)
        self.assertAlmostEqual(z1,6.25,places=12)
        expected_dz_com=33000.0*(6.25-5.2)/1158500.0
        actual_dz_com=after_m["center_of_mass_B_m"][2]-before_m["center_of_mass_B_m"][2]
        self.assertAlmostEqual(actual_dz_com,expected_dz_com,places=12)

if __name__=="__main__":
    unittest.main(verbosity=2)
