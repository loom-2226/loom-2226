"""Wayfarer E1 torch source-power realizability envelope.

No fusion gain, directed-energy fraction, or specific power is assumed. Explicit
candidate values may be evaluated for sensitivity only; they are never certified.
"""
import json

JET_POWER_W={
 "ECON":5112451811250.0,"CRUISE":11361004025000.0,"EXPEDITE":11361004025000.0,
 "FAST":11929054226250.0,"HARD":12781129528125.0,"LIMIT":12781129528125.0,
}

def build_envelope():
    return {
      "schema":"LOOM.Wayfarer.TorchSourcePowerRealizabilityEnvelope","schema_version":"0.1","status":"PASS",
      "authority":{"claim":"E1_TORCH_SOURCE_POWER_REALIZABILITY_REQUIREMENT_ENVELOPE_ONLY","campaign_state_mutation":"ZERO","llm_calculation_authority":"ZERO","canon_changed":False,"fusion_gain_certified":False,"specific_power_certified":False,"source_architecture_certified":False},
      "candidate_inputs":{"directed_energy_fraction":None,"fusion_gain_Q":None,"specific_power_W_kg":None},
      "known_direct_jet_power_W":JET_POWER_W,
      "derived_contract":["REQUIRED_FUSION_OUTPUT_POWER_EQUALS_DIRECT_JET_POWER_DIVIDED_BY_EXPLICIT_DIRECTED_ENERGY_FRACTION","IF_A_STATED_Q_DEFINITION_APPLIES_MINIMUM_EXTERNAL_DRIVER_POWER_EQUALS_FUSION_OUTPUT_POWER_DIVIDED_BY_Q","IF_A_STATED_SYSTEM_SPECIFIC_POWER_APPLIES_MINIMUM_SOURCE_SYSTEM_MASS_EQUALS_FUSION_OUTPUT_POWER_DIVIDED_BY_SPECIFIC_POWER"],
      "power_firewall":"FUSION_OUTPUT_AND_DRIVER_POWER_ARE_NOT_AUTOMATICALLY_VEHICLE_ELECTRICAL_LOAD_OR_WASTE_HEAT",
      "realizability_decision":"OPEN_NEEDS_PHYSICAL_BOUNDS",
      "blocking_holds":["DIRECTED_ENERGY_FRACTION_FROM_PHYSICAL_PARTITION","FUSION_GAIN_Q_BY_MODE","SOURCE_SYSTEM_SPECIFIC_POWER","DRIVER_RECIRCULATING_POWER_ARCHITECTURE","MAGNET_AND_AUXILIARY_POWER","RADIATION_AND_THERMAL_PARTITION","SOURCE_LIFETIME_AND_MAINTENANCE"],
      "research_boundary":"EXTERNAL_RESEARCH_ANALOGS_MAY_BOUND_OR_MOTIVATE_INPUTS_BUT_DO_NOT_CERTIFY_WAYFARER_VALUES",
      "qualified_next_step":"TORCH_RESEARCH_BOUND_PHYSICAL_PARTITION_GAIN_AND_SPECIFIC_POWER",
    }

def evaluate_candidate(mode,directed_energy_fraction,fusion_gain_Q,specific_power_W_kg):
    if mode not in JET_POWER_W: raise ValueError("unknown mode")
    if not (0.0 < directed_energy_fraction <= 1.0): raise ValueError("directed_energy_fraction must be in (0,1]")
    if fusion_gain_Q <= 0.0: raise ValueError("fusion_gain_Q must be positive")
    if specific_power_W_kg <= 0.0: raise ValueError("specific_power_W_kg must be positive")
    output=JET_POWER_W[mode]/directed_energy_fraction
    return {"mode":mode,"required_fusion_output_W":output,"minimum_external_driver_power_W_if_Q_definition_applies":output/fusion_gain_Q,"minimum_source_system_mass_kg_at_specific_power":output/specific_power_W_kg,"certified":False,"interpretation":"SENSITIVITY_ONLY_EXPLICIT_INPUTS_NOT_WAYFARER_CERTIFICATION"}

if __name__=="__main__": print(json.dumps(build_envelope(),indent=2,sort_keys=True))
