import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from simulation.offworld_mvp.build8.country_capital_input import load_investment_capacity, SOURCES

class CountryCapitalBoundaryTests(unittest.TestCase):
    def test_complete_coverage_and_2031_precedence(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)/'earth_long_run_economic_baseline_v4_2026_09_24'
            for i, source in enumerate(SOURCES):
                path=root/source
                path.parent.mkdir(parents=True,exist_ok=True)
                years=range(2026,2032) if i==0 else range(2031,2036)
                with path.open('w') as out:
                    for year in years:
                        for c in range(80):
                            out.write(json.dumps({'year':year,'iso3':f'C{c:02d}',
                                                  'investment': '10' if i==0 else '20'})+'\n')
            values,provenance=load_investment_capacity(root)
            self.assertEqual(len(values),800)
            self.assertEqual(values['C00',2031],Decimal('10'))
            self.assertEqual(values['C00',2032],Decimal('20'))
            self.assertEqual(provenance['standing'],'MODELED_INVESTMENT_CAPACITY_NOT_SPENDABLE_CASH')

if __name__=='__main__':unittest.main()

class CapitalPreviewTests(unittest.TestCase):
    def test_existing_mobilization_rule_unchanged(self):
        from offworld_kernel.prospecting import derive_mobilization
        from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
        scenario=load_prospecting_scenario()
        zero=derive_mobilization(investment_proxy=Decimal('1000000000000'),commercial_opportunity=Decimal(0),scenario=scenario)
        active=derive_mobilization(investment_proxy=Decimal('1000000000000'),commercial_opportunity=Decimal(1),scenario=scenario)
        self.assertEqual(zero[-1],Decimal(0))
        self.assertEqual(active[-1],Decimal('1'))
