import unittest
class RequiredAuthoritySurfaces(unittest.TestCase):
 def test_required_surface_count(self):
  required=('runtime/src/loom_gis.py','runtime/src/loom_navigator.py','data/LOOM_2226.sqlite3','data/LOOM_2226_CIVSTATE.sqlite3','campaign/LOOM_STATE_V1.json','campaign/LOOM_CAMPAIGN_HISTORY.jsonl.gz');self.assertEqual(len(required),6)
if __name__=='__main__':unittest.main()
