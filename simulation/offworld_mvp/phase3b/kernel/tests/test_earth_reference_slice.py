import unittest
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'build6/qualification'))
from build6d_fixture import make_kernel,policy_inputs,system_epoch,run_case
from offworld_kernel.boundary import *
from offworld_kernel.causal_trace import *
from offworld_kernel.kernel import InvariantError
from offworld_kernel.policy import build_decision_snapshot,SnapshotFact


import json,tempfile
from hashlib import sha256
from build6d_fixture import EARTH_PATH,EARTH_PARENT
class EarthReferenceTests(unittest.TestCase):
    def test_E01_full_byte_membership_and_immutability(self):
        before=sha256(EARTH_PATH.read_bytes()).hexdigest();v,h=load_earth_assertions(EARTH_PATH,parent_root=EARTH_PARENT)
        self.assertEqual(len(v),42);self.assertEqual(h,before);self.assertEqual(sha256(EARTH_PATH.read_bytes()).hexdigest(),before)
        doc=json.loads(EARTH_PATH.read_text());doc['rows'][0]['investment']='0'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'slice.json';p.write_text(json.dumps(doc))
            with self.assertRaisesRegex(InvariantError,'REFERENCE'):load_earth_assertions(p,parent_root=EARTH_PARENT)
    def test_E02_2030_2031_temporal_rule(self):
        doc=json.loads(EARTH_PATH.read_text());rows={r['year']:r for r in doc['rows']}
        self.assertTrue(rows[2030]['artifact'].startswith('stage_2026_2031'));self.assertTrue(rows[2031]['artifact'].startswith('stage_2031_2060'))
        doc['rows'][5]['artifact']=doc['rows'][0]['artifact']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'slice.json';p.write_text(json.dumps(doc))
            with self.assertRaisesRegex(InvariantError,'temporal'):load_earth_assertions(p,parent_root=EARTH_PARENT)
    def test_E03_coverage_gap_blocks(self):
        k,_=make_kernel();q=ConsumptionRequest('future','GENESIS','EARTH_REFERENCE','USA','investment','COUNTRY:USA','CALENDAR_YEAR','2101','2101','REAL','','GOVERNANCE','','ADMITTED','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR','EARTH_REFERENCE')
        v,_=admit_for_use(k,q);self.assertNotEqual(v.value_state,FactState.KNOWN)
    def test_E04_projection_not_cash(self):
        k,_=make_kernel();q=ConsumptionRequest('cash','GENESIS','EARTH_REFERENCE','USA','investment','COUNTRY:USA','CALENDAR_YEAR','2026','2026','REAL','','GOVERNANCE','','ADMITTED','MODEL_CURRENCY','EARTH_REFERENCE')
        with self.assertRaises(InvariantError):admit_for_use(k,q)
    def test_E05_parent_sources_pinned(self):
        doc=json.loads(EARTH_PATH.read_text())
        for src in doc['sources']:self.assertEqual(sha256((EARTH_PARENT/src['artifact']).read_bytes()).hexdigest(),src['sha256'])
    def test_E06_absent_flags_not_false_zero(self):
        v,_=load_earth_assertions(EARTH_PATH,parent_root=EARTH_PARENT);self.assertEqual(dict(v[0].exception_flags)['exception_flags'],'NOT_SUPPLIED');self.assertEqual(v[0].proposition_kind,'MODEL_PROJECTION')
    def test_E07_finite_cohort_no_national_population_injection(self):
        k,_=make_kernel();self.assertEqual(k.population.total(),1000);self.assertNotEqual(k.population.total(),348178045)
