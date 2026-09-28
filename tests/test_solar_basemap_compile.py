import unittest
import math
from types import SimpleNamespace

from src.loom_solar_basemap_compile import T, _rdp, _curve_sampling, _initial_curve_level


class SamplingTests(unittest.TestCase):
    def test_initial_solar_lod_is_selected_independently_per_curve(self):
        levels=[{"level":0,"error":1.0},{"level":1,"error":.2},{"level":2,"error":.01}]
        # A large orbit needs a finer level; a compact orbit can stay coarse.
        self.assertEqual(_initial_curve_level(levels,.1,.8), (1,.30000000000000004))
        self.assertEqual(_initial_curve_level(levels,.01,.5), (0,1.01))
        with self.assertRaisesRegex(ValueError,"no level"):
            _initial_curve_level(levels,2,.5)

    def test_rdp_keeps_open_endpoints_and_deviation(self):
        points = [[0,0,0,0], [1,1,0,0.01], [2,2,0,0], [3,3,0,0]]
        self.assertEqual(_rdp(points, .1), [0,3])
        self.assertEqual(_rdp(points, .001), [0,1,2,3])

    def _fake(self, gap=False, seam=False):
        source=SimpleNamespace(ephemeris_source_id='src',kernel_assets=(),sha256='0'*64)
        source2=SimpleNamespace(ephemeris_source_id='src2',kernel_assets=(),sha256='1'*64)
        class Registry:
            coverage=[]; sources={'src':source,'src2':source2}
            def source_for(self,body,et): return (source2 if seam and et>T+256 else source),None
        registry=Registry()
        class Inspector:
            def record(self,body,et):
                missing=gap and body=='PHOBOS' and T+10<=et<=T+15
                if missing:return {'resolution':'UNRESOLVED','reason':'fixture gap'}
                x=(100+math.sin((et-T)*.01)) if body=='PHOBOS' else (10+.2*math.cos((et-T)*.01))
                sid='src2' if seam and et>T+256 else 'src'
                return {'resolution':'RESOLVED','state':{'position_km':[x,0,0], 'velocity_km_s':[0,0,0],
                        'provenance':{'ephemeris_source_id':sid,'asset_sha256':('1' if sid=='src2' else '0')*64}},'authority_class':'DIRECT'}
        inspector=Inspector(); inspector.registry=registry
        inspector.service=SimpleNamespace(adapter=SimpleNamespace(registry=registry))
        return inspector

    def test_parent_reference_geometry_is_exact_subtraction_at_epoch(self):
        inspector=self._fake()
        result=_curve_sampling(inspector,'PHOBOS','MARS',{'start_et':T,'end_et':T+512,'status':'REVOLUTION_COMPLETE'})
        sample=next(x for x in result['audit']['samples'] if x['et']==T)
        body=sample['body_state']['position_km']; parent=sample['anchor_state']['position_km']
        q=sample['relative_position_km']
        self.assertEqual(q,[body[i]-parent[i] for i in range(3)])
        self.assertLess(result['probe_error'],result['epsilon'])

    def test_unresolved_interval_is_preserved_as_a_gap(self):
        result=_curve_sampling(self._fake(gap=True),'PHOBOS','MARS',{'start_et':T,'end_et':T+512,'status':'UNRESOLVED_BEFORE_COMPLETION'})
        self.assertEqual(result['status'],'PARTIAL')
        self.assertTrue(result['gaps'])
        self.assertGreaterEqual(len(result['levels'][0]['segments']),2)

    def test_source_pair_seam_is_a_segment_boundary(self):
        result=_curve_sampling(self._fake(seam=True),'PHOBOS','MARS',{'start_et':T,'end_et':T+512,'status':'REVOLUTION_COMPLETE'})
        self.assertGreaterEqual(len(result['levels'][-1]['segments']),2)
        self.assertNotEqual(result['levels'][-1]['segments'][0]['body_source_ref'],result['levels'][-1]['segments'][-1]['body_source_ref'])


if __name__ == "__main__": unittest.main()
