import unittest
from dataclasses import replace
from decimal import Decimal as D

from offworld_kernel.policy_runner import assert_policy_source_safe
from offworld_kernel.policies.manifest import (
    ObservationKnowledgeRelation,
    PolicyParameterStatus,
    policy_source_bytes,
    test_only_manifest,
)

class Build5PolicyManifestTests(unittest.TestCase):
    def test_test_fixture_is_explicitly_not_authorized_policy_baseline(self):
        m=test_only_manifest()
        self.assertEqual(m.manifest_status,PolicyParameterStatus.TEST_ONLY)
        with self.assertRaisesRegex(ValueError,'not authorized'):
            m.validate(require_authorized=True)
        m.validate(require_authorized=False)

    def test_policy_source_is_inside_hashed_tree_and_static_safe(self):
        source=policy_source_bytes()
        self.assertIn(b'FINANCIER_SCREENING_V1',source)
        self.assertTrue(assert_policy_source_safe(source))

    def test_policy_version_hash_binds_values_bounds_and_authorization(self):
        m=test_only_manifest()
        source=policy_source_bytes()
        base=m.policy_version_hash(source)
        p=m.parameter('hurdle_rate')
        changed_value=replace(p,value=p.value+D('0.01'))
        changed_bounds=replace(p,sensitivity_high=p.sensitivity_high+D('0.01'))
        changed_auth=replace(p,authorization_ref=p.authorization_ref+':CHANGED')
        for changed in (changed_value,changed_bounds,changed_auth):
            mm=replace(m,parameters=tuple(changed if x.semantic_name=='hurdle_rate' else x for x in m.parameters))
            self.assertNotEqual(base,mm.policy_version_hash(source))

    def test_perfect_observation_model_knowledge_requires_exact_likelihood_match(self):
        m=test_only_manifest()
        self.assertEqual(
            m.observation_knowledge_relation,
            ObservationKnowledgeRelation.PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION)
        self.assertEqual(m.parameter('agent_detection_rate').value,m.world_detection_rate)
        self.assertEqual(m.parameter('agent_false_positive_rate').value,m.world_false_positive_rate)
        broken=replace(m,world_detection_rate=D('0.81'))
        with self.assertRaisesRegex(ValueError,'differs from world'):
            broken.validate(require_authorized=False)

if __name__=='__main__':
    unittest.main()
