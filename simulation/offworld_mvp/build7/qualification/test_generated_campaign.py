import unittest
from decimal import Decimal as D

from simulation.offworld_mvp.build7.generated_campaign import load_config, _target_from_generated


class Build7GeneratedCampaignTests(unittest.TestCase):
    def binding(self, mass):
        return dict(
            body_key='CERES', body_name='Ceres', body_id='body-id',
            scenario_id='scenario-id', scenario_key='SOLAR_WATER_TEST', model_id='model-id',
            policy_id='policy-id', world_id='world-id', world_site_id='world-site-id',
            deposit_id='deposit-id', site_id='site-id', feature_id='feature-id',
            resource_class='WATER_BEARING_MATERIAL', block={'target_mass_kg': D(mass)},
            result_hash='0'*64,
        )

    def test_hidden_truth_does_not_imply_recovery_knowledge(self):
        target=_target_from_generated(self.binding('123000000'),load_config())
        resource=target['resource']
        self.assertEqual(resource.in_situ,D('123'))
        self.assertIsNone(resource.accessible)
        self.assertIsNone(resource.recoverable)
        self.assertIsNone(resource.remaining)
        self.assertNotIn('CABEU',repr(target).upper())

    def test_zero_hidden_resource_is_valid_generated_target(self):
        target=_target_from_generated(self.binding('0'),load_config())
        self.assertEqual(target['resource'].in_situ,D('0'))
        self.assertIsNone(target['resource'].recoverable)
        self.assertEqual(target['binding'].site_node_id,'OFF:CERES:GEN_SITE_1')
        self.assertEqual(target['binding'].resource_unit_key,'GEN_KG_V1')


if __name__=='__main__':
    unittest.main()
