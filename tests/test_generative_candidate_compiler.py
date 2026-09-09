from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "src" / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from generative_candidate_compiler import (  # noqa: E402
    GenerativeCandidateCompilerError,
    compile_survivor,
    compile_wayfarer_survivor_family,
    result_payload,
)
from generative_shipyard_foundation import run_wayfarer_config_experiment  # noqa: E402


class GenerativeCandidateCompilerTests(unittest.TestCase):
    def test_surviving_family_compiles_to_distinct_glbs(self):
        rows = compile_wayfarer_survivor_family()
        self.assertGreaterEqual(len(rows), 2)
        self.assertGreaterEqual(len({row.glb_sha256 for row in rows}), 2)
        self.assertGreaterEqual(len({row.governed_package_hash for row in rows}), 2)
        self.assertTrue(all(row.glb_bytes[:4] == b"glTF" for row in rows))
        self.assertTrue(all(row.flight_dynamics_authority is False for row in rows))

    def test_compilation_is_deterministic(self):
        first = compile_wayfarer_survivor_family()
        second = compile_wayfarer_survivor_family()
        self.assertEqual(
            [(row.candidate_id, row.glb_sha256, row.governed_package_hash) for row in first],
            [(row.candidate_id, row.glb_sha256, row.governed_package_hash) for row in second],
        )

    def test_rejected_candidate_cannot_be_compiled(self):
        result = run_wayfarer_config_experiment()
        rejected = next(row for row in result.outcomes if row.status != "SURVIVED_SCREEN")
        with self.assertRaises(GenerativeCandidateCompilerError):
            compile_survivor(rejected)

    def test_payload_keeps_authority_firewall(self):
        payload = result_payload(compile_wayfarer_survivor_family())
        self.assertFalse(payload["flight_dynamics_authority"])
        self.assertFalse(payload["canon_changed"])
        self.assertFalse(payload["production_shipclasses_changed"])
        self.assertGreaterEqual(payload["distinct_glb_count"], 2)
        self.assertNotIn("glb_bytes", payload["candidates"][0])


if __name__ == "__main__":
    unittest.main()
