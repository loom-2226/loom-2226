from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "src" / "loom" / "gis" / "flight_planning_selection.js"


class Phase6ClientDestinationGuardTest(unittest.TestCase):
    def test_raw_map_tokens_must_cross_authoritative_resolver(self):
        text = GUARD.read_text(encoding="utf-8")
        self.assertIn("LOOM_PHASE6_MVP_DESTINATION_GUARD_V2", text)
        self.assertIn("window.addEventListener('click',fpCaptureDestinationClick,true)", text)
        self.assertIn("fetch('/flight-planning/resolve'", text)
        self.assertIn("!CANONICAL_ENDPOINTS.has(panelDest)", text)
        self.assertIn("event.stopImmediatePropagation()", text)
        self.assertIn("NAVIGATION UNAVAILABLE", text)

    def test_only_declared_mvp_endpoint_tokens_are_client_canonical(self):
        text = GUARD.read_text(encoding="utf-8")
        for token in (
            "MERCURY", "VENUS", "EARTH", "LUNA", "MARS", "CERES",
            "JUPITER_SYSTEM", "SATURN_SYSTEM", "URANUS_SYSTEM",
            "NEPTUNE_SYSTEM", "PLUTO_SYSTEM",
        ):
            self.assertIn(repr(token), text)
        self.assertNotIn("'VST'", text)
        self.assertNotIn("'PSY'", text)


if __name__ == "__main__":
    unittest.main()
