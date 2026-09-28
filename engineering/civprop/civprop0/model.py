"""Small immutable runtime contracts; no persistent schema or database ownership."""
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass(frozen=True)
class Scenario:
    version: str = 'CIVPROP0_SCENARIO_V1'
    generator: str = 'SHA256_BERNOULLI_V1'
    prior_version: str = 'POLAR_TEST_PRIOR_V1'
    body_id: str = 'MOON'
    site_id: str = 'SCENARIO:MOON_POLAR_PSR:SITE_0'
    departure: str = '2026-09-28T00:00:00Z'
    arrival: str = '2026-10-03T00:00:00Z'
    prior: float = .3
    sensitivity: float = .85
    false_positive: float = .15
    capital: int = 100
    mission_cost: int = 5
    continuation_cost: int = 50
    success_value: int = 100
    threshold: float = 0
    technology: bool | None = True
    money_unit: str = 'SCENARIO_CREDIT (no currency conversion)'
    authority_class: str = 'SCENARIO_TEST_INPUT'

    def validate(self):
        for x in (self.prior, self.sensitivity, self.false_positive):
            if not math.isfinite(x) or not 0 < x < 1:
                raise ValueError('probabilities must be finite and strictly between zero and one')
        if self.sensitivity <= self.false_positive:
            raise ValueError('instrument must be informative')
        for x in (self.capital, self.mission_cost, self.continuation_cost, self.success_value):
            if type(x) is not int or x < 0:
                raise ValueError('money must be nonnegative integer scenario credits')
        if not self.mission_cost or not self.continuation_cost:
            raise ValueError('costs must be positive')
        if not math.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError('invalid decision threshold')
        if self.technology is not None and type(self.technology) is not bool:
            raise ValueError('technology is tri-state')
        if self.authority_class != 'SCENARIO_TEST_INPUT' or self.money_unit != 'SCENARIO_CREDIT (no currency conversion)':
            raise ValueError('scenario authority and monetary units are fixed')
        if self.body_id != 'MOON' or not self.site_id.startswith('SCENARIO:MOON_POLAR_PSR:'):
            raise ValueError('only synthetic lunar polar sites are supported')
        start, end = (datetime.fromisoformat(x.replace('Z', '+00:00')) for x in (self.departure, self.arrival))
        if start.tzinfo is None or end.tzinfo is None or end <= start:
            raise ValueError('arrival must follow timezone-aware departure')
        if (self.version, self.generator, self.prior_version) != (
                'CIVPROP0_SCENARIO_V1', 'SHA256_BERNOULLI_V1', 'POLAR_TEST_PRIOR_V1'):
            raise ValueError('unsupported model version')


@dataclass(frozen=True)
class Actor:
    actor_id: str
    name: str
    year: int
    source_snapshot: str


@dataclass(frozen=True)
class KnowledgeState:
    site_id: str
    probability: float
    source: str
    time: str
    observation_ids: tuple[str, ...] = ()
    visibility: str = 'PRIVATE'
    authority_class: str = 'SIMULATED_BELIEF'


    def __post_init__(self):
        if not math.isfinite(self.probability) or not 0 < self.probability < 1:
            raise ValueError('invalid belief probability')
        if self.authority_class != 'SIMULATED_BELIEF':
            raise ValueError('belief cannot be promoted')


@dataclass(frozen=True)
class Observation:
    observation_id: str
    mission_id: str
    site_id: str
    detected: bool
    sensitivity: float
    false_positive: float
    time: str
    quantity: str = 'ice_detection'
    units: str = 'binary (not abundance or ore grade)'
    error_model: str = 'BERNOULLI_CONFUSION_MATRIX_V1'
    authority_class: str = 'SIMULATED_OBSERVATION'


    def __post_init__(self):
        if type(self.detected) is not bool or not all(
                math.isfinite(v) and 0 < v < 1 for v in (self.sensitivity, self.false_positive)):
            raise ValueError('invalid binary observation or error model')
        if self.sensitivity <= self.false_positive:
            raise ValueError('uninformative instrument')
        if (self.authority_class, self.quantity, self.units, self.error_model) != (
                'SIMULATED_OBSERVATION', 'ice_detection', 'binary (not abundance or ore grade)',
                'BERNOULLI_CONFUSION_MATRIX_V1'):
            raise ValueError('observation semantics cannot change')


@dataclass(frozen=True)
class Economics:
    mission_cost: int
    continuation_cost: int
    success_value: int
    threshold: float
    sensitivity: float
    false_positive: float
    authority_class: str = 'SCENARIO_TEST_INPUT_NOT_DORRINGTON'


@dataclass(frozen=True)
class Decision:
    action: str
    expected_net_value: float
    reason: str
    authority_class: str = 'SCENARIO_DECISION'


@dataclass(frozen=True)
class Opportunity:
    status: str
    departure: str
    arrival: str
    duration_seconds: float
    context_distance_km: float | None
    liens: tuple[str, ...]
    authority_class: str = 'SCENARIO_TRANSPORT_WITH_GOVERNED_CONTEXT'


@dataclass(frozen=True)
class Mission:
    mission_id: str
    actor_id: str
    site_id: str
    departure: str
    arrival: str
    mission_class: str = 'ROBOTIC_POLAR_PROSPECTING'


@dataclass(frozen=True)
class CapitalTransaction:
    transaction_id: str
    amount: int
    purpose: str
    unit: str
    authority_class: str = 'SCENARIO_EXPENDITURE'


@dataclass(frozen=True)
class InfrastructureChange:
    asset_id: str
    site_id: str
    transaction_id: str
    kind: str
    authority_class: str = 'SCENARIO_ASSET_NOT_MINING_CAPACITY'


@dataclass(frozen=True)
class Event:
    event_id: str
    run_id: str
    actor_id: str
    event_type: str
    time: str
    parent_id: str | None
    payload: dict
    authority_class: str = 'SIMULATION_EVENT'


@dataclass(frozen=True)
class Run:
    run_id: str
    seed: int
    scenario: dict
    inputs: dict
    input_sha256: str
    implementation_sha256: dict
    actor: Actor
    opportunity: Opportunity
    initial_knowledge: KnowledgeState
    final_knowledge: KnowledgeState
    decisions: tuple[Decision, ...]
    mission: Mission | None
    observations: tuple[Observation, ...]
    transactions: tuple[CapitalTransaction, ...]
    infrastructure: tuple[InfrastructureChange, ...]
    ending_capital: int
    events: tuple[Event, ...]
    audit: dict
