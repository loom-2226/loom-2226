import unittest
from engineering.civprop.contracts.synthetic_household_v1 import *
class HouseholdTests(unittest.TestCase):
 def test_age_requires_explicit_birth_year(self):
  p=assign_age(person_id="p",observation_year=2200,birth_year=None,provenance_refs=())
  self.assertIsNone(p.age_years)
 def test_age_arithmetic(self):
  p=assign_age(person_id="p",observation_year=2200,birth_year=2175,provenance_refs=("fixture",))
  self.assertEqual(p.age_years,25)
 def test_future_birth_rejected(self):
  with self.assertRaisesRegex(ValueError,"BIRTH_AFTER"):
   assign_age(person_id="p",observation_year=2200,birth_year=2201,provenance_refs=("x",))
 def test_household_edges_must_reference_members(self):
  with self.assertRaisesRegex(ValueError,"OUTSIDE_HOUSEHOLD"):
   form_household(household_id="h",location_id="MARS",member_ids=("a","b"),
    relationship_edges=(("a","PARENT","c"),),provenance_refs=("fixture",))
 def test_relationship_type_not_inferred(self):
  h=form_household(household_id="h",location_id="MARS",member_ids=("a","b"),
   relationship_edges=(),provenance_refs=("fixture",))
  self.assertEqual(h.relationship_edges,())
 def test_partition_exact(self):
  a=form_household(household_id="a",location_id="MARS",member_ids=("p1","p2"),
   relationship_edges=(),provenance_refs=("x",))
  b=form_household(household_id="b",location_id="MARS",member_ids=("p3",),
   relationship_edges=(),provenance_refs=("x",))
  self.assertTrue(validate_household_partition(person_ids=("p1","p2","p3"),households=(a,b)))
 def test_person_cannot_be_in_two_households(self):
  a=form_household(household_id="a",location_id="MARS",member_ids=("p1",),
   relationship_edges=(),provenance_refs=("x",))
  b=form_household(household_id="b",location_id="MARS",member_ids=("p1",),
   relationship_edges=(),provenance_refs=("x",))
  with self.assertRaisesRegex(ValueError,"MULTIPLE_HOUSEHOLDS"):
   validate_household_partition(person_ids=("p1",),households=(a,b))
 def test_no_invented_person_attributes(self):
  p=assign_age(person_id="p",observation_year=2200,birth_year=2175,provenance_refs=("x",))
  for x in ("sex","gender","fertility","occupation","health","wealth","parent_id"):
   self.assertFalse(hasattr(p,x))
if __name__=="__main__": unittest.main()
