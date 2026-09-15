import unittest
from engineering.experience_one.qualification.e1_rcs_coarse_fine_offline_witness_replay import REPLAY_CASES, REPLAY_WITNESSES


class PixelWitnessReplayContractTests(unittest.TestCase):
    def test_replay_is_bounded_not_full_sweep(self):
        self.assertEqual(len(REPLAY_WITNESSES), 4)
        self.assertEqual(len(REPLAY_CASES), 2)
        self.assertLess(len(REPLAY_WITNESSES) * len(REPLAY_CASES), 45)

    def test_replay_uses_sampled_corners(self):
        self.assertEqual(set(REPLAY_WITNESSES), {(0.10,0.25),(0.10,1.00),(0.30,0.25),(0.30,1.00)})


if __name__ == '__main__':
    unittest.main()
