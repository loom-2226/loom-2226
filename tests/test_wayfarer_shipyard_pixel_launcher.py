from __future__ import annotations

import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "deploy" / "android" / "LOOM_Computational_Shipyard.py"
spec = importlib.util.spec_from_file_location("loom_shipyard_pixel", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class ShipyardPixelLauncherTests(unittest.TestCase):
    def make_ledger(self, root: Path) -> Path:
        path = root / "wayfarer_phase1_design_ledger.sqlite3"
        con = sqlite3.connect(path)
        con.executescript("""
        CREATE TABLE design_run(run_id TEXT PRIMARY KEY,created_at TEXT,seed INTEGER,status_json TEXT,authority_status TEXT);
        CREATE TABLE design_state(state_id TEXT PRIMARY KEY,run_id TEXT,candidate_id TEXT,parent_state_id TEXT,state_kind TEXT,state_hash TEXT,state_json TEXT,provenance_json TEXT);
        CREATE TABLE discipline_result(result_id TEXT PRIMARY KEY,state_id TEXT,discipline_id TEXT,model_id TEXT,model_version TEXT,fidelity_class TEXT,assumptions_hash TEXT,input_hash TEXT,result_hash TEXT,result_status TEXT,summary_json TEXT,provenance_json TEXT,authority_status TEXT);
        CREATE TABLE dependency_graph(graph_id TEXT PRIMARY KEY,state_id TEXT,graph_hash TEXT,graph_json TEXT,coupled_physics_status TEXT,authority_status TEXT);
        CREATE TABLE derived_artifact(artifact_id TEXT PRIMARY KEY,state_id TEXT,artifact_kind TEXT,artifact_hash TEXT,authority_status TEXT,provenance_json TEXT);
        """)
        state_json='{"structure":{"qualification_status":"NOT_STRUCTURALLY_QUALIFIED"},"packaging":{"open_items":["NO_ADMITTED_VOLUME::hab"]}}'
        graph_json='{"graph_id":"G","coupled_physics_status":"OPEN_NO_COUPLED_MDAO_SOLVE_ADMITTED_v0.1","edges":[{"edge_id":"E","source_node_id":"A","target_node_id":"B","quantity":"thermal feedback","status":"OPEN"}]}'
        con.execute("INSERT INTO design_run VALUES('R','2026-09-08T00:00:00Z',2226,'[]','DESIGN_HISTORY_EVIDENCE_ONLY')")
        con.execute("INSERT INTO design_state VALUES('S','R','CAND-X',NULL,'GOVERNED_SYNTHESIS','abc',?, '[]')",(state_json,))
        con.execute("INSERT INTO discipline_result VALUES('D','S','WAYFARER_S1_LAYOUT','solver','0.1','L1_DETERMINISTIC_REDUCED_ORDER','a','b','c','PASS','{}','[]','DECLARED_DISCIPLINE_EVIDENCE_ONLY')")
        con.execute("INSERT INTO dependency_graph VALUES('G','S','g',?,'OPEN_NO_COUPLED_MDAO_SOLVE_ADMITTED_v0.1','DEPENDENCY_DECLARATION_ONLY')",(graph_json,))
        con.commit(); con.close(); return path

    def test_activation_and_read_only_inspection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=self.make_ledger(root)
            old=os.environ.get("LOOM_SHIPYARD_HOME")
            os.environ["LOOM_SHIPYARD_HOME"]=str(root/"runtime")
            try:
                active=mod.activate_baseline(source)
                self.assertTrue(active.is_file())
                state=mod.current_design(active)
                self.assertEqual(state["candidate_id"],"CAND-X")
                self.assertEqual(state["structure_qualification"],"NOT_STRUCTURALLY_QUALIFIED")
                self.assertEqual(state["disciplines"][0]["fidelity_class"],"L1_DETERMINISTIC_REDUCED_ORDER")
                self.assertIn("NO_ADMITTED_VOLUME::hab",mod.open_items(active))
                self.assertTrue(any(x.startswith("DEPENDENCY::E::") for x in mod.open_items(active)))
            finally:
                if old is None: os.environ.pop("LOOM_SHIPYARD_HOME",None)
                else: os.environ["LOOM_SHIPYARD_HOME"]=old

    def test_invalid_sqlite_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.sqlite3"; p.write_bytes(b"not sqlite")
            self.assertFalse(mod._valid_ledger(p))

    def test_status_mode_is_noninteractive(self):
        self.assertEqual(mod.main(["--status"]),0)

    def test_server_binding_constant_is_loopback_only(self):
        text=MOD_PATH.read_text(encoding="utf-8")
        self.assertIn('ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)',text)
        self.assertNotIn('ThreadingHTTPServer(("0.0.0.0"',text)


if __name__ == "__main__":
    unittest.main()
