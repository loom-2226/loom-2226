"""Step C governed hard-authority resolution.

UNKNOWN may resolve only through an existing typed authority, a governed derivation,
a proposition-specific counterparty allocation, or an endogenous event.
"""
from dataclasses import dataclass
from enum import Enum
from .proposition_commitment_bridge_v0_3 import FeasibilityAuthorityV03,AuthorityStatus

class ResolutionPath(str,Enum):
 EXISTING_AUTHORITY="EXISTING_AUTHORITY"
 GOVERNED_DERIVATION="GOVERNED_DERIVATION"
 COUNTERPARTY_TRANSACTION="COUNTERPARTY_TRANSACTION"
 ENDOGENOUS_EVENT="ENDOGENOUS_EVENT"

@dataclass(frozen=True)
class AuthorityResolutionV03:
 authority:str; status:AuthorityStatus; satisfied:bool|None
 path:ResolutionPath|None; source_actor_id:str|None
 value:float|None; unit:str|None; provenance_refs:tuple[str,...]
 semantics:str="PROPOSITION_SCOPED_AUTHORITY_NOT_GENERAL_ACTOR_FACT"

def unresolved(authority,*refs):
 return AuthorityResolutionV03(authority,AuthorityStatus.UNKNOWN,None,None,None,None,None,tuple(refs))

def existing(authority,satisfied,*refs):
 return AuthorityResolutionV03(authority,AuthorityStatus.KNOWN,bool(satisfied),ResolutionPath.EXISTING_AUTHORITY,None,None,None,tuple(refs))

def allocate_financing(*,capital_identity,proposition_id,amount,already_allocated=0.0):
 """Explicit model allocation. Estimated capacity is a ceiling, never automatically cash."""
 cap=float(capital_identity.financial_capacity_estimate or 0.0)
 amount=float(amount); used=float(already_allocated)
 if amount<=0 or cap<=0 or used+amount>cap:
  return unresolved("SPENDABLE_BUDGET",proposition_id,"FINANCING_CAPACITY_INSUFFICIENT_OR_UNKNOWN")
 return AuthorityResolutionV03("SPENDABLE_BUDGET",AuthorityStatus.KNOWN,True,
   ResolutionPath.COUNTERPARTY_TRANSACTION,capital_identity.actor_id,amount,"MODEL_CURRENCY_UNITS",
   (proposition_id,capital_identity.actor_id,"MODEL_DERIVED_ALLOCATION_FROM_2026_CAPACITY"))

def provider_from_typed_capability(*,provider_actor_id,capability_status,proposition_id,refs=()):
 if capability_status!="USABLE": return unresolved("PROVIDER_CAPABILITY",proposition_id,*refs)
 return AuthorityResolutionV03("PROVIDER_CAPABILITY",AuthorityStatus.KNOWN,True,
   ResolutionPath.EXISTING_AUTHORITY,provider_actor_id,None,None,(proposition_id,)+tuple(refs))

def transport_from_accessibility(*,assessment_status,provider_actor_id,proposition_id,refs=()):
 if assessment_status=="FEASIBLE":
  return AuthorityResolutionV03("TRANSPORT_FEASIBILITY",AuthorityStatus.KNOWN,True,
    ResolutionPath.EXISTING_AUTHORITY,provider_actor_id,None,None,(proposition_id,)+tuple(refs))
 if assessment_status=="INFEASIBLE":
  return AuthorityResolutionV03("TRANSPORT_FEASIBILITY",AuthorityStatus.KNOWN,False,
    ResolutionPath.EXISTING_AUTHORITY,provider_actor_id,None,None,(proposition_id,)+tuple(refs))
 return unresolved("TRANSPORT_FEASIBILITY",proposition_id,*refs)

def to_feasibility(resolutions):
 return tuple(FeasibilityAuthorityV03(x.authority,x.status,x.satisfied,x.provenance_refs) for x in resolutions)
