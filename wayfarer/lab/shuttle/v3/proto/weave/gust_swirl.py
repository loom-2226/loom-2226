"""Exact swirl-gust family for the shift dash (axisymmetric swirl: no pressure term, rho * w_phi conserved). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226. Uses parcel end positions from weave_geometry_compare (R 15 / d 2 shift, 2 m lattice)."""
import os, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); S = json.load(open(os.path.join(H, 'weave_geometry_compare_series.json')))['fields']['shift']
p0 = np.array(S['p0']); x0 = np.array(S['x0']); pf = p0 + np.array(S['dp']); a = p0 / np.maximum(pf, 1e-6); m = 1.2 * 2 * np.pi * p0
out = dict(doc=__doc__, parcel_factor=dict(max=float(a.max()), p99=float(np.percentile(a, 99)), median=float(np.median(a))), blobs={})
for xc, pc in [(20, 2), (60, 1), (60, 3), (120, 2), (180, 2), (60, 8)]:
    b = np.exp(-((x0 - xc) ** 2 + (p0 - pc) ** 2) / 9.0); out['blobs'][f'x{xc}_r{pc}'] = float(np.sum(m * (b * a) ** 2) / np.sum(m * b ** 2))
json.dump(out, open(os.path.join(H, 'weave_shift_gust_swirl.json'), 'w'), indent=1); print(json.dumps(out['blobs']), out['parcel_factor'])
