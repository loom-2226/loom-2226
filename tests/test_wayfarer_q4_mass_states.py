import math

from src.wayfarer_q4_mass_states import build_q4_mass_state


def test_wet_state_places_normal_remass_in_four_radial_tanks():
    out = build_q4_mass_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    tanks = [e for e in out["elements"] if e["kind"] == "NORMAL_REMASS_TANK_FLUID"]
    assert len(tanks) == 4
    assert abs(sum(t["mass_t"] for t in tanks) - 250.0) < 1e-9
    for tank in tanks:
        assert abs(math.hypot(tank["y_m"], tank["z_m"]) - 2.7) < 1e-9


def test_balanced_depletion_preserves_lateral_symmetry_except_docked_launch():
    out = build_q4_mass_state(normal_remass_t=100.0, protected_water_t=50.0, launch_docked=True)
    com = out["center_of_mass_m"]
    assert abs(com[1]) < 1e-9
    assert com[2] > 0.0


def test_launch_absent_removes_known_positive_z_asymmetry():
    docked = build_q4_mass_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    absent = build_q4_mass_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=False)
    assert docked["center_of_mass_m"][2] > absent["center_of_mass_m"][2]
    assert docked["mass_t"] - absent["mass_t"] == 33.0


def test_roll_inertia_includes_radial_tank_distribution():
    wet = build_q4_mass_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    depleted = build_q4_mass_state(normal_remass_t=0.0, protected_water_t=50.0, launch_docked=True)
    assert wet["centroid_inertia_diag_kg_m2"][0] > depleted["centroid_inertia_diag_kg_m2"][0]


def test_state_explicitly_refuses_final_intrinsic_tensor_claim():
    out = build_q4_mass_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
    assert out["model_quality"] == "CENTROID_PLUS_KNOWN_RADIAL_FLUID_DISTRIBUTION"
    assert out["final_intrinsic_tensor_available"] is False
