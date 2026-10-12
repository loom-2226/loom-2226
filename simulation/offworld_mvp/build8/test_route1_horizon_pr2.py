"""Route 1 PR 2: 201-year Earth boundary, annual conservation and pinned old decade."""
from collections import Counter, defaultdict
from decimal import Decimal as D
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from .country_capital_input import load_investment_capacity, SOURCES
from .opening import EARTH_V4_ROOT
from .route1_cast_payments import run_cast_payments
from .route1_gate2 import run_gate2
from .sponsor_executor_network_trial import PUBLIC, PRIVATE, EXECUTORS

GOLDEN = Path(__file__).with_name('ROUTE1_HORIZON_MAIN_79a10e1_BASELINE.json')
SEGMENTS = (
    ('qualified_inputs/countries_2026_2031.ndjson', 2026, 2031),
    ('stage_2031_2060/countries_2031_2060.ndjson', 2032, 2060),
    ('successor_80_2226/results/countries_2060_2226.ndjson', 2061, 2226),
)


def serialized_sha(rows):
    return sha256(json.dumps(rows, sort_keys=True, separators=(',',':'),
                             default=str).encode()).hexdigest()


def ledger_transactions(kernel):
    return [dict(year=t.year,source=t.source_account,destination=t.destination_account,
                 amount=str(t.amount),purpose=t.purpose.value,
                 parents=list(t.parent_ids),id=t.id)
            for t in kernel.state.transactions]


class Route1HorizonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_year,cls.end_year=2026,2226
        cls.golden=json.loads(GOLDEN.read_text())
        cls.full_world=run_cast_payments(end_year=2226)
        cls.capacities,cls.provenance=load_investment_capacity(EARTH_V4_ROOT,end_year=2226)

    def test_201_annual_cycles_twenty_sponsors_and_sixteen_eligible_executors(self):
        r=self.full_world
        sponsors=set(PUBLIC)|set(PRIVATE)
        executors=set(EXECUTORS)
        self.assertEqual((len(sponsors),len(executors)),(20,16))
        years=set(range(2026,2227))
        self.assertEqual({x['year'] for x in r['rows']},years)
        self.assertEqual(len(r['rows']),4020)
        self.assertEqual(Counter(x['year'] for x in r['rows']),{y:20 for y in years})
        self.assertEqual(len({(x['year'],x['sponsor']) for x in r['rows']}),4020)
        self.assertEqual({x['sponsor'] for x in r['rows']},sponsors)
        self.assertEqual(len(r['executor_yearly']),3216)
        self.assertEqual(Counter(x['year'] for x in r['executor_yearly']),
                         {y:16 for y in years})
        for y in years:
            names={x['executor'] for x in r['executor_yearly'] if x['year']==y}
            self.assertEqual(names,executors)
        self.assertEqual(r['eligible_executors'],executors)
        self.assertEqual(len(r['deliveries']),20)
        self.assertEqual(sum(x['status'].startswith('PAID_') for x in r['executor_yearly']),15)
        self.assertEqual(Counter(x['year'] for x in r['deliveries']),{2026:20})
        self.assertEqual({x['year'] for x in r['rows'] if x['disbursement']},{2026})
        for row in r['rows']:
            if row['year']>2026:
                self.assertEqual((row['status'],row['policy'],row['reason']),
                                 ('COMPLETE','NOT_EVALUATED','ALREADY_PURCHASED'))
                self.assertIsNone(row['delivery'])
        self.assertEqual(
            sum(x['status']=='ELIGIBLE_NO_NEW_COMMISSION'
                for x in r['executor_yearly'] if x['year']>=2027),
            16*200)

    def test_complete_Earth_source_and_exact_handoffs(self):
        c=self.capacities
        self.assertEqual(len(c),80*201)
        countries={country for country,_ in c}
        self.assertEqual(len(countries),80)
        self.assertEqual({year for _,year in c},set(range(2026,2227)))
        self.assertEqual(len(SOURCES),2)  # Defense V2 pinned historical boundary
        self.assertEqual(len(self.provenance['sources']),3)
        self.assertEqual([x['path'] for x in self.provenance['sources']],
                         [x[0] for x in SEGMENTS])
        for index,(name,a,b) in enumerate(SEGMENTS):
            raw=(EARTH_V4_ROOT/name).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(),
                             self.provenance['sources'][index]['sha256'])
            selected={}
            for line in raw.splitlines():
                d=json.loads(line)
                if a <= d['year'] <= b:
                    selected[d['iso3'],d['year']]=D(str(d['investment']))
            self.assertEqual(len(selected),80*(b-a+1))
            for k,v in selected.items():
                self.assertEqual(c[k],v)
        self.assertTrue(all(v.is_finite() and v >= 0 for v in c.values()))
        # Source starts and ends are covered, not accidentally smoothed.
        for y in (2026,2031,2032,2035,2036,2060,2061,2226):
            self.assertEqual(sum((country,y) in c for country in countries),80)
        self.assertEqual(self.provenance['standing'],
                         'MODELED_INVESTMENT_CAPACITY_NOT_SPENDABLE_CASH')

    def test_malformed_or_missing_late_record_is_rejected(self):
        # Two first files are readonly symlinks; only the successor file is
        # rewritten inside a temporary fake baseline, never the real Earth v4.
        with tempfile.TemporaryDirectory() as folder:
            fake=Path(folder)/'earth_long_run_economic_baseline_v4_2026_09_24'
            fake.mkdir()
            for name,_,_ in SEGMENTS:
                target=fake/name
                target.parent.mkdir(parents=True,exist_ok=True)
                source=EARTH_V4_ROOT/name
                if 'successor_80_2226' not in name:
                    target.symlink_to(source)
                else:
                    target.write_bytes(source.read_bytes())
            name=SEGMENTS[-1][0]
            target=fake/name
            original=target.read_bytes().splitlines(keepends=True)
            selected_index=next(i for i,line in enumerate(original)
                                if (j:=json.loads(line))['year']==2226 and j['iso3']=='USA')
            removed=original[:selected_index]+original[selected_index+1:]
            target.write_bytes(b''.join(removed))
            with self.assertRaisesRegex(ValueError,'incomplete 80-economy'):
                load_investment_capacity(fake,end_year=2226)
            changed=list(original)
            wrong=json.loads(changed[selected_index])
            wrong['investment']='NaN'
            changed[selected_index]=(json.dumps(wrong)+'\n').encode()
            target.write_bytes(b''.join(changed))
            with self.assertRaisesRegex(ValueError,'malformed Earth v4 record'):
                load_investment_capacity(fake,end_year=2226)
        with self.assertRaisesRegex(ValueError,'2035..2226'):
            load_investment_capacity(EARTH_V4_ROOT,end_year=2227)
        with self.assertRaisesRegex(ValueError,'2029..2035'):
            run_gate2(end_year=2226)

    def test_2026_2035_rows_delivery_receipts_ledger_and_control_fingerprint_match_main(self):
        golden=self.golden
        self.assertEqual(golden['base_main_sha'],
                         '79a10e1f70f4992ff83fdbd2e4768c707318839d')
        prefix=[x for x in self.full_world['rows'] if x['year']<=2035]
        self.assertEqual(len(prefix),200)
        self.assertEqual(prefix,golden['rows'])
        self.assertEqual(list(self.full_world['deliveries']),golden['deliveries'])
        past=[t for t in ledger_transactions(self.full_world['kernel']) if t['year']<=2035]
        self.assertEqual(len(past),450)
        self.assertEqual(past,golden['transactions'])
        self.assertEqual(serialized_sha(prefix),
                         '15fdc6b00df21d6b748a67a36fe9fbbca6d6fcb6156222ff1b5657eecca8b9cb')
        self.assertEqual(serialized_sha(past),
                         'f7e5ea74867d051e41bffab7f366bbfb5dd3e801fc4a9d324703eeed55fbea86')
        unchanged=run_cast_payments()  # original default decade
        self.assertEqual(unchanged['rows'],golden['rows'])
        self.assertEqual(list(unchanged['deliveries']),golden['deliveries'])
        self.assertEqual(ledger_transactions(unchanged['kernel']),golden['transactions'])
        self.assertEqual(unchanged['kernel'].fingerprint(),golden['fingerprint'])
        self.assertNotIn('executor_yearly',unchanged)

    def test_every_year_cash_conserved_sponsor_country_project_and_supplier(self):
        run=self.full_world
        rows={(r['sponsor'],r['year']):r for r in run['rows']}
        sponsors=tuple(sorted(set(PUBLIC)|set(PRIVATE)))
        k=run['kernel']
        trans_by_year=defaultdict(list)
        for t in k.state.transactions:
            trans_by_year[t.year].append(t)
        previous={s:D(0) for s in sponsors}
        total_disbursement=D(0)
        total_supplier_payments=D(0)
        all_origins=set()
        for y in range(2026,2227):
            transactions=trans_by_year[y]
            for sponsor in sponsors:
                row=rows[sponsor,y]
                budget='route1:budget:'+sponsor
                alloc=sum((t.amount for t in transactions
                           if t.destination_account==budget
                           and t.source_account.startswith('route1:origin:')),D(0))
                spent=sum((t.amount for t in transactions
                           if t.source_account==budget
                           and t.purpose.value=='DISBURSE'),D(0))
                self.assertLessEqual(abs(previous[sponsor]+alloc-spent-
                                         D(row['closing'])),D('1e-24'),(sponsor,y))
                self.assertEqual(D(row['opening']),alloc if y==2026 else previous[sponsor])
                if y!=2026:
                    self.assertEqual(D(row['allocated']),alloc)
                self.assertEqual(bool(row['disbursement']),spent>0)
                if row['disbursement']:
                    self.assertEqual(spent,D(row['authored_price']))
                previous[sponsor]=D(row['closing'])
                total_disbursement+=spent
            source_origins={t.source_account for t in transactions
                            if t.source_account.startswith('route1:origin:')}
            all_origins.update(source_origins)
            self.assertEqual(len(source_origins),23,(y,'qualified country financing envelopes'))
            for origin in source_origins:
                self.assertEqual(k.state.accounts[origin].balance, D(0),origin)
            payments=[t for t in transactions if t.source_account.startswith(
                      'route1:cash:') and t.purpose.value=='CAPEX']
            funding=[t for t in transactions if t.purpose.value=='DISBURSE']
            self.assertEqual(sum((t.amount for t in funding),D(0)),
                             sum((t.amount for t in payments),D(0)))
            total_supplier_payments+=sum((t.amount for t in payments),D(0))
            if y>2026:
                self.assertEqual(len(funding),0)
                self.assertEqual(len(payments),0)
        self.assertEqual(len(all_origins),23*201)
        self.assertFalse(any('QAT' in origin for origin in all_origins))
        self.assertEqual(total_disbursement,total_supplier_payments)
        self.assertEqual(len(run['deliveries']),20)
        for sponsor in sponsors:
            self.assertEqual(k.state.accounts['route1:budget:'+sponsor].balance,
                             previous[sponsor])
            self.assertEqual(k.state.accounts['route1:cash:'+sponsor].balance,D(0))
        supplier_total=sum((k.state.accounts['route1:executor:'+e].balance
                            for e in run['paid_executors']),D(0))
        self.assertEqual(supplier_total,total_supplier_payments)
        k.assert_invariants()

    def test_extended_201_year_replay_is_deterministic(self):
        again=run_cast_payments(end_year=2226)
        self.assertEqual(again['rows'],self.full_world['rows'])
        self.assertEqual(again['executor_yearly'],self.full_world['executor_yearly'])
        self.assertEqual(again['deliveries'],self.full_world['deliveries'])
        self.assertEqual(again['kernel'].fingerprint(),
                         self.full_world['kernel'].fingerprint())
        self.assertEqual(len(again['kernel'].state.transactions),
                         len(self.full_world['kernel'].state.transactions))
