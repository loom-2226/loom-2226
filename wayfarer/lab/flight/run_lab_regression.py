"""Wayfarer flight lab full regression, including canonical Metric HOLD behavior.
ALL bodies. ALL sponsors. 2026-2226.
This executes tests of source-derived mode requirements, refused torch overlap,
ramp HOLD, epistemic limits and no invented arrival. It does not enable Metric.
Run: python wayfarer/lab/flight/run_lab_regression.py
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
MODULES = ('test_cards', 'test_flightlab', 'test_completion',
           'test_hardware_assess', 'test_canon_metric_operation')


def main():
    suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() and result.testsRun == 61 else 1


if __name__ == '__main__':
    raise SystemExit(main())
