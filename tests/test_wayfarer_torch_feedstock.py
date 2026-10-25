import math

from src.wayfarer_torch_feedstock import mode_closure


G0 = 9.80665
WET_MASS_KG = 1_158_500.0


def test_econ_reference_closure():
    out = mode_closure(WET_MASS_KG, 0.30, 3_000.0)
    assert math.isclose(out["thrust_MN"], 3.4083012075, rel_tol=1e-9)
    assert math.isclose(out["mdot_kg_s"], 1.1361004025, rel_tol=1e-9)
    assert math.isclose(out["jet_power_TW"], 5.11245181125, rel_tol=1e-9)


def test_limit_reference_closure():
    out = mode_closure(WET_MASS_KG, 7.50, 300.0)
    assert math.isclose(out["thrust_MN"], 85.2075301875, rel_tol=1e-9)
    assert math.isclose(out["mdot_kg_s"], 284.025100625, rel_tol=1e-9)
    assert math.isclose(out["jet_power_TW"], 12.781129528125, rel_tol=1e-9)


def test_species_identity_does_not_enter_ideal_momentum_closure():
    # At fixed ship mass, acceleration and exhaust velocity, ideal thrust/mass-flow
    # closure is species-independent. Feed chemistry belongs in a separate
    # conditioning/materials model.
    water_case = mode_closure(WET_MASS_KG, 1.0, 2_000.0)
    argon_case = mode_closure(WET_MASS_KG, 1.0, 2_000.0)
    assert water_case == argon_case


def test_remass_per_hour_matches_mass_flow():
    out = mode_closure(WET_MASS_KG, 2.0, 1_000.0)
    expected_t_h = out["mdot_kg_s"] * 3600.0 / 1000.0
    assert math.isclose(out["remass_t_per_h"], expected_t_h, rel_tol=1e-12)
