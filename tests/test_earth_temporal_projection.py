import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/postgres/earth_temporal_projection_manifest.json"

class EarthTemporalProjectionTests(unittest.TestCase):
  def test_projection_manifest_is_validated_and_scoped(self):
    data = json.loads(MANIFEST.read_text())
    self.assertEqual(data["snapshot_state"], "VALIDATED")
    self.assertEqual(data["coverage"]["demography"]["areas"], 237)
    self.assertEqual(data["coverage"]["economics"]["economies"], 80)
    self.assertEqual(data["selected_scenario"], "MED_CENTRAL__SYNTH_CENTRAL")
    self.assertEqual(data["endpoint_2226"]["workforce_invariant"], "80/80 PASS")

  def test_projection_preserves_category_boundaries_and_unavailable_semantics(self):
    text = (ROOT / "docs/earth_postgres_temporal_projection_2026_09_25.md").read_text()
    self.assertIn("Historical employment", text)
    self.assertIn("NULL means", text)
    self.assertIn("does not become canon", text)

  def test_forward_migrations_and_narrator_surface_exist(self):
    self.assertTrue((ROOT / "data/postgres/migrations/004_earth_temporal_authority.sql").exists())
    self.assertTrue((ROOT / "data/postgres/migrations/005_earth_narrator_views.sql").exists())
    self.assertTrue((ROOT / "data/postgres/migrations/006_earth_narrator_recognized_fix.sql").exists())
    sql = (ROOT / "data/postgres/migrations/005_earth_narrator_views.sql").read_text()
    self.assertIn("loom_narrator.current_earth_year", sql)
    self.assertIn("loom_narrator.current_country_fact", sql)
