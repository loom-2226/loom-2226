"""Canon and authority-integrity checks for CCR-2026-0001."""

import hashlib
import json
import re
import unittest
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
CANON = REPO / "canon/current"
GOV = REPO / "governance/current"
BASELINE = REPO / "manifests/earth_long_run_economic_baseline"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class EarthBiosyntheticCanonTests(unittest.TestCase):
    def test_registered_baseline_hashes_match_bytes(self):
        register = (GOV / "LOOM_2226_Baseline_File_Hashes_v2.4.md").read_text()
        rows = re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", register)
        self.assertEqual(9, len(rows))
        for name, expected in rows:
            path = (GOV / name) if name.startswith("LOOM_2226_Canon_") else (CANON / name)
            self.assertTrue(path.is_file(), name)
            self.assertEqual(expected, digest(path), name)

    def test_scoped_amendments_are_registered(self):
        manifest = (GOV / "LOOM_2226_Canon_Baseline_Manifest_v2.4.md").read_text()
        self.assertIn("LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md", manifest)
        self.assertIn("LOOM_2226_Earth_Biosynthetic_Canon_Amendment_v2.4b.md", manifest)
        self.assertIn("CCR-2026-0001", (CANON / "LOOM_2226_Earth_Biosynthetic_Canon_Amendment_v2.4b.md").read_text())

    def test_solar_totals_are_arithmetic_reconciliation_only(self):
        old_earth_bio = Decimal("8312538895.185726")
        old_earth_synth = Decimal("132394809.999859")
        old_solar_bio = Decimal("8571824599.944033")
        old_solar_synth = Decimal("214068428.575609")
        new_earth_bio = Decimal("7163281708.265873")
        new_earth_synth = Decimal("9672505.78986048")
        self.assertEqual(Decimal("7422567413.024180"), old_solar_bio - old_earth_bio + new_earth_bio)
        self.assertEqual(Decimal("91346124.36561048"), old_solar_synth - old_earth_synth + new_earth_synth)

    def test_current_pointers_select_successor_and_preserve_v4(self):
        economic = json.loads((BASELINE / "EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json").read_text())
        demographic = json.loads((BASELINE / "EARTH_DEMOGRAPHIC_AUTHORITY_CURRENT.json").read_text())
        designation = "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24"
        self.assertEqual(designation, economic["active_designation"])
        self.assertEqual(designation, demographic["active_designation"])
        self.assertEqual("EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
                         economic["previous_formal_designation"])
        self.assertTrue((BASELINE / "earth_long_run_economic_baseline_v4_2026_09_24").is_dir())
        self.assertTrue((BASELINE / "earth_demographic_correction_v4_1_2026_09_24").is_dir())


if __name__ == "__main__":
    unittest.main()
