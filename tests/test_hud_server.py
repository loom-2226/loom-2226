import tempfile
import unittest
from pathlib import Path

from loom.hud import server


class HudServerTests(unittest.TestCase):
    def test_checked_in_demo_page_exists(self):
        page = server.validate_assets()
        self.assertTrue(page.is_file())
        self.assertEqual(page.name, server.DEFAULT_PAGE)

    def test_missing_demo_page_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                server.validate_assets(Path(tmp))

    def test_default_port_is_valid(self):
        self.assertGreaterEqual(server.DEFAULT_PORT, 1)
        self.assertLessEqual(server.DEFAULT_PORT, 65535)


if __name__ == "__main__":
    unittest.main()
