"""Step 8.B proposition feasibility and commitment bridge.

NON_CANON / UNPROMOTED. This adapter proves independent authorities before
calling the already-qualified Gate-G atomic transaction primitive.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping,Sequence
from ..contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03,commit_transaction

class AuthorityStatus(str,Enum):
 KNOWN="KNOWN"; UNKNOWN="UNKNOWN"; NOT_REQUIRED="NOT_REQUIRED"

@dataclass(frozen=True)
class FeasibilityAuthorityV03:
 authority:str; status:AuthorityStatus; satisfied:bool|None
 provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class AssembledPropositionV03:
 proposition_id:str; origin_actor_id:str; provider_actor_id:str
 required_budget:float; provider_capacity_units:float
 authorities:tuple[FeasibilityAuthorityV03,...]
 accepted_counterparty_actor_ids:tuple[str,...]
 provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class PropositionFeasibilityV03:
 proposition_id:str; status:str; reason_codes:tuple[str,...]
 authority_results:tuple[FeasibilityAuthorityV03,...]
 semantics:str="FEASIBILITY_ONLY_NO_COMMITMENT_AUTHORITY"

@dataclass(frozen=True)
class CommitmentBridgeResultV03:
 proposition_id:str; feasibility:PropositionFeasibilityV03
 transaction_status:str; transaction_reason_codes:tuple[str,...]
 project_id:str|None; emitted_event_ids:tuple[str,...]
 semantics:str="COMMITMENT_ONLY_THROUGH_EXISTING_GATE_G"

REQUIRED_AUTHORITIES=("SPENDABLE_BUDGET","PROVIDER_CAPABILITY","ACCESS",
 "TRANSPORT_FEASIBILITY","INSURANCE","CERTIFICATION","REGULATORY")

def assess_feasibility(p:AssembledPropositionV03)->PropositionFeasibilityV03:
 by={x.authority:x for x in p.authorities}; reasons=[]
 for name in REQUIRED_AUTHORITIES:
  a=by.get(name)
  if a is None or a.status==AuthorityStatus.UNKNOWN:
   reasons.append(name+"_UNKNOWN"); continue
  if a.status==AuthorityStatus.KNOWN and a.satisfied is not True:
   reasons.append(name+"_UNSATISFIED")
 # accepted exploration is necessary evidence of assembly, never sufficient authority.
 if not p.accepted_counterparty_actor_ids:reasons.append("NO_ACCEPTED_COUNTERPARTIES")
 if not p.provenance_refs:reasons.append("MISSING_PROVENANCE")
 return PropositionFeasibilityV03(p.proposition_id,"FEASIBLE" if not reasons else "BLOCKED",
     tuple(reasons),p.authorities)

def commit_assembled_proposition(*,state:Mapping[str,object],proposition:AssembledPropositionV03,
                                 project_id:str,commit_year:int):
 f=assess_feasibility(proposition)
 if f.status!="FEASIBLE":
  return state,CommitmentBridgeResultV03(proposition.proposition_id,f,"NOT_ATTEMPTED",
      f.reason_codes,None,())
 req=TransactionRequestV03(
   transaction_id="TX:"+proposition.proposition_id,
   opportunity_id=proposition.proposition_id,
   customer_actor_id=proposition.origin_actor_id,
   provider_actor_id=proposition.provider_actor_id,
   required_budget=proposition.required_budget,
   provider_capacity_units=proposition.provider_capacity_units,
   project_id=project_id,future_event_year=commit_year,
   future_event_type="PROJECT_REVIEW",
   provenance_refs=proposition.provenance_refs)
 out,tr=commit_transaction(state=state,request=req)
 return out,CommitmentBridgeResultV03(proposition.proposition_id,f,tr.status,tr.reason_codes,
     project_id if tr.status=="COMMITTED" else None,tr.emitted_event_ids)

def known(authority:str,*refs:str)->FeasibilityAuthorityV03:
 return FeasibilityAuthorityV03(authority,AuthorityStatus.KNOWN,True,tuple(refs))
def unknown(authority:str,*refs:str)->FeasibilityAuthorityV03:
 return FeasibilityAuthorityV03(authority,AuthorityStatus.UNKNOWN,None,tuple(refs))

def assemble_from_exploratory_responses(*,decision,origin_identity,responses:Sequence[object],
                                        provider_actor_id:str|None=None,
                                        required_budget:float=0.0,provider_capacity_units:float=1.0):
 """Conservative handoff from Step A. Interest never manufactures hard authority.

 The current 2026 actor bootstrap contains estimated financial capacity, not a
 spendable allocation, so budget remains UNKNOWN. Step C/runtime may later supply
 governed authorities from actor state and qualified services.
 """
 accepted=tuple(sorted({str(x.responder_actor_id) for x in responses
   if getattr(getattr(x,"disposition",None),"value",None)=="ACCEPT_EXPLORATION"}))
 refs=tuple(sorted(set((decision.proposition_id,decision.context_id)+tuple(
   r for x in responses for r in getattr(x,"provenance_refs",())))))
 bycat={}
 for x in responses:
  if getattr(getattr(x,"disposition",None),"value",None)=="ACCEPT_EXPLORATION":
   bycat.setdefault(str(x.target_category),[]).append(str(x.responder_actor_id))
 provider=provider_actor_id or (sorted(bycat.get("SUPPLIER_PRIME",()) or bycat.get("INFRASTRUCTURE",())
                                      or bycat.get("INCUMBENT_INDUSTRY",()) or accepted or (origin_identity.actor_id,))[0])
 def a(name,proved):
  return known(name,*refs) if proved else unknown(name,*refs)
 # Accepted exploration proves only that a role is present and willing to investigate.
 # It does NOT prove the role's substantive authority. All hard gates remain UNKNOWN.
 authorities=tuple(a(name,False) for name in REQUIRED_AUTHORITIES)
 return AssembledPropositionV03(decision.proposition_id,origin_identity.actor_id,provider,
     float(required_budget),float(provider_capacity_units),authorities,accepted,refs)
