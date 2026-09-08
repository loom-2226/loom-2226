from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "qualification" / "synthesis" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


rg = load("requirement_graph")
ic = load("industrial_context")
cs = load("component_selection")
de = load("design_evidence")


class RequirementGraphTests(unittest.TestCase):
    def units(self):
        return (
            rg.UnitSpec("kg", "MASS", "kg", 1.0),
            rg.UnitSpec("t", "MASS", "t", 1000.0),
            rg.UnitSpec("m", "LENGTH", "m", 1.0),
        )

    def test_graph_is_deterministic_and_multi_input_provenance_ready(self):
        nodes = (
            rg.RequirementNode("cargo_mass", 2.0, "t", "MIN", "QUALIFICATION_ONLY", "REQ:CARGO"),
            rg.RequirementNode("crew", 8.0, "kg", "EXACT", "QUALIFICATION_ONLY", "REQ:CREW_TEST"),
            rg.RequirementNode("derived_load", 2008.0, "kg", "MIN", "QUALIFICATION_ONLY", "RULE:R1"),
        )
        edge = rg.RequirementEdge("E1", ("cargo_mass", "crew"), "derived_load", "RULE:R1", "QUALIFICATION_ONLY", "RULE:R1")
        a = rg.build_requirement_graph(nodes, edges=(edge,), units=self.units())
        b = rg.build_requirement_graph(tuple(reversed(nodes)), edges=(edge,), units=tuple(reversed(self.units())))
        self.assertEqual(a.graph_hash, b.graph_hash)

    def test_dimension_mismatch_fails_closed(self):
        with self.assertRaises(rg.RequirementGraphError):
            rg.convert_value(1.0, self.units()[0], self.units()[2])

    def test_cycle_fails_closed(self):
        nodes = (
            rg.RequirementNode("A", 1, "kg", "EXACT", "Q", "P"),
            rg.RequirementNode("B", 1, "kg", "EXACT", "Q", "P"),
        )
        edges = (
            rg.RequirementEdge("E1", ("A",), "B", "R1", "Q", "P"),
            rg.RequirementEdge("E2", ("B",), "A", "R2", "Q", "P"),
        )
        with self.assertRaises(rg.RequirementGraphError):
            rg.build_requirement_graph(nodes, edges=edges, units=self.units())


class IndustrialContextTests(unittest.TestCase):
    def test_context_hash_stable_under_input_order(self):
        a = ic.build_industrial_context(
            context_id="CERES_YARD_2226", context_date="2226-01-01",
            supplier_component_ids=("B", "A"), prohibited_component_ids=("Z",),
            economic_constraints=("LABOR_EXPENSIVE", "TITANIUM_SCARCE"),
            provenance_refs=("P2", "P1"),
        )
        b = ic.build_industrial_context(
            context_id="CERES_YARD_2226", context_date="2226-01-01",
            supplier_component_ids=("A", "B"), prohibited_component_ids=("Z",),
            economic_constraints=("TITANIUM_SCARCE", "LABOR_EXPENSIVE"),
            provenance_refs=("P1", "P2"),
        )
        self.assertEqual(a.context_hash, b.context_hash)

    def test_supplied_and_prohibited_overlap_fails(self):
        with self.assertRaises(ic.IndustrialContextError):
            ic.build_industrial_context(context_id="X", context_date="2226", supplier_component_ids=("A",), prohibited_component_ids=("A",))


class ComponentSelectionTests(unittest.TestCase):
    def catalog(self):
        return (
            cs.ComponentCatalogEntry("DOCK_A", "DOCK", ("DOCKING",), (), (), (), "QUALIFICATION_ONLY", "CAT:A"),
            cs.ComponentCatalogEntry("DOCK_B", "DOCK", ("DOCKING",), (), (), (), "QUALIFICATION_ONLY", "CAT:B"),
            cs.ComponentCatalogEntry("LANDER_OPEN", "LANDER", ("PLANETARY_LANDING",), (), (), (), "OPEN", "CAT:OPEN"),
        )

    def test_selection_is_deterministic(self):
        result = cs.select_components(required_capabilities=("DOCKING",), catalog=self.catalog(), available_component_ids=("DOCK_B", "DOCK_A"))
        self.assertEqual(result.selection_status, "PASS")
        self.assertEqual(result.selected_component_ids, ("DOCK_A",))

    def test_open_component_does_not_satisfy_capability(self):
        result = cs.select_components(required_capabilities=("PLANETARY_LANDING",), catalog=self.catalog(), available_component_ids=("LANDER_OPEN",))
        self.assertEqual(result.selection_status, "INFEASIBLE")
        self.assertIn("NO_ADMITTED_AVAILABLE_COMPONENT:PLANETARY_LANDING", result.infeasibility_reasons)


class EvidencePackageTests(unittest.TestCase):
    def test_evidence_package_preserves_authority_firewall(self):
        finding = de.EvidenceFinding("H1", "PACKAGING", "PASS", "0 collisions", "EVAL:H1", "QUALIFICATION_ONLY")
        row = de.build_evidence_package(
            candidate_id="C1", requirements_hash="R", institution_context_hash="I", industrial_context_hash="X",
            evaluation_hash="E", selected_component_ids=("DOCK_A",), hard_constraint_findings=(finding,),
            open_items=("FULL_INERTIA",), provenance_refs=("P",),
        )
        self.assertFalse(row.flight_dynamics_authority)
        self.assertFalse(row.canon_changed)
        self.assertFalse(row.production_shipclasses_changed)
        self.assertEqual(row.open_items, ("FULL_INERTIA",))

    def test_evidence_hash_stable_under_order(self):
        kwargs = dict(candidate_id="C1", requirements_hash="R", institution_context_hash="I", industrial_context_hash="X", evaluation_hash="E")
        a = de.build_evidence_package(**kwargs, selected_component_ids=("B", "A"), open_items=("O2", "O1"), provenance_refs=("P2", "P1"))
        b = de.build_evidence_package(**kwargs, selected_component_ids=("A", "B"), open_items=("O1", "O2"), provenance_refs=("P1", "P2"))
        self.assertEqual(a.package_hash, b.package_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
