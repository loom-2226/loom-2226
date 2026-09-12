import importlib.util
import sqlite3
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "loom_canon_context_projection.py"
spec = importlib.util.spec_from_file_location("loom_canon_context_projection", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _db(path: Path, script: str) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(script)
    conn.commit()
    conn.close()


def test_ceres_projection_is_read_only_and_grounded(tmp_path):
    world = tmp_path / "world.sqlite3"
    civ = tmp_path / "civ.sqlite3"

    _db(
        world,
        """
        CREATE TABLE atlas_profiles(entity_id TEXT PRIMARY KEY,title TEXT,bio TEXT,synth TEXT,status TEXT,summary TEXT,source TEXT);
        INSERT INTO atlas_profiles VALUES('CER','Ceres','7.73M','4.46M','DERIVED CANON','Ceres summary','Atlas');

        CREATE TABLE infrastructure_nodes(
          entity_id TEXT PRIMARY KEY,node_name TEXT,facility_type TEXT,traffic TEXT,
          commercial_1 TEXT,commercial_2 TEXT,commercial_regime TEXT,civil_authority TEXT,
          administrative_authority TEXT,security_authority TEXT,synthetic_constituency_1 TEXT,
          institutional_morphology TEXT,source TEXT,parent_entity_id TEXT
        );
        INSERT INTO infrastructure_nodes VALUES(
          'CER-P03','Ceres Belt Exchange','ORBITAL_HABITAT_PORT','EXTREME',
          'Concord','Ferrum','PLURAL','Ceres Commonwealth','Belt Transit Authority',
          'Belt Security','Continuity Assembly','NETWORK_COMPACT','CANON I','CER'
        );

        CREATE TABLE region_mobility(
          region TEXT PRIMARY KEY,bulk_torch TEXT,metric_traffic TEXT,loom_access TEXT,
          shipbuilding TEXT,heavy_repair TEXT,metric_overhaul TEXT,feeder_density TEXT,
          transport_role TEXT,source TEXT
        );
        INSERT INTO region_mobility VALUES('Ceres + Belt network','EXTREME','MAJOR','PRIMARY GATE','PRIMARY','YES','LIMITED','EXTREME','exchange','Atlas');

        CREATE TABLE regional_morphology(
          system TEXT PRIMARY KEY,political_morphology TEXT,network_form TEXT,
          civil_authorities TEXT,administrative_authorities TEXT,security_authorities TEXT,source TEXT
        );
        INSERT INTO regional_morphology VALUES('Ceres','commonwealth','network','Ceres Commonwealth','Belt Transit Authority','Belt Security','Register');
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
          'NODE:CER-P03','Ceres Belt Exchange','CER-P03','NETWORK_COMPACT',
          .67,.46,.34,.37,.43,.61,.57,.44,.41,.63,.77,.56,.46,
          'Ceres Commonwealth','Ceres Commonwealth','Belt Transit Authority','Belt Security','Concord',
          94466,82362,241151,460790731912,9026,35900246,.78,.78,.845
        );

        CREATE TABLE civ_demographic_state(
          subject_id TEXT,year INTEGER,biological_population REAL,synthetic_population REAL,
          transient_population REAL,working_age_population REAL,median_age REAL,households REAL,
          derivation_id TEXT
        );
        INSERT INTO civ_demographic_state VALUES('BODY:CERES:CERES',2226,7729118,4456610,NULL,5425571,52,NULL,'D');

        CREATE TABLE civ_economic_state(
          subject_id TEXT,year INTEGER,value_added REAL,investment REAL,productive_capital REAL,
          infrastructure_capital REAL,productivity_index REAL,income_per_capita REAL,derivation_id TEXT
        );
        INSERT INTO civ_economic_state VALUES('BODY:CERES:CERES',2226,5508368097289,1487259386268,40914708986935,13092706875819,8.23,452034,'D');

        CREATE TABLE v_graph_civstate_influence_edges(
          subject_id TEXT,subject_name TEXT,actor_name TEXT,influence_domain TEXT,
          influence_weight REAL,control_class TEXT,basis TEXT,derivation_id TEXT
        );
        INSERT INTO v_graph_civstate_influence_edges VALUES('NODE:CER-P03','Ceres Belt Exchange','Ceres Commonwealth','GOVERNANCE',.9,'DIRECT','civil authority','D');

        CREATE TABLE v_graph_civstate_actor_exposure(
          actor_name TEXT,geography_name TEXT,geography_subject_id TEXT,sector_id TEXT,
          control_weight REAL,service_dependency_weight REAL,derivation_id TEXT
        );
        INSERT INTO v_graph_civstate_actor_exposure VALUES('Concord','Ceres Belt Exchange','NODE:CER-P03','ALL',.55,0,'D');
        """,
    )

    before_world = world.read_bytes()
    before_civ = civ.read_bytes()
    out = mod.build_projection(world, civ, "Ceres")
    assert out["schema"] == "LOOM_CANON_CONTEXT_PROJECTION_V1"
    assert out["entity"]["entity_id"] == "CER"
    assert out["availability"]["place_count"] == 1
    assert out["places"][0]["entity_id"] == "CER-P03"
    assert out["places"][0]["runtime_context"]["transport_centrality"] == 0.845
    assert out["influence_edges"][0]["actor_name"] == "Ceres Commonwealth"
    assert out["authority_policy"]["read_only"] is True
    assert world.read_bytes() == before_world
    assert civ.read_bytes() == before_civ


def test_projection_fails_closed_for_unsupported_entity(tmp_path):
    try:
        mod.build_projection(tmp_path / "w", tmp_path / "c", "Neptune")
    except ValueError as exc:
        assert "supports only Ceres" in str(exc)
    else:
        raise AssertionError("unsupported entity must fail closed")
