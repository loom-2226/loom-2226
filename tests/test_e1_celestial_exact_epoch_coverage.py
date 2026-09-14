import unittest
from pathlib import Path

from src.loom_sqlite_celestial_provider import SQLiteCelestialCatalog


class E1CelestialExactEpochCoverageTests(unittest.TestCase):
    """Probe only the exact epochs already earned by the E1 Pixel qualification."""

    DB = Path(__file__).resolve().parents[1] / "data" / "LOOM_2226.sqlite3"
    DEPARTURE = "2226-08-22T01:32:00Z"
    ARRIVAL = "2226-08-22T09:45:17.864616Z"

    def test_ceres_departure_center_exact_epoch_is_available_navigation_grade(self):
        catalog = SQLiteCelestialCatalog(self.DB)
        state = catalog.direct_state("CERES", self.DEPARTURE)
        self.assertIsNotNone(state, "E1 needs either exact CERES coverage or the qualified interpolation seam")
        self.assertTrue(state.navigation_grade)

    def test_neptune_arrival_center_exact_epoch_is_available_navigation_grade(self):
        catalog = SQLiteCelestialCatalog(self.DB)
        state = catalog.direct_state("NEPTUNE", self.ARRIVAL)
        self.assertIsNotNone(state, "E1 needs either exact NEPTUNE coverage or the qualified interpolation seam")
        self.assertTrue(state.navigation_grade)


if __name__ == "__main__":
    unittest.main()
