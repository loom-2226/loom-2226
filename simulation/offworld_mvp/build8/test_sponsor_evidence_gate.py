"""Noncanon Sponsor policy negative controls: available observations, not hidden truth."""
import unittest
from decimal import Decimal as D
from .episode_a_gate_controls import evaluate


class SponsorEvidenceGateTests(unittest.TestCase):
    def test_economic_and_evidence_declines(self):
        for case, expected in [('positive','INITIATE_PROJECT'),('value','DECLINE'),
                               ('belief','DECLINE'),('funds','WAIT')]:
            with self.subTest(case=case):
                decision = evaluate(case)
                self.assertEqual(decision.outcome.value, expected)
                self.assertEqual(decision, evaluate(case))


if __name__ == '__main__':
    unittest.main()
