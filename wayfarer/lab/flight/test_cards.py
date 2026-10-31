"""Propulsion card tests. ALL bodies. ALL sponsors. 2026-2226."""
import json,unittest
from pathlib import Path
from cards import resolve,load_cards
from flightlab import run,source_hash
R=Path(__file__).resolve().parent
def L(p):return json.loads((R/p).read_text())
class CardTests(unittest.TestCase):
    def test_cards_load_one_kind_per_folder(self):
        c=load_cards();self.assertTrue({'rcs-25kN-rev7','torch-e1-working-card','metric-rev7-envelope'}<=set(c))
    def test_card_config_resolves_to_legacy(self):
        a,_=resolve(L('configs/wayfarer_cards.json'));b=L('configs/wayfarer.json')
        a.pop('name');b.pop('name');self.assertEqual(source_hash(a),source_hash(b))
    def test_config_without_cards_unchanged(self):
        s=L('configs/scout.json');self.assertEqual(resolve(s),(s,[]))
    def test_card_cannot_be_overridden(self):
        s=L('configs/wayfarer_cards.json');s['rcs'][0]['max_N']=1.0
        with self.assertRaises(ValueError):resolve(s)
    def test_wrong_kind_rejected(self):
        s=L('configs/wayfarer_cards.json');s['rcs'][0]['card']='torch-e1-working-card'
        with self.assertRaises(ValueError):resolve(s)
    def test_water_rcs_fuel_scales_with_exhaust_velocity(self):
        e={'name':'t','phases':[{'kind':'rcs_turn','duration_s':40,'axis':'pitch','angle_deg':180}],'checks':{}}
        used={}
        for ve in (1000,1960):
            s,_=resolve(L(f'configs/wayfarer_rcs_water{ve}.json'))
            r=run(s,e,dt=.1,sample_s=10.);used[ve]=r['metrics']['total_propellant_used_kg']
            self.assertGreater(used[ve],0);self.assertEqual(r['warnings'],[])
        self.assertAlmostEqual(used[1000]/used[1960],1.96,delta=.01)
if __name__=='__main__':unittest.main()
