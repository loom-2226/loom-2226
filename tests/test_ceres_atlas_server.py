"""Private Atlas integrity and real HTTP boundary tests. No SQLite writes."""
import hashlib
import http.client
import importlib.util
import json
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


def test_projection_matches_world_identity_without_using_db_at_runtime():
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


@pytest.mark.parametrize("path", ["/", "/index.html", "/style.css", "/app.mjs", "/model.mjs", "/manifest.json", "/assets/ceres-world-hero.png"])
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


def test_image_requests_leave_world_and_media_databases_unchanged(server, media_db):
    world = ROOT / "data/LOOM_2226.sqlite3"
    before = (hashlib.sha256(world.read_bytes()).hexdigest(),
              hashlib.sha256(media_db.read_bytes()).hexdigest())
    assert request(server, atlas.BODY_HERO_PATH)[0] == 200
    for record in atlas.load_manifest(ROOT)["facilities"]:
        assert request(server, "/images/" + record["filename"])[0] == 200
    after = (hashlib.sha256(world.read_bytes()).hexdigest(),
             hashlib.sha256(media_db.read_bytes()).hexdigest())
    assert after == before
