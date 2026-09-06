from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest

from loom.spatial.sqlite_source import AU_KM, DAY_S, SQLiteSpatialStateSource


class SpatialSQLiteSourceTest(unittest.TestCase):
    def _db(self, root: Path) -> Path:
        path = root / "world.sqlite3"
        with sqlite3.connect(path) as conn:
            conn.executescript("""
            CREATE TABLE entities(entity_id TEXT PRIMARY KEY,name TEXT NOT NULL);
            CREATE TABLE states(
                entity_id TEXT,epoch_utc TEXT,reference_frame TEXT,reference_plane TEXT,
                x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,
                source TEXT,navigation_grade INTEGER
            );
            CREATE TABLE spatial_states(
                entity_id TEXT,epoch_utc TEXT,center_entity_id TEXT,reference_frame TEXT,
                x_km REAL,y_km REAL,z_km REAL,vx_km_s REAL,vy_km_s REAL,vz_km_s REAL,
                state_source TEXT,model_id TEXT,navigation_grade INTEGER,validity_status TEXT
            );
            """)
            conn.execute("INSERT INTO entities VALUES('EARTH','Earth')")
            conn.execute("INSERT INTO entities VALUES('NODE:ONE','Node One')")
            conn.execute("INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (
                'EARTH','2226-06-15T09:59:34Z','J2000','ECLIPTIC',1.0,2.0,3.0,0.1,0.2,0.3,'JPL_HORIZONS',1
            ))
            conn.execute("INSERT INTO spatial_states VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                'NODE:ONE','2226-06-15T09:59:34Z','EARTH','J2000/ECLIPTIC',10.0,20.0,30.0,1.0,2.0,3.0,
                'DERIVED_PLACEMENT_MODEL','M1',0,'PROVISIONAL'
            ))
        return path

    def test_snapshot_promotes_xyz_velocity_and_authority_metadata_read_only(self):
        with TemporaryDirectory() as td:
            path = self._db(Path(td))
            before = path.read_bytes()
            snapshot = SQLiteSpatialStateSource(path).snapshot(
                '2226-06-15T09:59:34.811247Z',
                campaign_revision=9,
                campaign_epoch_utc='2226-06-15T09:59:34.811247Z',
                epoch_source='CAMPAIGN_CLOCK',
            )
            self.assertEqual(snapshot['contract'], 'LOOM_SPATIAL_STATE_SNAPSHOT_V1')
            self.assertEqual(snapshot['epoch_utc'], '2226-06-15T09:59:34Z')
            self.assertEqual(snapshot['campaign_stamp']['revision'], 9)
            self.assertEqual(snapshot['counts']['total'], 2)
            self.assertEqual(snapshot['counts']['celestial'], 1)
            self.assertEqual(snapshot['counts']['infrastructure'], 1)
            earth = next(row for row in snapshot['states'] if row['entity_id'] == 'EARTH')
            self.assertAlmostEqual(earth['position_km'][0], AU_KM)
            self.assertAlmostEqual(earth['velocity_km_s'][0], 0.1 * AU_KM / DAY_S)
            self.assertTrue(earth['navigation_grade'])
            node = next(row for row in snapshot['states'] if row['entity_id'] == 'NODE:ONE')
            self.assertEqual(tuple(node['position_km']), (10.0, 20.0, 30.0))
            self.assertFalse(node['navigation_grade'])
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
