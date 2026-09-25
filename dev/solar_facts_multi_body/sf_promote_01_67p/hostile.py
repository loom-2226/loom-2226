"""Hostile promotion checks: semantic laundering must not be representable by replay."""
import json, sqlite3, tempfile
from pathlib import Path
from promote import build

OUT=Path(__file__).with_name('LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_01_67P.sqlite3')

def main():
 with tempfile.TemporaryDirectory() as td:
  p=build(Path(td)/'x.sqlite3'); c=sqlite3.connect(p); c.execute('pragma foreign_keys=on')
  # No coma assertion is loaded as a nucleus property; the full assertion
  # remains scoped in the ledger/notes.
  assert c.execute("select count(*) from fact where property_code like '%NUCLEUS%'").fetchone()[0]==0
  assert c.execute("select count(*) from promotion_assertion where assertion_id='as-volatile-species' and claim_kind='OBSERVATION' and notes like '%coma%'").fetchone()[0]==1
  # No thermal scalar or timeless activity fact is fabricated.
  assert c.execute("select count(*) from fact where property_code='SURFACE_TEMPERATURE'").fetchone()[0]==0
  assert c.execute("select count(*) from observation where observation_id=1 and spatial_resolution_value=15").fetchone()[0]==1
  assert c.execute("select count(*) from activity_fact where notes like '%timeless%'").fetchone()[0]==1
  # Ranges remain ranges, never midpoint values.
  assert c.execute("select value_numeric,value_min,value_max from fact where property_code='POROSITY'").fetchone()==(None,72.0,74.0)
  # Frontier uncertainty is not a physical zero/fact.
  assert c.execute("select count(*) from epistemic_frontier where state_at_cutoff='UNKNOWN' and variable='site_scale_strength'").fetchone()[0]==1
  assert c.execute("select count(*) from fact where property_code='SITE_SCALE_STRENGTH'").fetchone()[0]==0
  # Promotion review cannot silently accept a changed disposition vocabulary.
  try: c.execute("update promotion_review set disposition='CURRENT' where promotion_assertion_id=1")
  except sqlite3.IntegrityError: pass
  else: raise AssertionError('invalid disposition accepted')
  # No preferred facts or Phase-4 writes are present.
  assert c.execute('select count(*) from preferred_fact').fetchone()[0]==0
  assert c.execute("select value from promotion_manifest where key='phase4_writes'").fetchone()[0]=='0'
 print('hostile promotion checks: PASS')

if __name__=='__main__': main()
