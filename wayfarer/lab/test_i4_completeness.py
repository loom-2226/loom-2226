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
        opt=I['habitat']['decks'][0]['command_layout']['crown_dome']['shell_option_c']
        self.assertEqual(opt['outer_tile_layer']['type_counts'],[1,12,12,12])
        self.assertEqual(opt['spares']['one_centre_and_two_of_each_annular_type'],[1,2,2,2])
        self.assertEqual(opt['l1_l2_hatches']['count'],2)
        self.assertIsNone(opt['visible_open_policy']['max_bow_dust_relative_speed_km_s'])
        self.assertIsNone(opt['visible_open_policy']['min_bow_to_flow_deg'])
        viewer_source=(R/'render/make_viewer.py').read_text()
        self.assertIn('crownSpeed',viewer_source)
        self.assertIn('crownFlow',viewer_source)
        views=get('render/views.json')['views']
        crown={v['id']:v for v in views if v['id'] in ('crown_open','crown_closed')}
        self.assertEqual(crown['crown_open']['crown']['open'],1)
        self.assertEqual(crown['crown_closed']['crown']['open'],0,
           'closed Strata gore render MUST NOT silently present the OPEN crown')
        geo=get('results/out/wayfarer_v05_geometry.json')
        sp=next(q for q in geo['parts'] if q['id']=='crown_c_seven_spare_panes')
        x,y,z=sp['centroid_m']
        self.assertTrue(14<=x<=17 and -4.3<=y<=-2 and abs(z)<=.8,
          'seven source spares must reside in hold_port, NEVER remass tanks')
        self.assertAlmostEqual(sp['mass_t'],opt['spares']['total_mass_t'],places=6)
        self.assertAlmostEqual(opt['nose_extension_forward_m'],1.2)
        self.assertAlmostEqual(opt['slope_deg'],50.)
        self.assertEqual(g['shellOptionC']['nose_tip_x_m'],-1.2)
        self.assertTrue(52<opt['outer_area_m2']<54)
        self.assertAlmostEqual(g['outerBandStaggerRad'],math.pi/12,places=9)
        self.assertLessEqual(a['maximum_outer_circumferential_edge_m'],1.9)
        self.assertEqual(c['i4_crown_option_B']['outer_count'],37)
if __name__=='__main__':unittest.main()
