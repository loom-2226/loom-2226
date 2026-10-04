from decimal import Decimal as D
import unittest

from offworld_kernel.build5_earth_shadow_fixture import earth_shadow_kernel, realize_shadow_flows
from offworld_kernel.model import TxPurpose


class Build5EarthShadowTests(unittest.TestCase):
    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20'):
        k=earth_shadow_kernel(universe_id,stock)
        reference=(k.run_identity.input_snapshot_id,
                   k.resource_constraints[('EARTH:X',1)].reference_fcf)
        realize_shadow_flows(k)
        return k,reference

    def test_shadow_classifies_realized_flows_without_extra_transactions(self):
        k,_=self.full_case()
        y1=k.earth_shadow_at(1); y2=k.earth_shadow_at(2)
        self.assertEqual(y1['capital_diverted_to_offworld'],D('40'))
        self.assertEqual(y1['offworld_purchases_from_earth'],D('20'))
        self.assertEqual(y1['qualifying_supplied_expenditure'],D('20'))
        self.assertEqual(y1['terrestrial_fcf_delta'],D('-20'))
        self.assertEqual(y2['earth_purchases_from_offworld'],D('10'))
        self.assertEqual(y2['capital_returned_to_earth'],D('5'))
        self.assertEqual(y2['migration_from_earth'],3)
        self.assertEqual(y2['returning_population'],0)
        self.assertEqual(len(k.state.transactions),4)

    def test_reference_lineage_and_reference_fcf_are_immutable(self):
        k,reference=self.full_case()
        self.assertEqual(
            (k.run_identity.input_snapshot_id,
             k.resource_constraints[('EARTH:X',1)].reference_fcf),reference)
        self.assertEqual(reference,('EARTH_REFERENCE_TEST013A_v1',D('100')))

    def test_shadow_is_derived_view_not_cash_or_population_side_effect(self):
        k,_=self.full_case()
        self.assertEqual(k.state.accounts['earth_finance'].balance,D('60'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('25'))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('20'))
        self.assertEqual(k.state.accounts['earth_return'].balance,D('5'))
        self.assertEqual(k.state.accounts['earth_market'].balance,D('90'))
        self.assertEqual(k.population.earth,997)
        self.assertEqual(k.population.offworld['OFF:T1'],3)
        self.assertEqual(k.population.total(),1000)

    def test_same_realized_flows_same_shadow_across_hidden_universes(self):
        snapshots=[]
        for uid,stock in [('NULL_FP_1','0'),('SPARSE_PUBLIC_1','3'),('RICH_PUBLIC_3','20')]:
            k,_=self.full_case(uid,stock)
            snapshots.append((k.earth_shadow_at(1),k.earth_shadow_at(2)))
        self.assertEqual(snapshots[0],snapshots[1])
        self.assertEqual(snapshots[1],snapshots[2])

    def test_non_cross_boundary_transfers_do_not_create_shadow_categories(self):
        k=earth_shadow_kernel()
        before=dict(k.earth_shadow_at(1))
        k.transfer(1,'earth_finance','earth_return',D('5'),TxPurpose.OTHER_INVESTMENT)
        k.transfer(1,'local_cash','project_cash',D('5'),TxPurpose.LOCAL_REINVESTMENT)
        self.assertEqual(k.earth_shadow_at(1),before)

    def test_earth_boundary_purchase_requires_offworld_project_seller_for_shadow(self):
        k=earth_shadow_kernel()
        k.boundary_purchase(1,'earth_market','earth_return',D('5'),'RES',D('1'))
        self.assertEqual(k.earth_shadow_at(1)['earth_purchases_from_offworld'],D('0'))

    def test_shadow_tampering_changes_epoch_fingerprint(self):
        k,_=self.full_case()
        before=k.methodology_fingerprint()
        k.state.earth_impact.capital_diverted_to_offworld[('EARTH:X',1)]+=D('1')
        self.assertNotEqual(k.methodology_fingerprint(),before)

    def test_returning_population_channel_is_explicit_but_not_invented(self):
        k,_=self.full_case()
        self.assertEqual(k.state.earth_impact.returning_population,{})
        self.assertEqual(k.earth_shadow_at(2)['returning_population'],0)


if __name__=='__main__':
    unittest.main()
