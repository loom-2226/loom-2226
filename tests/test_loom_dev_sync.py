from pathlib import Path
import json

from loom_dev_sync import discover_sources, sync


def test_dev_sync_only_copies_application_allowlist(tmp_path):
    repo = tmp_path / "repo"
    app = tmp_path / "runtime"
    (repo / "src/loom/application").mkdir(parents=True)
    (repo / "src/loom/application/contracts.py").write_text("x=1\n")
    (repo / "src/loom_gis.py").write_text("gis=1\n")
    (repo / "web").mkdir()
    (repo / "web/viewer.js").write_text("const x=1;\n")
    (repo / "data").mkdir()
    (repo / "data/LOOM_2226.sqlite3").write_bytes(b"DO NOT COPY")
    (repo / "campaign").mkdir()
    (repo / "campaign/LOOM_STATE_V1.json").write_text("{}")

    paths = [p.relative_to(repo).as_posix() for p in discover_sources(repo)]
    assert "src/loom/application/contracts.py" in paths
    assert "src/loom_gis.py" in paths
    assert "web/viewer.js" in paths
    assert not any(path.startswith("data/") for path in paths)
    assert not any(path.startswith("campaign/") for path in paths)

    result = sync(repo, app)
    assert result
    assert (app / "src/loom/application/contracts.py").exists()
    assert not (app / "data/LOOM_2226.sqlite3").exists()
    assert not (app / "campaign/LOOM_STATE_V1.json").exists()
    state = json.loads((app / ".loom_dev_state.json").read_text())
    assert state["authority_guards"]["campaign"] == "never touched"


def test_dev_sync_backs_up_replaced_application_file(tmp_path):
    repo = tmp_path / "repo"
    app = tmp_path / "runtime"
    source = repo / "src/loom/test.py"
    target = app / "src/loom/test.py"
    source.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    source.write_text("new\n")
    target.write_text("old\n")

    sync(repo, app)
    backups = list((app / ".loom_dev_backups").glob("*/src/loom/test.py"))
    assert len(backups) == 1
    assert backups[0].read_text() == "old\n"
    assert target.read_text() == "new\n"
