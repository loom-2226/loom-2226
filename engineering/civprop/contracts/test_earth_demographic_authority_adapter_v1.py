import unittest
from engineering.civprop.contracts.earth_demographic_authority_adapter_v1 import *

class EarthAdapterTests(unittest.TestCase):
 def rows(self):
  d=[{"snapshot_id":"S","year":2226,"biological_population":10,"births":1,"deaths":.5},
     {"snapshot_id":"S","year":2226,"biological_population":20,"births":2,"deaths":1}]
  l=[{"snapshot_id":"S","year":2226,"total_effective_labor":4},
     {"snapshot_id":"S","year":2226,"total_effective_labor":8}]
  return d,l
 def test_aggregates_authority_without_propagation(self):
  d,l=self.rows()
  p=aggregate_earth_authority(demographic_rows=d,labor_rows=l,snapshot_id="S",year=2226,
   provenance_refs=("loom_earth",))
  self.assertEqual((p.biological_population,p.births,p.deaths,p.workforce),(30,3,1.5,12))
 def test_unknown_births_stay_unknown(self):
  d,l=self.rows(); d[0]["births"]=None
  p=aggregate_earth_authority(demographic_rows=d,labor_rows=l,snapshot_id="S",year=2226,
   provenance_refs=("loom_earth",))
  self.assertIsNone(p.births)
 def test_missing_authority_rejected(self):
  with self.assertRaisesRegex(ValueError,"AUTHORITY_MISSING"):
   aggregate_earth_authority(demographic_rows=[],labor_rows=[],snapshot_id="S",year=2226,
    provenance_refs=("loom_earth",))
 def test_provenance_required(self):
  d,l=self.rows()
  with self.assertRaisesRegex(ValueError,"PROVENANCE"):
   aggregate_earth_authority(demographic_rows=d,labor_rows=l,snapshot_id="S",year=2226,
    provenance_refs=())
 def test_only_earth_surface(self):
  d,l=self.rows(); p=aggregate_earth_authority(demographic_rows=d,labor_rows=l,
   snapshot_id="S",year=2226,provenance_refs=("loom_earth",))
  with self.assertRaisesRegex(ValueError,"CANNOT_SEED_OFFWORLD"):
   apply_earth_authority_to_state(point=p,location_id="CERES")
 def test_no_recompute_contract(self):
  self.assertFalse(may_recompute_earth_demography())
if __name__=="__main__": unittest.main()
