import math
import unittest

from loom.spatial.ephemeris_interpolation import EphemerisAnchor, hermite_state, validate_uniform_anchors


class HermiteEphemerisTests(unittest.TestCase):
    def test_linear_motion_is_exact(self):
        a = EphemerisAnchor("2026-09-10T00:00:00Z", (0.0, 0.0, 0.0), (1.0, 2.0, 3.0))
        b = EphemerisAnchor("2026-09-10T01:00:00Z", (3600.0, 7200.0, 10800.0), (1.0, 2.0, 3.0))
        p, v = hermite_state(a, b, "2026-09-10T00:30:00Z")
        self.assertEqual(tuple(round(x, 9) for x in p), (1800.0, 3600.0, 5400.0))
        self.assertEqual(tuple(round(x, 9) for x in v), (1.0, 2.0, 3.0))

    def test_anchor_endpoints_are_exact(self):
        a = EphemerisAnchor("2026-09-10T00:00:00Z", (1.0, 2.0, 3.0), (0.1, 0.2, 0.3))
        b = EphemerisAnchor("2026-09-10T01:00:00Z", (4.0, 5.0, 6.0), (0.4, 0.5, 0.6))
        self.assertEqual(hermite_state(a, b, a.epoch_utc), (a.position_km, a.velocity_km_s))
        self.assertEqual(hermite_state(a, b, b.epoch_utc), (b.position_km, b.velocity_km_s))

    def test_outside_bracket_fails_closed(self):
        a = EphemerisAnchor("2026-09-10T00:00:00Z", (0, 0, 0), (1, 0, 0))
        b = EphemerisAnchor("2026-09-10T01:00:00Z", (3600, 0, 0), (1, 0, 0))
        with self.assertRaises(ValueError):
            hermite_state(a, b, "2026-09-10T02:00:00Z")

    def test_uniform_anchor_validation(self):
        anchors = [
            EphemerisAnchor("2026-09-10T00:00:00Z", (0, 0, 0), (0, 0, 0)),
            EphemerisAnchor("2026-09-10T01:00:00Z", (0, 0, 0), (0, 0, 0)),
            EphemerisAnchor("2026-09-10T02:00:00Z", (0, 0, 0), (0, 0, 0)),
        ]
        validate_uniform_anchors(anchors, expected_step_s=3600.0)
        with self.assertRaises(ValueError):
            validate_uniform_anchors(anchors, expected_step_s=1800.0)


if __name__ == "__main__":
    unittest.main()
