"""I5-D02 provisional regional truth invariants."""
import unittest

from simulation.offworld_mvp.build6e.generated_world import (
    MATERIAL_FAMILIES, regional_material_truth,
)


class RegionalTruthTests(unittest.TestCase):
    def test_body_absence_and_presence_constraints(self):
        body={family:family!='METALS' for family in MATERIAL_FAMILIES}
        result=regional_material_truth('SEED','TEST_BODY',body)
        self.assertEqual(len(result),10)
        self.assertFalse(any(row['METALS'] for row in result.values()))
        for family in MATERIAL_FAMILIES:
            if body[family]:self.assertTrue(any(row[family] for row in result.values()))
        self.assertEqual(result,regional_material_truth('SEED','TEST_BODY',body))
        self.assertTrue(any(not row['VOLATILES'] for row in result.values()))

    def test_present_families_are_heterogeneous_and_order_independent(self):
        body={family:True for family in MATERIAL_FAMILIES}
        for seed in ('REGIONAL-A','REGIONAL-B','REGIONAL-C'):
            rows=regional_material_truth(seed,'TEST_BODY',body)
            self.assertEqual(rows,regional_material_truth(seed,'TEST_BODY',dict(reversed(tuple(body.items())))))
            for family in MATERIAL_FAMILIES:
                self.assertTrue(any(row[family] for row in rows.values()))
                self.assertTrue(any(not row[family] for row in rows.values()))


if __name__=='__main__':unittest.main()
