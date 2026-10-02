"""Governed migration adapter for the qualified C-M causal architecture.

Opt-in only. Does not replace HYBRID_V1 or alter frozen-baseline execution.
NON-CANON / MIGRATION CANDIDATE / UNPROMOTED.
"""
from dataclasses import dataclass
from engineering.civprop.contracts.gate_f_causal_neighborhood_competition_v0_3 import arbitrate_scoped_competition
from engineering.civprop.contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03,commit_winning_branches
from engineering.civprop.contracts.gate_h_closed_loop_causality_v0_3 import run_closed_loop
from engineering.civprop.contracts.gate_i_physical_capacity_feedback_v0_3 import project_capacity
from engineering.civprop.contracts.gate_j_endogenous_opportunity_v0_3 import detect_capacity_opportunity

@dataclass(frozen=True)
class CausalRuntimeMigrationResultV03:
 competition:object; transaction_results:tuple; closed_loop:object
 capacity_states:tuple; endogenous_opportunities:tuple; final_state:dict

def run_migration_slice(*,actor_universe,seed_edges,opportunities,budget_value,
                        initial_state,request_by_opportunity,start_year,end_year,
                        installed_capacity_by_project,failure_year_by_project=None):
 competition=arbitrate_scoped_competition(trigger_actor_id="NASA",scope_token="CLPS",
  seed_edges=seed_edges,actor_universe=actor_universe,opportunities=opportunities,
  budget_status="KNOWN",budget_value=budget_value)
 branches=tuple({"opportunity_id":x.opportunity_id,"action":x.action} for x in competition.branches)
 state,tx=commit_winning_branches(state=initial_state,branches=branches,request_by_opportunity=request_by_opportunity)
 loop=run_closed_loop(committed_state=state,start_year=start_year,end_year=end_year)
 capacities=[]; endogenous=[]
 for pid,p in sorted(loop.final_state.get("projects",{}).items()):
  if p.get("status")!="ACTIVE": continue
  if pid not in installed_capacity_by_project: continue
  row=dict(p,project_id=pid,capital=1)
  cs=project_capacity(project=row,years=(end_year,),installed_capacity=installed_capacity_by_project[pid],
   failure_year=(failure_year_by_project or {}).get(pid))
  capacities.extend(cs)
  endogenous.append(detect_capacity_opportunity(states=cs,year=end_year,required_capacity=1.0))
 return CausalRuntimeMigrationResultV03(competition,tx,loop,tuple(capacities),tuple(endogenous),loop.final_state)
