import unittest

from engineering.experience_one.qualification.e1_collapse_boundary_seam_probe import (
    extract_relevant_source_lines,
    referenced_local_helpers,
)


class E1CollapseBoundarySeamProbeTests(unittest.TestCase):
    def test_extract_relevant_source_lines_filters_to_boundary_physics_terms(self):
        source = '''\ndef _solve_leg(a, b):\n    metric_distance = 10\n    collapse_position = (1, 2, 3)\n    terminal_burn = helper(metric_distance)\n    unrelated = 5\n    return collapse_position, terminal_burn\n'''
        lines = extract_relevant_source_lines(source)
        joined = "\n".join(lines)
        self.assertIn("metric_distance", joined)
        self.assertIn("collapse_position", joined)
        self.assertIn("terminal_burn", joined)
        self.assertNotIn("unrelated = 5", joined)

    def test_referenced_local_helpers_keeps_only_callable_names_present_in_module_namespace(self):
        class DummyCode:
            co_names = ("helper_a", "math", "missing", "helper_b")

        class DummyFn:
            __code__ = DummyCode()

        def helper_a():
            pass

        def helper_b():
            pass

        namespace = {
            "helper_a": helper_a,
            "helper_b": helper_b,
            "math": object(),
        }
        self.assertEqual(referenced_local_helpers(DummyFn(), namespace), ["helper_a", "helper_b"])


if __name__ == "__main__":
    unittest.main()
