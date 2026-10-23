"""Opt-in Build 8 Route 1 sponsor/executor payment experiment.

AUTHORED TEST_ONLY NON-CANON. The service units are abstract category-matched
work packages, NOT launch manifests, physical missions or measured vendor bids.
Only pre-existing Route 1 country-budget, project-cash and supplier accounts.
"""
from decimal import Decimal as D

from offworld_kernel.model import AccountKind, TxPurpose
from .master_cast import actor
from .route1_gate1 import CEILINGS
from .sponsor_executor_network_trial import EXECUTORS, PROJECTS, PUBLIC, PRIVATE

# Only the nine missing Route 1 participants. Existing eleven ceilings unchanged.
EXTRA_CEILINGS = {
    'Roscosmos': '.100', 'CSA': '.100', 'KASA': '.100',
    'SpaceX': '.200', 'Blue Origin': '.200', 'Axiom': '.100',
    'Isar Aerospace': '.100', 'Starlab': '.100', 'LandSpace': '.100',
}
assert not (set(EXTRA_CEILINGS) & set(CEILINGS))
assert set(EXTRA_CEILINGS) | set(CEILINGS) == set(PUBLIC) | set(PRIVATE)

# One comparable, site-agnostic TEST_ONLY work unit per category.
# This is deliberately NOT the network trial's project-size 'cost'.
SERVICES = {
    'BUILD': ('ONE_AUTHORED_BUILD_WORK_PACKAGE', '.015'),
    'LAND': ('ONE_AUTHORED_LANDING_WORK_PACKAGE', '.020'),
    'LAUNCH': ('ONE_AUTHORED_LAUNCH_SERVICE_UNIT', '.020'),
    'RUN': ('ONE_AUTHORED_OPERATIONS_SERVICE_UNIT', '.015'),
}

# Existing 20-sponsor network relationships are authored, not actual contracts.
PREFERRED = {
    'NASA': 'Astrobotic', 'CNSA': 'CASC', 'Roscosmos': 'RKK Energia',
    'ISRO': 'HAL / L&T', 'JAXA': 'Mitsubishi Heavy Industries',
    'ESA': 'Thales Alenia Space', 'CNES': 'Airbus Defence and Space',
    'DLR': 'OHB', 'CSA': 'MDA Space', 'KASA': 'Hanwha Aerospace',
    'Australian Space Agency': 'Toyota',
    'UAE Space Agency': 'Thales Alenia Space',
    'SpaceX': 'SpaceX', 'Blue Origin': 'Blue Origin',
    'Axiom': 'Thales Alenia Space', 'ispace': 'ispace',
    'Interlune': 'Northrop Grumman', 'Isar Aerospace': 'Isar Aerospace',
    'Starlab': 'MDA Space', 'LandSpace': 'CASC',
}

def available_quotes():
    """Each of the 16 selected executors offers its existing eligible categories.

    Price is explicit TEST_ONLY and equal within a category; authored preferred
    relations resolve ties, then the stable cast actor ID.
    """
    return {category: tuple((executor, D(price))
                            for executor, (_, caps) in sorted(EXECUTORS.items())
                            if category in caps)
            for category, (_, price) in SERVICES.items()}


class CastPaymentTrial:
    """Run-local hook; optional sponsor-scoped authored quote rows are test inputs."""

    def __init__(self, bids_by_sponsor=None, failures=()):
        self.ceilings = dict(EXTRA_CEILINGS)
        self.bids_by_sponsor = {} if bids_by_sponsor is None else {
            s: tuple((e, D(p)) for e, p in rows)
            for s, rows in bids_by_sponsor.items()
        }
        if set(self.bids_by_sponsor) - set(PROJECTS):
            raise ValueError('bid override references unlisted sponsor')
        self.failures = frozenset(failures)
        if self.failures - set(PROJECTS):
            raise ValueError('failure override references unlisted sponsor')
        self.deliveries = {}
        self.quotes_by_category = available_quotes()
        assert set(PREFERRED) == set(PROJECTS)
        assert set(self.quotes_by_category) == set(SERVICES)

    def choose_quote(self, sponsor, category):
        """Lowest comparable quote, then preferred relationship, then stable ID."""
        if sponsor not in PROJECTS or category != PROJECTS[sponsor][1]:
            raise ValueError('unrecognized sponsor/service category')
        if sponsor in self.bids_by_sponsor:
            bids = self.bids_by_sponsor[sponsor]
        else:
            bids = self.quotes_by_category[category]
        if not bids:
            raise ValueError('no authored comparable executor quote: ' + sponsor)
        ranked = []
        for executor, amount in bids:
            if executor not in EXECUTORS or category not in EXECUTORS[executor][1]:
                raise ValueError('executor lacks required capability: ' + str(executor))
            if not amount.is_finite() or amount <= 0:
                raise ValueError('invalid authored quote price')
            actor_id = actor(executor, 'executor', category)['id']
            ranked.append((amount, int(executor != PREFERRED[sponsor]),
                           actor_id, executor))
        if len({e for _, _, _, e in ranked}) != len(ranked):
            raise ValueError('duplicate bid from executor')
        amount, _, _, winner = min(ranked)
        return {'executor': winner, 'price': amount, 'category': category,
                'unit': SERVICES[category][0], 'offers': len(ranked),
                'offer_rows': tuple((e, str(p)) for p, _, _, e in sorted(ranked)),
                'comparison': 'LOWEST_PRICE_THEN_PREFERRED_THEN_ACTOR_ID',
                'classification': 'AUTHORED TEST_ONLY NON-CANON'}

    def audit_quote(self, kernel, year, sponsor, category, quote):
        kernel.audit('BUILD8_ROUTE1_EXECUTOR_QUOTE', year, sponsor=sponsor,
                     executor=quote['executor'], category=category,
                     service_unit=quote['unit'], price=quote['price'],
                     comparable_offers=quote['offers'],
                     offers=quote['offer_rows'], rank_rule=quote['comparison'],
                     standing=quote['classification'])

    def settle(self, kernel, year, sponsor, category, quote, disbursement):
        """One Route 1 project-cash -> executor-supplier transaction; no new money."""
        if not disbursement or not quote or quote['category'] != category:
            raise ValueError('paid delivery requires funded matching work')
        key = (sponsor, year)
        if key in self.deliveries:
            raise ValueError('duplicate payment for sponsor/year')
        price = quote['price']
        source = 'route1:cash:' + sponsor
        if kernel.state.accounts[source].balance != price:
            raise ValueError('project cash and awarded quote disagree')
        executor = quote['executor']
        destination = 'route1:executor:' + executor
        if destination not in kernel.state.accounts:
            kernel.add_account(destination, executor,
                               'EARTH:' + EXECUTORS[executor][0],
                               AccountKind.SUPPLIER)
        kernel.audit('BUILD8_ROUTE1_WORK_AUTHORIZATION', year,
                     sponsor=sponsor, executor=executor, service_unit=quote['unit'],
                     financing_receipt=disbursement, price=price,
                     classification='AUTHORED TEST_ONLY NON-CANON')
        transaction = kernel.transfer(year, source, destination, price,
                                      TxPurpose.CAPEX, parent_ids=(disbursement,))
        outcome = 'FAILED' if sponsor in self.failures else 'DELIVERED'
        receipt = {'sponsor': sponsor, 'year': year, 'executor': executor,
                   'category': category, 'unit': quote['unit'],
                   'price': str(price), 'transaction': transaction.id,
                   'source_disbursement': disbursement, 'outcome': outcome,
                   'produced': None if outcome == 'FAILED'
                   else 'BUILD8_TRIAL_DELIVERABLE:' + sponsor + ':' + str(year),
                   'same_owner': sponsor == executor}
        self.deliveries[key] = receipt
        kernel.audit('BUILD8_ROUTE1_EXECUTOR_SETTLEMENT', year,
                     **{k: v for k, v in receipt.items() if k != 'year'}, classification='AUTHORED TEST_ONLY NON-CANON',
                     full_payment_on_failure=True, physical_delivery_claim=False)
        if kernel.state.accounts[source].balance != 0:
            raise AssertionError('funded project cash not conserved through supplier payment')
        return 'PAID_' + outcome

    def delivery_for(self, sponsor, year):
        return self.deliveries.get((sponsor, year))


def run_cast_payments(share=D('.25'), scenario='B', end_year=2035,
                      root=None, bids_by_sponsor=None, failures=(),run_setting='cast_payments'):
    """Experimental Route 1: default decade or opt-in 2026-2226 horizon."""
    from .route1_gate2 import run_gate2
    from .opening import EARTH_V4_ROOT
    trial = CastPaymentTrial(bids_by_sponsor=bids_by_sponsor, failures=failures)
    if run_setting == 'cast_payments':
        selected = {'name': 'cast_payments', 'payload': trial}
    elif (isinstance(run_setting, dict) and set(run_setting) == {'name', 'campaign'}
          and run_setting['name'] in ('two_body_campaign', 'all_body_campaign', 'ceres_downstream', 'general_project_campaign')):
        selected = {**run_setting, 'payments': trial}
    else:
        raise ValueError('cast payment runner requires a named payment or campaign run')
    rows, kernel = run_gate2(share=share, scenario=scenario, end_year=end_year,
                             root=EARTH_V4_ROOT if root is None else root,
                             run_setting=selected)
    opening = [row for row in rows if row['year'] == 2026]
    distinct_deciders = {row['sponsor'] for row in opening if row['policy'] in
                         ('APPROVE', 'REJECT', 'DEFER')}
    eligible_executors = set().union(
        *(set(e for e, _ in quotes) for quotes in trial.quotes_by_category.values()))
    paid_executors = {receipt['executor'] for receipt in trial.deliveries.values()}
    kernel.assert_invariants()
    result = {'rows': rows, 'kernel': kernel, 'deliveries': tuple(
        trial.deliveries[key] for key in sorted(trial.deliveries)),
            'deciders': distinct_deciders, 'eligible_executors': eligible_executors,
            'paid_executors': paid_executors, 'trial': trial}
    if end_year > 2035:
        # Keep all 16 eligible executors visible annually without inventing
        # new commissions after the one currently authored 2026 work package.
        paid_by_year = {(r['year'], r['executor']): r['outcome']
                        for r in trial.deliveries.values()}
        result['executor_yearly'] = tuple({
            'year': year, 'executor': executor, 'eligible_services': EXECUTORS[executor][1],
            'status': ('PAID_' + paid_by_year[year, executor]
                       if (year, executor) in paid_by_year
                       else 'ELIGIBLE_NO_NEW_COMMISSION')}
            for year in range(2026, end_year + 1)
            for executor in sorted(EXECUTORS))
    return result
