import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"candidate_inputs/EARTH_COUNTRY_OPPORTUNITY_2026_V0_3.json"
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with open(P) as f: cls.x=json.load(f)
 def test_complete_surface(self): self.assertEqual((self.x["country_count"],self.x["sector_count"],self.x["row_count"]),(80,10,800))
 def test_every_country_has_all_sectors(self):
  d={}
  for r in self.x["rows"]:d.setdefault(r["iso3"],set()).add(r["sector"])
  self.assertTrue(all(len(v)==10 for v in d.values()))
 def test_no_missing_2026_fields_silently_zeroed(self):
  self.assertTrue(all("effective_labor" in r["unavailable_fields"] and "replacement_need" in r["unavailable_fields"] for r in self.x["rows"]))
 def test_signal_nonnegative(self): self.assertTrue(all(r["opportunity_signal"]>=0 for r in self.x["rows"]))
 def test_semantics_firewall(self): self.assertTrue(all(r["semantics"]=="OPPORTUNITY_CONTEXT_NOT_ACTOR_AUTHORITY" for r in self.x["rows"]))
if __name__=="__main__":unittest.main()
