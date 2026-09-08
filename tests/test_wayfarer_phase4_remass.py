from __future__ import annotations

import importlib.util
import math
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
SRC = ROOT / "src"
for path in (str(SYNTH), str(SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

from design_ledger import build_wayfarer_phase1_ledger  # noqa: E402
import shipyard_migrate  # noqa: E402
import shipyard_phase3  # noqa: E402
import shipyard_phase4_remass as phase4  # noqa: E402


def test_remass_sizing_kernel_is_deterministic_and_explicit() -> None:
    inp = phase4.RemassTankSizingInput(
        remass_mass_kg=62_500.0,
        remass_density_kg_m3=1000.0,
        ullage_fraction=0.05,
        internal_diameter_m=2.8,
        external_diameter_m=3.0,
        axial_end_allowance_m=0.4,
        pressure_temperature_state="TEST_FIXTURE_EXPLICIT_STATE",
        tankage_fraction_semantics="NOT_USED_FOR_VOLUME_SIZING_EXPLICITLY_DECLARED",
        geometry_rule="CYLINDER_X_EQUIVALENT_WITH_EXPLICIT_INTERNAL_DIAMETER_AND_END_ALLOWANCE",
    )
    a = phase4.evaluate_remass_tank(inp)
    b = phase4.evaluate_remass_tank(inp)
    assert a == b
    assert math.isclose(a.fluid_volume_m3, 62.5, rel_tol=0, abs_tol=1e-12)
    assert a.external_envelope_diameter_m == 3.0
    assert a.external_envelope_length_m > a.internal_cylinder_length_m
    assert a.authority_status == phase4.MODEL_AUTHORITY
    assert not a.flight_dynamics_authority
    assert not a.canon_changed
    assert not a.production_shipclasses_changed


def test_remass_sizing_kernel_rejects_unresolved_tankage_semantics() -> None:
    inp = phase4.RemassTankSizingInput(
        remass_mass_kg=62_500.0,
        remass_density_kg_m3=1000.0,
        ullage_fraction=0.05,
        internal_diameter_m=2.8,
        external_diameter_m=3.0,
        axial_end_allowance_m=0.4,
        pressure_temperature_state="TEST_FIXTURE_EXPLICIT_STATE",
        tankage_fraction_semantics="0.10",
        geometry_rule="CYLINDER_X_EQUIVALENT_WITH_EXPLICIT_INTERNAL_DIAMETER_AND_END_ALLOWANCE",
    )
    try:
        phase4.evaluate_remass_tank(inp)
    except RuntimeError as exc:
        assert "tankage_fraction semantics" in str(exc)
    else:
        raise AssertionError("model silently reinterpreted tankage_fraction")


def test_phase4_migration_adds_model_but_admits_no_live_envelope(tmp_path: Path) -> None:
    db = tmp_path / "shipyard.sqlite3"
    build_wayfarer_phase1_ledger(db)
    shipyard_migrate.apply_phase2(db)
    shipyard_phase3.apply_phase3(db)
    result = phase4.apply_phase4(db)
    assert result["model_fidelity"] == "L0_ANALYTIC"
    assert result["remass_tank_count"] == 4
    assert result["admitted_support_input_count"] == 12
    assert result["blocked_attempt_count"] == 4
    assert result["executed_attempt_count"] == 0
    assert result["remaining_open_count"] == 15
    assert result["spatial_effect"] == "NONE_BLOCKED_NO_ENVELOPE_ADMITTED"
    assert not result["canon_changed"]
    assert not result["production_shipclasses_changed"]
    assert not result["flight_dynamics_authority"]

    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM discipline_model").fetchone()[0] == 1
        assert con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0] == 12
        assert con.execute("SELECT COUNT(*) FROM discipline_execution_attempt").fetchone()[0] == 4
        assert con.execute("SELECT COUNT(*) FROM discipline_execution_attempt WHERE result_json IS NOT NULL").fetchone()[0] == 0
        state = con.execute("SELECT state_json FROM design_state WHERE state_kind='PHASE4_REMASS_SIZING_STATE'").fetchone()[0]
        assert 'NONE_BLOCKED_NO_ENVELOPE_ADMITTED' in state
    finally:
        con.close()

    again = phase4.apply_phase4(db)
    assert again["already_applied"] is True
    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM discipline_execution_attempt").fetchone()[0] == 4
    finally:
        con.close()
