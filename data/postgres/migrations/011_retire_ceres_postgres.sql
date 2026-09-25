-- LOOM 2226 — governed Ceres PostgreSQL retirement.
-- This migration is intentionally fail-closed and only targets the qualified
-- Ceres snapshot.  Earth, Solar, Timeline, and retained Narrator/control
-- authority are not mutated by this script.
DO $$
DECLARE
  sid constant text := 'ceres-v1-0231e5f7da744728ab5021268b6f239b';
  snapshot_consumer constant text := '520af8926fddf5bcfd32f8937dfe92b37d55b33e';
  snapshot_query constant text := '4a8845a8ccc84ec83ade1aaaa734f6a850fe6bcae8608e2728f1ab65d834b46b';
  snapshot_semantic constant text := '4d0aef377ddb033d65d4a0eb5faf147b0bd455b8165570c39670046b332a9368';
  snapshot_contract constant text := '56cb302042ee379ac1d368dcf1bf633c4bb92b7241cb01c9d98c931264ed78e6';
  expected jsonb := '{
    "loom_world.entities":7,"loom_world.celestial_properties":1,"loom_world.celestial_dynamics":1,
    "loom_world.infrastructure_nodes":5,"loom_world.image_assets":6,"loom_world.knowledge_entities":6,
    "loom_civ.civ_census_node_relation":11,"loom_civ.civ_demographic_state":4,"loom_civ.civ_derivation":3,
    "loom_civ.civ_economic_state":1,"loom_civ.civ_governance_profile":5,"loom_civ.civ_influence_edge":55,
    "loom_civ.civ_infrastructure_state":5,"loom_civ.civ_model_run":2,"loom_civ.civ_place_dna":5,
    "loom_civ.civ_social_pressure":40,"loom_civ.civ_social_state":5,"loom_civ.civ_subject":349,
    "loom_civ.civ_workforce_state":1,"loom_media.ceres_manifest_asset":5,
    "loom_media.ceres_manifest_zone_relation":11,"loom_media.media_assets":6,
    "loom_control.field_semantics":293,"loom_control.row_lineage":534
  }'::jsonb;
  item record;
  actual bigint;
BEGIN
  IF (SELECT count(*) FROM loom_control.snapshot WHERE snapshot_id=sid) <> 1
     OR (SELECT state FROM loom_control.snapshot WHERE snapshot_id=sid) <> 'VALIDATED'
     OR (SELECT consumer_git_commit FROM loom_control.snapshot WHERE snapshot_id=sid) <> snapshot_consumer
     OR (SELECT consumer_query_sha256 FROM loom_control.snapshot WHERE snapshot_id=sid) <> snapshot_query
     OR (SELECT semantic_sha256 FROM loom_control.snapshot WHERE snapshot_id=sid) <> snapshot_semantic
     OR (SELECT contract_sha256 FROM loom_control.snapshot WHERE snapshot_id=sid) <> snapshot_contract
  THEN RAISE EXCEPTION 'Ceres retirement precondition failed: snapshot identity/state differs'; END IF;

  FOR item IN SELECT * FROM jsonb_each_text(expected) LOOP
    EXECUTE format('SELECT count(*) FROM %s WHERE snapshot_id=$1', item.key) INTO actual USING sid;
    IF actual <> item.value::bigint THEN
      RAISE EXCEPTION 'Ceres retirement precondition failed: % has %, expected %', item.key, actual, item.value;
    END IF;
    EXECUTE format('SELECT count(*) FROM %s', item.key) INTO actual;
    IF actual <> item.value::bigint THEN
      RAISE EXCEPTION 'Ceres retirement precondition failed: % contains non-Ceres rows', item.key;
    END IF;
  END LOOP;

  IF (SELECT count(*) FROM loom_control.snapshot_source WHERE snapshot_id=sid) <> 7
     OR (SELECT count(*) FROM loom_control.source_artifact a JOIN loom_control.snapshot_source s USING (artifact_sha256) WHERE s.snapshot_id=sid) <> 7
     OR (SELECT count(*) FROM loom_control.field_semantics WHERE snapshot_id=sid) <> 293
     OR (SELECT count(*) FROM loom_control.row_lineage WHERE snapshot_id=sid) <> 534
  THEN RAISE EXCEPTION 'Ceres retirement precondition failed: control reachability differs'; END IF;

  -- Ceres media/control dependents first.
  DELETE FROM loom_media.ceres_manifest_zone_relation WHERE snapshot_id=sid;
  DELETE FROM loom_media.ceres_manifest_asset WHERE snapshot_id=sid;
  DELETE FROM loom_media.media_assets WHERE snapshot_id=sid;

  -- Ceres CIVSTATE projection, then its registries and subjects.
  DELETE FROM loom_civ.civ_census_node_relation WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_demographic_state WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_economic_state WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_governance_profile WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_influence_edge WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_infrastructure_state WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_place_dna WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_social_pressure WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_social_state WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_workforce_state WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_derivation WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_model_run WHERE snapshot_id=sid;
  DELETE FROM loom_civ.civ_subject WHERE snapshot_id=sid;

  -- Ceres WORLD projection, respecting its explicit foreign-key topology.
  DELETE FROM loom_world.celestial_dynamics WHERE snapshot_id=sid;
  DELETE FROM loom_world.celestial_properties WHERE snapshot_id=sid;
  DELETE FROM loom_world.infrastructure_nodes WHERE snapshot_id=sid;
  DELETE FROM loom_world.image_assets WHERE snapshot_id=sid;
  DELETE FROM loom_world.knowledge_entities WHERE snapshot_id=sid;
  DELETE FROM loom_world.provenance_sources WHERE snapshot_id=sid;
  DELETE FROM loom_world.entities WHERE snapshot_id=sid;

  DELETE FROM loom_control.field_semantics WHERE snapshot_id=sid;
  DELETE FROM loom_control.row_lineage WHERE snapshot_id=sid;
  DELETE FROM loom_control.snapshot_source WHERE snapshot_id=sid;
  DELETE FROM loom_control.source_artifact a
    WHERE NOT EXISTS (SELECT 1 FROM loom_control.snapshot_source s WHERE s.artifact_sha256=a.artifact_sha256);
  DELETE FROM loom_control.semantic_version v
    WHERE v.semantic_sha256=snapshot_semantic
      AND NOT EXISTS (SELECT 1 FROM loom_control.snapshot s WHERE s.semantic_sha256=v.semantic_sha256);
  DELETE FROM loom_control.snapshot WHERE snapshot_id=sid;

  IF EXISTS (SELECT 1 FROM loom_control.snapshot WHERE snapshot_id=sid)
     OR EXISTS (SELECT 1 FROM loom_control.snapshot_source WHERE snapshot_id=sid)
     OR EXISTS (SELECT 1 FROM loom_world.entities WHERE snapshot_id=sid)
     OR EXISTS (SELECT 1 FROM loom_civ.civ_subject WHERE snapshot_id=sid)
     OR EXISTS (SELECT 1 FROM loom_media.media_assets WHERE snapshot_id=sid)
  THEN RAISE EXCEPTION 'Ceres retirement postcondition failed: target rows remain'; END IF;

  -- These schemas were proven Ceres-only above. Drop known objects explicitly;
  -- dependent objects are enumerated explicitly, so unexpected dependencies fail closed.
  DROP VIEW loom_ceres.celestial_dynamics, loom_ceres.celestial_properties,
    loom_ceres.civ_census_node_relation, loom_ceres.civ_demographic_state,
    loom_ceres.civ_derivation, loom_ceres.civ_economic_state,
    loom_ceres.civ_governance_profile, loom_ceres.civ_influence_edge,
    loom_ceres.civ_infrastructure_state, loom_ceres.civ_model_run,
    loom_ceres.civ_place_dna, loom_ceres.civ_runtime_place_context,
    loom_ceres.civ_social_pressure, loom_ceres.civ_social_state,
    loom_ceres.civ_subject, loom_ceres.civ_workforce_state,
    loom_ceres.entities, loom_ceres.image_assets, loom_ceres.infrastructure_nodes,
    loom_ceres.knowledge_entities, loom_ceres.media_assets,
    loom_ceres.provenance_sources, loom_ceres.v_graph_civstate_influence_edges;
  DROP SCHEMA loom_ceres;
  DROP TABLE loom_media.ceres_manifest_zone_relation, loom_media.ceres_manifest_asset, loom_media.media_assets;
  DROP SCHEMA loom_media;
  DROP VIEW loom_civ.civ_runtime_place_context, loom_civ.v_graph_civstate_influence_edges;
  DROP TABLE loom_civ.civ_census_node_relation, loom_civ.civ_demographic_state,
    loom_civ.civ_derivation, loom_civ.civ_economic_state, loom_civ.civ_governance_profile,
    loom_civ.civ_influence_edge, loom_civ.civ_infrastructure_state, loom_civ.civ_model_run,
    loom_civ.civ_place_dna, loom_civ.civ_social_pressure, loom_civ.civ_social_state,
    loom_civ.civ_subject, loom_civ.civ_workforce_state;
  DROP SCHEMA loom_civ;
  DROP TABLE loom_world.celestial_dynamics, loom_world.celestial_properties,
    loom_world.entities, loom_world.image_assets, loom_world.infrastructure_nodes,
    loom_world.knowledge_entities, loom_world.provenance_sources;
  DROP SCHEMA loom_world;
END $$;
