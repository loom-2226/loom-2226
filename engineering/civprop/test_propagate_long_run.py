import unittest
from engineering.civprop.propagate_long_run import run

class LongRunActorMachineryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=run(42,2026,2226)

    def test_full_horizon_and_actor_decisions(self):
        self.assertEqual(len(self.out['annual']),201)
        self.assertEqual(len(self.out['decisions']),201*13)
        self.assertTrue(any(x['decision']=='COMMIT' for x in self.out['decisions']))

    def test_deterministic(self):
        self.assertEqual(self.out['canonical_sha256'],run(42,2026,2226)['canonical_sha256'])

    def test_seed_changes_trajectory(self):
        self.assertNotEqual(self.out['canonical_sha256'],run(43,2026,2226)['canonical_sha256'])

    def test_interactions_execute(self):
        self.assertTrue(self.out['transactions'])
        self.assertTrue(all(x['type']=='BUY/PARTNER' for x in self.out['transactions']))

    def test_lifecycle_is_causal(self):
        self.assertGreater(sum(x['retirements'] for x in self.out['annual']),0)
        self.assertGreater(sum(x['maintenance_requirement'] for x in self.out['annual']),0)
        self.assertTrue(any(f['retired_year'] is not None for f in self.out['facilities']))

    def test_replacement_is_separate_from_growth(self):
        self.assertGreater(sum(x['growth_investment'] for x in self.out['annual']),0)
        self.assertGreater(sum(x['replacement_investment'] for x in self.out['annual']),0)
        self.assertTrue({'GROWTH','REPLACEMENT'} <= {f['investment_class'] for f in self.out['facilities']})

    def test_no_future_canon_event_input(self):
        self.assertNotIn('canon', self.out['inputs'])

if __name__=='__main__': unittest.main()
