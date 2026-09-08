from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from design_ledger import (  # noqa: E402
    DEPENDENCY_AUTHORITY,
    DISCIPLINE_AUTHORITY,
    DISCIPLINE_RESULT_VERSION,
    DependencyEdge,
    DependencyNode,
    DesignLedgerError,
    DisciplineResult,
    EngineeringDependencyGraph,
    build_wayfarer_phase1_ledger,
    validate_dependency_graph,
    validate_discipline_result,
    wayfarer_dependency_graph,
)


class DesignLedgerTests(unittest.TestCase):
    def test_wayfarer_phase1_ledger_persists_traceable_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.sqlite3"
            result = build_wayfarer_phase1_ledger(path)
            self.assertTrue(path.is_file())
            self.assertEqual(result["counts"], {
                "design_run": 1,
                "design_state": 1,
                "discipline_result": 1,
                "dependency_graph": 1,
                "derived_artifact": 1,
            })
            self.assertEqual(result["coupled_physics_status"], "OPEN_NO_COUPLED_MDAO_SOLVE_ADMITTED_v0.1")
            self.assertFalse(result["flight_dynamics_authority"])
            self.assertFalse(result["canon_changed"])
            self.assertFalse(result["production_shipclasses_changed"])
            con = sqlite3.connect(path)
            try:
                row = con.execute("SELECT fidelity_class,result_status,authority_status FROM discipline_result").fetchone()
                self.assertEqual(row[0], "L1_DETERMINISTIC_REDUCED_ORDER")
                self.assertEqual(row[1], "PASS")
                self.assertEqual(row[2], DISCIPLINE_AUTHORITY)
                graph_json = con.execute("SELECT graph_json FROM dependency_graph").fetchone()[0]
                graph = json.loads(graph_json)
                self.assertEqual(graph["authority_status"], DEPENDENCY_AUTHORITY)
                open_edges = [e for e in graph["edges"] if e["status"] == "OPEN"]
                self.assertGreaterEqual(len(open_edges), 1)
                state_json = con.execute("SELECT state_json FROM design_state").fetchone()[0]
                state = json.loads(state_json)
                self.assertEqual(state["structure"]["qualification_status"], "NOT_STRUCTURALLY_QUALIFIED")
                self.assertEqual(len(state["packaging"]["open_items"]), 15)
            finally:
                con.close()

    def test_replay_is_deterministic_except_file_container(self):
        with tempfile.TemporaryDirectory() as td:
            a = build_wayfarer_phase1_ledger(Path(td) / "a.sqlite3")
            b = build_wayfarer_phase1_ledger(Path(td) / "b.sqlite3")
            for key in ("run_id", "state_id", "state_hash", "discipline_result_id", "dependency_graph_hash", "synthesis_package_hash", "counts"):
                self.assertEqual(a[key], b[key])

    def test_discipline_authority_escalation_fails_closed(self):
        row = DisciplineResult(
            version=DISCIPLINE_RESULT_VERSION,
            result_id="R",
            state_id="S",
            discipline_id="D",
            model_id="M",
            model_version="1",
            fidelity_class="L0_ANALYTIC",
            assumptions_hash="0" * 64,
            input_hash="1" * 64,
            result_hash="2" * 64,
            result_status="MEASURED",
            summary_json="{}",
            provenance_refs=("P",),
            authority_status="PHYSICAL_QUALIFICATION",
        )
        with self.assertRaises(DesignLedgerError):
            validate_discipline_result(row)

    def test_open_dependency_edges_do_not_become_admitted_cycles(self):
        graph = EngineeringDependencyGraph(
            version="LOOM_ENGINEERING_DEPENDENCY_GRAPH_v0.1",
            graph_id="G",
            state_id="S",
            nodes=(DependencyNode("A","X","a"), DependencyNode("B","X","b")),
            edges=(
                DependencyEdge("E1","A","B","q","ADMITTED",("P",)),
                DependencyEdge("E2","B","A","feedback","OPEN",("OPEN",)),
            ),
            coupled_physics_status="OPEN",
        )
        validate_dependency_graph(graph)

    def test_admitted_cycle_fails_closed_until_coupled_solver_contract_exists(self):
        graph = EngineeringDependencyGraph(
            version="LOOM_ENGINEERING_DEPENDENCY_GRAPH_v0.1",
            graph_id="G",
            state_id="S",
            nodes=(DependencyNode("A","X","a"), DependencyNode("B","X","b")),
            edges=(
                DependencyEdge("E1","A","B","q","ADMITTED",("P",)),
                DependencyEdge("E2","B","A","feedback","ADMITTED",("P",)),
            ),
            coupled_physics_status="OPEN",
        )
        with self.assertRaises(DesignLedgerError):
            validate_dependency_graph(graph)

    def test_wayfarer_dependency_graph_preserves_open_coupled_physics(self):
        graph = wayfarer_dependency_graph("STATE")
        self.assertEqual(graph.coupled_physics_status, "OPEN_NO_COUPLED_MDAO_SOLVE_ADMITTED_v0.1")
        self.assertIn("OPEN", {edge.status for edge in graph.edges})
        self.assertEqual(graph.authority_status, DEPENDENCY_AUTHORITY)


if __name__ == "__main__":
    unittest.main()
