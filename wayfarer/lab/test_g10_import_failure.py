"""G10 execution failures must fail certification, not become research holds."""
import builtins
import sys
import unittest
from unittest.mock import patch
import certify


class G10ImportFailureTest(unittest.TestCase):
    def assert_missing_import_fails(self, target):
        original_import = builtins.__import__
        hit = []

        def missing(name, *args, **kwargs):
            if name == target:
                hit.append(name)
                raise ModuleNotFoundError(f"No module named {name!r}", name=name)
            return original_import(name, *args, **kwargs)

        with patch.dict(sys.modules):
            sys.modules.pop('g10_flight_dynamics', None)
            with patch('builtins.__import__', new=missing):
                result = certify.g10({'checks': []}, [])
        self.assertEqual(hit, [target], 'expected import path was not exercised')
        self.assertEqual(result['verdict'], certify.FAIL)
        self.assertEqual(result['gate'], 'G10')
        self.assertFalse(result['checks'][0]['pass'])

    def test_missing_g10_test_module_is_fail(self):
        self.assert_missing_import_fails('g10_flight_dynamics')

    def test_missing_g10_dependency_is_fail(self):
        self.assert_missing_import_fails('src.wayfarer_rcs_closed_loop_gnc')


if __name__ == '__main__':
    unittest.main()
