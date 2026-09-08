from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from shipclasses_geometry_resolver import resolve_geometry_primitive_poses, resolve_mass_centroids_B

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
OVERLAY = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for path in (SCHEMA, SEED, OVERLAY):
        conn.executescript(path.read_text(encoding="utf-8"))
    return conn


class WayfarerGeometryCouplingTests(unittest.TestCase):
    def test_launch_mass_and_geometry_share_transform(self):
        conn = db()
        mass_pose = resolve_mass_centroids_B(conn)["m_planetary_launch"]
        geometry_pose = resolve_geometry_primitive_poses(conn)["g_planetary_launch"][0]
        self.assertEqual(mass_pose, geometry_pose)
        self.assertEqual(mass_pose, (21.8, 0.0, 5.2))

    def test_one_transform_change_moves_both(self):
        conn = db()
        conn.execute("UPDATE component_transform SET tz_m=6.25 WHERE component_id='planetary_launch'")
        mass_pose = resolve_mass_centroids_B(conn)["m_planetary_launch"]
        geometry_pose = resolve_geometry_primitive_poses(conn)["g_planetary_launch"][0]
        self.assertEqual(mass_pose, geometry_pose)
        self.assertEqual(mass_pose, (21.8, 0.0, 6.25))


if __name__ == "__main__":
    unittest.main(verbosity=2)
