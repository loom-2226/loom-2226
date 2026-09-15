"""Trade Wayfarer torch performance requirements against explicit source efficiency and mass."""
import math, json
JET={"ECON":5112451811250.0,"CRUISE":11361004025000.0,"EXPEDITE":11361004025000.0,"FAST":11929054226250.0,"HARD":12781129528125.0,"LIMIT":12781129528125.0}

def build_trade():
 return {"schema":"LOOM.Wayfarer.TorchRequirementsSourceMassEfficiencyTrade","schema_version":"0.1","status":"PASS",
 "authority":{"claim":"E1_TORCH_REQUIREMENTS_VS_SOURCE_MASS_AND_EFFICIENCY_TRADE_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"source_architecture_selected":False,"performance_cards_changed":False},
 "future_inputs":{"directed_fraction":None,"source_specific_power_W_kg":None,"source_mass_budget_kg":None},
 "known":{"direct_jet_power_W":JET,"candidate_total_propulsion_allocation_kg":160000.0},
 "allocation_firewall":"160_T_TOTAL_PROPULSION_ALLOCATION_IS_NOT_A_DEFAULT_SOURCE_MASS_BUDGET",
 "trade_axes":["PERFORMANCE_REQUIREMENT","DIRECTED_ENERGY_FRACTION","SOURCE_SPECIFIC_POWER","EXPLICIT_SOURCE_MASS_BUDGET"],
 "decision_options":["PRESERVE_ALL_SIX_PERFORMANCE_CARDS_AND_REQUIRE_BREAKTHROUGH_SOURCE","REDUCE_OR_RESHAPE_HIGH_MODES","INCREASE_EARNED_PROPULSION_MASS_ALLOCATION","CHANGE_SOURCE_ARCHITECTURE","CHANGE_VEHICLE_MASS_OR_MISSION_REQUIREMENTS"],
 "rules":["NO_2226_EFFICIENCY_OR_SPECIFIC_POWER_IS_INVENTED","MASS_BUDGET_MUST_BE_EXPLICIT","CURRENT_PERFORMANCE_CARDS_REMAIN_REQUIREMENTS_UNTIL_GOVERNED_CHANGE","RESEARCH_ANALOGS_ARE_SCALE_DIAGNOSTICS_NOT_CERTIFICATION"],
 "qualified_next_step":"TORCH_REQUIREMENTS_REDUCTION_AND_SOURCE_PACKAGING_DECISION_REVIEW"}

def evaluate_point(mode,directed_fraction,source_specific_power_W_kg,source_mass_budget_kg):
 if mode not in JET: raise ValueError("unknown mode")
 if directed_fraction is None or not math.isfinite(directed_fraction) or directed_fraction<=0 or directed_fraction>1: raise ValueError("directed fraction must be explicit in (0,1]")
 if source_specific_power_W_kg is None or not math.isfinite(source_specific_power_W_kg) or source_specific_power_W_kg<=0: raise ValueError("specific power must be explicit and positive")
 if source_mass_budget_kg is None or not math.isfinite(source_mass_budget_kg) or source_mass_budget_kg<=0: raise ValueError("source mass budget must be explicit and positive")
 p=JET[mode]/directed_fraction
 m=p/source_specific_power_W_kg
 return {"mode":mode,"source_power_W":p,"required_source_mass_kg":m,"explicit_source_mass_budget_kg":source_mass_budget_kg,"mass_margin_kg":source_mass_budget_kg-m,"required_specific_power_for_mass_budget_W_kg":p/source_mass_budget_kg,"certified":False,"status":"SENSITIVITY_ONLY_EXPLICIT_INPUTS"}

if __name__=="__main__": print(json.dumps(build_trade(),indent=2,sort_keys=True))
