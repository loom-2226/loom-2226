import importlib.util
import sqlite3
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

spec = importlib.util.spec_from_file_location(
    "loom_current_place_handoff", SRC / "loom_current_place_handoff.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

operator_spec = importlib.util.spec_from_file_location(
    "loom_campaign_operator_context", SRC / "loom_campaign_operator_context.py"
)
operator_mod = importlib.util.module_from_spec(operator_spec)
assert operator_spec.loader is not None
operator_spec.loader.exec_module(operator_mod)


def _state(location="CERES", epoch="2226-08-22T12:00:00Z"):
    return {
        "schema": "LOOM_STATE_V1",
        "state_id": "TEST",
        "state_sha256": "TEST_SHA",
        "revision": 1,
        "status": "TEST",
        "epoch_utc": epoch,
        "location_token": location,
        "kinematic_boundary": {"status": "BODY_RENDEZVOUS", "source": "TEST"},
        "ship_identity": {
            "ship_name": "wayfarer",
            "ship_instance_id": "SHIP-TEST",
            "ship_class": "WAYFARER",
            "ship_template": "WAYFARER_BASELINE",
        },
    }


def _db(path: Path, script: str) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(script)
    conn.commit()
    conn.close()


def _ceres_dbs(tmp_path):
    world = tmp_path / "world.sqlite3"
    civ = tmp_path / "civ.sqlite3"
    _db(
        world,
        """
        CREATE TABLE atlas_profiles(entity_id TEXT PRIMARY KEY,title TEXT,bio TEXT,synth TEXT,status TEXT,summary TEXT,source TEXT);
        INSERT INTO atlas_profiles VALUES('CER','Ceres','1','1','DERIVED CANON','Ceres summary','Atlas');
        CREATE TABLE infrastructure_nodes(
          entity_id TEXT PRIMARY KEY,node_name TEXT,facility_type TEXT,traffic TEXT,
          commercial_1 TEXT,commercial_2 TEXT,commercial_regime TEXT,civil_authority TEXT,
          administrative_authority TEXT,security_authority TEXT,synthetic_constituency_1 TEXT,
          institutional_morphology TEXT,source TEXT,parent_entity_id TEXT
        );
        INSERT INTO infrastructure_nodes VALUES(
          'CER-P01','Ceres Port','PORT','HIGH','A','B','PLURAL','Ceres Commonwealth',
          'Admin','Security','Synth','NETWORK','CANON','CER'
        );
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
          outsider_attitude REAL,ultimate_sovereign TEXT,local_civil_authority TEXT,
          administrative_authority TEXT,security_provider TEXT,primary_owner_operator TEXT,
          resident_population REAL,transient_daily_population REAL,workforce REAL,annual_value_added REAL,
          power_average_mw REAL,cargo_throughput_tonnes_year REAL,strategic_importance REAL,
          economic_centrality REAL,transport_centrality REAL
        );
        INSERT INTO civ_runtime_place_context VALUES(
          'NODE:CER-P01','Ceres Port','CER-P01','NETWORK',.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,
          'Ceres Commonwealth','Ceres Commonwealth','Admin','Security','A',1,1,1,1,1,1,.5,.5,.5
        );
        CREATE TABLE civ_demographic_state(
          subject_id TEXT,year INTEGER,biological_population REAL,synthetic_population REAL,
          transient_population REAL,working_age_population REAL,median_age REAL,households REAL,derivation_id TEXT
        );
        INSERT INTO civ_demographic_state VALUES('BODY:CERES:CERES',2226,1,1,NULL,1,1,NULL,'D');
        CREATE TABLE civ_economic_state(
          subject_id TEXT,year INTEGER,value_added REAL,investment REAL,productive_capital REAL,
          infrastructure_capital REAL,productivity_index REAL,income_per_capita REAL,derivation_id TEXT
        );
        INSERT INTO civ_economic_state VALUES('BODY:CERES:CERES',2226,1,1,1,1,1,1,'D');
        """,
    )
    return world, civ


def test_unsupported_mars_surfaces_honest_human_boundary(tmp_path):
    op = operator_mod.project_campaign_operator_context(_state("MARS", "2027-06-15T08:57:51Z"))
    out = mod.resolve_current_place_handoff(op, tmp_path / "missing-world", tmp_path / "missing-civ")
    assert out["status"] == "UNSUPPORTED_ENTITY"
    assert out["canon_context"] is None
    assert "unavailable" in out["human_message"].lower()
    assert "MARS" in out["human_message"]
    assert out["authority_policy"]["sources_merged"] is False


def test_supported_ceres_fails_closed_on_epoch_mismatch(tmp_path):
    world, civ = _ceres_dbs(tmp_path)
    op = operator_mod.project_campaign_operator_context(_state("CERES", "2027-06-15T08:57:51Z"))
    out = mod.resolve_current_place_handoff(op, world, civ)
    assert out["status"] == "TEMPORAL_MISMATCH"
    assert out["current_location"]["campaign_year"] == 2027
    assert out["canon_reference_year"] == 2226
    assert out["canon_context"] is None
    assert "does not match" in out["human_message"]


def test_supported_ceres_positive_control_when_temporally_aligned(tmp_path):
    world, civ = _ceres_dbs(tmp_path)
    op = operator_mod.project_campaign_operator_context(_state("CERES", "2226-08-22T12:00:00Z"))
    out = mod.resolve_current_place_handoff(op, world, civ)
    assert out["status"] == "AVAILABLE"
    assert out["canon_reference_year"] == 2226
    assert out["canon_context"]["schema"] == "LOOM_CANON_CONTEXT_PROJECTION_V1"
    assert out["canon_context"]["entity"]["entity_id"] == "CER"
    assert out["authority_policy"]["sources_merged"] is False


def test_non_available_status_never_exposes_rejected_canon_payload(tmp_path):
    world, civ = _ceres_dbs(tmp_path)
    op = operator_mod.project_campaign_operator_context(_state("CERES", "2027-01-01T00:00:00Z"))
    out = mod.resolve_current_place_handoff(op, world, civ)
    assert out["status"] != "AVAILABLE"
    assert out["canon_context"] is None


def test_handoff_does_not_mutate_operator_context(tmp_path):
    world, civ = _ceres_dbs(tmp_path)
    op = operator_mod.project_campaign_operator_context(_state())
    before = deepcopy(op)
    mod.resolve_current_place_handoff(op, world, civ)
    assert op == before


def test_bad_operator_authority_fails_closed(tmp_path):
    op = operator_mod.project_campaign_operator_context(_state())
    op["authority_policy"]["model_state_authority"] = "NONZERO"
    try:
        mod.resolve_current_place_handoff(op, tmp_path / "w", tmp_path / "c")
    except mod.CurrentPlaceHandoffError as exc:
        assert "ZERO" in str(exc)
    else:
        raise AssertionError("authority violation must fail closed")
