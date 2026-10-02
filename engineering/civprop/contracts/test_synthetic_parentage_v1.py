import unittest
from engineering.civprop.contracts.synthetic_parentage_v1 import *
class ParentageTests(unittest.TestCase):
 def test_parentage_explicit(self):
  a=assign_parentage(child_id="c",parent_ids=("p1","p2"),assignment_kind="BIOLOGICAL",
   provenance_refs=("fixture",),known_person_ids=("c","p1","p2"))
  self.assertEqual(a.parent_ids,("p1","p2"))
 def test_unresolved_lineage_can_have_zero_parents(self):
  a=assign_parentage(child_id="c",parent_ids=(),assignment_kind="BIOLOGICAL",
   provenance_refs=("unresolved",),known_person_ids=("c",))
  self.assertEqual(a.parent_ids,())
 def test_self_parentage_rejected(self):
  with self.assertRaisesRegex(ValueError,"SELF_PARENTAGE"):
   assign_parentage(child_id="c",parent_ids=("c",),assignment_kind="BIOLOGICAL",
    provenance_refs=("x",),known_person_ids=("c",))
 def test_no_two_parent_assumption(self):
  a=assign_parentage(child_id="c",parent_ids=("p",),assignment_kind="LEGAL",
   provenance_refs=("x",),known_person_ids=("c","p"))
  self.assertEqual(len(a.parent_ids),1)
 def test_artificial_gestation_distinct(self):
  a=assign_parentage(child_id="c",parent_ids=(),assignment_kind="ARTIFICIAL_GESTATION",
   provenance_refs=("tech-authority",),known_person_ids=("c",))
  self.assertEqual(a.assignment_kind,"ARTIFICIAL_GESTATION")
 def test_birth_set_must_reconcile(self):
  a=assign_parentage(child_id="c1",parent_ids=(),assignment_kind="BIOLOGICAL",
   provenance_refs=("x",),known_person_ids=("c1","c2"))
  with self.assertRaisesRegex(ValueError,"MISMATCH"):
   validate_parentage_set(assignments=(a,),birth_person_ids=("c1","c2"))
 def test_nonbirth_child_rejected(self):
  a=assign_parentage(child_id="x",parent_ids=(),assignment_kind="LEGAL",
   provenance_refs=("x",),known_person_ids=("x",))
  with self.assertRaisesRegex(ValueError,"NOT_AUTHORIZED_BIRTH"):
   validate_parentage_set(assignments=(a,),birth_person_ids=("c",))
 def test_family_event_explicit_and_nonbiological(self):
  e=family_event(event_id="e",event_kind="GUARDIANSHIP",participant_ids=("a","b"),
   year=2200,provenance_refs=("law",),known_person_ids=("a","b"))
  self.assertEqual(e.event_kind,"GUARDIANSHIP")
 def test_unknown_participant_rejected(self):
  with self.assertRaisesRegex(ValueError,"UNKNOWN_FAMILY_PARTICIPANT"):
   family_event(event_id="e",event_kind="LEGAL_PARTNERSHIP",participant_ids=("a","z"),
    year=2200,provenance_refs=("law",),known_person_ids=("a",))
 def test_parentage_has_no_sex_gender_fertility_inference(self):
  a=assign_parentage(child_id="c",parent_ids=("p",),assignment_kind="GENETIC",
   provenance_refs=("x",),known_person_ids=("c","p"))
  for x in ("mother_id","father_id","sex","gender","fertility","conception_method"):
   self.assertFalse(hasattr(a,x))
if __name__=="__main__": unittest.main()
