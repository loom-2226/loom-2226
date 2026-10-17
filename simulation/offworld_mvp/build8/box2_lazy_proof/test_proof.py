"""Narrow non-runtime input and result invariants."""
import json
import unittest
from pathlib import Path
from .proof import dates_for, sha

HERE=Path(__file__).resolve().parent

class ProofInvariants(unittest.TestCase):
    def test_authored_dates(self):
        config=json.loads((HERE/'experiment.json').read_text())
        for year in config['years']:
            dates=dates_for(year,config['sampling'])
            self.assertEqual(dates[0],f'{year}-01-01')
            self.assertEqual(dates[-1],f'{year}-12-31')
            self.assertEqual(len(dates),14)
    def test_report_replays_and_negative_controls(self):
        result=json.loads((HERE/'RESULT.json').read_text())
        self.assertEqual(result['authored_input_sha256'],sha((HERE/'experiment.json').read_bytes()))
        self.assertTrue(result['replay_match'])
        self.assertEqual(len(set(result['replay_hashes'])),1)
        for row in result['scientific_results']['results']:
            if row['body'] in ('ARROKOTH','EUROPA'):
                self.assertFalse(row['eligible_for_award'])
                self.assertIsNone(row['best'])
            if row['eligible_for_award']:
                self.assertGreater(float(row['sponsor_surplus_usd_millions']),0)
if __name__=='__main__':unittest.main()
