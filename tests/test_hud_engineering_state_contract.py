from loom.hud.contracts import AuthorityClass, Availability, StateDatum
from loom.hud.engineering_state_contract import build_wayfarer_engineering_hud_state


def test_wayfarer_engineering_hud_state_uses_typed_datums():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")

    assert isinstance(state.reference_wet_mass, StateDatum)
    assert state.reference_wet_mass.value == 1158.5
    assert state.reference_wet_mass.unit == "t"
    assert state.reference_wet_mass.authority == AuthorityClass.QUALIFICATION_ONLY
    assert state.reference_wet_mass.availability == Availability.AVAILABLE
    assert state.reference_wet_mass.quality == "ENGINEERING_BASELINE_NON_CANON"

    assert state.normal_remass.value == 250.0
    assert state.protected_water_reserve.value == 50.0
    assert state.protected_water_reserve.quality == "PROTECTED_NOT_ROUTINE_PROPULSION"


def test_open_and_candidate_statuses_survive_typed_adapter():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")

    assert state.power_thermal_status.value == "OPEN_BOUNDED"
    assert state.power_thermal_status.quality == "ENGINEERING_CANDIDATE_NON_CANON"
    assert state.dispatch_status.value == "CANDIDATE_NON_CANON"
    assert state.feedstock_primary.value == "H2O"
    assert state.feedstock_primary.quality == "PRIMARY_CANDIDATE_NOT_CERTIFIED"
    assert state.feedstock_certified_species.value == ()
    assert state.feedstock_certified_species.quality == "CERTIFIED_NONE"


def test_q5_attitude_energy_machine_detail_is_typed_without_widening_scope():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")

    assert state.attitude_energy_status.value == "OPEN_BOUNDED"
    assert state.attitude_energy_status.quality == "ENGINEERING_CANDIDATE_NON_CANON"
    assert state.attitude_energy_buffer_screen_pass.value is True
    assert state.attitude_energy_detail_available.value is True
    assert state.attitude_energy_detail_available.quality == "PINNED_MACHINE_READABLE_PR96_ARTIFACT"
    assert len(state.attitude_energy_maneuvers) == 12
    assert state.attitude_energy_max_jet_energy.value == 113.991693
    assert state.attitude_energy_max_waste_heat_energy.value == 12.665744
    assert state.attitude_energy_max_equivalent_expelled_mass.value == 227.983387

    pitch = state.attitude_energy_maneuvers["ONE_CLUSTER_OUT:PITCH_180"]
    assert pitch.qualified_transition_time.value == 68.98
    assert pitch.powered_rcs_time.value == 57.483333
    assert pitch.settle_margin_time.value == 11.496667
    assert pitch.worst_failed_cluster.value == "B"
    assert pitch.total_resultant_mount_thrust.value == 79.321561
    alt = pitch.candidates["alternate_50kms"]
    assert alt.jet_energy.value == 113.991693
    assert alt.waste_heat_energy.value == 12.665744
    assert alt.heat_fraction_of_50GJ_buffer.value == 0.253314874
    assert alt.radiator_transient_credit_applied.value is False

    assert state.combined_maneuver_energy_available.value is False
    assert state.combined_maneuver_energy_available.quality == "TIMING_OPEN_Q4_Q5"
    assert state.translation_maneuver_energy_available.value is False
    assert state.translation_maneuver_energy_available.quality == "TIMING_OPEN_Q4_Q5"


def test_reserve_concepts_remain_separate():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")

    assert state.normal_dispatch_remass.value == 150.0
    assert state.operational_remass_floor.value == 100.0
    assert state.protected_optimizer_reserve.value == 50.0
    assert state.protected_water_reserve.value == 50.0
    assert state.protected_optimizer_reserve.source != state.protected_water_reserve.source
    assert state.routine_optimizer_may_consume_protected_water.value is False


def test_torch_and_mobility_firewalls_survive_typed_adapter():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")

    cruise = state.torch_modes["CRUISE"]
    assert cruise.acceleration_g.value == 1.0
    assert cruise.exhaust_velocity.value == 2000.0
    assert cruise.status.value == "WORKING_ENGINEERING_CARD"
    assert state.torch_jet_power_is_electrical_bus_power.value is False
    assert state.metric_velocity_reset_allowed.value is False


def test_source_commit_is_present_on_every_datum():
    state = build_wayfarer_engineering_hud_state(epoch="QUALIFICATION_STATIC")
    datums = [
        state.reference_wet_mass,
        state.dry_mass,
        state.normal_remass,
        state.protected_water_reserve,
        state.power_thermal_status,
        state.attitude_energy_status,
        state.attitude_energy_buffer_screen_pass,
        state.attitude_energy_detail_available,
        state.attitude_energy_maneuvers["ONE_CLUSTER_OUT:PITCH_180"].candidates["alternate_50kms"].jet_energy,
        state.dispatch_status,
        state.feedstock_primary,
        state.routine_optimizer_may_consume_protected_water,
    ]
    for datum in datums:
        assert "835cccfb4a37a2a683c6196cbb7382b826271d67" in datum.source
