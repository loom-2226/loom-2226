"""Conventional flight-lab regression selection; deliberately excludes parked Metric/canonical integration.
ALL bodies. ALL sponsors. 2026-2226. No Navigator, no Metric execution.
Run from any directory: python wayfarer/lab/flight/run_nonmetric_regression.py
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
MODULES = ('test_cards', 'test_flightlab', 'test_completion', 'test_hardware_assess')

def flatten(suite):
    for node in suite:
        if isinstance(node, unittest.TestSuite):
            yield from flatten(node)
        else:
            yield node

def main():
    suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    all_cases = list(flatten(suite))
    parked = [case for case in all_cases if any(token in case.id().lower() for token in ('metric', 'canonical'))]
    conventional = [case for case in all_cases if case not in parked]
    print("Conventional lab regression:", len(conventional), "selected;",
          len(parked), "Metric/canonical studies EXCLUDED", flush=True)
    for case in parked:
        print("HOLD (not executed):", case.id(), flush=True)
    result = unittest.TextTestRunner(verbosity=1).run(unittest.TestSuite(conventional))
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    raise SystemExit(main())
