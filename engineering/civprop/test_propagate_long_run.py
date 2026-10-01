import unittest
from engineering.civprop.propagate_long_run import run

class IntegratedLongRunV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.out=run(42)

    def test_full_horizon_and_closed_gap_surface(self):
        e=self.out['metadata']['engine']; self.assertEqual((e['start_year'],e['end_year']),(2026,2226))
        gaps={x['gap_id']:x['status'] for x in self.out['known_gaps']}
        for i in range(1,14): self.assertEqual(gaps[f'GAP-{i:03d}'],'CLOSED')
        self.assertEqual(gaps['GAP-014'],'OPEN'); self.assertEqual(gaps['GAP-015'],'OPEN')

    def test_missions_are_not_facilities(self):
        self.assertGreater(len(self.out['missions']),0); self.assertGreater(len(self.out['observations']),0)
        self.assertNotIn('PROSPECTING_SURVEY',{x['project_archetype_id'] for x in self.out['facilities']})

    def test_closed_gap_outputs_are_present(self):
        for key in ('pressure_states','pressure_qualifications','resource_states','facility_production_states','power_states','traffic_demand_states','materialized_facilities','asset_lifecycle_states'):
            self.assertIn(key,self.out); self.assertGreater(len(self.out[key]),0,key)

    def test_infrastructure_emerges(self):
        self.assertTrue(any(x['action']=='COMMIT_PROJECT' for x in self.out['decisions']))
        self.assertGreater(len(self.out['facilities']),0)

    def test_no_parallel_toy_format(self):
        self.assertEqual(self.out['metadata']['engine']['id'],'HYBRID_V1')
        self.assertEqual(self.out['long_run_integration']['rule'],'CLOSED_GAP_CONTRACTS_ARE_CONSUMED_NOT_REIMPLEMENTED')

if __name__=='__main__': unittest.main()
