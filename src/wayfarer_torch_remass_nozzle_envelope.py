"""Requirement envelope for Wayfarer torch bulk-remass coupling and magnetic nozzle.
No working fluid, coupling efficiency, detachment efficiency, or component geometry is invented here.
"""
import json, math

MODE_REQUIREMENTS={
 'ECON': {'exhaust_velocity_km_s':3000.0,'mass_flow_kg_s':1.1361004025,'direct_jet_power_W':5_112_451_811_250.0},
 'CRUISE': {'exhaust_velocity_km_s':2000.0,'mass_flow_kg_s':5.6805020125,'direct_jet_power_W':11_361_004_025_000.0},
 'EXPEDITE': {'exhaust_velocity_km_s':1000.0,'mass_flow_kg_s':22.72200805,'direct_jet_power_W':11_361_004_025_000.0},
 'FAST': {'exhaust_velocity_km_s':700.0,'mass_flow_kg_s':48.69001725,'direct_jet_power_W':11_929_054_226_250.0},
 'HARD': {'exhaust_velocity_km_s':450.0,'mass_flow_kg_s':126.23337805555556,'direct_jet_power_W':12_781_129_528_125.0},
 'LIMIT': {'exhaust_velocity_km_s':300.0,'mass_flow_kg_s':284.025100625,'direct_jet_power_W':12_781_129_528_125.0},
}

def evaluate_coupling_candidate(mode, source_to_remass_coupling_fraction, magnetic_nozzle_directed_efficiency):
    if mode not in MODE_REQUIREMENTS: raise ValueError('unknown mode')
    c=float(source_to_remass_coupling_fraction); n=float(magnetic_nozzle_directed_efficiency)
    if not (math.isfinite(c) and 0<c<=1 and math.isfinite(n) and 0<n<=1): raise ValueError('fractions must be finite in (0,1]')
    combined=c*n; jet=MODE_REQUIREMENTS[mode]['direct_jet_power_W']
    return {'mode':mode,'direct_jet_power_W':jet,'source_to_remass_coupling_fraction':c,'magnetic_nozzle_directed_efficiency':n,'combined_directed_fraction':combined,'required_upstream_coupled_power_W':jet/combined,'upstream_power_is_electrical_load':False,'status':'SENSITIVITY_ONLY_NOT_CERTIFIED'}

def build_envelope():
    return {
      'schema':'LOOM.Wayfarer.TorchRemassCouplingMagneticNozzleEnvelope','schema_version':'0.1','status':'PASS',
      'authority':{'claim':'E1_TORCH_REMASS_COUPLING_AND_MAGNETIC_NOZZLE_EFFICIENCY_ENVELOPE_ONLY','campaign_state_mutation':'ZERO','llm_calculation_authority':'ZERO','canon_changed':False,'working_fluid_certified':False,'remass_coupling_certified':False,'nozzle_efficiency_certified':False,'plasma_detachment_certified':False,'nozzle_geometry_certified':False},
      'mode_requirements':MODE_REQUIREMENTS,
      'candidate_inputs':{'source_to_remass_coupling_fraction':None,'magnetic_nozzle_directed_efficiency':None,'working_fluid_identity':None,'plasma_detachment_fraction':None},
      'derived_requirements':[
        '250_T_NORMAL_REMASS_REQUIRES_A_PHYSICAL_INJECTION_HEATING_ENTRAINMENT_AND_EXHAUST_PATH',
        'SYSTEM_MUST_SPAN_1_136_TO_284_025_KG_S_MASS_FLOW_ACROSS_GOVERNED_MODES',
        'SYSTEM_MUST_SPAN_300_TO_3000_KM_S_EFFECTIVE_EXHAUST_VELOCITY',
        'MODE_CONTROL_MUST_TRADE_MASS_FLOW_AGAINST_ENERGY_PER_UNIT_MASS_WITHOUT_ASSUMING_CONSTANT_NOZZLE_EFFICIENCY',
        'MAGNETIC_NOZZLE_MUST_BOUND_DIVERGENCE_INTERCEPTION_AND_PLASMA_DETACHMENT_BY_MODE',
      ],
      'nozzle_physics_gates':{'expansion':'OPEN','plasma_detachment':'OPEN','divergence_angle':'OPEN','coil_interception':'OPEN','magnetic_field_strength_and_geometry':'OPEN','coil_stress_and_lifetime':'OPEN','mode_dependent_efficiency':'OPEN'},
      'working_fluid_gates':{'identity':'OPEN','storage_state':'OPEN','injection_architecture':'OPEN','ionization_and_heating_path':'OPEN','erosion_and_contamination':'OPEN','feed_system_thermal_load':'OPEN'},
      'research_analogy_firewall':'DIRECT_FUSION_DRIVE_AND_FUSION_DRIVEN_ROCKET_LITERATURE_SUPPORT_THE_EXISTENCE_OF_REMASS_AUGMENTATION_AND_MAGNETIC_NOZZLE_RESEARCH_ANALOGS_BUT_DO_NOT_SUPPLY_WAYFARER_EFFICIENCIES',
      'kill_criteria':['cannot_physically_couple_source_energy_into_bulk_remass','cannot_span_required_mass_flow_and_exhaust_velocity','nozzle_detachment_or_divergence_cannot_be_bounded','magnet_or_nozzle_interception_breaks_deposition_budget','required_upstream_power_depends_on_unearned_efficiency','working_fluid_or_feed_path_cannot_close_packaging_thermal_or_lifetime_constraints'],
      'carried_rcs_integration_holds':['PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP','WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD','MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE','VECTORING_DYNAMIC_RESPONSE_AND_LIFE','MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT'],
      'qualified_next_step':'TORCH_PHYSICAL_PLUME_AND_EXTERNAL_CLEARANCE_ENVELOPE'}

if __name__=='__main__': print(json.dumps(build_envelope(),indent=2,sort_keys=True))
