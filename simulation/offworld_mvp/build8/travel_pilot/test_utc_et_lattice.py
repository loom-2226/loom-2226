"""No SPICE dependency: assert shared UTC arithmetic and lattice identity."""
import unittest
from datetime import datetime, timedelta, timezone
from .utc_et_lattice import utc_epochs_to_et, UTC_J2000_CLOCK


class UtcEtLatticeTests(unittest.TestCase):
    def test_quarter_day_lattice_exactly_matches_shared_output(self):
        first = datetime(2026, 2, 15, tzinfo=timezone.utc)
        ticks = [first + timedelta(hours=6*i) for i in range(14425)]
        calls = []
        def deltet(seconds, system):
            calls.append((seconds, system))
            return 69.184
        actual = utc_epochs_to_et(ticks, deltet=deltet)
        expected = [(t-UTC_J2000_CLOCK).total_seconds()+69.184 for t in ticks]
        self.assertEqual(actual, expected)
        self.assertEqual(len(calls), len(ticks))
        self.assertTrue(all(system == 'UTC' for _, system in calls))

    def test_rejects_naive_epoch(self):
        with self.assertRaises(ValueError):
            utc_epochs_to_et([datetime(2026, 1, 1)], deltet=lambda *_: 0)

if __name__ == '__main__':
    unittest.main()
