from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from loom.navigation.live_gravity_guidance_compare import (
    LIVE_GRAVITY_GUIDANCE_COMPARE_CONTRACT,
    compare_live_route_guidance,
)


class LiveGravityGuidanceCompareTests(unittest.TestCase):
    def test_live_sqlite_field_runs_d2h_without_mutating_route_contract(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/"LOOM_2226.sqlite3"
            c=sqlite3.connect(db)
            c.executescript('''
            CREATE TABLE entities(entity_id TEXT PRIMARY KEY, entity_class TEXT);
            CREATE TABLE celestial_dynamics(entity_id TEXT PRIMARY KEY, primary_gravity_parent_id TEXT, gm_km3_s2 REAL, mean_radius_km REAL, source TEXT);
            CREATE TABLE celestial_properties(entity_id TEXT PRIMARY KEY, gm_km3_s2 REAL, mean_radius_km REAL, source_id TEXT, status TEXT);
            CREATE TABLE states(entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT, x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,source TEXT,navigation_grade INTEGER);
            CREATE TABLE ephemeris_states(entity_id TEXT, epoch_utc TEXT, center_entity_id TEXT, center_command TEXT, reference_frame TEXT, reference_plane TEXT, units TEXT, x REAL,y REAL,z REAL,vx REAL,vy REAL,vz REAL,source TEXT,ephemeris_status TEXT,navigation_grade INTEGER);
            ''')
            c.executemany('INSERT INTO entities VALUES(?,?)',[('SOL','STAR'),('EA','PLANET')])
            c.executemany('INSERT INTO celestial_dynamics VALUES(?,?,?,?,?)',[
                ('SOL',None,132712440018.0,695700.0,'fixture'),
                ('EA','SOL',398600.435,6378.1,'fixture'),
            ])
            c.executemany('INSERT INTO celestial_properties VALUES(?,?,?,?,?)',[
                ('SOL',132712440018.0,695700.0,'fixture','TEST'),
                ('EA',398600.435,6378.1,'fixture','TEST'),
            ])
            c.execute('INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(
                'EA','2226-06-15T00:00:00Z','J2000','ECLIPTIC',1.0,0,0,0,0.01720209895,0,'fixture',1
            ))
            c.commit(); c.close()

            au=149597870.7
            trajectory={
                'authority':'PYTHON_AUTHORED_SEQUENCE_B',
                'coordinate_frame':'J2000_ECLIPTIC',
                'samples':[
                    {'sample_index':1,'epoch_utc':'2226-06-15T00:00:00Z',
                     'ordinary_pos_x_km':au+20000.0,'ordinary_pos_y_km':0.0,'ordinary_pos_z_km':0.0,
                     'ordinary_vel_x_km_s':0.0,'ordinary_vel_y_km_s':1.0,'ordinary_vel_z_km_s':0.0},
                    {'sample_index':2,'epoch_utc':'2226-06-15T00:01:00Z',
                     'ordinary_pos_x_km':au+20000.0,'ordinary_pos_y_km':60.0,'ordinary_pos_z_km':0.0,
                     'ordinary_vel_x_km_s':0.0,'ordinary_vel_y_km_s':1.0,'ordinary_vel_z_km_s':0.0},
                    {'sample_index':3,'epoch_utc':'2226-06-15T00:02:00Z',
                     'ordinary_pos_x_km':au+20000.0,'ordinary_pos_y_km':120.0,'ordinary_pos_z_km':0.0,
                     'ordinary_vel_x_km_s':0.0,'ordinary_vel_y_km_s':1.0,'ordinary_vel_z_km_s':0.0},
                ],
            }
            out=compare_live_route_guidance(trajectory,db,max_step_s=5.0,guidance_accel_limit_km_s2=0.02)
            self.assertEqual(out['contract'],LIVE_GRAVITY_GUIDANCE_COMPARE_CONTRACT)
            self.assertEqual(out['authority'],'DIAGNOSTIC_GUIDANCE_SHADOW_ONLY_NOT_ROUTE_AUTHORITY')
            self.assertFalse(out['qualification']['route_mutation'])
            self.assertFalse(out['qualification']['campaign_mutation'])
            self.assertFalse(out['reference_cutoff']['applied'])
            self.assertEqual(out['report']['sample_count'],3)
            self.assertGreater(out['report']['guidance_correction_delta_v_km_s'],0.0)
            self.assertLessEqual(out['report']['max_guidance_correction_km_s2'],0.02+1e-12)


if __name__ == '__main__':
    unittest.main()
