from pathlib import Path


def test_phase7_viewer_has_no_mutating_sql():
    root = Path(__file__).resolve().parents[1]
    text = (root / "tools" / "shipyard_evidence_viewer.py").read_text(encoding="utf-8").upper()
    for verb in ("INSERT INTO", "UPDATE ", "DELETE FROM", "CREATE TABLE", "DROP TABLE"):
        assert verb not in text
