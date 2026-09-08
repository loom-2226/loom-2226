-- LOOM 2226 Phase 4 minimal-3D Wayfarer overlay v0.1
-- ENGINEERING / QUALIFICATION only. NOT CANON. NOT PRODUCTION.
-- Every primitive retains source/status. OPEN details remain OPEN and are not promoted.

INSERT OR IGNORE INTO configuration_domain VALUES
('radiator_state','wayfarer','Major radiator configuration','STOWED','prov_geometry_seed');
INSERT OR IGNORE INTO configuration_state VALUES
('radiator_state','STOWED',1),
('radiator_state','DEPLOYING',1),
('radiator_state','DEPLOYED',1);

INSERT INTO physical_component(component_id,variant_id,parent_component_id,component_type,component_name,authority_status,provenance_id) VALUES
('g_pressure_hull','wayfarer',NULL,'GEOMETRY','Pressure hull geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_technical_core','wayfarer',NULL,'GEOMETRY','Technical core geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_tank_1','wayfarer',NULL,'GEOMETRY','Tank 1 geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_tank_2','wayfarer',NULL,'GEOMETRY','Tank 2 geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_tank_3','wayfarer',NULL,'GEOMETRY','Tank 3 geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_tank_4','wayfarer',NULL,'GEOMETRY','Tank 4 geometry','DESIGN_BASELINE','prov_geometry_seed'),
('g_longeron_1','wayfarer',NULL,'GEOMETRY','Longeron 1 geometry','DESIGN_BASELINE','prov_geometry_compiler'),
('g_longeron_2','wayfarer',NULL,'GEOMETRY','Longeron 2 geometry','DESIGN_BASELINE','prov_geometry_compiler'),
('g_longeron_3','wayfarer',NULL,'GEOMETRY','Longeron 3 geometry','DESIGN_BASELINE','prov_geometry_compiler'),
('g_longeron_4','wayfarer',NULL,'GEOMETRY','Longeron 4 geometry','DESIGN_BASELINE','prov_geometry_compiler'),
('g_launch_bay','wayfarer',NULL,'GEOMETRY','Integrated launch bay envelope','DESIGN_BASELINE','prov_geometry_seed'),
('g_relational_region','wayfarer',NULL,'GEOMETRY','Relational plant region','DESIGN_BASELINE','prov_geometry_seed'),
('g_shadow_shield','wayfarer',NULL,'GEOMETRY','Propulsion shadow shield','DESIGN_BASELINE','prov_geometry_seed'),
('g_reactor','wayfarer',NULL,'GEOMETRY','Reactor/torch envelope','DESIGN_BASELINE','prov_geometry_seed'),
('g_nozzle','wayfarer',NULL,'GEOMETRY','Magnetic nozzle envelope','DESIGN_BASELINE','prov_geometry_seed'),
('g_radiator_root_1','wayfarer',NULL,'GEOMETRY','Radiator root 1','OPEN','prov_geometry_seed'),
('g_radiator_root_2','wayfarer',NULL,'GEOMETRY','Radiator root 2','OPEN','prov_geometry_seed'),
('g_radiator_root_3','wayfarer',NULL,'GEOMETRY','Radiator root 3','OPEN','prov_geometry_seed'),
('g_radiator_root_4','wayfarer',NULL,'GEOMETRY','Radiator root 4','OPEN','prov_geometry_seed'),
('g_docking_marker','wayfarer',NULL,'GEOMETRY','Docking-side marker','OPEN','prov_geometry_seed');

INSERT INTO component_transform(component_id,tx_m,ty_m,tz_m,qw,qx,qy,qz,transform_model,configuration_domain_id,provenance_id) VALUES
('g_pressure_hull',7.0,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_technical_core',26.0,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_compiler'),
('g_tank_1',25.0,1.909188309,1.909188309,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_tank_2',25.0,-1.909188309,1.909188309,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_tank_3',25.0,-1.909188309,-1.909188309,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_tank_4',25.0,1.909188309,-1.909188309,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_longeron_1',32.0,2.45,0,1,0,0,0,'FIXED',NULL,'prov_geometry_compiler'),
('g_longeron_2',32.0,0,2.45,1,0,0,0,'FIXED',NULL,'prov_geometry_compiler'),
('g_longeron_3',32.0,-2.45,0,1,0,0,0,'FIXED',NULL,'prov_geometry_compiler'),
('g_longeron_4',32.0,0,-2.45,1,0,0,0,'FIXED',NULL,'prov_geometry_compiler'),
('g_launch_bay',21.75,0,5.35,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_relational_region',26.0,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_shadow_shield',40.5,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_reactor',46.5,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_nozzle',53.5,0,0,1,0,0,0,'FIXED',NULL,'prov_geometry_seed'),
('g_radiator_root_1',35.5,4.5,0,1,0,0,0,'FIXED','radiator_state','prov_geometry_seed'),
('g_radiator_root_2',35.5,0,4.5,1,0,0,0,'FIXED','radiator_state','prov_geometry_seed'),
('g_radiator_root_3',35.5,-4.5,0,1,0,0,0,'FIXED','radiator_state','prov_geometry_seed'),
('g_radiator_root_4',35.5,0,-4.5,1,0,0,0,'FIXED','radiator_state','prov_geometry_seed'),
('g_docking_marker',16.0,0,-4.5,1,0,0,0,'FIXED',NULL,'prov_geometry_seed');

INSERT INTO geometry_primitive(primitive_id,component_id,primitive_type,dimensions_json,local_pose_json,physical_roles_json,authority_status,provenance_id) VALUES
('p_pressure_hull','g_pressure_hull','CYLINDER_X','{"length_m":14.0,"diameter_m":8.6}',NULL,'["RENDER","COLLISION_PROXY"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_technical_core','g_technical_core','CYLINDER_X','{"length_m":24.0,"diameter_m":1.4}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_compiler'),
('p_tank_1','g_tank_1','CYLINDER_X','{"length_m":14.0,"diameter_m":3.0}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_tank_2','g_tank_2','CYLINDER_X','{"length_m":14.0,"diameter_m":3.0}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_tank_3','g_tank_3','CYLINDER_X','{"length_m":14.0,"diameter_m":3.0}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_tank_4','g_tank_4','CYLINDER_X','{"length_m":14.0,"diameter_m":3.0}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_longeron_1','g_longeron_1','BOX','{"x_m":36.0,"y_m":0.28,"z_m":0.28}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_compiler'),
('p_longeron_2','g_longeron_2','BOX','{"x_m":36.0,"y_m":0.28,"z_m":0.28}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_compiler'),
('p_longeron_3','g_longeron_3','BOX','{"x_m":36.0,"y_m":0.28,"z_m":0.28}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_compiler'),
('p_longeron_4','g_longeron_4','BOX','{"x_m":36.0,"y_m":0.28,"z_m":0.28}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_compiler'),
('p_launch_bay','g_launch_bay','BOX','{"x_m":11.5,"y_m":4.4,"z_m":3.5}',NULL,'["RENDER","INTERFERENCE_PROXY"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_relational_region','g_relational_region','CYLINDER_X','{"length_m":16.0,"diameter_m":1.4}',NULL,'["RENDER","REGION_PROXY"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_shadow_shield','g_shadow_shield','CYLINDER_X','{"length_m":5.0,"diameter_m":5.5}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_reactor','g_reactor','CYLINDER_X','{"length_m":7.0,"diameter_m":4.25}',NULL,'["RENDER"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_nozzle','g_nozzle','CYLINDER_X','{"length_m":7.0,"diameter_m":6.0}',NULL,'["RENDER","ENVELOPE_PROXY"]','DESIGN_BASELINE','prov_geometry_seed'),
('p_radiator_root_1','g_radiator_root_1','MARKER','{"root_x_start_m":33.0,"root_x_end_m":38.0}',NULL,'["STATUS_MARKER"]','OPEN','prov_geometry_seed'),
('p_radiator_root_2','g_radiator_root_2','MARKER','{"root_x_start_m":33.0,"root_x_end_m":38.0}',NULL,'["STATUS_MARKER"]','OPEN','prov_geometry_seed'),
('p_radiator_root_3','g_radiator_root_3','MARKER','{"root_x_start_m":33.0,"root_x_end_m":38.0}',NULL,'["STATUS_MARKER"]','OPEN','prov_geometry_seed'),
('p_radiator_root_4','g_radiator_root_4','MARKER','{"root_x_start_m":33.0,"root_x_end_m":38.0}',NULL,'["STATUS_MARKER"]','OPEN','prov_geometry_seed'),
('p_docking_marker','g_docking_marker','MARKER','{"x_center_m":16.0,"side":"-Z"}',NULL,'["STATUS_MARKER"]','OPEN','prov_geometry_seed');

INSERT INTO physical_component VALUES
('g_reference_envelope','wayfarer',NULL,'REFERENCE','Canonical overall/main-body reference envelope','CANON','prov_canon_v24');
INSERT INTO component_transform VALUES
('g_reference_envelope',28.5,0,0,1,0,0,0,'FIXED',NULL,'prov_canon_v24');
INSERT INTO geometry_primitive VALUES
('p_reference_envelope','g_reference_envelope','CYLINDER_X','{"length_m":57.0,"diameter_m":9.0}',NULL,'["REFERENCE_ENVELOPE"]','CANON','prov_canon_v24');
