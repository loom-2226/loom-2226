import json
import tempfile
import unittest
from pathlib import Path

from validate_promotion import PromotionValidationError, validate


class PromotionTests(unittest.TestCase):
    def test_promoted_package_passes(self):
        result = validate()
        self.assertEqual("PASS", result["status"])
        self.assertEqual(80, result["workforce_invariant_passed"])
        self.assertEqual(0, result["workforce_invariant_failed"])

    def test_wrong_selected_scenario_fails_closed(self):
        source = Path(__file__).with_name("PROMOTION_MANIFEST.json")
        manifest = json.loads(source.read_text())
        manifest["selected_scenario"] = "MED_HIGH__SYNTH_HIGH"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(PromotionValidationError, "Wrong selected scenario"):
                validate(path)


if __name__ == "__main__":
    unittest.main()
