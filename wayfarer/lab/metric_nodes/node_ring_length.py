"""Four nacelles + aft ring: 14 m vs 10 m nacelles, same seeds and method as node_ring.py.
NON-CANON sketch search. Geometric evenness is a proxy only, not PR #356 domain qualification.
ALL bodies. ALL sponsors. 2026-2226."""
import os, json, numpy as np
import node_optimize as NO, node_nacelles as NN, node_ring as NR
HERE = os.path.dirname(os.path.abspath(__file__))
if __name__ == '__main__':
    rng = np.random.default_rng(2226)
    T = NO.load_glb(os.path.join(NO.W, 'render/out/wayfarer_exterior_detail_88ce19fc_stowed_closed.glb')); P, w = NO.envelope(T, rng)
    fixed = np.array([NO.cyl(n['x'], n['a'], n['r']) for n in NO.NB if n['c'] == 'bow'])
    out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON: nacelle length comparison; geometric proxy only', hoop=NR.HOOP, variants={})
    for name, x0 in (('nacelle_14m', 39.5), ('nacelle_10m', 43.5)):
        NN.NAC['x0'] = x0
        r = NR.run([0, 90, 180, 270], True, P, w, fixed); r['nacelle'] = dict(NN.NAC)
        out['variants'][name] = r; print(name, r['metrics'])
    json.dump(out, open(os.path.join(HERE, 'node_ring_length.json'), 'w'), indent=1)
