"""Phase 9 shared portfolio competition. NON_CANON machinery test."""
from dataclasses import dataclass
KINDS=frozenset({"MISSION","PROJECT","CERTIFICATION"})
@dataclass(frozen=True)
class PortfolioOpportunityV03:
    opportunity_id:str
    kind:str
    required_budget:float
    eligible:bool
    priority:float
    provenance_refs:tuple[str,...]
    authority_class:str="AUTHORED_MACHINERY_TEST_OPPORTUNITY"
@dataclass(frozen=True)
class PortfolioDecisionV03:
    opportunity_id:str
    kind:str
    action:str
    reason_codes:tuple[str,...]
    required_budget:float
@dataclass(frozen=True)
class PortfolioResultV03:
    actor_id:str
    starting_budget:float|None
    ending_budget:float|None
    decisions:tuple[PortfolioDecisionV03,...]
    authority_class:str="SIMULATED_SHARED_PORTFOLIO_RESULT"
def allocate_shared_portfolio(*,actor_id,opportunities,budget_status,budget_value):
    if budget_status!="KNOWN":
        return PortfolioResultV03(actor_id,None,None,tuple(
            PortfolioDecisionV03(o.opportunity_id,o.kind,"WAIT",("BUDGET_UNKNOWN",),o.required_budget)
            for o in opportunities))
    if budget_value is None or budget_value<0: raise ValueError("INVALID_KNOWN_BUDGET")
    for o in opportunities:
        if o.kind not in KINDS: raise ValueError("UNKNOWN_PORTFOLIO_KIND")
        if o.required_budget<0: raise ValueError("NEGATIVE_REQUIRED_BUDGET")
        if not o.provenance_refs: raise ValueError("MISSING_OPPORTUNITY_PROVENANCE")
    remaining=float(budget_value); out=[]
    for o in sorted(opportunities,key=lambda x:(-x.priority,x.opportunity_id)):
        if not o.eligible:
            out.append(PortfolioDecisionV03(o.opportunity_id,o.kind,"WAIT",("INELIGIBLE",),o.required_budget)); continue
        if o.required_budget>remaining:
            out.append(PortfolioDecisionV03(o.opportunity_id,o.kind,"WAIT",("INSUFFICIENT_SHARED_BUDGET",),o.required_budget)); continue
        remaining-=o.required_budget
        out.append(PortfolioDecisionV03(o.opportunity_id,o.kind,"COMMIT",("SHARED_PORTFOLIO_SELECTED",),o.required_budget))
    return PortfolioResultV03(actor_id,float(budget_value),remaining,tuple(out))
