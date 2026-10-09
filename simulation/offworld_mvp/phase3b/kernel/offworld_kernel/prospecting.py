"""Bounded Build 7 prospecting opportunity, capital, and initiation contracts."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D
from enum import Enum
from hashlib import sha256
from typing import Iterable

from .kernel import InvariantError
from .policy import DecisionSnapshot, FactState


MATERIAL_FAMILY_QUESTIONS = (
    'VOLATILES_PRESENT',
    'METALS_PRESENT',
    'SILICATES_ROCK_PRESENT',
    'CARBONACEOUS_ORGANICS_PRESENT',
)


@dataclass(frozen=True)
class ProspectingScenario:
    scenario_id: str
    required_capital: D
    information_value: D
    investment_proxy_units_per_model_currency: D
    m_max: D
    base_salience: D
    race_pressure: D
    authorization_ref: str
    standing: str
    scenario_version: str = 'BUILD7_PROSPECTING_ECONOMICS_V1'

    def validate(self):
        values=(self.required_capital,self.information_value,
                self.investment_proxy_units_per_model_currency,self.m_max,
                self.base_salience,self.race_pressure)
        if not self.scenario_id or not self.authorization_ref or not self.standing:
            raise InvariantError('prospecting scenario identity incomplete')
        if any(not D(value).is_finite() for value in values):
            raise InvariantError('prospecting scenario nonfinite')
        if (self.required_capital<=0 or self.information_value<=0
                or self.investment_proxy_units_per_model_currency<=0
                or not D(0)<=self.m_max<=D(1)
                or self.base_salience<0 or self.race_pressure<0):
            raise InvariantError('prospecting scenario parameter range')
        return self


@dataclass(frozen=True)
class ProspectingRegion:
    body_key: str
    region_key: str
    location_id: str
    ordinal: int
    region_version: str = 'BUILD7_PROSPECTING_REGION_V1'


@dataclass(frozen=True)
class ProspectingOpportunity:
    opportunity_id: str
    actor_id: str
    calendar_year: int
    body_key: str
    region_key: str
    location_id: str
    observation_ids: tuple[str,...]
    belief_keys: tuple[str,...]
    required_capital: D
    prospective_information_value: D
    commercial_opportunity: D
    opportunity_version: str = 'BUILD7_PROSPECTING_OPPORTUNITY_V1'


@dataclass(frozen=True)
class CapitalMobilizationRecord:
    year: int
    country_id: str
    investment_proxy: D
    normalized_investment: D
    commercial_opportunity: D
    base_salience: D
    race_pressure: D
    strategic_pressure: D
    mobilization_fraction: D
    mobilized_cash: D
    destination_account_id: str
    transaction_id: str
    source_ref: str
    record_version: str = 'BUILD7_CAPITAL_MOBILIZATION_V1'


@dataclass(frozen=True)
class CountryCapitalDisbursementRecord:
    year: int
    country_id: str
    project_id: str
    commitment_id: str
    amount: D
    available_cash_before: D
    available_cash_after: D
    exposure_before: D
    exposure_after: D
    transaction_id: str
    record_version: str = 'BUILD7_COUNTRY_CAPITAL_DISBURSEMENT_V1'


@dataclass(frozen=True)
class ProspectingProjectCreationRecord:
    year: int
    actor_id: str
    decision_id: str
    opportunity_id: str
    project_id: str
    body_key: str
    region_key: str
    location_id: str
    node_id: str
    cash_account_id: str
    project_stage: str
    event_id: str
    record_version: str = 'BUILD7_PROSPECTING_PROJECT_CREATION_V1'


class SponsorProspectingOutcome(str, Enum):
    INITIATE_PROJECT='INITIATE_PROJECT'
    WAIT='WAIT'
    DECLINE='DECLINE'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'


class SponsorProspectingReasonCode(str, Enum):
    POSITIVE_CHARACTERIZATION_FUNDED='POSITIVE_CHARACTERIZATION_FUNDED'
    FINANCING_NOT_AVAILABLE='FINANCING_NOT_AVAILABLE'
    NONPOSITIVE_CHARACTERIZATION='NONPOSITIVE_CHARACTERIZATION'
    NONPOSITIVE_PROSPECTING_ECONOMICS='NONPOSITIVE_PROSPECTING_ECONOMICS'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'


class SponsorOpportunityOutcome(str, Enum):
    CONSIDER_PROSPECTING='CONSIDER_PROSPECTING'
    RETAIN_PROJECT='RETAIN_PROJECT'
    WAIT='WAIT'
    BLOCKED_UNKNOWN='BLOCKED_UNKNOWN'


class SponsorOpportunityReasonCode(str, Enum):
    VISIBLE_ALTERNATIVE_WITHIN_FINANCING_CAPACITY='VISIBLE_ALTERNATIVE_WITHIN_FINANCING_CAPACITY'
    RETAIN_EXISTING_PROJECT='RETAIN_EXISTING_PROJECT'
    ALTERNATIVE_FINANCING_NOT_AVAILABLE='ALTERNATIVE_FINANCING_NOT_AVAILABLE'
    NO_ACTIONABLE_OPPORTUNITY='NO_ACTIONABLE_OPPORTUNITY'
    CAPABILITY_OR_OBJECTIVE_BLOCK='CAPABILITY_OR_OBJECTIVE_BLOCK'
    BLOCKED_REQUIRED_INPUT_UNKNOWN='BLOCKED_REQUIRED_INPUT_UNKNOWN'


@dataclass(frozen=True)
class SponsorOpportunityCandidate:
    opportunity_id: str
    body_key: str
    observation_ids: tuple[str,...]
    belief_keys: tuple[str,...]
    required_capital: D
    commercial_opportunity: D
    tie_break_key: str
    candidate_version: str = 'BUILD7_SPONSOR_OPPORTUNITY_CANDIDATE_V1'

    def validate_protocol(self):
        if (not self.opportunity_id or not self.body_key or not self.tie_break_key
                or len(self.observation_ids)!=len(MATERIAL_FAMILY_QUESTIONS)
                or len(self.belief_keys)!=len(MATERIAL_FAMILY_QUESTIONS)
                or len(set(self.observation_ids))!=len(self.observation_ids)
                or len(set(self.belief_keys))!=len(self.belief_keys)
                or D(self.required_capital)<=0
                or D(self.commercial_opportunity) not in (D(0),D(1))):
            raise ValueError('annual sponsor opportunity candidate invalid')
        return self


@dataclass(frozen=True)
class SponsorOpportunityRequest:
    id: str
    year: int
    actor_id: str
    existing_project_id: str
    candidates: tuple[SponsorOpportunityCandidate,...]
    required_fact_keys: tuple[str,...] = (
        'project.STATUS',
        'study.CURRENT_MATURITY',
        'portfolio.AVAILABLE_CAPITAL',
        'capital.AVAILABLE_F',
    )
    request_version: str = 'BUILD7_SPONSOR_ANNUAL_OPPORTUNITY_REQUEST_V1'

    def validate_protocol(self):
        if not self.id or self.year<0 or not self.actor_id or not self.existing_project_id:
            raise ValueError('annual sponsor opportunity request identity invalid')
        if len({c.opportunity_id for c in self.candidates})!=len(self.candidates):
            raise ValueError('duplicate annual sponsor opportunity')
        for candidate in self.candidates:candidate.validate_protocol()
        return self


@dataclass(frozen=True)
class SponsorOpportunityDecision:
    id: str
    request_id: str
    actor_id: str
    outcome: SponsorOpportunityOutcome
    selected_opportunity_id: str
    selected_body_key: str
    reason_code: SponsorOpportunityReasonCode
    reason: str
    unknown_input_keys: tuple[str,...]
    input_snapshot_ref: str
    policy_version: str
    decision_version: str = 'BUILD7_SPONSOR_ANNUAL_OPPORTUNITY_DECISION_V1'

    def validate_protocol(self,request:SponsorOpportunityRequest|None=None):
        if not all((self.id,self.request_id,self.actor_id,self.input_snapshot_ref,self.policy_version)):
            raise ValueError('annual sponsor opportunity decision identity invalid')
        if self.outcome==SponsorOpportunityOutcome.CONSIDER_PROSPECTING:
            if not self.selected_opportunity_id or not self.selected_body_key:
                raise ValueError('consider decision requires selected opportunity')
        elif self.selected_opportunity_id or self.selected_body_key:
            raise ValueError('non-consider decision selects opportunity')
        if self.outcome==SponsorOpportunityOutcome.BLOCKED_UNKNOWN:
            if (not self.unknown_input_keys or self.reason_code!=
                    SponsorOpportunityReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN):
                raise ValueError('blocked annual sponsor decision malformed')
        elif self.unknown_input_keys:
            raise ValueError('known annual sponsor decision carries unknown inputs')
        if request is not None:
            request.validate_protocol()
            if self.request_id!=request.id or self.actor_id!=request.actor_id:
                raise ValueError('annual sponsor decision/request lineage mismatch')
            if self.outcome==SponsorOpportunityOutcome.CONSIDER_PROSPECTING:
                matching=[c for c in request.candidates
                          if c.opportunity_id==self.selected_opportunity_id]
                if len(matching)!=1 or matching[0].body_key!=self.selected_body_key:
                    raise ValueError('annual sponsor selected opportunity outside request')
        return self


@dataclass(frozen=True)
class SponsorProspectingRequest:
    id: str
    year: int
    actor_id: str
    opportunity_id: str
    project_id: str
    body_key: str
    region_key: str
    location_id: str
    observation_ids: tuple[str,...]
    belief_keys: tuple[str,...]
    amount: D
    prospective_information_value: D
    required_fact_keys: tuple[str,...] = (
        'prospecting.REQUIRED_CAPITAL',
        'prospecting.INFORMATION_VALUE',
        'capital.AVAILABLE_F',
    )
    request_version: str = 'BUILD7_SPONSOR_PROSPECTING_REQUEST_V1'

    def validate_protocol(self):
        if (not all((self.id,self.actor_id,self.opportunity_id,self.project_id,
                     self.body_key,self.region_key,self.location_id)) or self.year<0):
            raise ValueError('prospecting request identity incomplete')
        if (len(self.observation_ids)!=len(MATERIAL_FAMILY_QUESTIONS)
                or len(self.belief_keys)!=len(MATERIAL_FAMILY_QUESTIONS)
                or len(set(self.observation_ids))!=len(self.observation_ids)
                or len(set(self.belief_keys))!=len(self.belief_keys)):
            raise ValueError('prospecting request material evidence incomplete')
        if D(self.amount)<=0 or D(self.prospective_information_value)<=0:
            raise ValueError('prospecting request economics invalid')
        return self


@dataclass(frozen=True)
class SponsorProspectingDecision:
    id: str
    request_id: str
    actor_id: str
    opportunity_id: str
    project_id: str
    amount: D
    outcome: SponsorProspectingOutcome
    reason_code: SponsorProspectingReasonCode
    reason: str
    unknown_input_keys: tuple[str,...]
    input_snapshot_ref: str
    policy_version: str
    decision_version: str = 'BUILD7_SPONSOR_PROSPECTING_DECISION_V1'

    def validate_protocol(self,request:SponsorProspectingRequest|None=None):
        if not all((self.id,self.request_id,self.actor_id,self.opportunity_id,
                    self.project_id,self.input_snapshot_ref,self.policy_version)):
            raise ValueError('prospecting decision identity incomplete')
        if self.outcome==SponsorProspectingOutcome.INITIATE_PROJECT:
            if self.amount<=0 or self.unknown_input_keys:
                raise ValueError('project initiation requires known positive financing')
        elif self.amount!=0:
            raise ValueError('non-initiation decision may not authorize capital')
        if self.outcome==SponsorProspectingOutcome.BLOCKED_UNKNOWN:
            if (not self.unknown_input_keys or
                    self.reason_code!=SponsorProspectingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN):
                raise ValueError('blocked prospecting decision malformed')
        elif self.unknown_input_keys:
            raise ValueError('unknown prospecting inputs must block')
        if request is not None:
            request.validate_protocol()
            if (self.request_id!=request.id or self.actor_id!=request.actor_id
                    or self.opportunity_id!=request.opportunity_id
                    or self.project_id!=request.project_id):
                raise ValueError('prospecting decision/request lineage mismatch')
        return self


def strategic_pressure(base_salience, race_pressure):
    total=D(base_salience)+D(race_pressure)
    return min(D(1),max(D(0),total))


def derive_mobilization(*,investment_proxy,commercial_opportunity,scenario:ProspectingScenario):
    scenario.validate()
    investment=D(investment_proxy); opportunity=D(commercial_opportunity)
    if not investment.is_finite() or investment<0 or opportunity not in (D(0),D(1)):
        raise InvariantError('capital mobilization input invalid')
    normalized=investment/scenario.investment_proxy_units_per_model_currency
    pressure=strategic_pressure(scenario.base_salience,scenario.race_pressure)
    # Increment 4 has authority for the bounded coupling, but no response
    # curve or relative commercial/strategic weights.  Use the smallest
    # executable parameterization: either admitted cause activates the same
    # ceiling.  The record retains both inputs so their provenance remains
    # distinguishable.
    fraction=scenario.m_max if opportunity==D(1) or pressure>D(0) else D(0)
    if not D(0)<=fraction<=scenario.m_max:
        raise InvariantError('capital mobilization fraction outside bound')
    return normalized,pressure,fraction,normalized*fraction


def derive_prospecting_opportunities(*,actor_id,calendar_year,body_key,regions,
                                     observations,beliefs,priors,
                                     scenario:ProspectingScenario):
    """Pure actor-visible derivation; observations and beliefs are already admitted."""
    scenario.validate();regions=tuple(regions);observations=tuple(observations)
    if len(regions)!=10 or tuple(r.ordinal for r in regions)!=tuple(range(1,11)):
        raise InvariantError('prospecting region profile')
    by_question={obs.question_ref:obs for obs in observations
                 if obs.body_id==body_key and obs.channel=='REMOTE'}
    if set(by_question)!=set(MATERIAL_FAMILY_QUESTIONS):
        return ()
    belief_keys=tuple('BODY:'+body_key+':'+question for question in MATERIAL_FAMILY_QUESTIONS)
    if any(key not in beliefs or key not in priors for key in belief_keys):
        commercial=D(0)
    else:
        commercial=D(1) if any(D(beliefs[key])>D(priors[key]) for key in belief_keys) else D(0)
    observation_ids=tuple(by_question[q].id for q in MATERIAL_FAMILY_QUESTIONS)
    result=[]
    for region in regions:
        oid='PROSPECTING_OPPORTUNITY_V1:'+actor_id+':'+str(calendar_year)+':'+body_key+':'+region.region_key
        result.append(ProspectingOpportunity(
            oid,actor_id,int(calendar_year),body_key,region.region_key,region.location_id,
            observation_ids,belief_keys,scenario.required_capital,
            scenario.information_value,commercial))
    return tuple(result)


def choose_equivalent_region(opportunities:Iterable[ProspectingOpportunity],decision_key):
    opportunities=tuple(opportunities)
    if not opportunities:return None
    ids=[o.opportunity_id for o in opportunities]
    if len(ids)!=len(set(ids)):raise InvariantError('duplicate prospecting opportunity')
    # Regions have no distinguishing evidence in Increment 4. The key is only
    # a replay-safe tie-break and conveys no geological or economic preference.
    return min(opportunities,key=lambda o:(
        sha256((str(decision_key)+'|'+o.opportunity_id).encode()).hexdigest(),o.opportunity_id))


def required_unknown_prospecting_inputs(request:SponsorProspectingRequest,
                                        snapshot:DecisionSnapshot):
    request.validate_protocol();facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:unknown.append(key)
    beliefs=dict(snapshot.beliefs);priors=dict(snapshot.priors)
    for key in request.belief_keys:
        if key not in beliefs:unknown.append('belief.'+key)
        if key not in priors:unknown.append('prior.'+key)
    for observation_id in request.observation_ids:
        if observation_id not in snapshot.information_refs:unknown.append('information.'+observation_id)
    return tuple(sorted(unknown))


def required_unknown_sponsor_opportunity_inputs(request:SponsorOpportunityRequest,
                                                snapshot:DecisionSnapshot):
    request.validate_protocol();facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:unknown.append(key)
    beliefs=dict(snapshot.beliefs);priors=dict(snapshot.priors)
    for candidate in request.candidates:
        for key in candidate.belief_keys:
            if key not in beliefs:unknown.append('belief.'+key)
            if key not in priors:unknown.append('prior.'+key)
        for observation_id in candidate.observation_ids:
            if observation_id not in snapshot.information_refs:
                unknown.append('information.'+observation_id)
    return tuple(sorted(set(unknown)))


def build_sponsor_opportunity_decision(
    decision_id,request:SponsorOpportunityRequest,snapshot:DecisionSnapshot,outcome,
    reason_code,reason,policy_version,selected_opportunity_id='',selected_body_key=''
):
    outcome=SponsorOpportunityOutcome(outcome)
    reason_code=SponsorOpportunityReasonCode(reason_code)
    unknowns=required_unknown_sponsor_opportunity_inputs(request,snapshot)
    if unknowns and outcome!=SponsorOpportunityOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown annual sponsor inputs must block')
    if not unknowns and outcome==SponsorOpportunityOutcome.BLOCKED_UNKNOWN:
        raise ValueError('blocked annual sponsor decision requires unknown inputs')
    return SponsorOpportunityDecision(
        str(decision_id),request.id,snapshot.agent_id,outcome,
        str(selected_opportunity_id),str(selected_body_key),reason_code,str(reason),unknowns,
        'decision-snapshot:'+snapshot.period_key+':'+snapshot.fingerprint(),str(policy_version)
    ).validate_protocol(request)


def build_prospecting_decision(decision_id,request,snapshot,outcome,reason_code,
                               reason,policy_version,unknowns=()):
    outcome=SponsorProspectingOutcome(outcome)
    amount=request.amount if outcome==SponsorProspectingOutcome.INITIATE_PROJECT else D(0)
    return SponsorProspectingDecision(
        str(decision_id),request.id,snapshot.agent_id,request.opportunity_id,
        request.project_id,amount,outcome,SponsorProspectingReasonCode(reason_code),
        str(reason),tuple(unknowns),
        'decision-snapshot:'+snapshot.period_key+':'+snapshot.fingerprint(),
        str(policy_version)).validate_protocol(request)
