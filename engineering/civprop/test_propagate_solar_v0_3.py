import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engineering.civprop.propagate_solar_v0_3 import canonical_sha, ledger_sizes, write_output
class SolarPropagateV03Tests(unittest.TestCase):
 def test_hash_deterministic(self): self.assertEqual(canonical_sha({'b':2,'a':1}),canonical_sha({'a':1,'b':2}))
 def test_hash_changes(self): self.assertNotEqual(canonical_sha({'a':1}),canonical_sha({'a':2}))

class StreamingEquivalenceTests(unittest.TestCase):
 def payloads(self):
  return [None, {}, [], {'unicode': 'Luna \u263e \U0001f680', 'escapes': '\n\t"\\'},
          {'floats': [-0.0, 1e-30, 1e30, 1.2345678901234567],
           'nested': [{'b': True, 'a': None}, [1, 2, False]]},
          {'ledger': [{'year': year, 'value': year / 7} for year in range(2026, 2227)]}]
 def test_streaming_hash_matches_original_dumps_bytes(self):
  for payload in self.payloads():
   with self.subTest(payload_type=type(payload).__name__):
    expected=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    self.assertEqual(canonical_sha(payload),expected)
 def test_streaming_file_matches_original_pretty_dumps_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/'output.json'
   for payload in self.payloads():
    expected=(json.dumps(payload,indent=2,sort_keys=True)+'\n').encode('utf-8')
    write_output(path,payload)
    self.assertEqual(path.read_bytes(),expected)
    self.assertEqual(json.loads(path.read_text(encoding='utf-8')),payload)
 def test_streaming_helpers_do_not_call_whole_payload_dumps(self):
  with tempfile.TemporaryDirectory() as td, patch('json.dumps',side_effect=AssertionError('whole-payload serialization')):
   canonical_sha({'ledger':[{'x':1}, {'x':2}]})
   write_output(Path(td)/'output.json',{'ledger':[{'x':1}, {'x':2}]})
 def test_sizes_are_sorted_top_level_lists_only_without_mutation(self):
  payload={'z':[], 'a':[1,2], 'nested':{'ledger':[3]}, 'tuple':(1,2), 'text':'abc'}
  before=canonical_sha(payload)
  sizes=ledger_sizes(payload)
  self.assertEqual(list(sizes.items()),[('a',2),('z',0)])
  self.assertEqual(canonical_sha(payload),before)
if __name__=='__main__': unittest.main()
