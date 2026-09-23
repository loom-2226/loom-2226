import json
import math
import unittest
from pathlib import Path

from long_run_repair import (OECD_ALPHA, OECD_KY, effective_alpha,
                             investment_budget, rebase_A)

HERE = Path(__file__).resolve().parent


class LongRunMechanics(unittest.TestCase):
    def test_alpha_transition_and_continuity(self):
        for original in (0.19, 0.35, 0.60):
            self.assertEqual(effective_alpha(original, 2060), original)
            self.assertLess(abs(effective_alpha(original, 2226)-OECD_ALPHA),
                            abs(original-OECD_ALPHA)/100)
            for old, new in ((original,effective_alpha(original,2061)),
                             (effective_alpha(original,2100),effective_alpha(original,2101))):
                for k,l in ((3e10,2e6),(1e12,1e8)):
                    A, factor = rebase_A(1.7,old,new,k,l)
                    prior=1.7*k**old*l**(1-old)
                    after=A*k**new*l**(1-new)
                    self.assertTrue(math.isclose(prior,after,rel_tol=2e-14))
                    self.assertTrue(math.isclose(A,1.7*factor,rel_tol=1e-15))
                    self.assertEqual(new+(1-new),1.0)

    def test_investment_convergence_rule(self):
        va=100.0; k=400.0; depreciation=20.0; prior_va=100.0
        self.assertEqual(investment_budget(2060,0.30,va,prior_va,k,depreciation),30.0)
        late=investment_budget(2226,0.30,va,prior_va,k,depreciation)
        target=depreciation+0.05*(OECD_KY*va-k)
        self.assertTrue(math.isclose(late,target,rel_tol=0.02))
        self.assertGreaterEqual(investment_budget(2226,0.01,va,200,1000,2),0)

    def test_active_boundary_preserves_country_accounting(self):
        path=HERE/'smoke_2061'/'results'
        if not path.exists(): self.skipTest('smoke run not present')
        def load(name):
            with (path/name).open() as source:
                return [json.loads(x) for x in source]
        countries={r['iso3']:r for r in load('countries_2060_2061.ndjson') if r['year']==2060}
        sectors=[r for r in load('country_sectors_2060_2061.ndjson') if r['year']==2060]
        assets=[r for r in load('country_sector_assets_2060_2061.ndjson') if r['year']==2060]
        self.assertEqual(len(countries),80)
        for iso,c in countries.items():
            local=[r for r in sectors if r['iso3']==iso]
            for field in ('value_added','capital','investment','employment','gross_output'):
                self.assertTrue(math.isclose(math.fsum(r[field] for r in local),c[field],rel_tol=1e-12), (iso,field))
            for r in local:
                asset_cap=math.fsum(a['capital'] for a in assets if a['iso3']==iso and a['sector']==r['sector'])
                self.assertTrue(math.isclose(asset_cap,r['capital'],rel_tol=1e-12), (iso,r['sector']))
        tw=next(r for r in sectors if r['iso3']=='TWN' and r['sector']=='ENERGY')
        self.assertGreater(tw['value_added'],0)
        self.assertGreater(tw['gross_output'],0)
        self.assertGreater(tw['capital'],0)
        self.assertGreater(tw['A'],0)
        repair=json.loads((path/'active_boundary_repairs.json').read_text())
        self.assertEqual([(r['iso3'],r['sector']) for r in repair],[('TWN','ENERGY')])
        self.assertLess(repair[0]['source_va_2024_current_usd_million'],0)


if __name__ == '__main__': unittest.main()
