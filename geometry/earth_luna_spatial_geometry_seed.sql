PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS spatial_objects (
    object_id TEXT PRIMARY KEY,
    object_kind TEXT NOT NULL CHECK (object_kind IN ('FACILITY','STANDARD_ORBIT')),
    world_entity_id TEXT,
    display_name TEXT NOT NULL,
    parent_body_id TEXT NOT NULL,
    operational_role TEXT NOT NULL,
    status TEXT NOT NULL,
    source_class TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS facility_world_bindings (
    object_id TEXT PRIMARY KEY REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    world_entity_id TEXT NOT NULL UNIQUE,
    imported_name TEXT NOT NULL,
    imported_parent_body_id TEXT NOT NULL,
    facility_type TEXT,
    system TEXT,
    traffic TEXT,
    civil_authority TEXT,
    administrative_authority TEXT,
    security_authority TEXT
);

CREATE TABLE IF NOT EXISTS standard_orbits (
    object_id TEXT PRIMARY KEY REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    representation TEXT NOT NULL,
    epoch_utc TEXT NOT NULL,
    semi_major_axis_km REAL,
    altitude_km REAL,
    eccentricity REAL NOT NULL DEFAULT 0.0,
    inclination_deg REAL NOT NULL DEFAULT 0.0,
    raan_deg REAL NOT NULL DEFAULT 0.0,
    arg_periapsis_deg REAL NOT NULL DEFAULT 0.0,
    mean_anomaly_deg REAL NOT NULL DEFAULT 0.0,
    reference_frame TEXT NOT NULL,
    navigation_grade INTEGER NOT NULL DEFAULT 0,
    epistemic_status TEXT NOT NULL,
    derivation_note TEXT
);

CREATE TABLE IF NOT EXISTS local_frames (
    frame_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    frame_role TEXT NOT NULL,
    handedness TEXT NOT NULL DEFAULT 'RIGHT_HANDED',
    x_axis TEXT NOT NULL,
    y_axis TEXT NOT NULL,
    z_axis TEXT NOT NULL,
    orientation_rule TEXT NOT NULL,
    navigation_authority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    UNIQUE(object_id, frame_role)
);

CREATE TABLE IF NOT EXISTS geometry_assets (
    asset_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    geometry_role TEXT NOT NULL,
    mime_type TEXT,
    asset_uri TEXT,
    asset_sha256 TEXT,
    asset_blob BLOB,
    lod_level INTEGER,
    scale_m_per_unit REAL,
    navigation_authority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    provenance TEXT,
    CHECK (asset_uri IS NOT NULL OR asset_blob IS NOT NULL OR geometry_role='HUD_SYMBOLIC')
);

CREATE TABLE IF NOT EXISTS operational_interfaces (
    interface_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    interface_type TEXT NOT NULL,
    local_frame_id TEXT REFERENCES local_frames(frame_id),
    x_m REAL NOT NULL DEFAULT 0.0,
    y_m REAL NOT NULL DEFAULT 0.0,
    z_m REAL NOT NULL DEFAULT 0.0,
    axis_x REAL,
    axis_y REAL,
    axis_z REAL,
    compatibility_class TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS approach_corridors (
    corridor_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    interface_id TEXT REFERENCES operational_interfaces(interface_id),
    local_frame_id TEXT REFERENCES local_frames(frame_id),
    shape_type TEXT NOT NULL,
    start_x_m REAL,
    start_y_m REAL,
    start_z_m REAL,
    end_x_m REAL,
    end_y_m REAL,
    end_z_m REAL,
    radius_m REAL,
    navigation_authority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS keepout_volumes (
    volume_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    local_frame_id TEXT REFERENCES local_frames(frame_id),
    shape_type TEXT NOT NULL,
    center_x_m REAL NOT NULL DEFAULT 0.0,
    center_y_m REAL NOT NULL DEFAULT 0.0,
    center_z_m REAL NOT NULL DEFAULT 0.0,
    radius_m REAL,
    size_x_m REAL,
    size_y_m REAL,
    size_z_m REAL,
    navigation_authority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS visual_profiles (
    object_id TEXT PRIMARY KEY REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
    hero_media_entity_id TEXT,
    default_symbol TEXT,
    orbit_render_style TEXT,
    minimum_pixel_radius REAL,
    label_priority INTEGER NOT NULL DEFAULT 0,
    render_near_km REAL,
    render_far_km REAL,
    status TEXT NOT NULL,
    notes TEXT
);

-- Standard operational orbit targets are navigation references, not infrastructure.
-- Semi-major axes are derived at build time from authoritative body radius where
-- available. Altitude values remain explicit here because they define the target.
INSERT OR REPLACE INTO spatial_objects VALUES
('ORB-EA-VLEO-250','STANDARD_ORBIT',NULL,'Earth Very Low Orbit 250 km','EA','PARKING_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-EA-LEO-400','STANDARD_ORBIT',NULL,'Earth Low Orbit 400 km','EA','PARKING_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-EA-POLAR-500','STANDARD_ORBIT',NULL,'Earth Polar Orbit 500 km','EA','POLAR_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-EA-HLEO-1500','STANDARD_ORBIT',NULL,'Earth High LEO 1500 km','EA','HIGH_LEO_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-EA-MEO-20200','STANDARD_ORBIT',NULL,'Earth Medium Orbit 20200 km','EA','MEO_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-EA-GEO-REF','STANDARD_ORBIT',NULL,'Earth Geosynchronous Reference Orbit','EA','GEOSYNCHRONOUS_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Reference altitude/orbit; longitude station-keeping requires Earth orientation model'),
('ORB-LU-LLO-100','STANDARD_ORBIT',NULL,'Lunar Low Orbit 100 km','LU','LUNAR_PARKING_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-LU-POLAR-100','STANDARD_ORBIT',NULL,'Lunar Polar Orbit 100 km','LU','LUNAR_POLAR_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target'),
('ORB-LU-HIGH-1000','STANDARD_ORBIT',NULL,'Lunar High Circular Orbit 1000 km','LU','LUNAR_HIGH_REFERENCE','ENGINEERING_REFERENCE','SPATIAL_GEOMETRY_SEED','earth_luna_spatial_geometry_seed.sql','Unoccupied standard orbit target');

INSERT OR REPLACE INTO standard_orbits VALUES
('ORB-EA-VLEO-250','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,250.0,0.0,28.5,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Standard target altitude; not a claim of persistent traffic occupancy'),
('ORB-EA-LEO-400','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,400.0,0.0,28.5,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Existing HUD qualification altitude promoted to first-class standard target'),
('ORB-EA-POLAR-500','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,500.0,0.0,90.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Polar operational reference'),
('ORB-EA-HLEO-1500','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,1500.0,0.0,28.5,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','High-LEO operational reference'),
('ORB-EA-MEO-20200','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,20200.0,0.0,55.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','MEO operational reference'),
('ORB-EA-GEO-REF','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,35786.0,0.0,0.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Geosynchronous-altitude reference only until body-fixed longitude/orientation runtime is qualified'),
('ORB-LU-LLO-100','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,100.0,0.0,30.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Lunar parking orbit reference'),
('ORB-LU-POLAR-100','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,100.0,0.0,90.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Lunar polar parking orbit reference'),
('ORB-LU-HIGH-1000','CIRCULAR_ALTITUDE','2226-01-01T00:00:00Z',NULL,1000.0,0.0,30.0,0.0,0.0,0.0,'J2000/ECLIPTIC',0,'ENGINEERING_REFERENCE','Lunar high circular operational reference');

INSERT OR REPLACE INTO geometry_assets(asset_id,object_id,geometry_role,status,provenance)
SELECT 'HUDSYM:'||object_id,object_id,'HUD_SYMBOLIC','ENGINEERING_REFERENCE','Generated symbolic orbit/facility representation; not navigation geometry'
FROM spatial_objects;

INSERT OR REPLACE INTO visual_profiles(object_id,default_symbol,orbit_render_style,label_priority,status,notes)
SELECT object_id,
       CASE WHEN object_kind='STANDARD_ORBIT' THEN 'ORBIT_RING' ELSE 'FACILITY' END,
       CASE WHEN object_kind='STANDARD_ORBIT' THEN 'REFERENCE_RING' ELSE NULL END,
       CASE WHEN object_kind='STANDARD_ORBIT' THEN 20 ELSE 50 END,
       'ENGINEERING_REFERENCE',
       'HUD defaults only; richer media/GLB bindings may override render representation'
FROM spatial_objects;
