import unittest
from types import SimpleNamespace
from src.loom_solar_temporal import hermite_position,adaptive_samples,compile_chunk

class Fake:
 def at(self,b,t,c):
  # exact quadratic: Hermite must reproduce it exactly with exact derivative
  return {'resolution':'RESOLVED','relative':{'position_km':[t*t,2*t,0],'velocity_km_s':[2*t,2,0]},'authority_class':'DIRECT','state':{'provenance':{'ephemeris_source_id':'S'}}}
 def record(self,c,t): return {'state':{'provenance':{'ephemeris_source_id':'C'}}}

class TemporalTests(unittest.TestCase):
 def test_hermite_exact_quadratic(self):
  a={'epoch_et':0,'position_km':[0,0,0],'velocity_km_s':[0,0,0]}; b={'epoch_et':2,'position_km':[4,0,0],'velocity_km_s':[4,0,0]}
  self.assertEqual(hermite_position(a,b,1),[1,0,0])
 def test_adaptive_qualified_samples(self):
  rows,err=adaptive_samples(Fake(),'B','C',0,10,.001); self.assertLessEqual(err,.001); self.assertGreaterEqual(len(rows),3)
 def test_deterministic_chunk(self):
  f=Fake(); args=(f,['B'],0,10,lambda b:'C',lambda b:.001)
  self.assertEqual(compile_chunk(*args),compile_chunk(*args))

if __name__=='__main__':unittest.main()

class PublishTests(unittest.TestCase):
 def test_publication_is_content_addressed(self):
  import tempfile,json
  from pathlib import Path
  from src.loom_solar_temporal_publish import publish
  class P(Fake):
   bodies={'B':{'body_class':'PLANET','parent_body_id':'SUN'},'SUN':{'body_class':'STAR','parent_body_id':None}}
   authority={'ledger_sha256':'x'}
   def orbital_center(self,b): return 'SUN'
  with tempfile.TemporaryDirectory() as d:
   m=publish(P(),Path(d),0,10,32,['B']); ptr=json.loads((Path(d)/'current.json').read_text()); self.assertEqual(ptr['build_id'],m['build_id']); self.assertTrue((Path(d)/m['chunks'][0]['uri']).is_file())

def test_v1_campaign_shared_source_seam_assigns_exact_et_to_left_interval():
    import importlib.util, math
    from pathlib import Path
    from src.loom_solar_inspector import Inspector
    path=Path(__file__).resolve().parents[1]/'tools'/'qualify_solar_functions_v1.py'
    spec=importlib.util.spec_from_file_location('qualify_solar_functions_v1_test',path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    I=Inspector.connect('loom_dev','/home/ubuntu/loom_solar_assets')
    start=I.time.parse('2026 JAN 01 TDB'); end=I.time.parse('2251 JAN 01 TDB')
    tasks=mod.tasks_for(I,['BENNU'],start,end,256)
    seam=4283755200.0
    left=[t for t in tasks if t[3]==seam]
    right=[t for t in tasks if t[2]==math.nextafter(seam,math.inf)]
    assert len(left)==1 and len(right)==1
    assert left[0][4]=='76bc8b4e1495e2cc2bde'
    assert I.registry.source_for('BENNU',left[0][3])[0].ephemeris_source_id=='JPL_BENNU_SB441'
    assert I.registry.source_for('BENNU',right[0][2])[0].ephemeris_source_id=='PROP_BENNU_2101955_PHASE4D'
