"""Narrow accounting gate: source pin, ceiling, unfunded rejection, funded replay."""
import unittest
from decimal import Decimal as D
from offworld_kernel.kernel import InvariantError
from .defense_v2_gate_trial import (
    run, admitted_value_added, PINNED_SHA256, EXPECTED_VA,
)
from .opening import EARTH_V4_ROOT, build_country_opening


@unittest.skipUnless(EARTH_V4_ROOT.exists(), 'pinned Earth v4 baseline unavailable')
class DefenseV2GateTests(unittest.TestCase):
    def test_off_by_default(self):
        self.assertIsNone(run())

    def test_assertion_and_ceiling(self):
        kernel, _, _, _ = build_country_opening(EARTH_V4_ROOT)
        value, assertion = admitted_value_added(EARTH_V4_ROOT, kernel)
        self.assertEqual(value, EXPECTED_VA)
        self.assertEqual(assertion.source_hashes, PINNED_SHA256)
        self.assertEqual(assertion.concept, 'value_added')
        with self.assertRaises(InvariantError):
            run(enabled=True, requested=D('1.6158486158505849241'), funded=D(10))

    def test_unfunded_rejected(self):
        with self.assertRaisesRegex(InvariantError, 'invalid transfer'):
            run(enabled=True)

    def test_funded_conserved_and_replayed(self):
        first = run(enabled=True, funded=D(2))
        second = run(enabled=True, funded=D(2))
        self.assertEqual(first, second)
        self.assertEqual(D(first[0]), D('1.6158486158505849240'))
        self.assertEqual(D(first[1]) + D(first[2]), D(2))
        self.assertEqual(first[1], first[3])
        self.assertGreaterEqual(D(first[2]), 0)
        with self.assertRaisesRegex(InvariantError, 'invalid transfer'):
            run(enabled=True, funded=D(1))
