"""TEST_ONLY, NON-CANON: one Ceres physical lifecycle on the Route 1 cash ledger.

The prior paid A1/A2 studies remain analytical expenses, not physical CAPEX.
Synthetic recovery and market assumptions do not acquire scientific standing.
No distance, travel time, cargo delivery or transport costs are modeled.
"""
from decimal import Decimal as D

from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import (
    AgentKind, AgentState, ScenarioResource,
    OperatingCycleDecision, OperatingCycleDecisionOutcome, OperatingCycleReasonCode,
    SaleDecision, SaleDecisionOutcome, SaleReasonCode,
    SurplusDistributionDecision, SurplusDistributionDecisionOutcome,
    SurplusDistributionReasonCode,
)
from offworld_kernel.project_lifecycle import ProjectDevelopmentPlan
from offworld_kernel.market import CommodityMarketEnvelope
from offworld_kernel.distribution import FinancingReturnClaim
from offworld_kernel.operating_protocol import build_operating_cycle_request
from offworld_kernel.market_protocol import build_sale_decision_request
from offworld_kernel.distribution_protocol import build_surplus_distribution_request
from .route1_all_body_campaign_pr3b import AllBodyCampaign
from .sponsor_executor_network_trial import EXECUTORS

# SINGLE AUTHORING TABLE. All monetary values are MODEL_CURRENCY, quantities
# MODEL_RESOURCE_UNIT_BY_FAMILY; dates are calendar years. Every assumption is
# synthetic TEST_ONLY, never an inferred fact about Ceres or a qualified baseline.
# The existing A1/A2 payments are observed ledger transactions, NOT repeated.
TEST_ONLY_TABLE = (
    # key                     value      basis / meaning
    ('body',                   'CERES',    'existing 6C authored A1/A2 standings'),
    ('sponsor',                'ISRO',     'observed Ceres A1/A2 paid receipts on main'),
    ('executor',               'HAL / L&T','observed Ceres A2 BUILD executor, existing cast'),
    ('share',                  '0.25',     'existing full 90-body Route 1 run allocation share'),
    ('end_year',               '2226',     'existing 90-body Route 1 campaign end'),
    ('a2_review_year',         '2038',     'existing positive Ceres A2 review, not generated truth'),
    ('construction_year_1',    '2039',     'test year immediately after eligible A2 review'),
    ('construction_year_2',    '2040',     'second test year to prove staged construction'),
    ('operation_year_1',       '2041',     'test year after asset commissioning'),
    ('operation_year_2',       '2042',     'test year to spend actual reinvestment'),
    ('buyer_endowment',        '100',      'existing Earth-market B=100 from Build 7 opening'),
    ('a2_paid_study',          '0.015',    'observed prior A2 analytical BUILD receipt; no new debit'),
    ('physical_construction_cost','0.060','synthetic separate physical asset; not A2 study'),
    ('construction_stage_1',   '0.030',    'half of separately authored construction cost'),
    ('construction_stage_2',   '0.030',    'second construction stage; sums to 0.060'),
    ('operating_float',        '0.020',    'initial funded OPEX for first extraction'),
    ('in_situ',                '20',       'synthetic hidden TEST_ONLY resource stock'),
    ('accessible',             '10',       'synthetic physical accessibility after commissioning'),
    ('recoverable',            '8',        'synthetic recoverable stock; <= accessible'),
    ('productive_capacity',    '5',        'existing Build 7 structural fixture capacity, reused only for test'),
    ('quantity_per_operation', '2',       'synthetic two-year operating throughput, within capacity'),
    ('unit_opex',              '0.010',    'synthetic executor operating charge per resource unit'),
    ('unit_sale_price',        '0.050',    'synthetic finite-buyer market price per unit'),
    ('demand_per_year',        '2',        'synthetic market demand per operating year'),
    ('financier_return_share', '0.20',     'synthetic return share of first realized sale proceeds'),
    ('local_reinvest_share',   '0.40',     'synthetic local reinvestment share of first realized proceeds'),
    ('owner_return_share',     '0.20',     'synthetic owner distribution share of first proceeds'),
    ('reserve_share',          '0.20',     'synthetic project cash retained from first proceeds'),
    ('earth_supply_fraction',  '1',        'test resource-constraint fraction; stage/OPEX amounts define envelope'),
)
A = dict((key, value) for key, value, _ in TEST_ONLY_TABLE)
T = lambda key: D(A[key])
BODY = A['body']
SPONSOR = A['sponsor']
EXECUTOR = A['executor']
NODE = 'OFF:ROUTE1:CERES'
PROJECT = 'P'             # Legacy frozen recoverability contract; only in this run.
ASSET = 'MINE-P'          # Legacy frozen recoverability contract; only in this run.
CASH = 'ceres:physical:cash'
FINANCIER = 'CERES_TEST_FINANCIER'
FIN_CASH = 'ceres:physical:financier'
REINVEST = 'ceres:physical:reinvestment'
RESOURCE = 'ceres:synthetic:volatile_resource'
PLAN = 'ceres:physical:construction'
COMMIT = 'ceres:physical:commitment'
CLAIM = 'ceres:physical:return_claim'
SUPPLIER = 'route1:executor:' + EXECUTOR
BUDGET = 'route1:budget:' + SPONSOR
POLICY = 'BUILD8_CERES_TEST_ONLY_AUTHORED_DECISION'


def _total_money(k):
    return sum((a.balance for a in k.state.accounts.values()), D(0))


class CeresDownstream(AllBodyCampaign):
    """Add one opt-in physical lifecycle after the unchanged paid study hook."""

    def __init__(self):
        super().__init__(body_count=90)
        self.physical = []
        self.buyer_checks = []
        self.study_observation = None

    def _positive_a2(self, k):
        receipt = next(r for r in self.receipts
                       if r['body'] == BODY and r['stage'] == 'A2')
        review = next(r for r in self.studies
                      if r['body'] == BODY and r['stage'] == 'A2')
        a1 = self.reviews[BODY]
        assert receipt['sponsor'] == review['sponsor'] == a1['sponsor'] == SPONSOR
        assert receipt['executor'] == EXECUTOR
        assert receipt['delivery'] == 'DELIVERED'
        assert review['review'] == 'ADVANCE' and review['result'] == 'SUPPORTS_ADVANCE'
        assert review['year'] == int(A['a2_review_year'])
        assert review['disbursement_id'] == receipt['disbursement_id']
        assert k.state.accounts['route1:campaign:cash:CERES:' + SPONSOR].balance == 0
        assert a1['observation_id'] in k.agents[SPONSOR].information
        self.study_observation = a1['observation_id']
        return receipt, review

    def _start(self, k, year):
        receipt, review = self._positive_a2(k)
        assert 'P' not in k.state.projects and 'MINE-P' not in k.state.assets
        assert k.state.accounts['earth_market'].balance == T('buyer_endowment')
        assert EXECUTORS[EXECUTOR][0] == 'IND'
        assert SUPPLIER in k.state.accounts
        assert k.state.accounts[BUDGET].balance >= T('physical_construction_cost') + T('operating_float')
        k.add_node(NODE, NodeKind.OFFWORLD)
        k.add_account(CASH, SPONSOR, NODE, AccountKind.PROJECT_CASH)
        k.add_project(PROJECT, NODE, CASH, {SPONSOR:D(1)})
        k.add_resource(ScenarioResource(RESOURCE, NODE, 'VOLATILES', T('in_situ'), None, None, None))
        k.add_account(REINVEST, SPONSOR, NODE, AccountKind.FUNDS)
        k.add_account(FIN_CASH, FINANCIER, 'EARTH:IND', AccountKind.FUNDS)
        k.add_agent(AgentState(FINANCIER, AgentKind.PRIVATE_FINANCIER,
                               'EARTH:IND', FIN_CASH, {'FINANCE'}, ('RETURN',)))
        k.agents[SPONSOR].capabilities.update(
            {'DEVELOP','OPERATE','EXTRACT','SELL','DISTRIBUTE_SURPLUS'})
        funded = T('physical_construction_cost') + T('operating_float')
        investment = k.transfer(year, BUDGET, FIN_CASH, funded, TxPurpose.OTHER_INVESTMENT,
                                parent_ids=(receipt['disbursement_id'],))
        k.add_commitment(COMMIT, FINANCIER, PROJECT, funded)
        payment = k.disburse(year, COMMIT, FIN_CASH, funded)
        k.transition_project_status(year, SPONSOR, PROJECT, 'DEVELOPMENT',
                                    reason_ref=receipt['disbursement_id'])
        k.register_development_plan(ProjectDevelopmentPlan(
            PLAN, PROJECT, 'ceres:physical:wip', ASSET, SUPPLIER, NODE,
            T('physical_construction_cost'),
            ((int(A['construction_year_1']), T('construction_stage_1')),
             (int(A['construction_year_2']), T('construction_stage_2'))),
            int(A['construction_year_2']), T('productive_capacity'),
            'BUILD8_CERES_TEST_ONLY_PHYSICAL_PLAN'))
        k.register_financing_return_claim(FinancingReturnClaim(
            CLAIM, FINANCIER, PROJECT, FIN_CASH,
            T('unit_sale_price') * T('quantity_per_operation') * T('financier_return_share'),
            (COMMIT,), 'BUILD8_CERES_TEST_ONLY_FUNDED_COMMITMENT',
            'SYNTHETIC_NOT_A_FORECAST'))
        self.physical.append(dict(year=year, stage='FINANCE',
            sponsor_debit=str(funded), financier_debit=str(funded),
            project_cash=str(k.state.accounts[CASH].balance),
            investment_tx=investment.id, disbursement_tx=payment.id,
            study_receipt=receipt['disbursement_id'], study_review=review['result']))

    def _construction(self, k, year):
        cost = (T('construction_stage_1') if year == int(A['construction_year_1'])
                else T('construction_stage_2'))
        k.set_resource_constraint('EARTH:IND', year, cost, T('earth_supply_fraction'))
        stage = k.execute_development_stage(year, PLAN)
        assert stage.outcome.value == 'SPENT'
        self.physical.append(dict(year=year, stage='CONSTRUCTION',
            amount=str(cost), tx=stage.transaction_id,
            project_cash=str(k.state.accounts[CASH].balance),
            supplier_balance=str(k.state.accounts[SUPPLIER].balance)))
        if year == int(A['construction_year_2']):
            commissioned = k.resolve_development_plan(year, PLAN)
            assert commissioned.outcome.value == 'OPERATING'
            k.assess_resource_recoverability(
                year, RESOURCE, ScenarioResource(
                    RESOURCE, NODE, 'VOLATILES', T('in_situ'),
                    T('accessible'), T('recoverable'), T('recoverable')))
            self.physical.append(dict(year=year, stage='COMMISSIONED',
                asset=ASSET, capacity=str(k.state.assets[ASSET].capacity),
                remaining=str(k.resources[RESOURCE].remaining)))

    def _operate(self, k, year):
        if year == int(A['operation_year_2']):
            amount = T('quantity_per_operation') * T('unit_opex')
            tx = k.transfer(year, REINVEST, CASH, amount,
                            TxPurpose.LOCAL_REINVESTMENT, parent_ids=(CLAIM,))
            self.physical.append(dict(year=year, stage='REINVESTED_INTO_OPERATIONS',
                amount=str(amount), transaction=tx.id))
        k.set_resource_constraint('EARTH:IND', year,
                                  T('quantity_per_operation') * T('unit_opex'),
                                  T('earth_supply_fraction'))
        request = build_operating_cycle_request('ceres:operate:'+str(year), year,
                                                 PROJECT, RESOURCE, ASSET,
                                                 self.study_observation)
        quantity = T('quantity_per_operation')
        decision = OperatingCycleDecision(
            'ceres:operate:decision:'+str(year), request.id, SPONSOR,
            OperatingCycleDecisionOutcome.OPERATE, D(0), quantity,
            quantity * T('unit_opex'), 'TEST_ONLY authorized operating fixture',
            OperatingCycleReasonCode.OPERATING_CYCLE_AUTHORIZED, (),
            'TEST_ONLY:ceres:operating:'+str(year), POLICY).validate_protocol(request)
        cost = k.spend_operating_cycle(year, SPONSOR, request, decision, SUPPLIER, T('unit_opex'))
        extracted = k.resolve_operating_extraction(year, SPONSOR, request, decision, cost)
        k.admit_realized_output_observation(year, SPONSOR, extracted.extraction_event_id)
        self.physical.append(dict(year=year, stage='EXTRACTED',
            opex=str(cost.total_opex), opex_tx=cost.transaction_id,
            actual=str(extracted.actual_extracted), remaining=str(extracted.resource_after),
            inventory=str(extracted.inventory_after), event=extracted.extraction_event_id))
        return extracted

    def _sell(self, k, year):
        # All buyer checks happen before registering the sale or touching inventory.
        buyer = k.state.accounts['earth_market']
        buyer_cash = buyer.balance
        inventory = k.colonies[NODE].resource_inventory
        quantity = min(inventory, T('demand_per_year'), T('quantity_per_operation'))
        value = quantity * T('unit_sale_price')
        if quantity <= 0 or value <= 0 or buyer_cash < value:
            raise ValueError('BLOCKED_AFFORDABILITY: finite TEST_ONLY Earth buyer; no sale mutation')
        envelope = CommodityMarketEnvelope(
            'ceres:market:'+str(year), year, RESOURCE, 'earth_market',
            T('unit_sale_price'), T('demand_per_year'),
            'MODEL_CURRENCY', 'MODEL_RESOURCE_UNIT_BY_FAMILY',
            'BUILD8_CERES_TEST_ONLY_MARKET', 'SYNTHETIC_NOT_REAL_DEMAND')
        k.register_market_envelope(envelope)
        request = build_sale_decision_request('ceres:sale:'+str(year), year,
                                               PROJECT, RESOURCE, envelope.id,
                                               self.study_observation)
        decision = SaleDecision(
            'ceres:sale:decision:'+str(year), request.id, SPONSOR,
            SaleDecisionOutcome.OFFER, quantity, 'TEST_ONLY finite-buyer offer',
            SaleReasonCode.MARKET_OFFER_AUTHORIZED, (),
            'TEST_ONLY:ceres:market:'+str(year), POLICY).validate_protocol(request)
        record = k.clear_market_sale(year, SPONSOR, request, decision)
        assert record.transaction_value == value
        assert buyer.balance >= 0
        self.buyer_checks.append(dict(year=year, before=str(buyer_cash),
                                      paid=str(value), after=str(buyer.balance)))
        self.physical.append(dict(year=year, stage='SOLD',
            quantity=str(record.cleared_quantity), revenue=str(record.transaction_value),
            tx=record.transaction_id, buyer_after=str(buyer.balance),
            project_cash=str(k.state.accounts[CASH].balance)))
        return record

    def _distribute(self, k, year):
        opening = k.state.accounts[CASH].balance
        pieces = {key: opening*T(key) for key in (
            'financier_return_share','local_reinvest_share','owner_return_share','reserve_share')}
        assert sum(pieces.values(), D(0)) == opening
        request = build_surplus_distribution_request(
            'ceres:distribution:'+str(year), year, PROJECT, CLAIM)
        decision = SurplusDistributionDecision(
            'ceres:distribution:decision:'+str(year), request.id, SPONSOR,
            SurplusDistributionDecisionOutcome.DISTRIBUTE,
            pieces['reserve_share'], pieces['financier_return_share'],
            pieces['local_reinvest_share'], pieces['owner_return_share'],
            'TEST_ONLY paid cash decomposition',
            SurplusDistributionReasonCode.DISTRIBUTION_AUTHORIZED, (),
            'TEST_ONLY:ceres:distribution:'+str(year), POLICY).validate_protocol(request)
        record = k.execute_surplus_distribution(year, SPONSOR, request, decision, REINVEST)
        assert k.state.accounts[FIN_CASH].balance == record.financier_return
        self.physical.append(dict(year=year, stage='DISTRIBUTED',
            financier_return=str(record.financier_return),
            reinvestment=str(record.local_reinvestment),
            owner_return=str(record.owner_distribution),
            project_reserve=str(record.reserve),
            txs=record.transaction_ids))

    def on_year(self, year, k, rows):
        super().on_year(year, k, rows)
        if year not in {int(A[key]) for key in ('construction_year_1','construction_year_2',
                                                'operation_year_1','operation_year_2')}:
            return
        total_before = _total_money(k)
        balance_before = k.state.accounts[BUDGET].balance
        if year == int(A['construction_year_1']):
            self._start(k, year)
            self._construction(k, year)
        elif year == int(A['construction_year_2']):
            self._construction(k, year)
        else:
            self._operate(k, year)
            self._sell(k, year)
            if year == int(A['operation_year_1']):
                self._distribute(k, year)
        assert _total_money(k) == total_before, 'downstream cash creation/destruction'
        assert k.state.accounts['earth_market'].balance >= 0, 'unfunded market buyer'
        # Original study spend remains separate; reflect the one extra budget debit.
        sponsor_row = next(r for r in rows if r['sponsor'] == SPONSOR)
        extra = balance_before - k.state.accounts[BUDGET].balance
        sponsor_row['downstream_budget_spend'] = str(extra)
        sponsor_row['closing'] = str(k.state.accounts[BUDGET].balance)
        self.annual[-1]['closing'] = str(sum(
            (k.state.accounts['route1:budget:'+s].balance for s in self.requesters), D(0)))
        assert D(sponsor_row['opening']) + D(sponsor_row['allocated']) == (
            D(sponsor_row['campaign_spend']) + extra + D(sponsor_row['closing']))
        # Route 1 already has independently funded annual EARTH_BOUNDARY origins
        # that do not use the older Build 4 global boundary-opening convention.
        # Audit the finite buyer explicitly, alongside unchanged Route 1 checks.
        assert (k.state.accounts['earth_market'].balance - T('buyer_endowment')
                == k.boundary_net['earth_market']), 'buyer ledger/boundary mismatch'
        assert all(a.balance >= 0 for a in k.state.accounts.values()
                   if a.kind != AccountKind.EARTH_BOUNDARY), 'negative non-boundary cash'
        k.assert_invariants()

    def report(self):
        report = super().report()
        report['physical'] = tuple(self.physical)
        report['buyer_checks'] = tuple(self.buyer_checks)
        report['classification'] = 'TEST_ONLY_NON_CANON_NO_TRANSPORT_OR_DISTANCE'
        return report


def run_ceres_downstream(*, root=None):
    """One opt-in 201-year Route 1 run; no change to other modes."""
    from .route1_cast_payments import run_cast_payments
    campaign = CeresDownstream()
    campaign.record_states(2026)
    result = run_cast_payments(
        share=T('share'), end_year=int(A['end_year']), root=root,
        run_setting={'name':'ceres_downstream','campaign':campaign})
    result['campaign'] = campaign.report()
    result['authored'] = TEST_ONLY_TABLE
    return result
