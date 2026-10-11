"""Cast eligibility is required even when the authored subcontract changes."""
import unittest
from unittest.mock import patch
from .screened_delivery import eligible_subcontract_parties


class CastSubcontractSelectionTests(unittest.TestCase):
    def test_existing_prime_and_sub(self):
        self.assertEqual(eligible_subcontract_parties(), ('Northrop Grumman', 'Firefly Aerospace'))

    def test_other_cast_eligible_pair(self):
        with patch('simulation.offworld_mvp.build8.screened_delivery.OPERATORS', {
            'BUILD': ('CASC', 1, 0, 1, 1), 'LAND': ('Astrobotic', 1, 0, 1, 1)
        }):
            self.assertEqual(eligible_subcontract_parties(), ('CASC', 'Astrobotic'))

    def test_ineligible_subcontractor_rejected(self):
        with patch('simulation.offworld_mvp.build8.screened_delivery.OPERATORS', {
            'BUILD': ('Northrop Grumman', 1, 0, 1, 1),
            'LAND': ('Northrop Grumman', 1, 0, 1, 1)
        }):
            with self.assertRaises(ValueError):
                eligible_subcontract_parties()
