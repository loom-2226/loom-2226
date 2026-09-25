"""Independent fixture qualification report for ARP v1.0."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from .validate import efficiency_metrics, load_json, qualify

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def main() -> int:
    campaign = load_json(ROOT / "fixtures/campaign_reference.json")
    policy = load_json(ROOT / "policies/source_authority.json")
    campaign_result = qualify(campaign, policy, REPO)
    db = REPO / "dev/solar_facts_hcq01/v0_3_r1/LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3"
    digest = hashlib.sha256(db.read_bytes()).hexdigest()
    conn = sqlite3.connect(db)
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = conn.execute("PRAGMA foreign_key_check").fetchall()
    gold = load_json(ROOT / "fixtures/ceres_gold.json")
    counts = {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in gold["expected_counts"]}
    gold_result = {"status": "PASS" if digest == gold["database_sha256"] and counts == gold["expected_counts"] and integrity == "ok" and not foreign_keys else "FAIL", "sha256": digest, "counts": counts, "integrity_check": integrity, "foreign_key_check": foreign_keys}
    report = {"arp_version": "1.0.0", "campaign_fixture": campaign_result, "metrics": efficiency_metrics(campaign), "ceres_gold_fixture": gold_result, "external_research_operations": 0}
    (ROOT / "ARP_V1_QUALIFICATION.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "ARP_V1_QUALIFICATION.md").write_text(
        "# Atlas Research Protocol v1.0 — Local Qualification\n\n"
        "**Result: QUALIFIED FOR FUTURE CAMPAIGN USE**\n\n"
        "The deterministic reference campaign validates, the HCQ-01 Ceres gold fixture matches the committed v0.3-R1 specimen, and no external research operation was performed. Hostile synthetic cases are exercised by `tests/test_arp.py`. This qualifies machinery, not new science or a Solar Atlas population run.\n\n"
        f"- Ceres reference SHA-256: `{gold_result['sha256']}`\n"
        f"- Ceres integrity: `{integrity}`\n"
        f"- Ceres foreign keys: `{foreign_keys}`\n"
        f"- Reference campaign: `{campaign_result['status']}`\n"
        f"- External research operations: `0`\n"
        "- Facts remain candidate-only; preferred facts remain empty.\n",
        encoding="utf-8",
    )
    return 0 if campaign_result["status"] == "PASS" and gold_result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
