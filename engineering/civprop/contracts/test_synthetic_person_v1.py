import unittest
from dataclasses import replace
from engineering.civprop.contracts.synthetic_person_v1 import *
class SyntheticPersonTests(unittest.TestCase):
 def test_exactly_realizes_authorized_population(self):
  r=realize_synthetic_population(cohort_id="MARS:C1",location_id="MARS",year=2140,
   authorized_population=12,provenance_refs=("demography:test",),realization_key="seed42")
  self.assertEqual(len(r.persons),12); self.assertTrue(reconcile_synthetic_population(r))
 def test_deterministic_ids(self):
  kw=dict(cohort_id="C",location_id="CERES",year=2200,authorized_population=3,
   provenance_refs=("p",),realization_key="k")
  a=realize_synthetic_population(**kw); b=realize_synthetic_population(**kw)
  self.assertEqual([p.person_id for p in a.persons],[p.person_id for p in b.persons])
 def test_different_key_changes_identity_not_count(self):
  base=dict(cohort_id="C",location_id="LUNA",year=2100,authorized_population=2,provenance_refs=("p",))
  a=realize_synthetic_population(**base,realization_key="a")
  b=realize_synthetic_population(**base,realization_key="b")
  self.assertEqual(len(a.persons),len(b.persons)); self.assertNotEqual(a.persons,b.persons)
 def test_fractional_population_rejected(self):
  with self.assertRaisesRegex(TypeError,"INTEGER_POPULATION"):
   realize_synthetic_population(cohort_id="C",location_id="MARS",year=2100,
    authorized_population=1.5,provenance_refs=("p",),realization_key="k")
 def test_no_provenance_no_people(self):
  with self.assertRaisesRegex(ValueError,"MISSING_POPULATION_PROVENANCE"):
   realize_synthetic_population(cohort_id="C",location_id="MARS",year=2100,
    authorized_population=1,provenance_refs=(),realization_key="k")
 def test_reconciliation_detects_extra_person(self):
  r=realize_synthetic_population(cohort_id="C",location_id="MARS",year=2100,
   authorized_population=1,provenance_refs=("p",),realization_key="k")
  bad=replace(r,persons=r.persons+r.persons)
  with self.assertRaisesRegex(ValueError,"DUPLICATE|COUNT_MISMATCH"):
   reconcile_synthetic_population(bad)
 def test_person_has_no_demographic_generator_fields(self):
  r=realize_synthetic_population(cohort_id="C",location_id="MARS",year=2100,
   authorized_population=1,provenance_refs=("p",),realization_key="k")
  p=r.persons[0]
  for forbidden in ("fertility","birth_rate","death_rate","migration_probability","economic_value"):
   self.assertFalse(hasattr(p,forbidden))
if __name__=="__main__": unittest.main()
