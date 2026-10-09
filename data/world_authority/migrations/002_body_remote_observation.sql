-- Build 7 Increment 3: an authorized REMOTE mission may characterize a body
-- before any surface location is selected. Existing location-scoped rows keep
-- their location foreign keys and their original meaning.
BEGIN;
ALTER TABLE wa_run.mission ALTER COLUMN target_location_id DROP NOT NULL;
ALTER TABLE wa_run.mission ADD CONSTRAINT mission_body_remote_scope CHECK (
    target_location_id IS NOT NULL OR
    (project_id IS NULL AND interaction_contract_ref = 'REMOTE:EXPLORATION_REQUEST_BODY_V1')
);
ALTER TABLE wa_run.observation ALTER COLUMN location_id DROP NOT NULL;
ALTER TABLE wa_run.observation ADD CONSTRAINT observation_body_remote_scope CHECK (
    location_id IS NOT NULL OR
    (mission_id IS NOT NULL AND method_ref = 'REMOTE'
     AND measurement_schema_ref = 'BODY_REMOTE_SIGNAL_V1')
);
CREATE FUNCTION wa_run.guard_body_remote_observation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    IF NEW.location_id IS NULL AND NOT EXISTS (
        SELECT 1 FROM wa_run.mission m
        WHERE m.run_id = NEW.run_id AND m.mission_id = NEW.mission_id
          AND m.world_id = NEW.world_id AND m.body_id = NEW.body_id
          AND m.target_location_id IS NULL AND m.project_id IS NULL
          AND m.interaction_contract_ref = 'REMOTE:EXPLORATION_REQUEST_BODY_V1'
    ) THEN
        RAISE EXCEPTION 'body-scoped observation requires a governed body-scoped REMOTE mission';
    END IF;
    RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER body_remote_observation_scope
AFTER INSERT ON wa_run.observation DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION wa_run.guard_body_remote_observation();
COMMIT;
