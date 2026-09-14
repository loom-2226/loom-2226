import unittest

from engineering.civstate.phase13_provenance_loss_boundary import build_boundary


class Phase13ProvenanceLossBoundaryTests(unittest.TestCase):
    def test_exact_checkpoint_recovered_but_builder_not_recovered(self):
        out = build_boundary()
        self.assertEqual(out["phase13_checkpoint_status"], "EXACT_CHECKPOINT_RECOVERED")
        self.assertEqual(out["original_materializer_source_status"], "NOT_RECOVERED")
        self.assertEqual(out["generator_reconstruction_authority"], "ZERO")

    def test_hashes_are_preserved(self):
        out = build_boundary()
        self.assertEqual(out["phase13_sqlite_sha256"], "5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753")
        self.assertEqual(out["navigator_sha256"], "906a31616ef4895997ce6e02e389789e884240671f7fef89abc59ca370d5f4a2")

    def test_next_step_requires_new_evidence(self):
        out = build_boundary()
        self.assertIn("NEW_PRIMARY_SOURCE", out["unlock_condition"])
        self.assertEqual(out["allocator_implementation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
