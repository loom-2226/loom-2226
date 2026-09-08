-- LOOM 2226 Phase 3 geometry-coupling overlay v0.1
-- Prototype only. Demonstrates one governed component transform driving
-- both the planetary-launch physical centroid and its low-detail geometry.
-- NOT CANON. NOT PRODUCTION.

UPDATE component_transform
SET tx_m=21.8, ty_m=0.0, tz_m=5.2, qw=1.0, qx=0.0, qy=0.0, qz=0.0,
    transform_model='FIXED', provenance_id='prov_geometry_seed'
WHERE component_id='planetary_launch';

UPDATE mass_element
SET cx_m=0.0, cy_m=0.0, cz_m=0.0
WHERE mass_element_id='m_planetary_launch';

INSERT OR REPLACE INTO geometry_primitive(
    primitive_id,component_id,primitive_type,dimensions_json,local_pose_json,
    physical_roles_json,authority_status,provenance_id
) VALUES (
    'g_planetary_launch',
    'planetary_launch',
    'BOX',
    '{"x_m":10.5,"y_m":3.9,"z_m":3.1}',
    '{"translation_m":[0.0,0.0,0.0],"quaternion_wxyz":[1.0,0.0,0.0,0.0]}',
    '["LOW_DETAIL_RENDER","INTERFERENCE_PLACEHOLDER"]',
    'DESIGN_BASELINE',
    'prov_geometry_seed'
);
