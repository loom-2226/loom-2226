"""Independent switches, authored precedence and descriptive-only tier admission."""
import json
import unittest
from pathlib import Path
from .capacity_options import descriptive_tier, authored_fallbacks
from .master_cast import actors


class CapacityOptionsTests(unittest.TestCase):
    def test_all_research_rows_match_cast_capabilities(self):
        rows = json.loads(Path(__file__).with_name('capacity_tiers_descriptive.json').read_text())['capabilities']
        ids = {(a['id'], c['category']) for a in actors().values() for c in a['capabilities']}
        self.assertEqual(len(rows), 75)
        self.assertEqual(len({(r['actor_id'], r['category']) for r in rows}), len(rows))
        self.assertEqual({(r['actor_id'], r['category']) for r in rows}, ids)
        self.assertTrue(all(r['basis'] in ('MEASURED','ESTIMATED','AUTHORED_DEFAULT','ANALOGUE') for r in rows))

    def test_independent_opt_in_and_authored_precedence(self):
        name, category = 'ispace', 'LAND'
        self.assertIsNone(descriptive_tier(name, category))
        self.assertEqual(descriptive_tier(name, category, tiers=True)['inference'], 'INFERRED_TIER')
        self.assertEqual(authored_fallbacks(name, category), (None, None))
        self.assertEqual(authored_fallbacks(name, category, slots=True), (None, 1))
        self.assertEqual(authored_fallbacks(name, category, prices=True), ( __import__('decimal').Decimal('3.00'), None))
        self.assertEqual(authored_fallbacks(name, category, slots=True, prices=True,
                                           authored_quote=__import__('decimal').Decimal('1.50'),
                                           authored_slots=2), (__import__('decimal').Decimal('1.50'), 2))
        self.assertEqual(authored_fallbacks('Rocket Lab', 'LAUNCH', prices=True), (None, None))

if __name__ == '__main__': unittest.main()

class YearlySwitchTests(unittest.TestCase):
    def test_default_and_independent_switches_keep_frozen_economics(self):
        from .screened_yearly import run_yearly
        from .test_yearly_acceptance import OPTIONS
        for scenario, options in OPTIONS.items():
            with self.subTest(scenario=scenario):
                base = run_yearly(**options)[2]
                for flags in ({'tiers':True}, {'slots':True}, {'prices':True}):
                    changed = run_yearly(**options, **flags)[2]
                    self.assertEqual([(t.source_account,t.destination_account,t.amount)
                                      for t in base.state.transactions],
                                     [(t.source_account,t.destination_account,t.amount)
                                      for t in changed.state.transactions])
                    if not flags.get('tiers'):
                        self.assertEqual(base.fingerprint(),changed.fingerprint())
