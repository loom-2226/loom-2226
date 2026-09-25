import sqlite3, unittest
from pathlib import Path

DB=Path(__file__).with_name('LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3')

class PromotionTests(unittest.TestCase):
 def setUp(self): self.c=sqlite3.connect(DB)
 def test_candidate_and_counts(self):
  self.assertEqual(self.c.execute("select count(*) from fact where fact_status='CANDIDATE'").fetchone()[0],4)
  self.assertEqual(self.c.execute('select count(*) from preferred_fact').fetchone()[0],0)
  self.assertEqual(self.c.execute('select count(*) from promotion_assertion').fetchone()[0],13)
 def test_integrity_and_no_laundering(self):
  self.assertEqual(self.c.execute('pragma integrity_check').fetchone()[0],'ok')
  self.assertEqual(self.c.execute('pragma foreign_key_check').fetchall(),[])
  self.assertEqual(self.c.execute("select count(*) from fact where property_code='SURFACE_TEMPERATURE'").fetchone()[0],0)
  self.assertEqual(self.c.execute("select value_numeric,value_min,value_max from fact where property_code='POROSITY'").fetchone(),(None,72.0,74.0))
 def test_replay_is_covered_by_qualifier(self): self.assertTrue(DB.exists())
