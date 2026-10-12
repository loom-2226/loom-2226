"""Opt-in Route 1 all-sponsor / all-executor, TEST_ONLY money-loop tests."""
import unittest
from decimal import Decimal as D

from offworld_kernel.model import AccountKind, TxPurpose
from .master_cast import actor
from .sponsor_executor_network_trial import EXECUTORS, PROJECTS, PUBLIC, PRIVATE
from .route1_gate1 import CEILINGS, run_gate1
from .route1_gate2 import run_gate2
from .route1_cast_payments import (
    EXTRA_CEILINGS, PREFERRED, SERVICES, CastPaymentTrial, run_cast_payments,
)


class Route1CastPaymentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.standard = run_cast_payments()

    def test_all_twenty_sponsors_get_real_financier_decisions(self):
        run = self.standard
        names = set(PUBLIC) | set(PRIVATE)
        self.assertEqual(len(names),20)
        self.assertEqual(run['deciders'],names)
        opening = [x for x in run['rows'] if x['year']==2026]
        self.assertEqual(len(opening),20)
        self.assertTrue(all(x['policy'] in ('APPROVE','REJECT','DEFER') for x in opening))
        self.assertEqual({x['year'] for x in run['rows']},set(range(2026,2036)))
        self.assertEqual(len(run['rows']),200)
        self.assertEqual(len({(x['year'],x['sponsor']) for x in run['rows']}),200)
        self.assertTrue(all(x['disbursement'] == x['delivery']['source_disbursement']
                            for x in opening if x['disbursement']))
        self.assertEqual(len(EXTRA_CEILINGS),9)
        self.assertFalse(set(EXTRA_CEILINGS) & set(CEILINGS))
        self.assertEqual(set(EXTRA_CEILINGS) | set(CEILINGS),names)
        for sponsor in names:
            row=next(x for x in opening if x['sponsor']==sponsor)
            self.assertEqual(D(row['authored_ceiling']),
                D(EXTRA_CEILINGS.get(sponsor,CEILINGS.get(sponsor))))
        self.assertEqual(sum(bool(x['disbursement']) for x in opening),20)

    def test_all_sixteen_executors_are_eligible_and_can_be_paid(self):
        names=set(EXECUTORS)
        self.assertEqual(len(names),16)
        self.assertEqual(self.standard['eligible_executors'],names)
        # Normal TEST_ONLY quotes pay fifteen; Mitsubishi is legitimately
        # ineligible for preferred JAXA LAND. This controlled comparable
        # BUILD quote demonstrates the missing sixteenth can also be paid
        # without changing capability, the country envelope, or the kernel.
        self.assertEqual(len(self.standard['paid_executors']),15)
        self.assertNotIn('Mitsubishi Heavy Industries',
                         self.standard['paid_executors'])
        probe=run_cast_payments(bids_by_sponsor={
            'UAE Space Agency':(('Mitsubishi Heavy Industries','.014'),)})
        self.assertEqual(probe['deciders'],set(PUBLIC) | set(PRIVATE))
        self.assertEqual(probe['paid_executors'],names)
        self.assertEqual(len(probe['deliveries']),20)
        self.assertTrue(all(x['transaction'] and x['source_disbursement']
                            for x in probe['deliveries']))
        mhi=[r for r in probe['deliveries']
             if r['executor']=='Mitsubishi Heavy Industries']
        self.assertEqual(len(mhi),1)
        self.assertEqual((mhi[0]['sponsor'],mhi[0]['category'],mhi[0]['price']),
                         ('UAE Space Agency','BUILD','0.014'))
        repeated=run_cast_payments(bids_by_sponsor={
            'UAE Space Agency':(('Mitsubishi Heavy Industries','.014'),)})
        self.assertEqual(probe['deliveries'],repeated['deliveries'])
        self.assertEqual(probe['kernel'].fingerprint(),
                         repeated['kernel'].fingerprint())

    def test_quotes_rank_by_price_then_preference_then_stable_cast_id(self):
        self.assertEqual(set(SERVICES),{'BUILD','LAND','LAUNCH','RUN'})
        x=CastPaymentTrial(bids_by_sponsor={'ESA':(
            ('Thales Alenia Space','.015'),
            ('Airbus Defence and Space','.010'))})
        self.assertEqual(x.choose_quote('ESA','BUILD')['executor'],
                         'Airbus Defence and Space')
        x=CastPaymentTrial(bids_by_sponsor={'ESA':(
            ('Airbus Defence and Space','.015'),
            ('Thales Alenia Space','.015'))})
        self.assertEqual(x.choose_quote('ESA','BUILD')['executor'],
                         'Thales Alenia Space')
        x=CastPaymentTrial(bids_by_sponsor={'ISRO':(
            ('Airbus Defence and Space','.015'),('OHB','.015'))})
        stable=min(('Airbus Defence and Space','OHB'),
                   key=lambda n:actor(n,'executor','BUILD')['id'])
        self.assertEqual(x.choose_quote('ISRO','BUILD')['executor'],stable)
        self.assertTrue(all(
            category in caps for category, rows in x.quotes_by_category.items()
            for e,_ in rows for caps in (EXECUTORS[e][1],)))
        self.assertEqual(PREFERRED['JAXA'],'Mitsubishi Heavy Industries')
        self.assertNotIn('LAND',EXECUTORS['Mitsubishi Heavy Industries'][1])
        with self.assertRaisesRegex(ValueError,'lacks required capability'):
            CastPaymentTrial(bids_by_sponsor={
                'JAXA':(('Mitsubishi Heavy Industries','.001'),)
            }).choose_quote('JAXA','LAND')
        with self.assertRaisesRegex(ValueError,'no authored comparable'):
            CastPaymentTrial(bids_by_sponsor={'NASA':()}).choose_quote('NASA','LAND')

    def test_payments_conserve_route1_cash_and_do_not_invent_credit(self):
        r=self.standard
        k=r['kernel']
        self.assertEqual(len(r['deliveries']),20)
        total=sum((D(x['price']) for x in r['deliveries']),D(0))
        actual=sum((x.amount for x in k.state.transactions
                    if x.purpose == TxPurpose.CAPEX and
                    str(x.source_account).startswith('route1:cash:')),D(0))
        self.assertEqual(total,actual)
        for x in r['deliveries']:
            self.assertEqual(x['outcome'],'DELIVERED')
            self.assertIsNotNone(x['produced'])
            self.assertEqual(k.state.accounts['route1:cash:'+x['sponsor']].balance,D(0))
            self.assertEqual(k.state.accounts['route1:executor:'+x['executor']].owner_id,
                             x['executor'])
            self.assertEqual(x['same_owner'],x['sponsor']==x['executor'])
        self.assertTrue(any(x['same_owner'] for x in r['deliveries']))
        self.assertTrue(all(not x.startswith(('bank:','loan:','interest:'))
                            for x in k.state.accounts))
        self.assertEqual(sum(k.state.accounts['route1:executor:'+e].balance
                             for e in r['paid_executors']), total)
        k.assert_invariants()

    def test_failed_service_is_paid_but_produces_no_deliverable(self):
        r=run_cast_payments(failures=('NASA',))
        nasa=next(x for x in r['deliveries'] if x['sponsor']=='NASA')
        self.assertEqual(nasa['outcome'],'FAILED')
        self.assertIsNone(nasa['produced'])
        self.assertEqual(nasa['price'],'0.020')
        self.assertTrue(nasa['transaction'])
        self.assertEqual(r['kernel'].state.accounts['route1:cash:NASA'].balance, D(0))
        self.assertTrue(all(x['outcome']=='DELIVERED' for x in r['deliveries']
                            if x['sponsor']!='NASA'))
        r['kernel'].assert_invariants()

    def test_default_gate_snapshots_and_future_horizons_remain_separate(self):
        # Original Gate 1 and Gate 2 routes, including legacy prices, are not
        # changed by an opt-in separate caller. Full historical golden suite
        # remains the authoritative byte comparison (17 fingerprints).
        self.assertNotIn('LAUNCH',__import__(
            'simulation.offworld_mvp.build8.route1_gate1',
            fromlist=['DEFAULT_PRICE']).DEFAULT_PRICE)
        self.assertEqual(len(CEILINGS),11)
        self.assertEqual(max(x['year'] for x in self.standard['rows']),2035)
        self.assertTrue(all(x['year']<=2035 for x in self.standard['rows']))
        self.assertFalse(any(x.get('body') for x in self.standard['rows']))
        with self.assertRaisesRegex(ValueError,'separate opt-in'):
            run_gate1(cast_trial=CastPaymentTrial(),followon_trial={'rules':{}})
        with self.assertRaisesRegex(ValueError,'cannot be mixed'):
            run_gate2(cast_trial=CastPaymentTrial(),followon_trial={'rules':{}})


if __name__ == '__main__':
    unittest.main()
