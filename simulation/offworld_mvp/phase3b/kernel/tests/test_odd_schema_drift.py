import json
import unittest
from pathlib import Path

from offworld_kernel.schema_registry import (
    ODD_SCHEMA_REGISTRY_VERSION,
    executable_schema_registry,
)

class OddSchemaDriftTests(unittest.TestCase):
    def _odd_registry(self):
        odd=Path(__file__).resolve().parents[2]/'OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md'
        text=odd.read_text()
        begin='<!-- ODD_SCHEMA_REGISTRY_BEGIN -->'
        end='<!-- ODD_SCHEMA_REGISTRY_END -->'
        self.assertIn(begin,text); self.assertIn(end,text)
        block=text.split(begin,1)[1].split(end,1)[0]
        raw=block.split('```json',1)[1].split('```',1)[0].strip()
        return json.loads(raw)

    def test_odd_registry_exactly_matches_executable_dataclass_fields(self):
        doc=self._odd_registry()
        self.assertEqual(doc['registry_version'],ODD_SCHEMA_REGISTRY_VERSION)
        self.assertEqual(doc['types'],executable_schema_registry())

    def test_registry_covers_build5_financing_interface(self):
        types=self._odd_registry()['types']
        self.assertIn('FinancingRequest',types)
        self.assertIn('required_underwriting_keys',types['FinancingRequest'])
        self.assertIn('FinancingDecision',types)
        for field in ('outcome','reason_code','unknown_input_keys','input_snapshot_ref','policy_version'):
            self.assertIn(field,types['FinancingDecision'])

if __name__=='__main__':
    unittest.main()
