"""Exact pre-migration outputs, including kernel fingerprint, balances and knowledge."""
import unittest
from .baselines.pre_cast_migration.capture import HERE, NAMES, capture


class MasterCastSnapshotTests(unittest.TestCase):
    def test_captured_experiments_are_exact(self):
        for name in NAMES:
            with self.subTest(experiment=name):
                self.assertEqual(capture(name), (HERE / (name + '.json')).read_text())
