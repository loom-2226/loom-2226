import unittest
from types import SimpleNamespace
from src.loom_solar_temporal import hermite_position,adaptive_samples,compile_chunk

class Fake:
 def at(self,b,t,c):
  # exact quadratic: Hermite must reproduce it exactly with exact derivative
  return {'relative':{'position_km':[t*t,2*t,0],'velocity_km_s':[2*t,2,0]},'authority_class':'DIRECT','state':{'provenance':{'ephemeris_source_id':'S'}}}
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
