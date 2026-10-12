"""Pinned off-state isolation against live main 0ae8dfd1, not self-comparison."""
import hashlib
import json
import os
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

from simulation.offworld_mvp.build8.route1_gate1 import run_gate1
from simulation.offworld_mvp.build8.route1_gate2 import run_gate2
from simulation.offworld_mvp.build8.nasa_moon_a1 import run as run_nasa_a1
from simulation.offworld_mvp.build8.nasa_moon_a2 import run as run_nasa_a2

GOLD=Path(__file__).with_name('FOLLOWON_PR1_MAIN_BASELINE_0ae8dfd1.json')

def digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),
                   ensure_ascii=True,default=str).encode()
    return hashlib.sha256(raw).hexdigest()

def capture():
    records={}
    for scenario in ('A','B'):
        for share in (D('.10'),D('.25')):
            rows,k=run_gate1(share,scenario=scenario)
            records['gate1:'+scenario+':'+str(share)]={
                'rows_sha256':digest(rows),'fingerprint':k.fingerprint()}
    for share in (D('.10'),D('.25')):
        for cap in (None,0,1,2):
            rows,k=run_gate2(share,carry_cap=cap)
            records['gate2:'+str(share)+':cap='+str(cap)]={
                'rows_sha256':digest(rows),'fingerprint':k.fingerprint()}
        rows,k=run_gate2(share,carry_cap=1,end_year=2035)
        records['gate2:'+str(share)+':cap=1:2035']={
            'rows_sha256':digest(rows),'fingerprint':k.fingerprint()}
    row,earth,moon=run_nasa_a1()
    records['nasa:a1']={'rows_sha256':digest(row),
                        'earth_fingerprint':earth.fingerprint(),
                        'moon_fingerprint':moon.fingerprint(),
                        'result_sha256':digest([(r.activity_id,r.standing.value,r.result_ref)
                            for r in moon.project_study_result_records])}
    for cap in (None,1):
        rows,earth,moon,a2,decision,evidence=run_nasa_a2(cap)
        records['nasa:a2:'+str(cap)]={
            'rows_sha256':digest(rows),'decision_sha256':digest(decision),
            'evidence_sha256':digest(evidence),
            'earth_fingerprint':earth.fingerprint(),
            'a1_fingerprint':moon.fingerprint(),
            'a2_fingerprint':a2.fingerprint()}
    return records

class FollowonOffIsolation(unittest.TestCase):
    def test_off_rows_and_fingerprints_identical_to_prechange_main(self):
        golden=json.loads(GOLD.read_text())
        self.assertEqual(golden['base_main_sha'],
            '0ae8dfd17cc6986347c98f8ed1a7c74bd2c52dc8')
        self.assertEqual(capture(),golden['records'])

if __name__=='__main__':
    if sys.argv[1:]==['--capture']:
        print(json.dumps({'base_main_sha':
            '0ae8dfd17cc6986347c98f8ed1a7c74bd2c52dc8',
            'records':capture()},sort_keys=True,indent=2))
    else:
        unittest.main()
