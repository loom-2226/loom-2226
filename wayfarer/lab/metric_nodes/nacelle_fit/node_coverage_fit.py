"""Node coverage for the fitted nacelle geometry (nacelle_fit.py 'fixed'): hoop moved aft to x 53.9, R 4.6; nacelles to x 54.3.
Same method and seeds as node_ring.py. NON-CANON geometric proxy only. ALL bodies. ALL sponsors. 2026-2226."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import node_optimize as NO, node_nacelles as NN, node_ring as NR
if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = NO.load_glb(os.path.join(NO.W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = NO.envelope(T, rng)
    fixed = np.array([NO.cyl(n['x'], n['a'], n['r']) for n in NO.NB if n['c'] == 'bow'])
    NN.NAC['x1'] = 54.3; NR.HOOP.update(x=53.9, R=4.6)
    r = NR.run([0, 90, 180, 270], True, P, w, fixed); print(r['metrics'])
    json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', nacelle=dict(NN.NAC), hoop=dict(NR.HOOP), metrics=r['metrics'], nodes=r['nodes']),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_coverage_fit.json'), 'w'), indent=1)
