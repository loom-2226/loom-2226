"""Opt-in TEST_ONLY Route 1 A1 flyby-price experiment; no physical missions."""
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal as D
from pathlib import Path
from time import perf_counter

from ..route1_body_campaign import SETTINGS
from ..route1_all_body_campaign_pr3b import AllBodyCampaign
from ..route1_cast_payments import run_cast_payments

QUOTE_PATH = Path(__file__).with_name('A_VEHICLE_MISSION_PAIRS.csv')
RULE = {
    'A1': 'PRICED_TEST_ONLY baseline flyby lowest_price_usd / 1000000000; otherwise unchanged abstract A1 price',
    'table_years': [2026, 2027],
    'held_year': 2026,
    'year_policy': 'exact authored year when available, otherwise 2026',
    'labels': ['TABLE', 'HELD', 'ABSTRACT'],
    'abstract_policy': 'missing, infeasible or unpriced quote uses existing A1_SERVICE_PRICE',
    'A2': 'unchanged',
    'synthetic_study': True,
}
RULE_HASH = hashlib.sha256(json.dumps(RULE, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
QUOTE_HASH = hashlib.sha256(QUOTE_PATH.read_bytes()).hexdigest()


def stable_projection(result):
    campaign = dict(result['campaign'])
    for field in ('runtime_total_seconds', 'yearly_runtime_seconds', 'runtime_decades'):
        campaign.pop(field, None)
    return dict(rows=result['rows'], deliveries=result['deliveries'],
                executor_yearly=result['executor_yearly'], campaign=campaign)


def stable_hash(result):
    return hashlib.sha256(json.dumps(stable_projection(result), sort_keys=True,
                       default=str, separators=(',', ':')).encode()).hexdigest()


class FlybyCampaign(AllBodyCampaign):
    def __init__(self, ceilings_enabled=False):
        super().__init__(body_count=90, ceilings_enabled=ceilings_enabled)
        self.flyby_quotes = {}
        with QUOTE_PATH.open(newline='') as stream:
            for row in csv.DictReader(stream):
                if row['vehicle_class_id'] == 'baseline' and row['mission_type_id'] == 'flyby':
                    key = (int(row['year']), row['body'])
                    if key in self.flyby_quotes:
                        raise AssertionError('duplicate flyby quote')
                    self.flyby_quotes[key] = row
        self.price_source_attempts = Counter()
        self.price_source_paid = Counter()

    def attempt(self, k, sponsor, body, stage, year, used=0):
        source = 'UNCHANGED_A2'
        price = SETTINGS['A1_SERVICE_PRICE']
        if stage == 'A1':
            source_year = year if year in (2026, 2027) else 2026
            quote = self.flyby_quotes.get((source_year, body))
            if quote and quote['status'] == 'PRICED_TEST_ONLY' and quote['lowest_price_usd']:
                price = D(quote['lowest_price_usd']) / D('1000000000')
                source = 'TABLE' if year == source_year else 'HELD'
            else:
                source = 'ABSTRACT'
        # Single-threaded runner: only A1's existing price lookup is temporarily
        # supplied a different value. Existing decision and ledger chain stay intact.
        original = SETTINGS['A1_SERVICE_PRICE']
        try:
            if stage == 'A1':
                SETTINGS['A1_SERVICE_PRICE'] = price
            row = super().attempt(k, sponsor, body, stage, year, used)
        finally:
            SETTINGS['A1_SERVICE_PRICE'] = original
        row['price_source'] = source
        if stage == 'A1':
            self.price_source_attempts[year, source] += 1
        if row['outcome'] == 'FUNDED':
            self.receipts[-1]['price_source'] = source
            if stage == 'A1':
                self.price_source_paid[year, source] += 1
        return row

    def report(self):
        report = super().report()
        report['flyby_pricing'] = dict(rule=RULE, rule_sha256=RULE_HASH,
                                        pinned_quote_sha256=QUOTE_HASH,
                                        price_source_attempts=tuple(sorted((y, s, n) for (y, s), n in self.price_source_attempts.items())),
                                        price_source_paid=tuple(sorted((y, s, n) for (y, s), n in self.price_source_paid.items())))
        return report


def run_variant(ceilings_enabled=False):
    campaign = FlybyCampaign(ceilings_enabled=ceilings_enabled)
    campaign.record_states(2026)
    start = perf_counter()
    result = run_cast_payments(end_year=2226,
        run_setting={'name': 'all_body_campaign', 'campaign': campaign})
    paid = {(r['year'], r['executor']) for r in campaign.receipts}
    result['executor_yearly'] = tuple(dict(row, status=('PAID_TEST_ONLY_STUDY'
        if (row['year'], row['executor']) in paid else row['status']))
        for row in result['executor_yearly'])
    result['campaign'] = campaign.report()
    result['campaign']['runtime_total_seconds'] = round(perf_counter() - start, 6)
    return result


def run_identity(ceilings_enabled=False):
    return "variant_ceilings_" + ("on" if ceilings_enabled else "off")
