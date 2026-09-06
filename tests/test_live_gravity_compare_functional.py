from __future__ import annotations

from pathlib import Path
import sqlite3

from loom.navigation.live_gravity_compare import SQLiteDynamicGravityField


def test_moon_anchor_and_major_body_models_feed_one_live_field(tmp_path: Path):
    db=tmp_path/'LOOM_2226.sqlite3'; c=sqlite3.connect(db)
    c.executescript('''
    CREATE TABLE entities(entity_id TEXT PRIMARY KEY, entity_class TEXT);
    CREATE TABLE celestial_dynamics(entity_id TEXT PRIMARY KEY, primary_gravity_parent_id TEXT, gm_km3_s2 REAL, mean_radius_km REAL, source TEXT);
    CREATE TABLE celestial_properties(entity_id TEXT PRIMARY KEY, gm_km3_s2 REAL, mean_radius_km REAL, source_id TEXT, status TEXT);
    CREATE TABLE states(entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT, x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,source TEXT,navigation_grade INTEGER);
    CREATE TABLE ephemeris_states(entity_id TEXT, epoch_utc TEXT, center_entity_id TEXT, center_command TEXT, reference_frame TEXT, reference_plane TEXT, units TEXT, x REAL,y REAL,z REAL,vx REAL,vy REAL,vz REAL,source TEXT,ephemeris_status TEXT,navigation_grade INTEGER);
    ''')
    c.executemany('INSERT INTO entities VALUES(?,?)',[('SOL','STAR'),('EA','PLANET'),('MO','MOON')])
    c.executemany('INSERT INTO celestial_dynamics VALUES(?,?,?,?,?)',[('SOL',None,132712440018.0,695700.0,'fixture'),('EA','SOL',398600.435,6378.1,'fixture'),('MO','EA',4902.8,1737.4,'fixture')])
    c.executemany('INSERT INTO celestial_properties VALUES(?,?,?,?,?)',[('SOL',132712440018.0,695700.0,'fixture','TEST'),('EA',398600.435,6378.1,'fixture','TEST'),('MO',4902.8,1737.4,'fixture','TEST')])
    c.execute('INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',('EA','2226-06-15T00:00:00Z','J2000','ECLIPTIC',1.0,0,0,0,0.01720209895,0,'fixture',1))
    # Moon parent-centric circular-ish state in AU/AU-day.
    au=149597870.7; day=86400.0; r=384400.0; v=(398600.435/r)**0.5
    c.execute('INSERT INTO ephemeris_states VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',('MO','2200-01-01T00:00:00Z','EA','399','J2000','ECLIPTIC','AU / AU-day',r/au,0,0,0,v*day/au,0,'fixture-direct','JPL_HORIZONS_DIRECT',1))
    c.commit(); c.close()
    field=SQLiteDynamicGravityField(db,'2226-06-15T00:00:00Z')
    earth=field.resolve_state('EA','2226-06-15T00:00:30Z')
    moon=field.resolve_state('MO','2226-06-15T00:00:30Z')
    assert earth.provenance['state_source']=='PROPAGATED_OSCULATING_FOR_D2E'
    assert moon.provenance['state_source']=='PROPAGATED_OSCULATING_FOR_D2E'
    g=field.evaluator((earth.position_km[0]+20000.0,earth.position_km[1],earth.position_km[2]),'2226-06-15T00:00:30Z',minimum_acceleration_km_s2=0.0)
    ids={x.entity_id for x in g.contributions}
    assert {'SOL','EA','MO'} <= ids
