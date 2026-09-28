"""Decision functions receive beliefs, observations, opportunity status and budget only."""
from dataclasses import replace
from .model import KnowledgeState, Observation, Economics, Decision


def update(knowledge: KnowledgeState, observation: Observation) -> KnowledgeState:
    if observation.site_id != knowledge.site_id or observation.observation_id in knowledge.observation_ids:
        raise ValueError('wrong scope or duplicate observation')
    if observation.time < knowledge.time:
        raise ValueError('observation predates knowledge')
    p = knowledge.probability
    a = observation.sensitivity if observation.detected else 1 - observation.sensitivity
    b = observation.false_positive if observation.detected else 1 - observation.false_positive
    return replace(knowledge, probability=p*a / (p*a + (1-p)*b),
                   source=observation.observation_id, time=observation.time,
                   observation_ids=knowledge.observation_ids + (observation.observation_id,))


def continuation(k: KnowledgeState, e: Economics, budget: int) -> Decision:
    net = k.probability * e.success_value - e.continuation_cost
    action = 'CONTINUE' if net > e.threshold and budget >= e.continuation_cost else 'REJECT'
    return Decision(action, net, 'Expected continuation value minus cost; affordable and above threshold required')


def prospect(k: KnowledgeState, e: Economics, budget: int, feasibility: str) -> Decision:
    p = k.probability
    positive = p*e.sensitivity + (1-p)*e.false_positive
    p_yes = p*e.sensitivity / positive
    p_no = p*(1-e.sensitivity) / (1-positive)
    # Value of sample information relative to the best current continuation choice.
    # Unaffordable follow-up cannot contribute speculative option value.
    affordable = budget >= e.mission_cost + e.continuation_cost
    after = (positive*max(0, p_yes*e.success_value-e.continuation_cost) +
             (1-positive)*max(0, p_no*e.success_value-e.continuation_cost)) if affordable else 0
    before = max(0, p*e.success_value-e.continuation_cost) if budget >= e.continuation_cost else 0
    net = after - before - e.mission_cost
    action = 'PROSPECT' if feasibility == 'FEASIBLE' and budget >= e.mission_cost and net > e.threshold else 'WAIT'
    return Decision(action, net, 'Expected value of sample information minus mission cost; feasible and affordable required')
