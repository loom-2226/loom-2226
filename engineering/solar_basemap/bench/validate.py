"""Offline validation of the architecture packet and disposable measurement math.
This validates specification/evidence consistency, NOT prototype qualification.
Requires jsonschema; never calls physical services or edits authority.
"""
import copy, gzip, hashlib, importlib.util, json, math, re, struct, unittest
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('basemap_decision_measure',ROOT/'bench/measure.py')
measure=importlib.util.module_from_spec(spec);spec.loader.exec_module(measure)

class DecisionEvidence(unittest.TestCase):
    def test_schema_and_negative_semantic_shape(self):
        schema=json.loads((ROOT/'product.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        definition={'$schema':schema['$schema'],'$defs':schema['$defs'],'$ref':'#/$defs/feature'}
        d={'body_id':'DACTYL','name':'Dactyl','body_class':'NATURAL_SATELLITE','catalog_parent_id':None,
           'resolution':'UNRESOLVED','reason':'shape-only unit fixture','position_semantic':'PHYSICAL_EPOCH_POSITION',
           'position_km':None,'source_ref':None,'geometry_status':'UNRESOLVED','node_id':'solar'}
        jsonschema.validate(d,definition)
        invalid=copy.deepcopy(d);invalid['resolution']='ASSUMED'
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(invalid,definition)
        invalid=copy.deepcopy(d);invalid['position_km']=[1,2]
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(invalid,definition)
    def test_recorded_formats(self):
        corpus=json.loads((ROOT/'evidence/sample_corpus.json').read_text())
        evidence=json.loads((ROOT/'evidence/measurements.json').read_text())
        self.assertEqual(corpus['authority'],evidence['authority'])
        for body,path in corpus['paths'].items():
            points=[x['relative']['position_km'] for x in path['points']]
            actual=evidence['paths'][body]
            self.assertEqual(len(points),actual['vertices'])
            for name,raw in [('json',measure.encoded(points)),('f64le',struct.pack('<'+'d'*len(points)*3,*sum(points,[]))),('f32le',struct.pack('<'+'f'*len(points)*3,*sum(points,[])))]:
                self.assertEqual(measure.sizes(raw),actual['formats'][name])
            for lod in actual['simplifications']:
                self.assertEqual(measure.simplify(points,lod['tolerance_km']),lod)
    def test_simplification_independent_cases(self):
        # Abstract polylines, not physical or publication data.
        p=[[0,0,0],[1,0,0],[2,0,0]]
        self.assertEqual(measure.simplify(p,0)['vertices'],2)
        self.assertEqual(measure.simplify([[0,0,0],[1,1,0],[2,0,0]],.5)['vertices'],3)
        self.assertEqual(measure.dist_segment([3,1,0],[0,0,0],[2,0,0]),math.sqrt(2))
        self.assertEqual(measure.dist_segment([0,0,1],[0,0,0],[0,0,0]),1)
    def test_corpus_boundaries(self):
        corpus=json.loads((ROOT/'evidence/sample_corpus.json').read_text())
        for body,path in corpus['paths'].items():
            self.assertEqual(path['body_id'],body);self.assertFalse(path['closed_by_renderer'])
            times=[p['epoch_et'] for p in path['points']]
            self.assertTrue(all(a<b for a,b in zip(times,times[1:])))
            self.assertEqual(times[0],corpus['epoch_et']);self.assertEqual(path['reference_frame'],'ECLIPJ2000')
            self.assertEqual(path['gap_indices'],[])
            self.assertEqual(path['segments'][0]['indices'],list(range(len(times))))
    def test_local_document_links(self):
        for p in ROOT.glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((p.parent/target.split('#')[0]).exists(),f'{p.name}: {target}')
    def test_root_projection_and_live_identity(self):
        scene=json.loads((ROOT/'evidence/catalog_2226_snapshot.json').read_text())
        recorded=json.loads((ROOT/'evidence/measurements.json').read_text())
        verified=json.loads((ROOT/'evidence/ledger_reverification.json').read_text())
        self.assertEqual(scene['authority']['ledger_sha256'],verified['ledger_sha256'])
        self.assertEqual(scene['counts'],recorded['counts'])
        root=[{k:v for k,v in x.items() if k in ('body_id','canonical_name','body_class','parent_body_id','resolution','reason')} |
              ({'position_km':x['relative']['position_km']} if 'relative' in x else {}) for x in scene['objects']]
        self.assertEqual(measure.sizes(measure.encoded(root)),recorded['root_identity_position_projection'])
    def test_spec_policy_consistency(self):
        p=json.loads((ROOT/'generation-spec.json').read_text())
        self.assertEqual(p['epoch_et'],7131844800.0)
        self.assertEqual(len(p['requested_reference_curves']),12)
        self.assertEqual(p['requested_reference_curves']['PHOBOS'],'MARS')
        self.assertLess(p['client_policy']['coarsen_sse_css_px'],p['client_policy']['prefetch_sse_css_px'])
        self.assertLess(p['client_policy']['prefetch_sse_css_px'],p['client_policy']['refine_sse_css_px'])
        self.assertFalse(p['simplification_policy']['closed'])

if __name__=='__main__':unittest.main(verbosity=2)
