"""Structural Build 6B standing from bounded REGION observations."""
import unittest
from types import SimpleNamespace

from offworld_kernel.project_study import ProjectStudyResultStanding
from simulation.offworld_mvp.build7.increment5 import classify_regional_material_observation


class Increment5AdapterTests(unittest.TestCase):
    def test_positive_supports_adjacent_information_stage_only(self):
        observations=[SimpleNamespace(signal=s) for s in ('NEGATIVE','POSITIVE','NEGATIVE','NEGATIVE')]
        self.assertEqual(classify_regional_material_observation(observations),
                         ProjectStudyResultStanding.SUPPORTS_ADVANCE)

    def test_negative_and_unknown_remain_distinct(self):
        negative=[SimpleNamespace(signal='NEGATIVE') for _ in range(4)]
        self.assertEqual(classify_regional_material_observation(negative),
                         ProjectStudyResultStanding.NEGATIVE)
        self.assertEqual(classify_regional_material_observation([]),
                         ProjectStudyResultStanding.INSUFFICIENT)
        self.assertEqual(classify_regional_material_observation([
            SimpleNamespace(signal='UNKNOWN')]),ProjectStudyResultStanding.INSUFFICIENT)


if __name__ == '__main__': unittest.main()
