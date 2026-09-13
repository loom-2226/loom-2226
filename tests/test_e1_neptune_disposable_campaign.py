from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_neptune_disposable_campaign.py"
spec = importlib.util.spec_from_file_location("e1_neptune_qualification", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_campaign_hashes_tracks_only_campaign_artifacts(tmp_path):
    (tmp_path / "LOOM_STATE_V1.json").write_text("state", encoding="utf-8")
    (tmp_path / "LOOM_STATE_V1.bak").write_text("backup", encoding="utf-8")
    (tmp_path / "LOOM_CAMPAIGN_HISTORY.jsonl.gz").write_bytes(b"history")
    (tmp_path / "unrelated.txt").write_text("ignore", encoding="utf-8")
    hashes = mod.campaign_hashes(tmp_path)
    assert tuple(hashes) == mod.CAMPAIGN_FILES
    assert all(hashes[name] for name in mod.CAMPAIGN_FILES)


def test_prepare_disposable_refuses_to_infer_missing_campaign(tmp_path):
    dst = tmp_path / "dst"
    dst.mkdir()
    try:
        mod.prepare_disposable(tmp_path, dst)
    except RuntimeError as exc:
        assert "refusing to create or infer a campaign" in str(exc)
    else:
        raise AssertionError("missing campaign should fail closed")


def test_prepare_disposable_copies_campaign_without_mutating_source(tmp_path):
    real = tmp_path / "real"
    dst = tmp_path / "dst"
    real.mkdir(); dst.mkdir()
    (real / "LOOM_STATE_V1.json").write_text('{"state":"before"}', encoding="utf-8")
    (real / "LOOM_STATE_V1.bak").write_text("backup", encoding="utf-8")
    (real / "LOOM_CAMPAIGN_HISTORY.jsonl.gz").write_bytes(b"history")
    before = mod.campaign_hashes(real)
    mod.prepare_disposable(real, dst)
    assert mod.campaign_hashes(real) == before
    assert (dst / "LOOM_STATE_V1.json").read_text(encoding="utf-8") == '{"state":"before"}'
    assert (dst / "LOOM_CAMPAIGN_HISTORY.jsonl.gz").read_bytes() == b"history"
