from __future__ import annotations

from pathlib import Path


def test_phase7_viewer_file_present():
    root = Path(__file__).resolve().parents[1]
    text = (root / "tools" / "shipyard_evidence_viewer.py").read_text(encoding="utf-8")
    assert "NO SPATIAL ENVELOPE ADMITTED" in text
    assert "ThreadingHTTPServer" in text
