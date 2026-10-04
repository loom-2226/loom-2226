import json
import unittest
from pathlib import Path

from offworld_kernel.schema_registry import canonical_registry_payload

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

    def test_odd_registry_exactly_matches_executable_types_enums_and_units(self):
        self.assertEqual(self._odd_registry(),canonical_registry_payload())

    def test_registry_covers_build5_financing_semantics(self):
        reg=self._odd_registry()
        request_fields={x['name']:x['type'] for x in reg['types']['FinancingRequest']}
        decision_fields={x['name']:x['type'] for x in reg['types']['FinancingDecision']}
        snapshot_fields={x['name']:x['type'] for x in reg['types']['DecisionSnapshot']}
        self.assertIn('required_underwriting_keys',request_fields)
        self.assertIn('required_belief_keys',request_fields)
        self.assertIn('required_prior_keys',request_fields)
        self.assertIn('priors',snapshot_fields)
        for field in ('outcome','reason_code','unknown_input_keys','input_snapshot_ref','policy_version'):
            self.assertIn(field,decision_fields)
        self.assertTrue({'CEILING','CONCENTRATION','BELOW_RETURN',
                         'BLOCKED_REQUIRED_INPUT_UNKNOWN'}.issubset(
            set(reg['enums']['FinancingReasonCode'])))
        self.assertEqual(reg['units']['FinancingRequest.amount'],
                         'FIELD:FinancingRequest.currency_unit')
        self.assertEqual(reg['units']['UnderwritingInput.value'],
                         'FIELD:UnderwritingInput.unit')
        self.assertEqual(reg['units']['UnderwritingInput.basis_year'],'SIM_YEAR')

if __name__=='__main__':
    unittest.main()
