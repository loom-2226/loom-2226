"""Checkpoint: chronological financing and reservations before consequences."""
import unittest
from .screened_delivery import run_screened
from .screened_yearly import run_yearly_checkpoint

SCENARIOS = ({}, {'subcontract':True,'capacity_slots':1},
             {'subcontract':True,'capacity_slots':1,'sub_failure':True,'resource_on_failure':True})

class YearlyCheckpointTests(unittest.TestCase):
    def test_financing_and_stage_dates(self):
        for options in SCENARIOS:
            with self.subTest(options=options):
                old=run_screened(**options)
                new=run_yearly_checkpoint(**options)
                expected=sorted((w.project,w.category,w.start,w.finish) for w in old[0])
                actual=sorted((j['project'],j['category'],j['start'],j['finish']) for j in new['planned'])
                self.assertEqual(actual,expected)
                self.assertEqual(new['occupied'],old[3])
                self.assertEqual(new['approvals'],{row[0]:row[4] for row in old[1] if row[4] is not None})
                self.assertFalse(new['active'])

if __name__=='__main__': unittest.main()
