from __future__ import annotations

import json
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

SYNTH = Path(__file__).resolve().parents[1] / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from model_permutation_experiment import build_designer_packet, designer_prompt  # noqa: E402


class WayfarerRealModelPacketExportTests(unittest.TestCase):
    def test_export_exact_designer_packet_for_first_real_model_run(self):
        packet = build_designer_packet(2226)
        prompt = designer_prompt(packet)
        self.assertEqual(packet.authority_status, "MODEL_INPUT_ONLY")
        self.assertEqual(len(packet.packet_hash), 64)
        print("LOOM_REAL_MODEL_DESIGNER_PACKET_JSON=" + json.dumps(asdict(packet), sort_keys=True, separators=(",", ":")))
        print("LOOM_REAL_MODEL_DESIGNER_PROMPT=" + prompt)


if __name__ == "__main__":
    unittest.main()
