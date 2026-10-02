import unittest
from engineering.civprop.contracts.synthetic_person_v1 import realize_synthetic_population
from engineering.civprop.contracts.synthetic_life_course_v1 import *
class SyntheticLifeCourseTests(unittest.TestCase):
 def people(self,n=10):
  return realize_synthetic_population(cohort_id="C",location_id="MARS",year=2100,
   authorized_population=n,provenance_refs=("p",),realization_key="open").persons
 def test_exact_reconciliation(self):
  r=realize_life_course(opening_persons=self.people(),cohort_id="C",location_id="MARS",
   year=2101,authorized_births=2,authorized_deaths=1,
   outbound_migrant_ids=(self.people()[0].person_id,),realization_key="k")
  self.assertTrue(reconcile_life_course(realization=r,authorized_opening=10,
   authorized_births=2,authorized_deaths=1,authorized_out_migration=1))
  self.assertEqual(len(r.closing_person_ids),10)
 def test_no_spontaneous_births(self):
  r=realize_life_course(opening_persons=self.people(2),cohort_id="C",location_id="MARS",
   year=2101,authorized_births=0,authorized_deaths=0,realization_key="k")
  self.assertEqual(r.birth_person_ids,()); self.assertEqual(len(r.closing_person_ids),2)
 def test_deaths_cannot_exceed_population(self):
  with self.assertRaisesRegex(ValueError,"DEATHS_EXCEED"):
   realize_life_course(opening_persons=self.people(2),cohort_id="C",location_id="MARS",
    year=2101,authorized_births=0,authorized_deaths=3,realization_key="k")
 def test_migrant_must_exist(self):
  with self.assertRaisesRegex(ValueError,"INVALID_OUTBOUND_MIGRANT"):
   realize_life_course(opening_persons=self.people(2),cohort_id="C",location_id="MARS",
    year=2101,authorized_births=0,authorized_deaths=0,
    outbound_migrant_ids=("invented-person",),realization_key="k")
 def test_deterministic_life_events(self):
  kw=dict(opening_persons=self.people(5),cohort_id="C",location_id="MARS",
   year=2101,authorized_births=1,authorized_deaths=1,realization_key="k")
  self.assertEqual(realize_life_course(**kw),realize_life_course(**kw))
 def test_death_and_migration_cannot_double_remove(self):
  ps=self.people(1)
  with self.assertRaisesRegex(ValueError,"EXHAUSTS"):
   realize_life_course(opening_persons=ps,cohort_id="C",location_id="MARS",
    year=2101,authorized_births=0,authorized_deaths=1,
    outbound_migrant_ids=(ps[0].person_id,),realization_key="k")
 def test_events_do_not_invent_attributes(self):
  r=realize_life_course(opening_persons=self.people(2),cohort_id="C",location_id="MARS",
   year=2101,authorized_births=1,authorized_deaths=0,realization_key="k")
  for e in r.events:
   for forbidden in ("cause_of_death","fertility","occupation","health","wealth","parent_id"):
    self.assertFalse(hasattr(e,forbidden))
if __name__=="__main__": unittest.main()
