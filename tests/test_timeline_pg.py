import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("timeline_pg",ROOT/"tools/timeline_pg.py")
timeline_pg=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(timeline_pg)

class TimelineProjectionTests(unittest.TestCase):
    def test_source_projection_counts_and_authority_classes(self):
        rows=timeline_pg.parse_milestones()
        counts={}
        for row in rows:
            counts[row["timeline_kind"]]=counts.get(row["timeline_kind"],0)+1
        self.assertEqual(counts,timeline_pg.EXPECTED)
        self.assertEqual(len(rows),43)
        self.assertTrue(all(r["authority_class"]=="GOVERNING_CANON" for r in rows if r["timeline_kind"]=="CANON_HISTORY"))
        self.assertTrue(all(r["authority_class"]=="PROVISIONAL_SIMULATION_SCAFFOLD" for r in rows if r["timeline_kind"]!="CANON_HISTORY"))

    def test_known_authority_sentinels(self):
        by_id={r["milestone_id"]:r for r in timeline_pg.parse_milestones()}
        self.assertEqual(by_id["TRN-2100-TORCH-EMERGE"]["authority_class"],"GOVERNING_CANON")
        self.assertEqual(by_id["SPEC-MOD-METRIC-SHIP"]["authority_class"],"PROVISIONAL_SIMULATION_SCAFFOLD")
        self.assertEqual(by_id["SPEC-MOD-METRIC-SHIP"]["start_year"],2205)
        self.assertEqual(by_id["TRN-2221-LOOM-PROBE"]["temporal_precision"],"APPROX_YEAR")

    def test_dual_canon_id_is_preserved_as_alias(self):
        by_id={r["milestone_id"]:r for r in timeline_pg.parse_milestones()}
        self.assertIn("IND-2140-OUTER",by_id["TRN-2140-TORCH-MATURE"]["aliases"])

    def test_social_anchor_does_not_invent_source_id(self):
        row=next(r for r in timeline_pg.parse_milestones() if r["timeline_kind"]=="SOCIAL_SCENARIO_ANCHOR")
        self.assertEqual(row["id_origin"],"PROJECTION_GENERATED")
        self.assertIn("source defines no milestone ID",row["notes_md"])

    def test_interpretation_rules_are_exact_source_text(self):
        text=timeline_pg.TECH_PATH.read_text(encoding="utf-8")
        for rule in timeline_pg.RULES.values(): self.assertIn(rule,text)
        self.assertIn("DATE_DOES_NOT_UNLOCK",timeline_pg.RULES)

    def test_manifest_hashes_match_sources(self):
        manifest=timeline_pg.build_manifest()
        self.assertEqual(manifest["sources"]["canon"]["sha256"],timeline_pg.sha256(timeline_pg.CANON_PATH))
        self.assertEqual(manifest["sources"]["technology"]["sha256"],timeline_pg.sha256(timeline_pg.TECH_PATH))
        self.assertEqual(manifest["total_milestones"],43)

    def test_migration_preserves_authority_separation(self):
        sql=(ROOT/"data/postgres/migrations/010_timeline_projection.sql").read_text()
        self.assertIn("loom_timeline.milestone",sql)
        self.assertIn("GOVERNING_CANON",sql)
        self.assertIn("PROVISIONAL_SIMULATION_SCAFFOLD",sql)
        self.assertIn("Persistence never upgrades provisional scenario material to canon",sql)

if __name__=="__main__": unittest.main()
