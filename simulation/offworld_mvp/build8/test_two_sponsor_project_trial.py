import unittest
from decimal import Decimal as D
from pathlib import Path
from .two_sponsor_project_trial import run_two_sponsor_projects

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'promoted Earth v4 baseline absent')
class TwoSponsorProjectTrialTests(unittest.TestCase):
    def test_four_motivation_scenarios(self):
        for commercial,strategic,expected in (
            (False,False,('WAIT','WAIT')),
            (False,True,('FUNDED','WAIT')),
            (True,False,('WAIT','FUNDED')),
            (True,True,('FUNDED','FUNDED'))):
            result,fingerprint=run_two_sponsor_projects(ROOT,commercial=commercial,
                                                        strategic=strategic)
            self.assertEqual(tuple(row[1] for row in result),expected)
            self.assertEqual((result,fingerprint),
                             run_two_sponsor_projects(ROOT,commercial=commercial,
                                                      strategic=strategic))

    def test_unpooled_public_country_cannot_fund(self):
        result,_=run_two_sponsor_projects(ROOT,strategic=True,pooled_public=False)
        self.assertEqual(result[0][1],'WAIT')
        self.assertLess(D(result[0][2]),D(2))
