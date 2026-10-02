"""Private Atlas integrity and real HTTP boundary tests. No SQLite writes."""
import hashlib
import http.client
import importlib.util
import json
import shutil
import sqlite3
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ceres_atlas_server", ROOT / "tools/serve_ceres_atlas.py")
atlas = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(atlas)
MEDIA_SPEC = importlib.util.spec_from_file_location(
    "ceres_media_fixture", ROOT / "tests/create_ceres_media_fixture.py")
media_fixture = importlib.util.module_from_spec(MEDIA_SPEC)
MEDIA_SPEC.loader.exec_module(media_fixture)


@pytest.fixture(scope="module")
def media_db(tmp_path_factory):
    path = tmp_path_factory.mktemp("ceres-media") / "media.sqlite3"
    media_fixture.create_fixture(path)
    return path


@pytest.fixture(scope="module")
def server(media_db):
    instance = atlas.create_server(0, media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance
    instance.shutdown()
    instance.server_close()
    thread.join(timeout=3)


def request(server, path, method="GET", headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def test_projection_has_exact_identities_and_no_census_or_extra_fields():
    source = json.loads((ROOT / "docs/ceres/manifest.json").read_text())
    payload = atlas.load_manifest(ROOT)
    assert payload["schema_version"] == 1
    assert payload["source_sha256"] == atlas.MANIFEST_SHA256
    assert len(payload["facilities"]) == 5
    for original, projected in zip(source, payload["facilities"]):
        assert set(projected) == set(atlas.FIELDS)
        assert projected == {key: original[key] for key in atlas.FIELDS}
        assert "civstate_zones" not in projected


def test_media_projection_matches_world_identity_read_only():
    import sqlite3
    path = ROOT / "data/LOOM_2226.sqlite3"
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        for r in atlas.load_manifest(ROOT)["facilities"]:
            matches = con.execute("""
                SELECT k.spatial_entity_id, k.noun_id, a.media_key, a.content_hash,
                       a.byte_length, a.asset_role, a.review_status, a.is_current
                FROM image_assets a JOIN knowledge_entities k ON k.noun_id=a.entity_id
                WHERE a.asset_id=?
            """, (r["asset_id"],)).fetchall()
            assert matches == [(r["node_id"], r["noun_id"], r["media_key"], r["sha256"],
                                r["byte_length"], "HERO", "APPROVED_REFERENCE", 1)]
    finally:
        con.close()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_manifest_drift_refuses_startup(tmp_path):
    directory = tmp_path / "docs/ceres"
    directory.mkdir(parents=True)
    raw = (ROOT / "docs/ceres/manifest.json").read_bytes()
    (directory / "manifest.json").write_bytes(raw + b"\n")
    with pytest.raises(ValueError, match="snapshot"):
        atlas.create_server(0, root=tmp_path)


@pytest.mark.parametrize("path", ["/", "/index.html", "/style.css", "/app.mjs", "/model.mjs", "/manifest.json", "/atlas-data.json", "/healthz", "/assets/ceres-world-hero.png"])
def test_application_resources_are_available_with_local_only_policy(server, path):
    status, headers, content = request(server, path)
    assert server.server_address[0] == "127.0.0.1"
    assert status == 200 and content
    assert headers["Cache-Control"] == "no-store"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "connect-src 'self'" in headers["Content-Security-Policy"]
    assert "Access-Control-Allow-Origin" not in headers
    if path.endswith(".mjs"):
        assert headers["Content-Type"].startswith("text/javascript")


def test_world_hero_is_exact_approved_media_blob(server):
    status, headers, content = request(server, "/assets/ceres-world-hero.png")
    assert status == 200 and headers["Content-Type"] == "image/png"
    assert len(content) == 1261154
    assert hashlib.sha256(content).hexdigest() == "fa5fc5876d8f66631837ce498d77e139444b9247e8b2a66ff6dd8ad611e1f08e"


def test_http_images_are_exact_approved_bytes(server):
    for r in atlas.load_manifest(ROOT)["facilities"]:
        status, headers, content = request(server, "/images/" + r["filename"])
        assert status == 200 and headers["Content-Type"] == "image/png"
        assert len(content) == r["byte_length"]
        assert hashlib.sha256(content).hexdigest() == r["sha256"]


@pytest.mark.parametrize("path", [
    "/data/LOOM_2226.sqlite3", "/data/LOOM_2226_CIVSTATE.sqlite3", "/.git/config",
    "/docs/inspector/", "/docs/ceres/manifest.json", "/README.md",
    "/../data/LOOM_2226.sqlite3", "/%2e%2e/data/LOOM_2226.sqlite3",
    "/images/../../data/LOOM_2226.sqlite3", "/images/unknown.png",
])
def test_unlisted_resources_and_traversal_are_not_served(server, path):
    assert request(server, path)[0] == 404


def test_foreign_host_and_write_requests_rejected(server):
    assert request(server, "/", headers={"Host": "foreign.example"})[0] == 403
    assert request(server, "/manifest.json", method="POST")[0] == 501


def test_explicit_proxy_host_is_allowed_without_weakening_foreign_host_rejection(media_db):
    trusted_host = "ceres-atlas.tailnet.example"
    instance = atlas.create_server(0, media_db=media_db, allowed_hosts={trusted_host})
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, "/healthz", headers={"Host": trusted_host})[0] == 200
        assert request(instance, "/", headers={"Host": "foreign.example"})[0] == 403
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_head_returns_headers_without_body(server):
    status, headers, content = request(server, "/manifest.json", method="HEAD")
    assert status == 200 and int(headers["Content-Length"]) > 0 and content == b""


@pytest.mark.parametrize("condition", ["missing", "corrupt", "wrong_asset", "wrong_hash"])
def test_bad_media_row_returns_404_but_identity_remains_available(tmp_path, condition):
    path = tmp_path / "media.sqlite3"
    media_fixture.create_fixture(path)
    record = atlas.load_manifest(ROOT)["facilities"][0]
    with sqlite3.connect(path) as connection:
        if condition == "missing":
            connection.execute("DELETE FROM media_assets WHERE media_key=?", (record["media_key"],))
        elif condition == "corrupt":
            connection.execute("UPDATE media_assets SET original_blob=? WHERE media_key=?",
                               (b"not the approved image", record["media_key"]))
        elif condition == "wrong_asset":
            connection.execute("UPDATE media_assets SET asset_id='unapproved' WHERE media_key=?",
                               (record["media_key"],))
        else:
            connection.execute("UPDATE media_assets SET original_sha256='unapproved' WHERE media_key=?",
                               (record["media_key"],))
    instance = atlas.create_server(0, media_db=path)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, "/images/" + record["filename"])[0] == 404
        status, _, body = request(instance, "/manifest.json")
        assert status == 200 and json.loads(body)["facilities"][0]["node_id"] == "CER-P01"
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_unapproved_world_identity_is_never_served(tmp_path, media_db):
    world = tmp_path / "world.sqlite3"
    with sqlite3.connect(world) as connection:
        connection.execute("""CREATE TABLE image_assets (
            asset_id TEXT, entity_id TEXT, asset_role TEXT, review_status TEXT,
            media_key TEXT, content_hash TEXT, byte_length INTEGER, is_current INTEGER
        )""")
        record = atlas.BODY_HERO
        connection.execute("INSERT INTO image_assets VALUES (?,?,?,?,?,?,?,?)", (
            record["asset_id"], record["noun_id"], "HERO", "PENDING",
            record["media_key"], record["sha256"], record["byte_length"], 1,
        ))
    instance = atlas.create_server(0, world_db=world, media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, atlas.BODY_HERO_PATH)[0] == 404
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_missing_database_keeps_app_available_and_images_explicitly_unavailable(tmp_path):
    instance = atlas.create_server(0, media_db=tmp_path / "missing.sqlite3")
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, "/")[0] == 200
        assert request(instance, atlas.BODY_HERO_PATH)[0] == 404
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_requests_leave_all_three_databases_unchanged(server, media_db):
    world = ROOT / "data/LOOM_2226.sqlite3"
    civstate = ROOT / "data/LOOM_2226_CIVSTATE.sqlite3"
    before = (hashlib.sha256(world.read_bytes()).hexdigest(),
              hashlib.sha256(civstate.read_bytes()).hexdigest(),
              hashlib.sha256(media_db.read_bytes()).hexdigest())
    assert request(server, "/atlas-data.json")[0] == 200
    assert request(server, atlas.BODY_HERO_PATH)[0] == 200
    for record in atlas.load_manifest(ROOT)["facilities"]:
        assert request(server, "/images/" + record["filename"])[0] == 200
    after = (hashlib.sha256(world.read_bytes()).hexdigest(),
             hashlib.sha256(civstate.read_bytes()).hexdigest(),
             hashlib.sha256(media_db.read_bytes()).hexdigest())
    assert after == before


def test_live_atlas_projection_has_representative_values_nulls_and_sources(server):
    status, headers, raw = request(server, "/atlas-data.json")
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")
    payload = json.loads(raw)
    assert payload["schema_version"] == 1 and payload["epoch"] == 2226
    assert payload["world"]["entity_id"] == "CER"
    assert payload["world"]["mean_radius_km"] == pytest.approx(469.7)
    assert payload["body"]["demographic"]["biological_population"] == pytest.approx(7729118.998)
    assert payload["body"]["demographic"]["transient_population"] is None
    assert payload["body"]["economy"]["value_added"] == pytest.approx(5508368097289.042)
    occator = payload["facilities"]["CER-P01"]
    assert occator["identity"]["node_name"] == "Occator Industrial Lift & Surface Port"
    assert occator["runtime_context"]["navigator_node_id"] == "CER-P01"
    assert occator["infrastructure"]["resident_population"] == pytest.approx(24914.173528769374)
    assert occator["social"]["institutional_trust"] == pytest.approx(0.431)
    assert len(payload["zones"]) == 3
    assert payload["provenance"]["facilities"]["view"] == "civ_runtime_place_context"
    assert payload["support"]["transit_od_corridors"] == "UNSUPPORTED_PENDING_ENDPOINT_VALIDATION"


def test_health_check_verifies_all_three_read_only_boundaries(server):
    status, headers, raw = request(server, "/healthz")
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")
    assert json.loads(raw) == {"status": "ok", "epoch": 2226, "facilities": 5, "media_assets": 6}


def test_typed_relationships_are_reciprocal_and_navigable(server):
    payload = json.loads(request(server, "/atlas-data.json")[2])
    occator_edges = payload["facilities"]["CER-P01"]["institutions"]
    commonwealth_edge = next(edge for edge in occator_edges if edge["relationship"] == "civil authority")
    assert commonwealth_edge["institution_id"].startswith("NOUN:")
    dossier = payload["institutions"][commonwealth_edge["institution_id"]]
    assert dossier["name"] == "Ceres Commonwealth"
    assert {edge["facility_id"] for edge in dossier["facilities"]} == {
        "CER-P01", "CER-P02", "CER-P03", "CER-P04", "CER-P05"
    }
    assert all(edge["institution_id"] == dossier["id"] for edge in dossier["facilities"])


def test_missing_civstate_database_keeps_shell_available_and_data_unavailable(tmp_path, media_db):
    instance = atlas.create_server(0, civstate_db=tmp_path / "missing.sqlite3", media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, "/")[0] == 200
        assert request(instance, "/atlas-data.json")[0] == 404
        assert request(instance, "/healthz")[0] == 503
        assert request(instance, atlas.BODY_HERO_PATH)[0] == 200
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_disposable_civstate_change_updates_runtime_response_without_frontend_edit(tmp_path, media_db):
    authoritative = ROOT / "data/LOOM_2226_CIVSTATE.sqlite3"
    source_hash = hashlib.sha256(authoritative.read_bytes()).hexdigest()
    copy = tmp_path / "civstate-copy.sqlite3"
    shutil.copyfile(authoritative, copy)
    changed_value = 123456789.25
    with sqlite3.connect(copy) as connection:
        connection.execute("""
            UPDATE civ_economic_state SET value_added=?
            WHERE subject_id='BODY:CERES:CERES' AND year=2226
        """, (changed_value,))
        connection.execute("""
            UPDATE civ_infrastructure_state
            SET transient_daily_population=NULL, ship_calls_year=0
            WHERE node_subject_id='NODE:CER-P01' AND year=2226
        """)
    instance = atlas.create_server(0, civstate_db=copy, media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        payload = json.loads(request(instance, "/atlas-data.json")[2])
        assert payload["body"]["economy"]["value_added"] == changed_value
        assert payload["facilities"]["CER-P01"]["infrastructure"]["transient_daily_population"] is None
        assert payload["facilities"]["CER-P01"]["infrastructure"]["ship_calls_year"] == 0
        assert str(changed_value) not in (ROOT / "web/ceres-atlas/app.mjs").read_text()
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)
    assert hashlib.sha256(authoritative.read_bytes()).hexdigest() == source_hash


def test_missing_facility_measurement_row_is_returned_as_unavailable_data(tmp_path, media_db):
    copy = tmp_path / "civstate-copy.sqlite3"
    shutil.copyfile(ROOT / "data/LOOM_2226_CIVSTATE.sqlite3", copy)
    with sqlite3.connect(copy) as connection:
        connection.execute("""
            DELETE FROM civ_infrastructure_state
            WHERE node_subject_id='NODE:CER-P01' AND year=2226
        """)
    instance = atlas.create_server(0, civstate_db=copy, media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        payload = json.loads(request(instance, "/atlas-data.json")[2])
        assert payload["facilities"]["CER-P01"]["infrastructure"] is None
        assert payload["facilities"]["CER-P01"]["identity"]["node_id"] == "CER-P01"
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_missing_world_database_keeps_shell_available_and_data_unavailable(tmp_path, media_db):
    instance = atlas.create_server(0, world_db=tmp_path / "missing.sqlite3", media_db=media_db)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        assert request(instance, "/")[0] == 200
        assert request(instance, "/atlas-data.json")[0] == 404
        assert request(instance, atlas.BODY_HERO_PATH)[0] == 404
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=3)


def test_frontend_loads_runtime_projection_without_embedded_measurement_tables():
    source = (ROOT / "web/ceres-atlas/app.mjs").read_text()
    assert "fetch('atlas-data.json'" in source
    assert "const FACILITY_DATA" not in source
    assert "const METRICS" not in source
    assert "const INSTITUTIONS" not in source
    assert "5508368097289" not in source
    assert "243054451997" not in source
