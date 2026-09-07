PRAGMA foreign_keys = ON;

-- LOOM 2226 Phase 3 prototype only.
-- Generic ship-class physical authority schema implementing the Phase-2 v0.2 contract.
-- NOT production, NOT canon, Wayfarer-only seed target.

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE provenance_source (
    provenance_id TEXT PRIMARY KEY,
    authority_status TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_version TEXT,
    source_note TEXT
);

CREATE TABLE ship_class (
    ship_class_id TEXT PRIMARY KEY,
    ship_class_name TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    physical_model_version TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    valid_from TEXT,
    valid_until TEXT,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE ship_variant (
    variant_id TEXT PRIMARY KEY,
    ship_class_id TEXT NOT NULL REFERENCES ship_class(ship_class_id),
    variant_name TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE body_frame (
    frame_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES ship_variant(variant_id),
    origin_definition TEXT NOT NULL,
    axis_x_definition TEXT NOT NULL,
    axis_y_definition TEXT NOT NULL,
    axis_z_definition TEXT NOT NULL,
    handedness TEXT NOT NULL CHECK(handedness IN ('RIGHT','LEFT')),
    linear_unit TEXT NOT NULL DEFAULT 'm',
    angular_unit TEXT NOT NULL DEFAULT 'rad',
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE physical_component (
    component_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES ship_variant(variant_id),
    parent_component_id TEXT REFERENCES physical_component(component_id),
    component_type TEXT NOT NULL,
    component_name TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE component_transform (
    component_id TEXT PRIMARY KEY REFERENCES physical_component(component_id),
    tx_m REAL NOT NULL DEFAULT 0,
    ty_m REAL NOT NULL DEFAULT 0,
    tz_m REAL NOT NULL DEFAULT 0,
    qw REAL NOT NULL DEFAULT 1,
    qx REAL NOT NULL DEFAULT 0,
    qy REAL NOT NULL DEFAULT 0,
    qz REAL NOT NULL DEFAULT 0,
    transform_model TEXT NOT NULL DEFAULT 'FIXED',
    configuration_domain_id TEXT,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE configuration_domain (
    configuration_domain_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES ship_variant(variant_id),
    domain_name TEXT NOT NULL,
    initial_state TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE configuration_state (
    configuration_domain_id TEXT NOT NULL REFERENCES configuration_domain(configuration_domain_id),
    state_code TEXT NOT NULL,
    is_physically_present INTEGER NOT NULL DEFAULT 1 CHECK(is_physically_present IN (0,1)),
    PRIMARY KEY(configuration_domain_id, state_code)
);

CREATE TABLE configuration_transition (
    configuration_domain_id TEXT NOT NULL REFERENCES configuration_domain(configuration_domain_id),
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    transition_mode TEXT NOT NULL CHECK(transition_mode IN ('ATOMIC','KINEMATIC','EXTERNAL_SEQUENCE')),
    duration_s REAL,
    transition_model_version TEXT,
    preconditions_json TEXT,
    effects_json TEXT,
    PRIMARY KEY(configuration_domain_id, from_state, to_state)
);

CREATE TABLE component_state_rule (
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    configuration_domain_id TEXT NOT NULL REFERENCES configuration_domain(configuration_domain_id),
    state_code TEXT NOT NULL,
    active INTEGER NOT NULL CHECK(active IN (0,1)),
    PRIMARY KEY(component_id, configuration_domain_id, state_code)
);

CREATE TABLE geometry_primitive (
    primitive_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    primitive_type TEXT NOT NULL,
    dimensions_json TEXT NOT NULL,
    local_pose_json TEXT,
    physical_roles_json TEXT NOT NULL,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE mass_element (
    mass_element_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    mass_kind TEXT NOT NULL,
    reference_mass_kg REAL NOT NULL CHECK(reference_mass_kg >= 0),
    cx_m REAL NOT NULL DEFAULT 0,
    cy_m REAL NOT NULL DEFAULT 0,
    cz_m REAL NOT NULL DEFAULT 0,
    ixx_kg_m2 REAL,
    iyy_kg_m2 REAL,
    izz_kg_m2 REAL,
    ixy_kg_m2,
    ixz_kg_m2,
    iyz_kg_m2,
    inertia_reference TEXT NOT NULL DEFAULT 'CENTROID',
    inertia_frame TEXT NOT NULL DEFAULT 'COMPONENT_LOCAL',
    primitive_mass_model TEXT,
    mutable_store_id TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE mutable_store (
    store_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    substance_or_resource TEXT NOT NULL,
    capacity_kg REAL NOT NULL CHECK(capacity_kg >= 0),
    reference_quantity_kg REAL NOT NULL CHECK(reference_quantity_kg >= 0),
    minimum_protected_quantity_kg REAL CHECK(minimum_protected_quantity_kg >= 0),
    centroid_model_type TEXT NOT NULL,
    centroid_model_json TEXT,
    inertia_model_type TEXT NOT NULL,
    inertia_model_json TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id),
    CHECK(reference_quantity_kg <= capacity_kg),
    CHECK(minimum_protected_quantity_kg IS NULL OR minimum_protected_quantity_kg <= capacity_kg)
);

CREATE TABLE store_operational_label (
    store_id TEXT NOT NULL REFERENCES mutable_store(store_id),
    label_code TEXT NOT NULL,
    quantity_limit_kg REAL,
    semantics TEXT NOT NULL,
    PRIMARY KEY(store_id, label_code)
);

CREATE TABLE force_effector (
    effector_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    effector_type TEXT NOT NULL,
    ax_m REAL NOT NULL,
    ay_m REAL NOT NULL,
    az_m REAL NOT NULL,
    dx REAL NOT NULL,
    dy REAL NOT NULL,
    dz REAL NOT NULL,
    max_force_N REAL NOT NULL CHECK(max_force_N >= 0),
    min_force_N REAL,
    command_domain TEXT NOT NULL,
    command_units TEXT NOT NULL,
    command_limits_json TEXT NOT NULL,
    response_type TEXT NOT NULL,
    response_parameters_json TEXT,
    intrinsic_moment_model_json TEXT,
    mass_flow_model_json TEXT,
    gimbal_model_json TEXT,
    enabled_rule_json TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE effector_feed (
    effector_id TEXT NOT NULL REFERENCES force_effector(effector_id),
    store_id TEXT NOT NULL REFERENCES mutable_store(store_id),
    priority INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(effector_id, store_id)
);

CREATE TABLE attachment_interface (
    interface_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    interface_type TEXT NOT NULL,
    pose_json TEXT NOT NULL,
    capture_geometry_json TEXT,
    hard_dock_geometry_json TEXT,
    allowed_mates_json TEXT,
    load_limits_json TEXT,
    transfer_capabilities_json TEXT,
    state_machine_json TEXT NOT NULL,
    rigid_aggregation_state TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE torch_system (
    torch_system_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    effector_id TEXT REFERENCES force_effector(effector_id),
    nominal_axis_json TEXT NOT NULL,
    operating_modes_json TEXT NOT NULL,
    thrust_law_json TEXT NOT NULL,
    mass_flow_law_json TEXT NOT NULL,
    resource_store_id TEXT REFERENCES mutable_store(store_id),
    gimbal_limits_json TEXT,
    thermal_constraints_json TEXT,
    mutual_exclusion_constraints_json TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE metric_system (
    metric_system_id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES physical_component(component_id),
    hardware_membership_json TEXT NOT NULL,
    topology_identifiers_json TEXT,
    mc_applicability_json TEXT,
    bank_thermal_capability_json TEXT,
    operating_modes_json TEXT NOT NULL,
    configuration_prerequisites_json TEXT NOT NULL,
    certification_applicability_keys_json TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

CREATE TABLE reference_invariant (
    invariant_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES ship_variant(variant_id),
    invariant_type TEXT NOT NULL,
    expected_value_json TEXT NOT NULL,
    tolerance_json TEXT,
    authority_status TEXT NOT NULL,
    provenance_id TEXT NOT NULL REFERENCES provenance_source(provenance_id)
);

INSERT INTO metadata(key,value) VALUES
('schema_name','LOOM_2226_SHIPCLASSES_PROTOTYPE'),
('schema_version','0.1'),
('contract_version','0.2'),
('status','PHASE3_PROTOTYPE_NOT_PRODUCTION'),
('vehicle_scope','WAYFARER_ONLY');
