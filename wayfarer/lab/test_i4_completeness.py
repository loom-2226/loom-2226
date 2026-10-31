"""Fail-closed one-to-one source-preservation check for original f07354f I4 scene.
No architecture. Source data is pinned verbatim under docs. Run python -m unittest wayfarer/lab/test_i4_completeness.py
"""
import json,math,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def get(p):return json.loads((R/p).read_text())
class I4Completeness(unittest.TestCase):
    def test_all_source_scene_items_mapped(self):
        src=get('docs/I4_ORIGINAL_SCENE_2026_10_29.json')
        I=get('config/wayfarer_v05_inputs.json')
        cmd=I['habitat']['decks'][0]['command_layout']
        x=get('render/out/l1_scene.json')
        items={q['id'] for q in I['i4_carryover']['items']}
        pl=set(cmd['i4_lock']['platforms'])
        blocks={v['tag'] for v in src['interior']['blocks']}
        self.assertEqual(blocks,{'command_terrace_trim_inner','navigator_platform','engineering_cabinet',
                                 'sensors_cabinet','shared_map_table','equipment_workbench','workbench_display'},
              'unmapped source block added: classify it explicitly first')
        for tag in blocks:
            dst='command_terrace' if tag=='command_terrace_trim_inner' else tag
            self.assertTrue(dst in pl or dst in items, f'unmapped I4 block {tag}')
        self.assertIn('navigator_platform',x,'NAV source platform MUST be in 3D viewer data')
        self.assertEqual({q['id'] for q in src['layout']['seats']},
                         {q['id'] for q in cmd['i4_lock']['stations']})
        self.assertEqual({q['id'] for q in src['layout']['seats']},{q['id'] for q in x['couches']})
        self.assertEqual({q['for_station'] for q in src['screens']},
                         {q['for'] for q in x['displays']})
        self.assertEqual(len(src['interior']['rails']),4)
        self.assertTrue({f'rails_{j}' for j in range(4)}<=items)
        self.assertEqual(len(src['interior']['lights']),2)
        self.assertTrue({f'lights_{j}' for j in range(2)}<=items)
        self.assertEqual(len(src['interior']['transfers']),2)
        self.assertTrue({f'transfer_{j}' for j in range(2)}<=items)
        self.assertEqual(len(src['interior']['consoles']),1)
        self.assertIn('map_console',items)
        self.assertIn('observation_rail',items)
        self.assertIn('low_g_command_point',items,'source low-g stand must be preserved')
        self.assertIn('equipment_workbench',items,'source independent work area must be preserved')
        self.assertEqual(src['levels'],4)
        self.assertEqual(set(src['role_centres']),{q['role'] for q in src['layout']['seats']})
        self.assertEqual(len(src['interior']['phases']),3)
        phases=(R/'docs/I4_INTEGRATED_OPERATING_PHASES_2026_11_01.md').read_text()
        for phase in src['interior']['phases']:self.assertIn(phase,phases)
        self.assertEqual(len(x['l1_l2_hatches']),2)
        self.assertEqual({q['id'] for q in x['l1_l2_hatches']},
                         {'l1_l2_hatch_0','l1_l2_hatch_1'})
        meshes=(R/'render/loomgl.js').read_text()
        for sentinel in ('sc.navigator_platform','sc.command_terrace','sc.l1_l2_hatches','crown_glass','crown_pane','outerBandStaggerRad','gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA)'):
            self.assertIn(sentinel,meshes,'3D renderer does not actually draw required object/surface: '+sentinel)
        self.assertTrue((R/'render/i4_original_canvas2d_viewer.html').is_file())
        self.assertTrue((R/'docs/NOSE_2226_ADAPTIVE_OPTOGEL_CANOPY_RESEARCH_CLOSED_20261029.md').is_file())
    def test_exact_original_outer_37_pattern(self):
        I=get('config/wayfarer_v05_inputs.json')
        c=I['habitat']['decks'][0]['command_layout']['crown_dome']
        a=c['panes'];g=get('results/out/wayfarer_v05_geometry.json')['crown']
        self.assertEqual(a['ring_boundaries_m'],[0,.75,2.,2.75,3.5])
        self.assertEqual(g['outerPaneRings'],a['ring_boundaries_m'])
        self.assertAlmostEqual(g['outerBandStaggerRad'],math.pi/12,places=9)
        self.assertLessEqual(a['maximum_outer_circumferential_edge_m'],1.9)
        self.assertEqual(c['i4_crown_option_B']['outer_count'],37)
if __name__=='__main__':unittest.main()
