"""Scenario driven generic economic lifecycle for Build 8.

All amounts, actors, identities, body data and calendar offsets arrive through
the project state. This module contains no body, sponsor, executor or year rule.
Synthetic outputs are explicitly PLACEHOLDER; the kernel's realized extraction
is retained for exact Ceres API equivalence but is not promoted as an observation.
"""
from collections import Counter
from decimal import Decimal as D
import hashlib
import json

from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import (
    AgentKind, AgentState, ScenarioResource, OperatingCycleDecision,
    OperatingCycleDecisionOutcome, OperatingCycleReasonCode, SaleDecision,
    SaleDecisionOutcome, SaleReasonCode, SurplusDistributionDecision,
    SurplusDistributionDecisionOutcome, SurplusDistributionReasonCode,
)
from offworld_kernel.project_lifecycle import ProjectDevelopmentPlan
from offworld_kernel.market import CommodityMarketEnvelope
from offworld_kernel.distribution import FinancingReturnClaim
from offworld_kernel.operating_protocol import build_operating_cycle_request
from offworld_kernel.market_protocol import build_sale_decision_request
from offworld_kernel.distribution_protocol import build_surplus_distribution_request
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.sponsor_executor_network_trial import EXECUTORS
from simulation.offworld_mvp.build8.return_routing import apply_operator_grants, resolve_destination


def _d(value):
    return D(str(value))


def _total_money(kernel):
    return sum((account.balance for account in kernel.state.accounts.values()), D(0))


def scenario_identity(scenario, price_bytes):
    # The stored identity field is excluded so the scenario can carry the
    # computed value without a recursive/self-referential digest.
    payload = dict(scenario)
    payload.pop('run_identity', None)
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(canonical + b'\0' + hashlib.sha256(price_bytes).digest()).hexdigest()


class ProjectState:
    """Mutable state for one project, separate from campaign orchestration."""
    def __init__(self, definition, material_families):
        self.definition = definition
        self.family = material_families[definition['material_family']]
        self.body = definition['body']
        self.sponsor = definition['sponsor']
        self.executor = definition['executor']
        self.project_id = definition['project_id']
        self.accounts = definition['accounts']
        self.ids = definition['ids']
        self.start_year = int(definition['start_year'])
        self.schedule = {key: self.start_year + int(offset)
                         for key, offset in definition['schedule_offsets'].items()}
        self.physical = []
        self.buyer_checks = []
        self.return_receipts = []
        self.return_spends = []
        self.appropriations = []
        self.operator_grants = ()
        self.owner_destination = None
        self.sales = {}
        self.realized_outputs = []

    def value(self, key):
        return _d(self.definition[key])

    def family_value(self, key):
        return _d(self.family[key])

    def offset_year(self, key):
        return self.schedule[key]

    @property
    def project(self):
        return self.project_id

    @property
    def node(self):
        return self.ids['node']

    @property
    def asset(self):
        return self.ids['asset']

    @property
    def resource(self):
        return self.ids['resource']

    @property
    def cash(self):
        return self.accounts['project_cash']

    @property
    def financier_cash(self):
        return self.accounts['financier_cash']

    @property
    def reinvestment(self):
        return self.accounts['reinvestment']

    @property
    def commitment(self):
        return self.ids['commitment']

    @property
    def return_claim(self):
        return self.ids['return_claim']

    @property
    def plan(self):
        return self.ids['plan']

    @property
    def policy(self):
        return self.ids['policy']


class EconomicLifecycle:
    """Six kernel lifecycle operations, each parameterized by ProjectState."""
    def __init__(self, project_state, scenario):
        self.p = project_state
        self.scenario = scenario
        self.sponsor = self.p.sponsor
        self.executor = self.p.executor
        self.budget = self.p.accounts['budget_prefix'] + self.sponsor
        self.supplier = self.p.accounts['supplier_prefix'] + self.executor
        self.financier = self.p.definition['financier_id']
        self.owner = self.p.definition['owner_id']
        self.buyer = self.p.definition['buyer']

    def _start(self, kernel, year, study_receipt, study_review):
        p = self.p
        assert p.project not in kernel.state.projects and p.asset not in kernel.state.assets
        assert kernel.state.accounts[self.buyer['account']].balance == _d(self.buyer['endowment'])
        assert kernel.state.accounts[self.budget].balance >= p.value('physical_construction_cost') + p.value('operating_float')
        kernel.add_node(p.node, NodeKind.OFFWORLD)
        kernel.add_account(p.cash, self.sponsor, p.node, AccountKind.PROJECT_CASH)
        country_node = kernel.agents[self.sponsor].node_id
        country = country_node.removeprefix('EARTH:')
        owner = 'STATE:' + country
        treasury = p.accounts['treasury_prefix'] + country
        kernel.add_account(treasury, owner, country_node, AccountKind.FUNDS)
        kernel.add_project(p.project, p.node, p.cash, {owner: D(1)})
        grants = tuple((g['operator'], p.project, g['owner'], g['reason'])
                       for g in p.definition['operator_grants'])
        p.operator_grants = apply_operator_grants(kernel, grants)
        p.owner_destination = resolve_destination(
            kernel, p.definition['return_revenue_source'], p.definition['owner_type'],
            owner, self.sponsor)
        assert p.owner_destination['delay_years'] == int(p.definition['appropriation_delay_years'])
        family = p.family
        kernel.add_resource(ScenarioResource(p.resource, p.node,
            p.definition['material_family'], p.family_value('in_situ'), None, None, None))
        kernel.add_account(p.reinvestment, self.sponsor, p.node, AccountKind.FUNDS)
        executor_country = p.definition['executor_location']
        kernel.add_account(p.financier_cash, self.financier, 'EARTH:' + executor_country,
                           AccountKind.FUNDS)
        kernel.add_agent(AgentState(self.financier, AgentKind.PRIVATE_FINANCIER,
                                    'EARTH:' + executor_country, p.financier_cash,
                                    {'FINANCE'}, ('RETURN',)))
        kernel.agents[self.sponsor].capabilities.update(
            {'DEVELOP', 'OPERATE', 'EXTRACT', 'SELL', 'DISTRIBUTE_SURPLUS'})
        funded = p.value('physical_construction_cost') + p.value('operating_float')
        investment = kernel.transfer(year, self.budget, p.financier_cash, funded,
                                     TxPurpose.OTHER_INVESTMENT,
                                     parent_ids=(study_receipt,))
        kernel.add_commitment(p.commitment, self.financier, p.project, funded)
        payment = kernel.disburse(year, p.commitment, p.financier_cash, funded)
        kernel.transition_project_status(year, self.sponsor, p.project, 'DEVELOPMENT',
                                         reason_ref=study_receipt)
        stages = ((p.offset_year('construction_year_1'), p.value('construction_stage_1')),
                  (p.offset_year('construction_year_2'), p.value('construction_stage_2')))
        kernel.register_development_plan(ProjectDevelopmentPlan(
            p.plan, p.project, p.ids['wip'], p.asset, self.supplier, p.node,
            p.value('physical_construction_cost'), stages,
            p.offset_year('construction_year_2'), p.family_value('productive_capacity'),
            p.ids['development_plan_basis']))
        kernel.register_financing_return_claim(FinancingReturnClaim(
            p.return_claim, self.financier, p.project, p.financier_cash,
            p.family_value('unit_sale_price') * p.family_value('quantity_per_operation') *
            p.value('financier_return_share'), (p.commitment,),
            p.ids['financing_claim_basis'], p.ids['financing_claim_scope']))
        p.physical.append(dict(year=year, stage='FINANCE', sponsor_debit=str(funded),
            financier_debit=str(funded), project_cash=str(kernel.state.accounts[p.cash].balance),
            investment_tx=investment.id, disbursement_tx=payment.id,
            study_receipt=study_receipt, study_review=study_review))

    def _construction(self, kernel, year):
        p = self.p
        cost = (p.value('construction_stage_1') if year == p.offset_year('construction_year_1')
                else p.value('construction_stage_2'))
        kernel.set_resource_constraint('EARTH:' + p.definition['executor_location'], year,
            cost, p.family_value('earth_supply_fraction'))
        stage = kernel.execute_development_stage(year, p.plan)
        assert stage.outcome.value == 'SPENT'
        p.physical.append(dict(year=year, stage='CONSTRUCTION', amount=str(cost),
            tx=stage.transaction_id, project_cash=str(kernel.state.accounts[p.cash].balance),
            supplier_balance=str(kernel.state.accounts[self.supplier].balance)))
        if year == p.offset_year('construction_year_2'):
            commissioned = kernel.resolve_development_plan(year, p.plan)
            assert commissioned.outcome.value == 'OPERATING'
            kernel.assess_resource_recoverability(year, p.resource, ScenarioResource(
                p.resource, p.node, p.definition['material_family'],
                p.family_value('in_situ'), p.family_value('accessible'),
                p.family_value('recoverable'), p.family_value('recoverable')))
            p.physical.append(dict(year=year, stage='COMMISSIONED', asset=p.asset,
                capacity=str(kernel.state.assets[p.asset].capacity),
                remaining=str(kernel.resources[p.resource].remaining)))

    def _operate(self, kernel, year, observation_id=None, admit_observation=False):
        p = self.p
        quantity = p.family_value('quantity_per_operation')
        amount = quantity * p.family_value('unit_opex')
        if year == p.offset_year('operation_year_2'):
            tx = kernel.transfer(year, p.reinvestment, p.cash, amount,
                                 TxPurpose.LOCAL_REINVESTMENT, parent_ids=(p.return_claim,))
            p.physical.append(dict(year=year, stage='REINVESTED_INTO_OPERATIONS',
                                   amount=str(amount), transaction=tx.id))
        elif year == p.offset_year('operation_year_3'):
            assert kernel.state.accounts[p.cash].balance >= amount
            p.physical.append(dict(year=year, stage='PROJECT_RESERVE_FUNDED_OPERATIONS',
                amount=str(amount), source=p.cash,
                classification='EXPLICIT_NO_TREASURY_FALLBACK'))
        elif year == p.offset_year('operation_year_4') and p.definition.get('scripted_appropriations_enabled', True):
            appropriation = next(r for r in p.appropriations if r['paid_year'] == year)
            assert _d(appropriation['amount']) == amount
            tx = kernel.transfer(year, self.budget, p.cash, amount,
                TxPurpose.OTHER_INVESTMENT, parent_ids=(appropriation['tx'],
                appropriation['source_return_tx'], appropriation['source_sale_tx']))
            p.return_spends.append(dict(year=year, source_sale_tx=appropriation['source_sale_tx'],
                source_return_tx=appropriation['source_return_tx'],
                source_appropriation_tx=appropriation['tx'], funding_tx=tx.id,
                amount=str(amount), source='TREASURY_OWNER_DISTRIBUTION',
                classification='SCRIPTED_NOT_A_DECISION'))
            p.physical.append(dict(year=year, stage='APPROPRIATION_FUNDED_OPERATIONS_SCRIPTED',
                amount=str(amount), transaction=tx.id, appropriation_tx=appropriation['tx'],
                classification='SCRIPTED_NOT_A_DECISION'))
        elif year == p.offset_year('operation_year_4'):
            # V3: project operating reserve, not a treasury budget appropriation.
            # Keep the physical opex debit in the validated operating transition.
            assert kernel.state.accounts[p.cash].balance >= amount
            p.physical.append(dict(year=year, stage='PROJECT_RESERVE_FUNDED_OPERATIONS',
                amount=str(amount), source=p.cash, classification='NO_TREASURY_FALLBACK'))
        earth = 'EARTH:' + p.definition['executor_location']
        kernel.set_resource_constraint(earth, year, amount, p.family_value('earth_supply_fraction'))
        request = build_operating_cycle_request(p.ids['operate_request_prefix'] + str(year), year,
            p.project, p.resource, p.asset, observation_id)
        decision = OperatingCycleDecision(p.ids['operate_decision_prefix'] + str(year), request.id,
            self.sponsor, OperatingCycleDecisionOutcome.OPERATE, D(0), quantity, amount,
            p.ids['operate_decision_reason'],
            OperatingCycleReasonCode.OPERATING_CYCLE_AUTHORIZED, (),
            p.ids['operate_decision_evidence_prefix'] + str(year), p.policy).validate_protocol(request)
        cost = kernel.spend_operating_cycle(year, self.sponsor, request, decision,
                                             self.supplier, p.family_value('unit_opex'))
        extracted = kernel.resolve_operating_extraction(year, self.sponsor, request, decision, cost)
        if admit_observation:
            kernel.admit_realized_output_observation(year, self.sponsor,
                                                     extracted.extraction_event_id)
        # Extraction event is operational output, not evidence. The sidecar
        # explicitly records PLACEHOLDER standing and never admits it as REAL.
        p.realized_outputs.append(dict(year=year, event=extracted.extraction_event_id,
            amount=str(extracted.actual_extracted), evidence='PLACEHOLDER',
            source='SYNTHETIC_SCENARIO_RESOURCE'))
        p.physical.append(dict(year=year, stage='EXTRACTED', opex=str(cost.total_opex),
            opex_tx=cost.transaction_id, actual=str(extracted.actual_extracted),
            remaining=str(extracted.resource_after), inventory=str(extracted.inventory_after),
            event=extracted.extraction_event_id, evidence='PLACEHOLDER'))
        if year == p.offset_year('operation_year_4') and p.definition.get('scripted_appropriations_enabled', True):
            funding = p.return_spends[-1]
            assert _d(funding['amount']) == _d(cost.total_opex)
            funding['expense_tx'] = cost.transaction_id
            kernel.audit(p.ids['appropriation_spent_event'], year,
                sale_tx=funding['source_sale_tx'], owner_return_tx=funding['source_return_tx'],
                appropriation_tx=funding['source_appropriation_tx'], funding_tx=funding['funding_tx'],
                expense_tx=cost.transaction_id, amount=funding['amount'],
                classification='SCRIPTED_NOT_A_DECISION')
        return extracted

    def _sell(self, kernel, year, observation_id=None):
        p = self.p
        buyer = kernel.state.accounts[self.buyer['account']]
        buyer_cash = buyer.balance
        inventory = kernel.colonies[p.node].resource_inventory
        quantity = min(inventory, p.family_value('demand_per_year'),
                       p.family_value('quantity_per_operation'))
        price = p.family_value('unit_sale_price')
        value = quantity * price
        if quantity <= 0 or value <= 0 or buyer_cash < value:
            raise ValueError('BLOCKED_AFFORDABILITY: finite buyer; sale was not mutated')
        envelope = CommodityMarketEnvelope(p.ids['market_prefix'] + str(year), year, p.resource,
            self.buyer['account'], price, p.family_value('demand_per_year'),
            p.definition['currency'], p.definition['resource_unit'],
            p.ids['market_source'], 'SYNTHETIC_NOT_REAL_DEMAND')
        kernel.register_market_envelope(envelope)
        request = build_sale_decision_request(p.ids['sale_request_prefix'] + str(year), year,
            p.project, p.resource, envelope.id, observation_id)
        decision = SaleDecision(p.ids['sale_decision_prefix'] + str(year), request.id,
            self.sponsor, SaleDecisionOutcome.OFFER, quantity, p.ids['sale_decision_reason'],
            SaleReasonCode.MARKET_OFFER_AUTHORIZED, (), p.ids['sale_decision_evidence_prefix'] + str(year),
            p.policy).validate_protocol(request)
        record = kernel.clear_market_sale(year, self.sponsor, request, decision)
        assert record.transaction_value == value and buyer.balance >= 0
        p.buyer_checks.append(dict(year=year, before=str(buyer_cash), paid=str(value),
                                   after=str(buyer.balance)))
        p.physical.append(dict(year=year, stage='SOLD', quantity=str(record.cleared_quantity),
            revenue=str(record.transaction_value), tx=record.transaction_id,
            buyer_after=str(buyer.balance), project_cash=str(kernel.state.accounts[p.cash].balance),
            evidence='PLACEHOLDER'))
        p.sales[year] = record
        return record

    def _distribute(self, kernel, year):
        p = self.p
        sale = p.sales[year]
        paid = D(sale.transaction_value)
        opening = kernel.state.accounts[p.cash].balance
        claim_remaining = kernel.financing_return_remaining(p.return_claim)
        financier_target = paid * p.value('financier_return_share')
        financier_paid = min(financier_target, claim_remaining)
        owner_paid = paid * p.value('owner_return_share') + financier_target - financier_paid
        local_paid = paid * p.value('local_reinvest_share')
        reserve = opening - financier_paid - owner_paid - local_paid
        assert reserve == opening - paid + paid * p.value('reserve_share')
        request = build_surplus_distribution_request(p.ids['distribution_request_prefix'] + str(year),
                                                       year, p.project, p.return_claim)
        decision = SurplusDistributionDecision(p.ids['distribution_decision_prefix'] + str(year),
            request.id, self.sponsor, SurplusDistributionDecisionOutcome.DISTRIBUTE, reserve,
            financier_paid, local_paid, owner_paid, p.ids['distribution_decision_reason'],
            SurplusDistributionReasonCode.DISTRIBUTION_AUTHORIZED, (),
            p.ids['distribution_decision_evidence_prefix'] + str(year), p.policy).validate_protocol(request)
        record = kernel.execute_surplus_distribution(year, self.sponsor, request, decision,
                                                      p.reinvestment)
        assert kernel.state.accounts[p.cash].balance == record.reserve
        txmap = {tx.id: tx for tx in kernel.state.transactions}
        for txid in record.transaction_ids:
            origin = txmap[txid]
            if origin.purpose == TxPurpose.OWNER_DISTRIBUTION:
                assert origin.destination_account == p.owner_destination['account']
                kind, owner_type = 'owner', p.owner_destination['owner_type']
            elif origin.purpose == TxPurpose.FINANCIER_RETURN:
                destination = resolve_destination(kernel, p.definition['return_revenue_source'],
                    'financier', self.financier, self.sponsor,
                    financing_claim=kernel.financing_return_claims[p.return_claim])
                assert origin.destination_account == destination['account']
                kind, owner_type = 'financier', 'financier'
            else:
                continue
            p.return_receipts.append(dict(year=year, kind=kind, owner_type=owner_type,
                source=p.definition['return_revenue_source'], owner=origin.destination_account,
                sale_tx=sale.transaction_id, return_tx=origin.id, amount=str(origin.amount)))
        p.physical.append(dict(year=year, stage='DISTRIBUTED', sale_tx=sale.transaction_id,
            financier_return=str(record.financier_return), reinvestment=str(record.local_reinvestment),
            owner_return=str(record.owner_distribution), project_reserve=str(record.reserve),
            txs=record.transaction_ids))

    def _appropriate(self, kernel, year):
        p = self.p
        for rule in p.definition['appropriations']:
            paid_year = p.start_year + int(rule['paid_offset'])
            if paid_year != year:
                continue
            receipt_year = p.start_year + int(rule['receipt_offset'])
            receipt = next(row for row in p.return_receipts
                           if row['year'] == receipt_year and row['kind'] == 'owner')
            eligible_year = receipt_year + p.owner_destination['delay_years']
            amount = _d(rule['amount'])
            assert paid_year >= eligible_year and amount <= _d(receipt['amount'])
            source = p.owner_destination['account']
            assert kernel.state.accounts[source].balance >= amount
            tx = kernel.transfer(year, source, self.budget, amount, TxPurpose.PUBLIC_SUBSIDY,
                                 parent_ids=(receipt['return_tx'], receipt['sale_tx']))
            row = dict(receipt_year=receipt_year, eligible_year=eligible_year, paid_year=year,
                amount=str(amount), source_return_tx=receipt['return_tx'],
                source_sale_tx=receipt['sale_tx'], tx=tx.id, destination_account=self.budget,
                reason=rule['reason'], scripted=True, spent_on_project='0',
                unspent_amount=str(amount))
            p.appropriations.append(row)
            p.physical.append(dict(year=year, stage='TREASURY_APPROPRIATION', **row))


class GeneralProjectCampaign(AllBodyCampaign):
    """Route 1 campaign parent plus a generic project lifecycle hook."""
    def __init__(self, scenario, price_table, ceilings_enabled=True,
                 conversion_enabled=True, project_override=None):
        super().__init__(body_count=90, ceilings_enabled=ceilings_enabled)
        self.scenario = scenario
        self.price_table = price_table
        self.conversion_enabled = conversion_enabled
        definition = dict(project_override or scenario['project'])
        self.project_state = ProjectState(definition, scenario['material_families'])
        self.lifecycle = EconomicLifecycle(self.project_state, scenario)
        self.project_events = []
        self.yearly_lifecycle = []
        self.unpriced = Counter()
        self.mission_price_by_body = {
            row['body']: row for row in price_table
            if row['vehicle_class_id'] == scenario['price_inputs']['vehicle_class']
            and row['mission_type_id'] == scenario['price_inputs']['mission_type']
            and int(row['year']) == int(scenario['price_inputs']['held_year'])}
        self.placeholder_outputs = []
        self.project_started = False
        self.study_receipt = None
        self.study_review = None
        self.equivalence_mode = project_override is not None
        self.year_rollup = []
        if not self.equivalence_mode:
            first_year = int(scenario['full_clock']['start_year'])
            quote = self._quote(self.project_state.body, first_year)
            self.unpriced.update(body for body in self.bodies if self._quote(body, first_year) is None)
            self.yearly_lifecycle.append(dict(year=first_year,
                mission_price_status='UNPRICED' if quote is None else quote['status'],
                mission_quote_source_year=None if quote is None else quote['source_year'],
                quote_held=False if quote is None else quote['held'],
                conversion_enabled=self.conversion_enabled, funded=0, completed=0,
                sales=0, returns=0, sponsor_exhausted=()))
            self.year_rollup.append(dict(year=first_year, funded=0, completed=0,
                sales=0, returns=0, exhausted_sponsors=()))

    def _quote(self, body, year):
        row = self.mission_price_by_body.get(body)
        if not row or row.get('status') != self.scenario['price_inputs']['supported_status']:
            return None
        # Held quotes are explicit and retain source-year provenance.
        return dict(status='PRICED_TEST_ONLY', source_year=int(row['year']),
                    held=(int(year) != int(row['year'])), usd=row['lowest_price_usd'],
                    model_currency=(D(row['lowest_price_usd']) /
                        D(self.scenario['price_inputs']['usd_per_model_currency'])
                        if self.conversion_enabled else D(0)))

    def on_year(self, year, kernel, rows):
        super().on_year(year, kernel, rows)
        p = self.project_state
        if self.equivalence_mode:
            self._on_year_equivalence(year, kernel, rows)
            return
        q = self._quote(p.body, year)
        row = dict(year=year, mission_price_status='UNPRICED' if q is None else q['status'],
            mission_quote_source_year=None if q is None else q['source_year'],
            quote_held=False if q is None else q['held'], conversion_enabled=self.conversion_enabled,
            funded=0, completed=0, sales=0, returns=0,
            sponsor_exhausted=tuple(sorted(s for s in self.requesters
                if kernel.state.accounts['route1:budget:' + s].balance == 0)))
        self.yearly_lifecycle.append(row)
        schedule = p.schedule
        if year not in set(schedule.values()):
            self.year_rollup.append(dict(year=year, funded=0, completed=0,
                sales=0, returns=0, exhausted_sponsors=row['sponsor_exhausted']))
            return
        if year == schedule['construction_year_1'] and q and q['model_currency'] > 0:
            try:
                receipt, review = self._positive_a2(kernel)
            except (StopIteration, AssertionError):
                receipt = review = None
            if receipt is not None:
                price = q['model_currency']
                if kernel.state.accounts[self.lifecycle.budget].balance >= price + p.value('physical_construction_cost') + p.value('operating_float'):
                    if self.lifecycle.supplier not in kernel.state.accounts:
                        kernel.add_account(self.lifecycle.supplier, self.lifecycle.executor,
                            'EARTH:' + p.definition['executor_location'], AccountKind.SUPPLIER)
                    mission_tx = kernel.transfer(year, self.lifecycle.budget,
                        self.lifecycle.supplier, price, TxPurpose.CAPEX,
                        parent_ids=(receipt['disbursement_id'],))
                    kernel.audit('GENERAL_PROJECT_MISSION_PRICE_SETTLED', year,
                        project=p.project, body=p.body, sponsor=p.sponsor,
                        executor=p.executor, source_year=q['source_year'], held=q['held'],
                        source_usd=q['usd'], converted_price=str(price),
                        mission_type=self.scenario['price_inputs']['mission_type'],
                        classification='PRICED_TEST_ONLY_PHYSICAL_MISSION')
                    self.study_receipt, self.study_review = receipt, review
                    self.lifecycle._start(kernel, year, receipt['disbursement_id'], review['result'])
                    self.project_started = True
                    row['funded'] = 1
                    row['mission_price_transaction'] = mission_tx.id
                    row['mission_price_usd'] = q['usd']
                    row['mission_price_model_currency'] = str(price)
                    self.lifecycle._construction(kernel, year)
        elif year == schedule['construction_year_2'] and self.project_started:
            self.lifecycle._construction(kernel, year)
        elif self.project_started:
            if year in (schedule['operation_year_4'], schedule['appropriation_year_2']):
                self.lifecycle._appropriate(kernel, year)
            if year != schedule['appropriation_year_2']:
                try:
                    self.lifecycle._operate(kernel, year, self.study_observation)
                except Exception as exc:
                    raise RuntimeError(f'generic lifecycle operation failed at year {year}; '
                        f'project_cash={kernel.state.accounts[p.accounts["project_cash"]].balance}; '
                        f'reinvestment={kernel.state.accounts[p.accounts["reinvestment"]].balance}') from exc
                if year in (schedule['operation_year_1'], schedule['operation_year_2']):
                    returns_before = len(p.return_receipts)
                    sale = self.lifecycle._sell(kernel, year, self.study_observation)
                    self.lifecycle._distribute(kernel, year)
                    row['sales'] = 1
                    row['returns'] = len(p.return_receipts) - returns_before
                    row['sale_amount'] = str(sale.transaction_value)
                if year == schedule['operation_year_4']:
                    row['completed'] = 1
                    spent = p.family_value('quantity_per_operation') * p.family_value('unit_opex')
                    p.appropriations[-1]['spent_on_project'] = str(spent)
                    p.appropriations[-1]['unspent_amount'] = '0'
                    event = next(item for item in p.physical
                        if item['stage'] == 'TREASURY_APPROPRIATION' and item['year'] == year)
                    event['spent_on_project'] = str(spent)
                    event['unspent_amount'] = '0'
        row['sponsor_exhausted'] = tuple(sorted(s for s in self.requesters
            if kernel.state.accounts['route1:budget:' + s].balance == 0))
        self.year_rollup.append(dict(year=year, funded=row['funded'],
            completed=row['completed'], sales=row['sales'], returns=row['returns'],
            exhausted_sponsors=row['sponsor_exhausted']))

    def _on_year_equivalence(self, year, kernel, rows):
        p, flow = self.project_state, self.lifecycle
        schedule = p.schedule
        decision_years = set(schedule.values())
        if year not in decision_years:
            return
        total_before = _total_money(kernel)
        balance_before = kernel.state.accounts[flow.budget].balance
        if year == schedule['construction_year_1']:
            self.study_receipt, self.study_review = self._positive_a2(kernel)
            flow._start(kernel, year, self.study_receipt['disbursement_id'],
                        self.study_review['result'])
            flow._construction(kernel, year)
            self.project_started = True
        elif year == schedule['construction_year_2']:
            flow._construction(kernel, year)
        else:
            if year in (schedule['operation_year_4'], schedule['appropriation_year_2']):
                flow._appropriate(kernel, year)
            if year != schedule['appropriation_year_2']:
                flow._operate(kernel, year, self.study_observation, admit_observation=True)
                if year in (schedule['operation_year_1'], schedule['operation_year_2']):
                    flow._sell(kernel, year, self.study_observation)
                    flow._distribute(kernel, year)
        if year == schedule['operation_year_4']:
            p.appropriations[-1]['spent_on_project'] = str(
                p.family_value('quantity_per_operation') * p.family_value('unit_opex'))
            p.appropriations[-1]['unspent_amount'] = '0'
        assert _total_money(kernel) == total_before
        assert kernel.state.accounts[flow.buyer['account']].balance >= 0
        row = next(item for item in rows if item['sponsor'] == flow.sponsor)
        received = sum((_d(x['amount']) for x in p.appropriations if x['paid_year'] == year), D(0))
        extra = balance_before + received - kernel.state.accounts[flow.budget].balance
        row['downstream_budget_spend'] = str(extra)
        row['downstream_appropriation_received'] = str(received)
        row['closing'] = str(kernel.state.accounts[flow.budget].balance)
        self.annual[-1]['closing'] = str(sum((kernel.state.accounts[
            p.accounts['budget_prefix'] + sponsor].balance for sponsor in self.requesters), D(0)))
        assert _d(row['opening']) + _d(row['allocated']) + received == (
            _d(row['campaign_spend']) + extra + _d(row['closing']))
        assert kernel.state.accounts[flow.buyer['account']].balance - _d(flow.buyer['endowment']) == kernel.boundary_net[flow.buyer['account']]
        assert all(a.balance >= 0 for a in kernel.state.accounts.values()
                   if a.kind != AccountKind.EARTH_BOUNDARY)
        kernel.assert_invariants()

    def _positive_a2(self, kernel):
        p = self.project_state
        receipt = next(r for r in self.receipts if r['body'] == p.body and r['stage'] == 'A2')
        review = next(r for r in self.studies if r['body'] == p.body and r['stage'] == 'A2')
        a1 = self.reviews[p.body]
        if not (receipt['sponsor'] == review['sponsor'] == a1['sponsor'] == p.sponsor
                and receipt['executor'] == p.executor and receipt['delivery'] == 'DELIVERED'
                and review['review'] == 'ADVANCE' and review['result'] == 'SUPPORTS_ADVANCE'
                and review['year'] == int(self.scenario['project']['study_a2_review_year'])
                and review['disbursement_id'] == receipt['disbursement_id']
                and a1['observation_id'] in kernel.agents[p.sponsor].information):
            raise AssertionError('Ceres authored A2 gate mismatch')
        self.study_observation = a1['observation_id']
        return receipt, review

    def report(self):
        report = super().report()
        p = self.project_state
        report.update(generic_project=dict(project_id=p.project, body=p.body,
            sponsor=p.sponsor, executor=p.executor, start_year=p.start_year,
            schedule=p.schedule, physical=tuple(p.physical), sales=tuple(
                (year, record.transaction_id) for year, record in sorted(p.sales.items())),
            returns=tuple(p.return_receipts), appropriations=tuple(p.appropriations),
            return_spends=tuple(p.return_spends), buyer_checks=tuple(p.buyer_checks),
            placeholder_outputs=tuple(p.realized_outputs)),
            yearly_lifecycle=tuple(self.yearly_lifecycle),
            unpriced_bodies=tuple(sorted(self.unpriced)),
            unpriced_count=len(self.unpriced), year_rollup=tuple(self.year_rollup),
            sponsor_count=len(self.requesters), executor_count=len(EXECUTORS),
            body_count=len(self.bodies))
        return report
