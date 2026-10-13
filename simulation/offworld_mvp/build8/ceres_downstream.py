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
from .country_capital_input import load_investment_capacity
from .opening import EARTH_V4_ROOT
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario

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
    ('operation_year_3',       '2043',     'scripted TEST_ONLY test of returned ISRO cash paying Ceres OPEX'),
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
    ('return_revenue_source',   'resource_export_to_earth_buyer',
                                'one existing paid Ceres export sale source; TEST_ONLY policy key'),
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
RETURNED = 'route1:returned_cash:ISRO'
LABEL = 'fixed Earth, no feedback to Earth'

# TEST_ONLY RETURN ROUTING, NOT A MODEL RULE. Exactly one source/owner row;
# later independent revenue sources add rows here, not new accounting code.
# Percentages and their bases live ONLY in TEST_ONLY_TABLE above.
RETURN_POLICY = {
    (A['return_revenue_source'], SPONSOR): {
        'owner_budget': BUDGET,
        'financier_intermediary': FIN_CASH,
        'returned_cash_test_instrument': RETURNED,
        'local_reinvestment': REINVEST,
        'reserve_account': CASH,
        'financier_share_key': 'financier_return_share',
        'owner_share_key': 'owner_return_share',
        'local_share_key': 'local_reinvest_share',
        'reserve_share_key': 'reserve_share',
        'exhausted_financier_claim': 'RESIDUAL_TO_OWNER_NOT_NEW_FINANCIER_CLAIM',
    },
}


def _total_money(k):
    return sum((a.balance for a in k.state.accounts.values()), D(0))


class CeresDownstream(AllBodyCampaign):
    """Add one opt-in physical lifecycle after the unchanged paid study hook."""

    def __init__(self):
        super().__init__(body_count=90)
        self.physical = []
        self.buyer_checks = []
        self.study_observation = None
        self.return_receipts = []
        self.return_spends = []
        self.sales = {}

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
        # TEST INSTRUMENT ONLY. Segregates repatriated cash to prove actual
        # later spending. NOT a structural bank/accounting/model requirement.
        k.add_account(RETURNED, SPONSOR, 'EARTH:IND', AccountKind.FUNDS)
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
        elif year == int(A['operation_year_3']):
            # Use a specific 2041 financier return, swept through ISRO, to
            # fund the next real Ceres OPEX. Cash is segregated for TEST proof.
            amount = T('quantity_per_operation') * T('unit_opex')
            lot = next(r for r in self.return_receipts
                       if r['year'] == int(A['operation_year_1'])
                       and r['kind'] == 'financier')
            assert D(lot['amount']) >= amount
            assert k.state.accounts[RETURNED].balance >= amount
            tx = k.transfer(year, RETURNED, CASH, amount,
                            TxPurpose.OTHER_INVESTMENT,
                            parent_ids=(lot['sweep_tx'], lot['sale_tx']))
            self.return_spends.append(dict(
                year=year, source_sale_tx=lot['sale_tx'],
                source_return_tx=lot['return_tx'], source_sweep_tx=lot['sweep_tx'],
                funding_tx=tx.id, amount=str(amount)))
            self.physical.append(dict(year=year, stage='RETURNED_CASH_FUNDED_OPERATIONS',
                amount=str(amount), transaction=tx.id,
                return_source_tx=lot['sweep_tx']))
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
        if year == int(A['operation_year_3']):
            funding = self.return_spends[-1]
            assert D(funding['amount']) == D(cost.total_opex)
            assert k.state.accounts[CASH].balance >= 0
            funding['expense_tx'] = cost.transaction_id
            k.audit('BUILD8_TEST_ONLY_RETURN_ACTUALLY_SPENT', year,
                    sale_tx=funding['source_sale_tx'],
                    return_tx=funding['source_return_tx'],
                    swept_tx=funding['source_sweep_tx'],
                    funding_tx=funding['funding_tx'],
                    expense_tx=cost.transaction_id,
                    amount=funding['amount'],
                    classification='TEST_ONLY_MECHANICAL_NOT_DECISION')
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
        self.sales[year] = record
        return record

    def _distribute(self, k, year):
        sale = self.sales[year]
        policy = RETURN_POLICY[(A['return_revenue_source'], SPONSOR)]
        paid = D(sale.transaction_value)
        opening = k.state.accounts[CASH].balance
        claim_remaining = k.financing_return_remaining(CLAIM)
        financier_target = paid * T(policy['financier_share_key'])
        financier_paid = min(financier_target, claim_remaining)
        # TEST_ONLY RULE CHOICE: an exhausted financier claim cannot be
        # expanded; its unpaid 20% share goes to the 100% owner ISRO.
        owner_paid = (paid * T(policy['owner_share_key'])
                      + financier_target - financier_paid)
        local_paid = paid * T(policy['local_share_key'])
        reserve = opening - financier_paid - owner_paid - local_paid
        prior_reserve = opening - paid
        assert reserve == prior_reserve + paid * T(policy['reserve_share_key'])
        assert min(financier_paid, owner_paid, local_paid, reserve) >= 0
        request = build_surplus_distribution_request(
            'ceres:distribution:'+str(year), year, PROJECT, CLAIM)
        decision = SurplusDistributionDecision(
            'ceres:distribution:decision:'+str(year), request.id, SPONSOR,
            SurplusDistributionDecisionOutcome.DISTRIBUTE,
            reserve, financier_paid, local_paid, owner_paid,
            'TEST_ONLY paid cash decomposition; exhausted claim residual to ISRO',
            SurplusDistributionReasonCode.DISTRIBUTION_AUTHORIZED, (),
            'TEST_ONLY:ceres:distribution:'+str(year), POLICY).validate_protocol(request)
        record = k.execute_surplus_distribution(
            year, SPONSOR, request, decision, policy['local_reinvestment'])
        assert k.state.accounts[CASH].balance == record.reserve
        txmap = {t.id:t for t in k.state.transactions}
        k.audit('BUILD8_TEST_ONLY_SALE_RETURN_LINK', year, sale_tx=sale.transaction_id,
                distribution_txs=record.transaction_ids,
                financier_return=str(financier_paid), owner_return=str(owner_paid),
                local_reinvest=str(local_paid), reserve=str(reserve),
                classification='TEST_ONLY_MECHANICAL_NOT_DECISION')
        # The frozen method must pay the financier account belonging to the
        # real, disbursed financing claim. Repatriate the cash afterward.
        for txid in record.transaction_ids:
            origin = txmap[txid]
            if origin.purpose not in (TxPurpose.FINANCIER_RETURN, TxPurpose.OWNER_DISTRIBUTION):
                continue
            if origin.purpose == TxPurpose.FINANCIER_RETURN:
                assert origin.destination_account == FIN_CASH
                repatriation = k.transfer(
                    year, FIN_CASH, policy['owner_budget'], origin.amount,
                    TxPurpose.RETURN_TO_EARTH,
                    parent_ids=(origin.id, sale.transaction_id))
                origin_for_sweep = repatriation.id
                kind = 'financier'
            else:
                assert origin.destination_account == policy['owner_budget']
                origin_for_sweep = origin.id
                kind = 'owner'
            sweep = k.transfer(
                year, policy['owner_budget'], policy['returned_cash_test_instrument'],
                origin.amount, TxPurpose.RETURN_TO_EARTH,
                parent_ids=(origin_for_sweep, sale.transaction_id))
            self.return_receipts.append(dict(
                year=year, kind=kind, source=A['return_revenue_source'],
                owner=SPONSOR, sale_tx=sale.transaction_id,
                return_tx=origin.id, sweep_tx=sweep.id, amount=str(origin.amount)))
        self.physical.append(dict(year=year, stage='DISTRIBUTED',
            sale_tx=sale.transaction_id, financier_return=str(record.financier_return),
            reinvestment=str(record.local_reinvestment),
            owner_return=str(record.owner_distribution),
            project_reserve=str(record.reserve),
            txs=record.transaction_ids))

    def on_year(self, year, k, rows):
        super().on_year(year, k, rows)
        if year not in {int(A[key]) for key in ('construction_year_1','construction_year_2',
                                                'operation_year_1','operation_year_2',
                                                'operation_year_3')}:
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
            if year in (int(A['operation_year_1']), int(A['operation_year_2'])):
                self._sell(k, year)
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
        report['label'] = LABEL
        report['closure'] = 'MECHANICAL_SCRIPTED_2043_NOT_DECISION'
        report['returned_cash_account'] = RETURNED
        report['returned_cash_instrument_not_model_rule'] = True
        report['return_policy'] = tuple(dict(revenue_source=source, owner=owner,
                                             **policy)
                                        for (source, owner), policy in RETURN_POLICY.items())
        report['return_receipts'] = tuple(self.return_receipts)
        report['return_spends'] = tuple(self.return_spends)
        return report

def _earth_gauge(k, root):
    # Reporting only; no change to the exogenous Earth v4 projection.
    # Draw is exactly the kernel's Earth-to-offworld capital shadow ledger.
    # Earth supplier study/CAPEX/OPEX payments are NOT another capital draw.
    # Sale REVENUE is an Earth purchase, NOT capital draw or capital return.
    capacities, provenance = load_investment_capacity(root, end_year=int(A['end_year']))
    units = load_prospecting_scenario().investment_proxy_units_per_model_currency
    impact = k.state.earth_impact
    output = []
    for (country, year), investment in sorted(capacities.items(), key=lambda x:(x[0][1],x[0][0])):
        capacity = investment / units
        node = 'EARTH:' + country
        draw = D(impact.capital_diverted_to_offworld.get((node,year),D(0)))
        returned = D(impact.capital_returned_to_earth.get((node,year),D(0)))
        output.append(dict(
            year=year, country=country, capacity=str(capacity),
            offworld_draw=str(draw), returns_received=str(returned),
            draw_pct_of_capacity=(('0' if not draw else str(draw / capacity * D(100))) if capacity else None),
            returns_pct_of_capacity=(('0' if not returned else str(returned / capacity * D(100))) if capacity else None),
            label=LABEL))
    return tuple(output), dict(
        label=LABEL, source=provenance['designation'],
        draw_definition='kernel earth_impact.capital_diverted_to_offworld Earth-to-offworld DISBURSE/PUBLIC_SUBSIDY/OTHER_INVESTMENT crossings',
        return_definition='kernel earth_impact.capital_returned_to_earth offworld-to-Earth RETURN_TO_EARTH/FINANCIER_RETURN/OWNER_DISTRIBUTION crossings',
        counted='Earth-to-offworld project financing including funded analytic studies and recycled sponsor funding; genuine capital returns',
        not_counted='Earth supplier study/CAPEX/OPEX payments as another draw; Earth buyer payments for exports as returns or capital draws; internal Earth-to-Earth sweeps; offworld-to-offworld reinvestment',
        denominator='Earth v4 annual country investment proxy / Build7 units_per_model_currency; reporting only, no feedback',
        zero_capacity='Undefined percentage (null), zero value amounts still 0',
        closure='mechanical scripted 2043 operation, not a decision')


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
    result['label'] = LABEL
    result['earth_gauge'], result['earth_gauge_definition'] = _earth_gauge(
        result['kernel'], EARTH_V4_ROOT if root is None else root)
    return result
