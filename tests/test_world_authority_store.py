import unittest
from src.loom_world_authority.store import stable_uuid, length_prefixed, require_sha256, IntegrityFailure

class StoreIdentityTests(unittest.TestCase):
    def test_authoritative_body_vectors(self):
        expected = {
            "MOON": "9426049d-f5f8-5146-9eca-be36f8c4bc32",
            "MARS": "8d40f6b7-d4f2-543c-8bf6-257de8d41c9e",
            "CERES": "4292aec6-6341-524f-b9f0-d715b070472c",
            "BENNU": "8b4641bf-e70e-567e-b6de-e1c0754bc271",
        }
        for key, want in expected.items():
            self.assertEqual(str(stable_uuid("BODY", "LOOM_BODY_V1", key, "IDENTITY_V1")), want)

    def test_byte_not_character_length(self):
        self.assertEqual(length_prefixed("é"), b"2:" + bytes((0xC3, 0xA9)))

    def test_no_unicode_normalization(self):
        self.assertNotEqual(
            stable_uuid("X", "A", "é", "R"),
            stable_uuid("X", "A", "e\u0301", "R"),
        )

    def test_sha256_guard(self):
        self.assertEqual(require_sha256("a" * 64), "a" * 64)
        with self.assertRaises(IntegrityFailure):
            require_sha256("A" * 64)

if __name__ == "__main__":
    unittest.main()
