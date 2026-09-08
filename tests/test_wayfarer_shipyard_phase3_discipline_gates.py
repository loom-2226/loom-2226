from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
SRC = ROOT / "src"
for path in (SYNTH, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from design_ledger import build_wayfarer_phase1_ledger
import shipyard_migrate
import shipyard_phase3


class ShipyardPhase3DisciplineGateTests(unittest.TestCase):
    def _build(self, root: Path) -> Path:
        db = root / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        phase2 = shipyard_migrate.apply_phase2(db)
        self.assertFalse(phase2["already_applied"])
        return db

    def test_phase3_persists_contracts_and_fail_closed_gates(self):
        with tempfile.TemporaryDirectory() as td:
            db = self._build(Path(td))
            result = shipyard_phase3.apply_phase3(db)
            self.assertFalse(result["already_applied"])
            self.assertEqual(result["discipline_contract_count"], 9)
            self.assertEqual(result["ready_contract_count"], 0)
            self.assertEqual(result["blocked_contract_count"], 9)
            self.assertEqual(result["workflow_gate_count"], 4)
            self.assertEqual(result["satisfied_gate_count"], 1)
            self.assertEqual(result["blocked_gate_count"], 3)
            self.assertEqual(result["remaining_open_count"], 15)
            self.assertEqual(result["spatial_effect"], "NONE_NO_ENVELOPE_ADMITTED")
            self.assertFalse(result["canon_changed"])
            self.assertFalse(result["production_shipclasses_changed"])
            self.assertFalse(result["flight_dynamics_authority"])

            con = sqlite3.connect(db)
            con.row_factory = sqlite3.Row
            try:
                state = con.execute("SELECT state_kind,state_json FROM design_state WHERE state_id=?", (result["state_id"],)).fetchone()
                self.assertEqual(state["state_kind"], "PHASE3_DISCIPLINE_GATE_STATE")
                payload = json.loads(state["state_json"])
                self.assertEqual(payload["phase3_spatial_effect"], "NONE_NO_ENVELOPE_ADMITTED")
                self.assertEqual(len(payload["phase3_discipline_contracts"]), 9)
                self.assertEqual(len(payload["phase3_workflow_gates"]), 4)
                self.assertEqual(len(payload["packaging"]["open_items"]), 15)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM discipline_contract").fetchone()[0], 9)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM workflow_gate").fetchone()[0], 4)
            finally:
                con.close()

    def test_phase3_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            db = self._build(Path(td))
            first = shipyard_phase3.apply_phase3(db)
            second = shipyard_phase3.apply_phase3(db)
            self.assertFalse(first["already_applied"])
            self.assertTrue(second["already_applied"])
            self.assertEqual(first["state_id"], second["state_id"])
            self.assertEqual(first["state_hash"], second["state_hash"])
            con = sqlite3.connect(db)
            try:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM discipline_contract").fetchone()[0], 9)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM workflow_gate").fetchone()[0], 4)
            finally:
                con.close()

    def test_contract_cannot_claim_result_or_authority(self):
        row = shipyard_phase3.DisciplineContract(
            version=shipyard_phase3.VERSION,
            contract_id="C",
            state_id="S",
            source_id="X",
            discipline_id="D",
            model_id="M",
            model_version="OPEN",
            fidelity_class="OPEN",
            required_inputs=("a",),
            admitted_inputs=(),
            open_inputs=("a",),
            execution_status="BLOCKED_MISSING_ADMITTED_INPUTS",
            result_admission_status="NO_RESULT_ADMITTED",
        )
        shipyard_phase3.validate_contract(row)
        with self.assertRaises(RuntimeError):
            shipyard_phase3.validate_contract(replace(row, result_admission_status="PASS"))
        with self.assertRaises(RuntimeError):
            shipyard_phase3.validate_contract(replace(row, authority_status="PHYSICAL_AUTHORITY"))

    def test_gate_status_must_match_blockers(self):
        gate = shipyard_phase3.WorkflowGate(
            version=shipyard_phase3.VERSION,
            gate_id="G",
            state_id="S",
            phase_name="DISCIPLINE_INPUT_ADMISSION",
            gate_status="BLOCKED",
            blocking_items=("x",),
            evidence_refs=("e",),
        )
        shipyard_phase3.validate_gate(gate)
        with self.assertRaises(RuntimeError):
            shipyard_phase3.validate_gate(replace(gate, gate_status="SATISFIED"))


if __name__ == "__main__":
    unittest.main()
