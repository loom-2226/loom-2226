from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from loom.navigation.gravity_shadow import GravityShadowError, ordinary_samples_from_route_trajectory
from loom.navigation.live_gravity_compare import compare_live_route_trajectory


def _db(path: Path) -> None:
    c=sqlite3.connect(path)
    c.executescript('''
    CREATE TABLE entities(entity_id TEXT PRIMARY KEY, entity_class TEXT);
    CREATE TABLE celestial_dynamics(entity_id TEXT PRIMARY KEY, primary_gravity_parent_id TEXT, gm_km3_s2 REAL, mean_radius_km REAL);
    CREATE TABLE celestial_properties(entity_id TEXT PRIMARY KEY, gm_km3_s2 REAL, mean_radius_km REAL, source_id TEXT, status TEXT);
    CREATE TABLE states(entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT, x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,source TEXT,navigation_grade INTEGER);
    CREATE TABLE ephemeris_states(entity_id TEXT, epoch_utc TEXT, center_entity_id TEXT, center_command TEXT, reference_frame TEXT, reference_plane TEXT, units TEXT, x REAL,y REAL,z REAL,vx REAL,vy REAL,vz REAL,source TEXT,ephemeris_status TEXT,navigation_grade INTEGER);
    ''')
    c.executemany('INSERT INTO entities VALUES(?,?)',[('SOL','STAR'),('EA','PLANET')])
    c.executemany('INSERT INTO celestial_dynamics VALUES(?,?,?,?)',[('SOL',None,132712440018.0,695700.0),('EA','SOL',398600.435,6378.1)])
    c.executemany('INSERT INTO celestial_properties VALUES(?,?,?,?,?)',[('SOL',132712440018.0,695700.0,'fixture','TEST'),('EA',398600.435,6378.1,'fixture','TEST')])
    c.execute('INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',('EA','2226-06-15T00:00:00Z','J2000','ECLIPTIC',1.0,0.0,0.0,0.0,0.01720209895,0.0,'fixture',1))
    c.commit(); c.close()


def _ordinary_row(index: int, epoch: str, x: float, y: float, vx: float = 0.0, vy: float = 29.78):
    return {
        'sample_index':index,'epoch_utc':epoch,
        'ordinary_pos_x_km':x,'ordinary_pos_y_km':y,'ordinary_pos_z_km':0.0,
        'ordinary_vel_x_km_s':vx,'ordinary_vel_y_km_s':vy,'ordinary_vel_z_km_s':0.0,
    }


def test_duplicate_terminal_epoch_same_state_collapses_to_later_sample():
    x=149597870.7+20000
    trajectory={'samples':[
        _ordinary_row(98,'2226-06-15T00:00:00Z',x,0.0),
        _ordinary_row(99,'2226-06-15T00:01:00Z',x,1786.8),
        _ordinary_row(100,'2226-06-15T00:01:00Z',x,1786.8),
    ]}
    samples=ordinary_samples_from_route_trajectory(trajectory)
    assert len(samples)==2
    assert samples[-1].sample_index==100


def test_duplicate_epoch_conflicting_state_fails_closed():
    x=149597870.7+20000
    trajectory={'samples':[
        _ordinary_row(98,'2226-06-15T00:00:00Z',x,0.0),
        _ordinary_row(99,'2226-06-15T00:01:00Z',x,1786.8),
        _ordinary_row(100,'2226-06-15T00:01:00Z',x,1787.8),
    ]}
    with pytest.raises(GravityShadowError, match='conflicting position/velocity'):
        ordinary_samples_from_route_trajectory(trajectory)


def test_live_compare_core_backed_shadow(tmp_path: Path):
    db=tmp_path/'LOOM_2226.sqlite3'; _db(db)
    trajectory={
        'authority':'PYTHON_AUTHORED_SEQUENCE_B','coordinate_frame':'J2000_ECLIPTIC','route_plan_id':'R1','solution_key':'X',
        'samples':[
            _ordinary_row(0,'2226-06-15T00:00:00Z',149597870.7+20000,0.0),
            _ordinary_row(1,'2226-06-15T00:01:00Z',149597870.7+20000,1786.8),
            _ordinary_row(2,'2226-06-15T00:02:00Z',149597870.7+20000,3573.6),
        ]
    }
    out=compare_live_route_trajectory(trajectory,db,max_step_s=20)
    assert out['contract']=='LOOM_NAV_PHYSICS_V2_LIVE_GRAVITY_COMPARE_V1'
    assert out['authority']=='DIAGNOSTIC_SHADOW_ONLY_NOT_ROUTE_AUTHORITY'
    assert out['report']['sample_count']==3
    assert out['report']['terminal_position_error_km']>0
    assert out['qualification']['campaign_mutation'] is False
    assert out['qualification']['display_fallbacks']=='REJECTED'

    d2f=out['characterization']
    assert d2f['contract']=='LOOM_NAV_PHYSICS_V2_D2F_CHARACTERIZATION_V1'
    assert d2f['duration_s']==120.0
    assert len(d2f['error_profile'])==3
    assert d2f['error_profile'][0]['elapsed_s']==0.0
    assert d2f['error_profile'][-1]['elapsed_s']==120.0
    assert d2f['position_error_growth_km_per_min']>0
    assert d2f['velocity_error_growth_m_s_per_min']>0
    assert 0.0 <= d2f['position_error_non_decreasing_fraction'] <= 1.0
    assert 0.0 <= d2f['velocity_error_non_decreasing_fraction'] <= 1.0
    assert isinstance(d2f['dominant_gravity_source_counts'],dict)
    assert d2f['reference_cutoff_penetration_km'] is None
