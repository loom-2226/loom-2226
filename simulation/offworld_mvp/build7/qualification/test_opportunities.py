"""Increment 2 public opportunity and hidden-truth firewall proofs."""
import ast
from dataclasses import asdict
import inspect
import unittest

from simulation.offworld_mvp.build7 import opportunities
from simulation.offworld_mvp.build7.generated_campaign import (
    _build_kernel, derive_world_mission_candidates, load_config,
)

WORLD = dict(scenario_id='00000000-0000-0000-0000-000000000001',
             scenario_key='SOLAR_WATER_NO_TARGET_TEST', sealed_world_digest='0'*64,
             body_count=90)


class OpportunityTests(unittest.TestCase):
    def test_tiny_visible_fixture_unknown_capability_and_order(self):
        bodies = [dict(semantic_key=key, canonical_name=key.title(), body_class='ASTEROID')
                  for key in ('A', 'B', 'C')]
        rows = [dict(body_id=key, year=2026, accessibility_status=status,
                     method_id='TEST', sampled_departure_utc='2026-01-15T00:00:00Z',
                     sampled_time_of_flight_days=180, departure_vinf_km_s=3.0,
                     arrival_vinf_km_s=4.0, transfer_burden_km_s=burden)
                for key, status, burden in (('A', 'SCREENED', 7.0),
                                            ('B', 'UNKNOWN', None),
                                            ('C', 'SCREENED', 12.0))]
        def derive(bs, rs, caps=('EXPLORE',)):
            return opportunities.derive_mission_candidates(
                actor_id='PUB', capabilities=caps, calendar_year=2026,
                public_bodies=bs, accessibility_rows=rs)
        first = derive(bodies, rows)
        self.assertEqual(first, derive(reversed(bodies), reversed(rows)))
        self.assertEqual([c.destination_body_id for c in first], ['A', 'B', 'C'])
        self.assertEqual(first[1].qualification_state, 'ACCESS_UNKNOWN')
        self.assertIsNone(first[1].transfer_burden_km_s)
        self.assertEqual(first[0].qualification_state, 'PRELIMINARY_COMPARABLE')
        self.assertNotEqual(first[0].transfer_burden_km_s, first[2].transfer_burden_km_s)
        self.assertEqual(derive(bodies, rows, ())[0].qualification_state,
                         'CAPABILITY_UNAVAILABLE')

    def test_full_public_surface_83_screened_7_unknown_without_privilege(self):
        catalog, screen = opportunities.load_visible_inputs()
        candidates = opportunities.derive_mission_candidates(
            actor_id='PUB', capabilities={'EXPLORE'}, calendar_year=2026,
            public_bodies=catalog['bodies'], accessibility_rows=screen['rows'])
        self.assertEqual(len(candidates), 90)
        self.assertEqual(sum(c.accessibility_status == 'SCREENED' for c in candidates), 83)
        unknown = {c.destination_body_id for c in candidates if c.accessibility_status == 'UNKNOWN'}
        self.assertEqual(unknown, {'DACTYL','HYDRA','KERBEROS','NIX','PROTEUS','SELAM','STYX'})
        self.assertEqual(len({c.candidate_id for c in candidates}), 90)
        self.assertTrue(all(c.origin_body_id == 'EARTH' for c in candidates))
        self.assertTrue(all(c.candidate_id.endswith(':'+c.destination_body_id) for c in candidates))
        self.assertTrue(all('GEN_SITE' not in str(asdict(c)) for c in candidates))
        self.assertEqual(candidates, opportunities.derive_mission_candidates(
            actor_id='PUB', capabilities={'EXPLORE'}, calendar_year=2026,
            public_bodies=reversed(catalog['bodies']),
            accessibility_rows=reversed(screen['rows'])))
        burdens = {c.destination_body_id: c.transfer_burden_km_s for c in candidates}
        self.assertNotEqual(burdens['MARS'], burdens['CERES'])
        self.assertNotEqual(burdens['MOON'], burdens['BENNU'])
        for body in ('MARS','MOON','CERES','BENNU','CABEUS'):
            if body in burdens:
                self.assertEqual(next(c.action for c in candidates if c.destination_body_id == body),
                                 opportunities.ACTION)

    def test_hidden_world_counterfactual_and_structural_firewall(self):
        config = load_config()
        first, h1 = _build_kernel(None, config, world_seed='SEED-A', world=WORLD)
        altered = {**WORLD, 'sealed_world_digest': 'f'*64}
        second, h2 = _build_kernel(None, config, world_seed='SEED-B', world=altered)
        a = derive_world_mission_candidates(first, h1, 2026)
        b = derive_world_mission_candidates(second, h2, 2026)
        self.assertEqual(a, b)
        self.assertEqual(first.state.projects, {})
        self.assertEqual(first.colonies, {})
        self.assertEqual(first.population.offworld, {})
        self.assertFalse(any('GEN_SITE' in str(asdict(c)) for c in a))
        source = inspect.getsource(opportunities)
        tree = ast.parse(source)
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names}
        imports.update(node.module or '' for node in ast.walk(tree)
                       if isinstance(node, ast.ImportFrom))
        self.assertFalse(any('generated_world' in name for name in imports))
        self.assertNotIn('world', inspect.signature(opportunities.derive_mission_candidates).parameters)
        self.assertNotIn('deposit', source.lower())


if __name__ == '__main__':
    unittest.main()
