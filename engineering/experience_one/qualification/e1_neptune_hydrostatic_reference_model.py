import json

from src.loom_neptune_hydrostatic_reference_model import NeptuneHydrostaticReferenceModel


model = NeptuneHydrostaticReferenceModel()
pressure = model.pressure_envelope_pa(40.0)
density = model.density_envelope_kg_m3(40.0)

report = {
    "schema": "LOOM_E1_NEPTUNE_HYDROSTATIC_REFERENCE_MODEL_V1",
    "status": "PASS",
    "body": "NE",
    "classification": "BOUNDED_HISTORICAL_PHYSICAL_REFERENCE_MODEL_ONLY",
    "source_epoch_class": model.source_epoch_class,
    "domain_altitude_from_one_bar_km": [model.altitude_min_km, model.altitude_max_km],
    "temperature_assumption": "LINEAR_BETWEEN_QUALIFIED_72K_AND_52K_HISTORICAL_ANCHORS",
    "hydrostatic_assumption": "IDEAL_GAS_HYDROSTATIC_BALANCE",
    "gravity_assumption": "CONSTANT_SPHERICAL_G_AT_VOYAGER_1BAR_EQUATORIAL_RADIUS",
    "composition_assumption": "H2_NUMBER_FRACTION_0.78_TO_0.84_REMAINDER_HE",
    "pressure_at_40km_model_envelope_pa": [pressure.minimum_pa, pressure.maximum_pa],
    "published_tropopause_reference_pa": pressure.observed_reference_pa,
    "pressure_relative_error_envelope": [pressure.minimum_relative_error, pressure.maximum_relative_error],
    "density_at_40km_model_envelope_kg_m3": [density.minimum, density.maximum],
    "model_validation": "NOT_FORCED_TO_MATCH_TROPOPAUSE_PRESSURE_ANCHOR",
    "interpolation_authority": model.interpolation_authority,
    "extrapolation_authority": model.extrapolation_authority,
    "density_authority": "HISTORICAL_REFERENCE_MODEL_ONLY",
    "local_2226_endpoint_values_earned": False,
    "admissibility_authority": model.admissibility_authority,
    "loom_coherence_authority": model.loom_coherence_authority,
    "runtime_policy_authority": "ZERO",
    "authority_note": "BOUNDED_REFERENCE_MODEL_ONLY_NO_2226_PROPAGATION_NO_ATMOSPHERIC_CUTOFF_NO_THRESHOLD_NO_SCORE_NO_RUNTIME_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
    "next_action": "DECIDE_WHETHER_TO_QUALIFY_A_2226_EVOLUTION_UNCERTAINTY_MODEL_OR_KEEP_ENDPOINT_ENVIRONMENT_UNKNOWN",
}

print(json.dumps(report, indent=2, sort_keys=True))
