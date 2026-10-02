"""Phase 10 group actor integration. NON_CANON machinery test."""
from dataclasses import dataclass
@dataclass(frozen=True)
class ActorCategoryContractV03:
 category_id:str
 engine_actor_type:str
 decision_rule:str
 decline_codes:tuple[str,...]
 belief_lag:str
 publishes:str
 budget_status:str
 budget_scope:str|None
 authority_class:str="NON_CANON_SEED_CATEGORY_CONTRACT"
@dataclass(frozen=True)
class IntegratedActorV03:
 actor_id:str
 name:str
 category_id:str
 engine_actor_type:str
 belief_lag:str
 budget_status:str
 confidence:str
 verified_by_search:bool
 authority_class:str="NON_CANON_2026_ACTOR_CANDIDATE"
def compile_category_contracts(seed):
 out={}
 for cid,c in seed["categories"].items():
  b=c.get("budget") or {}
  out[cid]=ActorCategoryContractV03(cid,c["engine_actor_type_hint"],
   c["decision_rule"],tuple(c["decline_codes"]),c["belief_lag"],c["publishes"],
   b.get("status","UNKNOWN"),b.get("scope"))
 return out
def integrate_actor_candidates(seed):
 cats=compile_category_contracts(seed); out=[]
 for a in seed["actors"]:
  cid=a["category"]
  if cid not in cats: raise ValueError("ACTOR_CATEGORY_NOT_DEFINED")
  c=cats[cid]
  out.append(IntegratedActorV03(a["id"],a["name"],cid,c.engine_actor_type,
   c.belief_lag,c.budget_status,a.get("conf","UNKNOWN"),
   bool(a.get("verified_by_search",False))))
 return tuple(out)
def actor_can_commit_budget(actor):
 return actor.budget_status=="KNOWN"
def validate_decline_code(category,code):
 return code in category.decline_codes
