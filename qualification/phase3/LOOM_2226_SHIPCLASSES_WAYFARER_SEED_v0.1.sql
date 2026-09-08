-- LOOM 2226 Phase 3 Wayfarer prototype seed v0.1
-- Derived only from live GitHub Wayfarer authority / current engineering baseline.
-- NOT CANON, NOT PRODUCTION.

INSERT INTO provenance_source VALUES
('prov_canon_v24','CANON','canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md','v2.4','Governing engineering/ships/operations canon'),
('prov_wayfarer_v24a','CANON','canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md','v2.4a','Governing Wayfarer launch-bay packaging amendment'),
('prov_geometry_seed','DESIGN_BASELINE','geometry/wayfarer_geometry_seed.sql','2026-09-06','Current deterministic Wayfarer geometry/mass seed'),
('prov_geometry_compiler','DERIVED','src/wayfarer_geometry.py','2026-09-06','Current deterministic Wayfarer mass/CoM compatibility model'),
('prov_phase3','DESIGN_BASELINE','qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql','v0.1','Phase-3 non-production mapping into generic contract');

INSERT INTO ship_class VALUES
('courier_ref','Reference Courier','0.2','phase3-wayfarer-v0.1','DESIGN_BASELINE',NULL,NULL,'prov_canon_v24');
INSERT INTO ship_variant VALUES
('wayfarer','courier_ref','Wayfarer','DESIGN_BASELINE','prov_canon_v24');

INSERT INTO body_frame VALUES
('wayfarer_body','wayfarer','Bow datum x=0 m; origin on thrust axis','+X forward-to-aft','+Y transverse','+Z transverse; launch-bay side','RIGHT','m','rad','prov_geometry_seed');

INSERT INTO configuration_domain VALUES
('launch_state','wayfarer','Planetary launch carried-state','DOCKED','prov_wayfarer_v24a');
INSERT INTO configuration_state VALUES
('launch_state','DOCKED',1),
('launch_state','EXTRACTING',1),
('launch_state','ABSENT',0);
INSERT INTO configuration_transition VALUES
('launch_state','DOCKED','EXTRACTING','KINEMATIC',NULL,'phase3-v0.1',NULL,NULL),
('launch_state','EXTRACTING','ABSENT','EXTERNAL_SEQUENCE',NULL,'phase3-v0.1',NULL,NULL),
('launch_state','ABSENT','DOCKED','EXTERNAL_SEQUENCE',NULL,'phase3-v0.1',NULL,NULL);

INSERT INTO physical_component VALUES
('structure','wayfarer',NULL,'STRUCTURE','Primary structure','DESIGN_BASELINE','prov_geometry_seed'),
('armor_fixed_shield','wayfarer',NULL,'STRUCTURE','Armor / fixed shield','DESIGN_BASELINE','prov_geometry_seed'),
('habitation_life_support','wayfarer',NULL,'EQUIPMENT','Habitation / life support','DESIGN_BASELINE','prov_geometry_seed'),
('relational_plant','wayfarer',NULL,'EQUIPMENT','Unified relational plant','CANON_MASS_DESIGN_POSITION','prov_geometry_seed'),
('thermal_radiators','wayfarer',NULL,'THERMAL','Thermal / radiators','DESIGN_BASELINE','prov_geometry_seed'),
('propulsion','wayfarer',NULL,'PROPULSION','Reactor / torch / nozzle propulsion group','DESIGN_BASELINE','prov_geometry_seed'),
('electrical','wayfarer',NULL,'EQUIPMENT','Electrical systems','DESIGN_BASELINE','prov_geometry_seed'),
('planetary_launch','wayfarer',NULL,'ATTACHED_VEHICLE','Planetary launch','DESIGN_BASELINE','prov_wayfarer_v24a'),
('avionics_sensors_comms','wayfarer',NULL,'EQUIPMENT','Avionics / sensors / comms','DESIGN_BASELINE','prov_geometry_seed'),
('rcs_docking_service','wayfarer',NULL,'EQUIPMENT','RCS / docking / service allowance','DESIGN_BASELINE','prov_geometry_seed'),
('mission_courier_systems','wayfarer',NULL,'EQUIPMENT','Mission / courier systems','DESIGN_BASELINE','prov_geometry_seed'),
('engineering_reserve','wayfarer',NULL,'RESERVE','Engineering reserve','DESIGN_BASELINE','prov_geometry_seed'),
('working_fluid_remass','wayfarer',NULL,'STORE','Normal remass-capable working-fluid inventory','DESIGN_BASELINE','prov_geometry_compiler'),
('protected_water','wayfarer',NULL,'STORE','Protected water reserve','DESIGN_BASELINE','prov_geometry_compiler');

INSERT INTO component_transform(component_id,tx_m,ty_m,tz_m,qw,qx,qy,qz,transform_model,configuration_domain_id,provenance_id)
SELECT component_id,0,0,0,1,0,0,0,'FIXED',CASE WHEN component_id='planetary_launch' THEN 'launch_state' ELSE NULL END,'prov_phase3'
FROM physical_component;

INSERT INTO component_state_rule VALUES
('planetary_launch','launch_state','DOCKED',1),
('planetary_launch','launch_state','EXTRACTING',1),
('planetary_launch','launch_state','ABSENT',0);

INSERT INTO mass_element(mass_element_id,component_id,mass_kind,reference_mass_kg,cx_m,cy_m,cz_m,authority_status,provenance_id) VALUES
('m_structure','structure','fixed_structure',150000,28,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_armor_fixed_shield','armor_fixed_shield','fixed_structure',105000,9.5,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_habitation_life_support','habitation_life_support','equipment',45000,8,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_relational_plant','relational_plant','equipment',88000,26,0,0,'CANON_MASS_DESIGN_POSITION','prov_geometry_seed'),
('m_thermal_radiators','thermal_radiators','equipment',90000,35,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_propulsion','propulsion','equipment',160000,46.5,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_electrical','electrical','equipment',55000,31,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_planetary_launch','planetary_launch','attached_vehicle',33000,21.8,0,5.2,'DESIGN_BASELINE','prov_geometry_seed'),
('m_avionics_sensors_comms','avionics_sensors_comms','equipment',20000,12,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_rcs_docking_service','rcs_docking_service','equipment',25000,28,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_mission_courier_systems','mission_courier_systems','equipment',20000,17,0,0,'DESIGN_BASELINE','prov_geometry_seed'),
('m_engineering_reserve','engineering_reserve','reserve',67500,28,0,0,'DESIGN_BASELINE','prov_geometry_seed');

INSERT INTO mutable_store VALUES
('store_normal_remass','working_fluid_remass','working_fluid_water',250000,250000,0,'FIXED','{"centroid_B_m":[25.0,0.0,0.0]}','POINT_MASS',NULL,'DESIGN_BASELINE','prov_geometry_compiler'),
('store_protected_water','protected_water','working_fluid_water',50000,50000,50000,'FIXED','{"centroid_B_m":[12.5,0.0,0.0]}','POINT_MASS',NULL,'DESIGN_BASELINE','prov_geometry_compiler');

INSERT INTO store_operational_label VALUES
('store_normal_remass','REMASS_CAPABLE',250000,'Physical quantity available to ordinary torch/remass accounting at reference state'),
('store_protected_water','PROTECTED_WATER',50000,'Protected reserve; same 300 t total working-fluid/water inventory family, not additive beyond this physical store');

INSERT INTO reference_invariant VALUES
('wayfarer_docked_dry_mass','wayfarer','TOTAL_MASS_KG','858500','{"abs_kg":1e-6}','CANON','prov_canon_v24'),
('wayfarer_docked_wet_mass','wayfarer','TOTAL_MASS_KG','1158500','{"abs_kg":1e-6}','CANON','prov_canon_v24'),
('wayfarer_docked_dry_com','wayfarer','CENTER_OF_MASS_M','[27.990564938846827,0.0,0.19988351776354105]','{"abs_m":1e-12}','DERIVED','prov_geometry_compiler'),
('wayfarer_docked_wet_com','wayfarer','CENTER_OF_MASS_M','[26.676650841605525,0.0,0.14812257229175657]','{"abs_m":1e-12}','DERIVED','prov_geometry_compiler'),
('wayfarer_absent_dry_mass','wayfarer','TOTAL_MASS_KG','825500','{"abs_kg":1e-6}','DERIVED','prov_geometry_compiler'),
('wayfarer_absent_wet_mass','wayfarer','TOTAL_MASS_KG','1125500','{"abs_kg":1e-6}','DERIVED','prov_geometry_compiler'),
('wayfarer_absent_dry_com','wayfarer','CENTER_OF_MASS_M','[28.238037552998183,0.0,0.0]','{"abs_m":1e-12}','DERIVED','prov_geometry_compiler'),
('wayfarer_absent_wet_com','wayfarer','CENTER_OF_MASS_M','[26.819635717458908,0.0,0.0]','{"abs_m":1e-12}','DERIVED','prov_geometry_compiler');
