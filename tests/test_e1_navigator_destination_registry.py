import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.e1_navigator_destination_registry import (
    load_navigator_registry,
    resolve_destination,
    resolve_priority,
)


class E1NavigatorDestinationRegistryTests(unittest.TestCase):
    def test_reads_literal_registry_without_executing_navigator(self):
        source = '''\nDEST_ALIASES={\n "EARTH":"EARTH",\n "PLUTO":"PLUTO_SYSTEM",\n "PLUTO_SYSTEM":"PLUTO_SYSTEM"\n}\nPRIORITIES={"BALANCED","FASTEST"}\nraise RuntimeError("must never execute")\n'''
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "navigator.py"
            path.write_text(source, encoding="utf-8")
            aliases, priorities = load_navigator_registry(path)
            self.assertEqual(aliases["PLUTO"], "PLUTO_SYSTEM")
            self.assertEqual(priorities, {"BALANCED", "FASTEST"})

    def test_live_registry_resolves_pluto_and_other_navigator_destinations(self):
        self.assertEqual(resolve_destination("Pluto"), "PLUTO_SYSTEM")
        self.assertEqual(resolve_destination("Moon"), "LUNA")
        self.assertEqual(resolve_destination("Jupiter"), "JUPITER_SYSTEM")
        self.assertEqual(resolve_destination("Ceres"), "CERES")

    def test_unknown_destination_fails_closed(self):
        with self.assertRaises(ValueError):
            resolve_destination("Vulcan")

    def test_priority_comes_from_navigator_registry_with_bounded_phrase_normalization(self):
        self.assertEqual(resolve_priority("balanced"), "BALANCED")
        self.assertEqual(resolve_priority("balanced profile"), "BALANCED")
        with self.assertRaises(ValueError):
            resolve_priority("YOLO")


if __name__ == "__main__":
    unittest.main()
