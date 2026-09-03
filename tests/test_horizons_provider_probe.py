import json
import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import horizons_provider_probe as hp


class HorizonsProviderProbeTests(unittest.TestCase):
    def test_parse_machine_vector(self):
        result = """header\n$$SOE\n2460000.500000000, A.D. 2226-Aug-22 00:00:00.0000, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0,\n$$EOE\nfooter"""
        payload = json.dumps({"signature": {"source": "NASA/JPL Horizons API"}, "result": result})
        parsed = hp.parse_horizons_result(payload)
        self.assertEqual(parsed["position_km"], [1.0, 2.0, 3.0])
        self.assertEqual(parsed["velocity_km_s"], [4.0, 5.0, 6.0])
        self.assertEqual(parsed["provider"], "JPL_HORIZONS")

    def test_request_is_heliocentric_vectors(self):
        url = hp.horizons_url("499", "2226-08-22 00:00")
        self.assertIn("EPHEM_TYPE", url)
        self.assertIn("500%4010", url)
        self.assertIn("VECTORS", url)

    def test_hash_is_stable(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        self.assertEqual(hp.sha256_obj(a), hp.sha256_obj(b))


if __name__ == "__main__":
    unittest.main()
