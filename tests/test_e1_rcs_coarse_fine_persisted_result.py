import json
import unittest
from pathlib import Path


RESULT = Path('engineering/experience_one/results/e1_rcs_coarse_fine_offline_sweep.json')


class PersistedCoarseFineSweepResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding='utf-8'))

    def test_result_is_bound_to_successful_offline_execution(self):
        self.assertEqual(self.result['source_head_sha'], '4ccd92a33ef64bf8e495aefe20c686025b155c0d')
        self.assertEqual(self.result['source_workflow_run_id'], 34923328218)
        self.assertEqual(self.result['source_artifact_id'], 10379120717)
        self.assertEqual(self.result['source_result_sha256'], '6ba805ce09be05aba364f9923612c15369ae7ad98febd28feb95988382be9832')
        self.assertEqual(self.result['execution']['case_runs'], 45)
        self.assertEqual(self.result['execution']['pass_region_points'], 9)
        self.assertTrue(self.result['execution']['all_explored_points_passed'])

    def test_claim_is_sampled_not_continuous_or_hardware(self):
        authority = self.result['authority']
        self.assertEqual(authority['claim'], 'SAMPLED_NUMERICAL_PASS_REGION_ONLY')
        self.assertFalse(authority['continuous_region_interpolation_certified'])
        self.assertEqual(authority['hardware_inference'], 'PROHIBITED_WITHOUT_SEPARATE_EVIDENCE')
        self.assertFalse(authority['final_thruster_hardware_certified'])
        self.assertEqual(authority['campaign_state_mutation'], 'ZERO')
        self.assertEqual(authority['llm_calculation_authority'], 'ZERO')

    def test_pixel_witnesses_cover_four_sampled_corners_and_existing_interior(self):
        witnesses = {(x['coarse_activation_fraction'], x['fine_quantization_fraction']) for x in self.result['pixel_witnesses']}
        self.assertEqual(witnesses, {(0.10,0.25),(0.10,1.00),(0.20,0.50),(0.30,0.25),(0.30,1.00)})


if __name__ == '__main__':
    unittest.main()
