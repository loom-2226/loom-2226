from __future__ import annotations
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Dict, Iterable, Tuple

from .mvp_state import FinancingDecisionOutcome
from .policies.manifest import FinancierPolicyManifest, PolicyParameter

D=Decimal

DECISION_RANK={
    FinancingDecisionOutcome.REJECT:0,
    FinancingDecisionOutcome.DEFER:1,
    FinancingDecisionOutcome.APPROVE:2,
}

@dataclass(frozen=True,slots=True)
class BehavioralAdequacyReport:
    weak_monotonicity_passed:bool
    discrimination_passed:bool
    comparisons:Tuple[Tuple[str,str,str],...]

    @property
    def passed(self):
        return self.weak_monotonicity_passed and self.discrimination_passed

@dataclass(frozen=True,slots=True)
class PolicyEnsembleReport:
    total_requests:int
    blocked_requests:int
    blocked_request_share:D
    comparable_pairs:int
    decision_flips:int
    decision_flip_share:D
    flip_share_by_parameter:Tuple[Tuple[str,str],...]

def rank(outcome):
    outcome=FinancingDecisionOutcome(outcome)
    if outcome==FinancingDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN excluded from known-input decision ranking')
    return DECISION_RANK[outcome]

def adequacy_from_pairs(pairs:Iterable[tuple[str,object,object]],require_discrimination=True):
    comparisons=[]
    mono=True
    discriminate=False
    for label,worse,better in pairs:
        rw=rank(worse.outcome)
        rb=rank(better.outcome)
        comparisons.append((label,worse.outcome.value,better.outcome.value))
        if rb<rw:
            mono=False
        if rb!=rw:
            discriminate=True
    return BehavioralAdequacyReport(
        mono,
        discriminate if require_discrimination else True,
        tuple(comparisons),
    )

def perturbed_manifest(manifest:FinancierPolicyManifest,name:str,direction:int):
    p=manifest.parameter(name)
    delta=p.local_perturbation*D(direction)
    new_value=p.value+delta
    if new_value<p.sensitivity_low or new_value>p.sensitivity_high:
        raise ValueError(f'perturbation leaves authorized sensitivity range: {name}')
    new_p=replace(p,value=new_value)
    params=tuple(new_p if x.semantic_name==name else x for x in manifest.parameters)
    return replace(manifest,parameters=params)

def ensemble_report(base_outcomes:Iterable[object],
                    perturbation_pairs:Dict[str,Iterable[tuple[object,object]]]):
    base=tuple(base_outcomes)
    total=len(base)
    blocked=sum(1 for x in base if x.outcome==FinancingDecisionOutcome.BLOCKED_UNKNOWN)
    blocked_share=D(blocked)/D(total) if total else D('0')
    by_param=[]
    total_pairs=0
    total_flips=0
    for name,pairs_iter in sorted(perturbation_pairs.items()):
        pairs=tuple(pairs_iter)
        comparable=[(a,b) for a,b in pairs
                    if a.outcome!=FinancingDecisionOutcome.BLOCKED_UNKNOWN
                    and b.outcome!=FinancingDecisionOutcome.BLOCKED_UNKNOWN]
        flips=sum(1 for a,b in comparable if a.outcome!=b.outcome)
        count=len(comparable)
        share=D(flips)/D(count) if count else D('0')
        by_param.append((name,str(share)))
        total_pairs+=count
        total_flips+=flips
    overall=D(total_flips)/D(total_pairs) if total_pairs else D('0')
    return PolicyEnsembleReport(total,blocked,blocked_share,total_pairs,total_flips,overall,tuple(by_param))
