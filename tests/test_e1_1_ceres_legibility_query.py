import importlib.util
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "engineering" / "experience_one" / "spikes" / "e1_1_ceres_legibility_query.py"
spec = importlib.util.spec_from_file_location("e1_1_ceres_legibility_query", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _db(path: Path, script: str) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(script)
    conn.commit()
    conn.close()


def _fixture_state(epoch="2226-08-22T12:00:00Z", location="CERES"):
    return {
        "schema": "LOOM_STATE_V1",
        "state_id": "TEST",
        "state_sha256": "TEST_SHA",
        "revision": 0,
        "status": "QUALIFICATION_FIXTURE_NON_AUTHORITATIVE",
        "epoch_utc": epoch,
        "location_token": location,
        "kinematic_boundary": {"status": "BODY_RENDEZVOUS", "source": "TEST"},
        "ship_identity": {
            "ship_name": "wayfarer",
            "ship_instance_id": "TEST_SHIP",
            "ship_class": "WAYFARER",
            "ship_template": "WAYFARER_BASELINE",
        },
    }


def _build_dbs(tmp_path: Path):
    world = tmp_path / "world.sqlite3"
    civ = tmp_path / "civ.sqlite3"
    _db(
        world,
        """
        CREATE TABLE atlas_profiles(entity_id TEXT PRIMARY KEY,title TEXT,bio TEXT,synth TEXT,status TEXT,summary TEXT,source TEXT);
        INSERT INTO atlas_profiles VALUES('CER','Ceres','7.73M','4.46M','DERIVED CANON','Ceres is a major Belt exchange and industrial node.','Atlas');
        CREATE TABLE infrastructure_nodes(
          entity_id TEXT PRIMARY KEY,node_name TEXT,facility_type TEXT,traffic TEXT,
          commercial_1 TEXT,commercial_2 TEXT,commercial_regime TEXT,civil_authority TEXT,
          administrative_authority TEXT,security_authority TEXT,synthetic_constituency_1 TEXT,
          institutional_morphology TEXT,source TEXT,parent_entity_id TEXT
        );
        INSERT INTO infrastructure_nodes VALUES
        ('CER-P01','Occator Industrial Lift & Surface Port','SURFACE_PORT','HIGH','A','B','PLURAL','Ceres Commonwealth','Belt Standards Directorate','Belt Security & Rescue Directorate','SYNTH','NETWORK_COMPACT','WORLD','CER'),
        ('CER-P05','Ceres Metric & Loom Anchorage','STRATEGIC_PORT','RESTRICTED','Axiom Precision & Metrology','B','PLURAL','Ceres Commonwealth','Belt Standards Directorate','Belt Security & Rescue Directorate','SYNTH','NETWORK_COMPACT','WORLD','CER');
        CREATE TABLE region_mobility(region TEXT PRIMARY KEY,bulk_torch TEXT,metric_traffic TEXT,loom_access TEXT,shipbuilding TEXT,heavy_repair TEXT,metric_overhaul TEXT,feeder_density TEXT,transport_role TEXT,source TEXT);
        INSERT INTO region_mobility VALUES('Ceres + Belt network','EXTREME','MAJOR','PRIMARY GATE','PRIMARY','YES','LIMITED','EXTREME','Belt exchange and transport hub','Atlas');
        CREATE TABLE regional_morphology(system TEXT PRIMARY KEY,political_morphology TEXT,network_form TEXT,civil_authorities TEXT,administrative_authorities TEXT,security_authorities TEXT,source TEXT);
        INSERT INTO regional_morphology VALUES('Ceres','Commonwealth network polity','NETWORK_COMPACT','Ceres Commonwealth','Belt Standards Directorate','Belt Security & Rescue Directorate','Register');
        """,
    )
    _db(
        civ,
        """
        CREATE TABLE civ_runtime_place_context(
          subject_id TEXT,display_name TEXT,navigator_entity_id TEXT,governance_style TEXT,
          security_posture REAL,commercial_openness REAL,corporate_proxy_level REAL,local_autonomy REAL,
          institutional_trust REAL,synthetic_acceptance REAL,migration_openness REAL,frontier_mentality REAL,
          scarcity_pressure REAL,social_tension REAL,law_enforcement_reach REAL,data_sharing_level REAL,
          outsider_attitude TEXT,ultimate_sovereign TEXT,local_civil_authority TEXT,
          administrative_authority TEXT,security_provider TEXT,primary_owner_operator TEXT,
          resident_population REAL,transient_daily_population REAL,workforce REAL,annual_value_added REAL,
          power_average_mw REAL,cargo_throughput_tonnes_year REAL,strategic_importance REAL,
          economic_centrality REAL,transport_centrality REAL
        );
        INSERT INTO civ_runtime_place_context VALUES
        ('NODE:CER-P01','Occator Industrial Lift & Surface Port','CER-P01','CIVIC',.5,.7,.2,.6,.6,.7,.6,.5,.3,.2,.6,.6,'OPEN','Ceres Commonwealth','Ceres Commonwealth','Belt Standards Directorate','Belt Security & Rescue Directorate','A',100,20,80,1000,100,1000,.60,.70,.80),
        ('NODE:CER-P05','Ceres Metric & Loom Anchorage','CER-P05','CIVIC_ASSERTIVE',.875,.20,.4,.3,.5,.7,.4,.5,.2,.2,.9,.8,'GUARDED','Ceres Commonwealth','Ceres Commonwealth','Belt Standards Directorate','Belt Security & Rescue Directorate','Axiom Precision & Metrology',100,20,80,1000,100,1000,.95,.80,.90);
        CREATE TABLE civ_demographic_state(subject_id TEXT,year INTEGER,biological_population REAL,synthetic_population REAL,transient_population REAL,working_age_population REAL,median_age REAL,households REAL,derivation_id TEXT);
        INSERT INTO civ_demographic_state VALUES('BODY:CERES:CERES',2226,1,1,NULL,1,50,NULL,'D');
        CREATE TABLE civ_economic_state(subject_id TEXT,year INTEGER,value_added REAL,investment REAL,productive_capital REAL,infrastructure_capital REAL,productivity_index REAL,income_per_capita REAL,derivation_id TEXT);
        INSERT INTO civ_economic_state VALUES('BODY:CERES:CERES',2226,1,1,1,1,1,1,'D');
        """,
    )
    return world, civ


def test_positive_control_returns_grounded_orientation_and_interesting_items(tmp_path):
    world, civ = _build_dbs(tmp_path)
    result = mod.evaluate_legibility(_fixture_state(), world, civ, max_items=2)
    assert result["all_pass"] is True
    assert result["status"] == "EVALUATED"
    orient = result["questions"]["what_is_this_place"]
    interesting = result["questions"]["what_is_interesting_here"]
    assert orient["answer_kind"] == "ORIENTATION"
    assert orient["facts"]["identity"]["value"]["name"] == "Ceres"
    assert interesting["answer_kind"] == "INTERESTING_PLACES"
    assert [item["entity_id"] for item in interesting["items"]] == ["CER-P05", "CER-P01"]


def test_temporal_mismatch_blocks_before_query(tmp_path):
    world, civ = _build_dbs(tmp_path)
    result = mod.evaluate_legibility(_fixture_state(epoch="2027-01-01T00:00:00Z"), world, civ)
    assert result["all_pass"] is False
    assert result["status"] == "BLOCKED_BY_HANDOFF"
    assert result["handoff_status"] == "TEMPORAL_MISMATCH"


def test_unsupported_location_blocks_before_query(tmp_path):
    world, civ = _build_dbs(tmp_path)
    result = mod.evaluate_legibility(_fixture_state(location="MARS"), world, civ)
    assert result["all_pass"] is False
    assert result["status"] == "BLOCKED_BY_HANDOFF"
    assert result["handoff_status"] == "UNSUPPORTED_ENTITY"


def test_fixed_inputs_are_deterministic(tmp_path):
    world, civ = _build_dbs(tmp_path)
    a = mod.evaluate_legibility(_fixture_state(), world, civ, max_items=2)
    b = mod.evaluate_legibility(_fixture_state(), world, civ, max_items=2)
    assert a == b


def test_harness_preserves_zero_model_authority(tmp_path):
    world, civ = _build_dbs(tmp_path)
    result = mod.evaluate_legibility(_fixture_state(), world, civ)
    assert result["authority"]["model_called"] is False
    assert result["authority"]["model_calculation_authority"] == "ZERO"
    assert result["authority"]["model_state_authority"] == "ZERO"
    assert result["authority"]["model_canon_authority"] == "ZERO"
    assert result["authority"]["sources_merged"] is False
