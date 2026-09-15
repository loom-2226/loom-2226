"""Research-bounded E1 torch source scaling diagnostics.

External DFD/PFRC values remain provenance anchors, never Wayfarer parameters.
"""
import json

JET={"ECON":5.11245181125e12,"CRUISE":1.1361004025e13,"EXPEDITE":1.1361004025e13,"FAST":1.192905422625e13,"HARD":1.2781129528125e13,"LIMIT":1.2781129528125e13}
ANCHORS=[1500.0,25000.0,100000.0,1e6,1e7,1e8]
ALLOC_T=160.0

def build_scaling_review():
    diag={}
    for mode,p in JET.items():
        d={f"source_mass_t_at_{int(sp)}_W_kg":p/sp/1000.0 for sp in ANCHORS}
        d["improvement_over_1500_W_kg_for_160_t"]=(p/(ALLOC_T*1000.0))/1500.0
        diag[mode]=d
    return {
      "schema":"LOOM.Wayfarer.TorchResearchBoundedSourceScaling","schema_version":"0.1","status":"PASS",
      "authority":{"claim":"E1_TORCH_RESEARCH_BOUNDED_SOURCE_SCALING_DIAGNOSTICS_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"external_anchor_promoted_to_wayfarer_parameter":False,"candidate_propulsion_allocation_closed":False,"source_architecture_certified":False},
      "external_research":{"authority":"EXTERNAL_RESEARCH_SYNTHESIS","present_DFD_specific_power_range_W_kg":[300.0,1500.0],"published_or_illustrative_high_specific_power_anchors_W_kg":[25000.0,100000.0],"PFRC_DFD_power_class_W":[1e6,1e7],"warning":"VALUES_ARE_RESEARCH_PROVENANCE_NOT_WAYFARER_INPUTS"},
      "wayfarer_candidate_inputs":{"source_specific_power_W_kg":None,"directed_energy_fraction":None,"fusion_gain_Q":None},
      "candidate_propulsion_allocation_t":ALLOC_T,
      "minimum_jet_specific_power_if_entire_160_t_were_source_W_kg":{m:p/(ALLOC_T*1000.0) for m,p in JET.items()},
      "scaling_diagnostics":diag,
      "interpretation":["EVEN_THE_FULL_160_T_CANDIDATE_PROPULSION_ALLOCATION_WOULD_REQUIRE_ORDER_3E7_TO_8E7_W_KG_AT_JET_POWER_BEFORE_LOSSES","PRESENT_DFD_ESTIMATES_ARE_TENS_OF_THOUSANDS_OF_TIMES_TOO_LOW_FOR_A_160_T_LIMIT_MODE_SOURCE","A_100_MW_KG_SOURCE_IS_AN_ILLUSTRATIVE_SCALING_POINT_NOT_A_FORECAST_OR_CERTIFIED_2226_VALUE","SOURCE_SHIELD_MAGNET_NOZZLE_FEED_STRUCTURE_AND_THERMAL_MASS_MUST_SHARE_THE_PROPULSION_BUDGET"],
      "technology_direction_decision":"RETAIN_AS_RESEARCH_TOPOLOGY_ONLY_PHYSICAL_SCALE_NOT_CLOSED",
      "blocking_holds":["ORDERS_OF_MAGNITUDE_SOURCE_SPECIFIC_POWER_ADVANCE","PHYSICAL_DIRECTED_ENERGY_PARTITION","FUSION_GAIN_AND_RECIRCULATING_POWER","SOURCE_PLUS_SHIELD_MAGNET_NOZZLE_MASS_RECONCILIATION","THERMAL_AND_RADIATION_LIFETIME_CLOSURE"],
      "qualified_next_step":"TORCH_ENERGY_PARTITION_AND_MASS_BUDGET_FEASIBILITY_ENVELOPE"
    }

if __name__=="__main__": print(json.dumps(build_scaling_review(),indent=2,sort_keys=True))
