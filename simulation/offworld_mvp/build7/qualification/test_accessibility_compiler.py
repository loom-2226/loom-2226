"""Focused checks for the offline qualified-SPK transfer screen."""
import ast
import inspect
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from simulation.offworld_mvp.build7 import compile_solar_accessibility as compiler


class AccessibilityCompilerTests(unittest.TestCase):
    def test_compiler_has_no_generated_world_dependency(self):
        source = inspect.getsource(compiler)
        tree = ast.parse(source)
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names}
        imports.update(node.module or '' for node in ast.walk(tree)
                       if isinstance(node, ast.ImportFrom))
        self.assertFalse(any('generated_world' in name for name in imports))
        self.assertNotIn('world', inspect.signature(compiler.compile_screen).parameters)

    def test_all_derivable_records_have_qualified_direct_source(self):
        sources, _ = compiler._source_index(Path('/assets-not-read-by-metadata-test'))
        authority = json.loads(compiler.INPUT.read_text())
        derivable = [record for record in authority['records']
                     if record['accessibility_status'] == 'DERIVABLE']
        unknown = [record for record in authority['records']
                   if record['accessibility_status'] == 'UNKNOWN']
        self.assertEqual((len(derivable), len(unknown)), (83, 7))
        for record in derivable:
            registry = compiler._registry_for(record, sources)
            self.assertEqual(registry.body_identifier(record['body_id']).identifier_value,
                             record['active_naif_ids'][0])
            for sid, source in registry.sources.items():
                self.assertTrue(source.navigation_grade, (record['body_id'], sid))
                self.assertEqual(source.status, 'QUALIFIED')

    def test_screen_uses_relative_velocity_and_finite_grid(self):
        class FakeAdapter:
            def resolve(self, body_id, epoch):
                if body_id == 'EARTH':
                    return SimpleNamespace(position_km=(149597870.7, 0.0, 0.0),
                                           velocity_km_s=(0.0, 29.78, 0.0))
                return SimpleNamespace(position_km=(0.0, 227939200.0, 0.0),
                                       velocity_km_s=(-24.13, 0.0, 0.0),
                                       provenance={'ephemeris_source_id': 'TEST_PUBLIC_SPK'})
        screen = compiler._screen('TEST_BODY', 2026, FakeAdapter())
        self.assertEqual(screen['accessibility_status'], 'SCREENED')
        self.assertGreater(screen['departure_vinf_km_s'], 0)
        self.assertGreater(screen['arrival_vinf_km_s'], 0)
        self.assertAlmostEqual(screen['transfer_burden_km_s'],
                               screen['departure_vinf_km_s'] + screen['arrival_vinf_km_s'],
                               places=5)
        self.assertIn(screen['sampled_time_of_flight_days'], compiler.TOF_DAYS)
        self.assertEqual(screen['ephemeris_source_ids'], ['TEST_PUBLIC_SPK'])


if __name__ == '__main__':
    unittest.main()
