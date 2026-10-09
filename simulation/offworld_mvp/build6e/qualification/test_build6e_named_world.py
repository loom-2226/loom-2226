import copy
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / 'simulation/offworld_mvp/phase3b/kernel'), str(ROOT / 'src'),
                str(ROOT / 'simulation/offworld_mvp/build6e')]
from loom_world_authority import store
from named_world import (NamedWorldBlocked, compile_world_rows, load_manifest)


class NamedWorldContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load_manifest()
        cls.body = store.stable_uuid('BODY', 'LOOM_BODY_V1', 'MOON', 'IDENTITY_V1')
        cls.parent = store.stable_uuid('LOCATION', 'LOOM_LOCATION_V1',
            store.length_prefixed('MOON', 'CABEU').decode(), 'IDENTITY_V1')
        cls.site = store.stable_uuid('AUTHORED_LOCATION', 'LOOM_BUILD6E_NAMED_WORLD_V1',
            store.length_prefixed('MOON', 'B6E_MOON_CABEU_SITE_01').decode(), 'IDENTITY_V1')
        cls.feature = store.stable_uuid('AUTHORED_LOCATION', 'LOOM_BUILD6E_NAMED_WORLD_V1',
            store.length_prefixed('MOON', 'B6E_MOON_CABEU_FEATURE_01').decode(), 'IDENTITY_V1')
        cls.admission = store.stable_uuid('SCIENCE_ADMISSION', 'LOOM_WORLD_AUTHORITY_V1',
            store.length_prefixed(cls.doc['accepted_source']['assertion_id'],
                cls.doc['fixture_admission']['use_contract_ref'], '1').decode(), 'fixture')
        cls.source = {
            'body_id': cls.body, 'location_id': cls.parent,
            'support_id': cls.doc['accepted_source']['support_id'],
            'admission_id': cls.admission, 'scope_kind': 'LOCAL_SITE',
            'extrapolation_warrant_id': None, 'initial_standing': 'CANDIDATE',
            'standing': 'ADMITTED',
        }

    def compile(self, doc, variant, seed=None):
        return compile_world_rows(doc, self.source, variant, site_id=self.site,
            feature_id=self.feature, parent_id=self.parent, world_seed=seed)

    def test_fixed_manifest_is_exactly_the_cabeus_local_site_profile(self):
        self.assertEqual(self.doc['metadata']['parent_required_kind'], 'SITE')
        self.assertEqual(self.doc['metadata']['parent_required_original_region_type'], 'LOCAL_SITE')
        self.assertEqual(self.doc['accepted_source']['scope'], 'LOCAL_SITE')
        self.assertEqual(self.doc['accepted_source']['support_location_key'], 'CABEU')
        self.assertEqual(self.doc['accepted_source']['initial_standing'], 'CANDIDATE')
        self.assertEqual(self.doc['fixture_admission']['use_contract_ref'], 'BUILD6E_SCOPED_AUTHORING_INPUT_V1')

    def test_all_variants_keep_resource_state_typed_and_reserve_unknown(self):
        for variant, expected in (('NULL', Decimal(0)), ('SPARSE', Decimal(3)), ('RICH', Decimal(20))):
            with self.subTest(variant=variant):
                binding, rows = self.compile(self.doc, variant)
                states = [v for table, v in rows if table == 'wa_world.hidden_state']
                by_prop = {v['property_code']: v for v in states if v['property_code'].startswith('R_')}
                self.assertEqual(by_prop['R_IN_SITU']['numeric_value'], expected)
                self.assertEqual(by_prop['R_ACCESSIBLE']['numeric_value'], expected)
                self.assertEqual(by_prop['R_RECOVERABLE']['numeric_value'], expected)
                self.assertEqual(by_prop['R_RESERVE']['value_state'], 'UNKNOWN')
                self.assertIsNone(by_prop['R_RESERVE']['numeric_value'])
                self.assertEqual(binding.support_id, self.doc['accepted_source']['support_id'])
                deposit = next(v for t, v in rows if t == 'wa_world.deposit')
                self.assertEqual(deposit['concentration_state'], 'UNKNOWN')
                self.assertIsNone(deposit['concentration_value'])

    def test_nominal_measurement_stays_at_cabeus_support_and_local_grade_unknown(self):
        _, rows = self.compile(self.doc, 'RICH')
        known = [v for t, v in rows if t == 'wa_world.hidden_state'
                 and v['property_code'] == 'WATER_ICE_WT_PERCENT' and v['value_state'] == 'KNOWN']
        unknown = [v for t, v in rows if t == 'wa_world.hidden_state'
                   and v['property_code'] == 'WATER_ICE_WT_PERCENT' and v['value_state'] == 'UNKNOWN']
        constraint = next(v for t, v in rows if t == 'wa_world.constraint_binding')
        self.assertEqual(len(known), 1)
        self.assertEqual(known[0]['location_id'], self.parent)
        self.assertEqual(known[0]['numeric_value'], Decimal('5.6'))
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]['location_id'], self.feature)
        self.assertEqual(constraint['target_support_id'], self.doc['accepted_source']['support_id'])
        self.assertIsNone(constraint['extrapolation_warrant_id'])

    def test_policy_seed_cannot_change_world_identity_or_bytes(self):
        changed = copy.deepcopy(self.doc)
        changed['world_generation']['policy_seed'] = 'independent-policy-seed-control'
        self.assertEqual(self.compile(self.doc, 'SPARSE'), self.compile(changed, 'SPARSE'))

    def test_exact_repeat_is_byte_and_identity_stable(self):
        first = self.compile(self.doc, 'RICH', seed='repeat-control-seed')
        second = self.compile(self.doc, 'RICH', seed='repeat-control-seed')
        self.assertEqual(first, second)

    def test_unregistered_variant_and_cross_support_are_blocked(self):
        with self.assertRaisesRegex(NamedWorldBlocked, 'BLOCKED_WORLD_VARIANT'):
            self.compile(self.doc, 'UNREGISTERED')
        for key, value in (('support_id', '00000000-0000-0000-0000-000000000001'),
                           ('location_id', '00000000-0000-0000-0000-000000000002')):
            altered = dict(self.source)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(NamedWorldBlocked):
                compile_world_rows(self.doc, altered, 'SPARSE', site_id=self.site,
                    feature_id=self.feature, parent_id=self.parent)

    def test_generation_policy_rejects_missing_and_extra_fields(self):
        for mode in ('missing', 'extra', 'vector-extra', 'vector-missing'):
            altered = copy.deepcopy(self.doc)
            generation = altered['world_generation']
            if mode == 'missing':
                generation.pop('policy_version')
            elif mode == 'extra':
                generation['unreviewed_policy'] = 'MUST_NOT_BE_IGNORED'
            elif mode == 'vector-extra':
                generation['scenarios']['SPARSE']['hidden_grade'] = '0.5'
            else:
                generation['scenarios']['RICH'].pop('recoverable')
            expected = ('BLOCKED_GENERATION_VECTOR_FIELDS' if mode.startswith('vector-')
                        else 'BLOCKED_GENERATION_POLICY_FIELDS')
            with self.subTest(mode=mode), self.assertRaisesRegex(NamedWorldBlocked, expected):
                compile_world_rows(altered, self.source, 'SPARSE', site_id=self.site,
                    feature_id=self.feature, parent_id=self.parent)

    def test_source_lexical_provenance_drift_is_blocked(self):
        for key, value in (('value_lexeme', '99.0'), ('unit_lexeme', 'invented-unit'),
                           ('uncertainty_lexeme', '±99'),
                           ('representativeness', 'BODY_REPRESENTATIVE')):
            altered = copy.deepcopy(self.doc)
            altered['accepted_source'][key] = value
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'altered.json'
                path.write_text(json.dumps(altered))
                with self.subTest(key=key), self.assertRaisesRegex(
                        NamedWorldBlocked, 'BLOCKED_SOURCE_PROVENANCE_OR_SCOPE'):
                    load_manifest(path)

    def test_source_scope_or_candidate_status_drift_blocks(self):
        for key, value in (('scope_kind', 'REGIONAL'), ('initial_standing', 'ADMITTED'),
                           ('standing', 'HOLD'), ('extrapolation_warrant_id', 'unapproved')):
            altered = dict(self.source)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(NamedWorldBlocked):
                compile_world_rows(self.doc, altered, 'SPARSE', site_id=self.site,
                    feature_id=self.feature, parent_id=self.parent)

    def test_governed_habitat_low_case_is_valid_and_insufficient(self):
        protocol=json.loads((ROOT/'simulation/offworld_mvp/build6e/inputs/BUILD6E_QUALIFICATION_V2.json').read_text())
        case=protocol['case_parameters']['HABITAT_LOW']
        self.assertGreater(int(case['habitat_capacity']),0)
        self.assertLess(int(case['habitat_capacity']),int(case['requested_residents']))
        self.assertEqual(protocol['governed_corrections'][0]['id'],'BUILD6E-QUAL-PROTOCOL-CORR-001')
        self.assertFalse(protocol['governed_corrections'][0]['frozen_6d_kernel_modified'])


if __name__ == '__main__':
    unittest.main()
