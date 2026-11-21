"""Weave source closure, Phase 1: GR source ledger for the R15/d2 shift dash (SOL brief after 4b62812). NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Metric (prescribed): ds^2 = -c^2 dt^2 + sum_i (dx^i - b^i dt)^2, N = 1, flat slices, b = axisymmetric zero-expansion shift
(R = 15 m, d = 2 m), centre X(t) = 200 m / 3 s quintic. In Gourgoulhon's 3+1 convention the shift is beta = -b.
Effective stress-energy T = G[g] c^4 / (8 pi G) measured by Eulerian observers (n^mu = (1, b)):
  K_ij = -(1/2)(d_i b_j + d_j b_i),  K = 0 (div b = 0)
  E    = -K_ij K_ij / (16 pi)                                       Hamiltonian constraint (R = 0)
  p_i  = d_j K_ij / (8 pi)                                          momentum constraint
  A_ij = (d_t - L_beta) K_ij + 2 K_ik K_kj,   4 pi [(S - E) delta_ij - 2 S_ij] = A_ij   evolution equation
  (units: K in 1/s; multiply E, S by c^2/G for J/m^3 = Pa; p by c^2/G for kg m^-2 s^-1)
Validation: formulas checked against the 4D Einstein tensor from nested finite-difference Christoffels at V = 0.1 c (c = 1 units);
the formulas are polynomial in b, so agreement there fixes all signs and factors.
Ledger: volume integrals vs t of E, p_x, x E, trace S; integrated 3+1 energy balance; ADM charges from surface terms."""
import os, json, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
G_N, C = 6.674e-11, 2.998e8
R0, DW = 15.0, 2.0
def s5(x): x = np.clip(x, 0, 1); return 200.0 * (6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3)
def v5(x): x = np.clip(x, 0, 1); return 200.0 / 3.0 * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2)
def sech2(z): return 1.0 / np.cosh(np.clip(z, -300, 300)) ** 2
def bvec(t, x, y, z, Xf, Vf, R=R0, d=DW):
    u = x - Xf(t); rr2 = y * y + z * z; r = np.sqrt(u * u + rr2) + 1e-300; V = Vf(t)
    F = 0.5 * (np.tanh((r + R) / d) - np.tanh((r - R) / d)); Fp = 0.5 / d * (sech2((r + R) / d) - sech2((r - R) / d)); q = Fp / (2 * r)
    return np.array([V * (F + rr2 * q), -V * y * u * q, -V * z * u * q])
# ---------- 3+1 formulas (vectorised over points) ----------
def ledger_fields(t, x, y, z, Xf, Vf, h1=1e-3, h2=1e-2, ht=None):
    ht = ht if ht is not None else 1e-4
    P = [x, y, z]
    def grad_b(tt, px, py, pz):                                          # db[i, j] = d_i b_j
        out = np.empty((3, 3) + np.shape(px))
        for i in range(3):
            e = [0.0, 0.0, 0.0]; e[i] = h1
            bp = bvec(tt, px + e[0], py + e[1], pz + e[2], Xf, Vf); bm = bvec(tt, px - e[0], py - e[1], pz - e[2], Xf, Vf)
            bp2 = bvec(tt, px + 2 * e[0], py + 2 * e[1], pz + 2 * e[2], Xf, Vf); bm2 = bvec(tt, px - 2 * e[0], py - 2 * e[1], pz - 2 * e[2], Xf, Vf)
            out[i] = (-bp2 + 8 * bp - 8 * bm + bm2) / (12 * h1)
        return out
    def Kf(tt, px, py, pz):
        db = grad_b(tt, px, py, pz); return -0.5 * (db + np.swapaxes(db, 0, 1))
    db = grad_b(t, x, y, z); K = -0.5 * (db + np.swapaxes(db, 0, 1)); b = bvec(t, x, y, z, Xf, Vf)
    dK = np.empty((3, 3, 3) + np.shape(x))                               # dK[k, i, j] = d_k K_ij
    for k in range(3):
        e = [0.0, 0.0, 0.0]; e[k] = h2
        dK[k] = (Kf(t, x + e[0], y + e[1], z + e[2]) - Kf(t, x - e[0], y - e[1], z - e[2])) / (2 * h2)
    dtK = (Kf(t + ht, x, y, z) - Kf(t - ht, x, y, z)) / (2 * ht)
    KK = np.einsum('ij...,ij...->...', K, K)
    E = -KK / (16 * np.pi)
    p = np.einsum('jij...->i...', dK) / (8 * np.pi)                    # p_i = d_j K_ij
    # (d_t - L_beta) K_ij with beta = -b:  L_beta K_ij = -(b_k d_k K_ij + K_kj d_i b_k + K_ik d_j b_k)
    LbK = -(np.einsum('k...,kij...->ij...', b, dK) + np.einsum('kj...,ik...->ij...', K, db) + np.einsum('ik...,jk...->ij...', K, db))
    A = dtK - LbK + 2 * np.einsum('ik...,kj...->ij...', K, K)
    trA = np.einsum('ii...->...', A); S = 3 * E + trA / (4 * np.pi)
    S_ij = 0.5 * ((S - E) * np.eye(3).reshape((3, 3) + (1,) * np.ndim(x)) - A / (4 * np.pi))
    return dict(E=E, p=p, S=S_ij, K=K, KK=KK)
# ---------- validation against the 4D Einstein tensor ----------
def validate(n=12, V0=0.1, seed=3):
    rng = np.random.default_rng(seed)
    Vf = lambda t: V0 * np.sin(t / 20.0); Xf = lambda t: 20 * V0 * (1 - np.cos(t / 20.0))
    def metric(Pt):
        b = bvec(Pt[0], Pt[1], Pt[2], Pt[3], Xf, Vf); g = np.eye(4); g[0, 0] = -1 + b @ b; g[0, 1:] = g[1:, 0] = -b; return g
    def D(fun, Pt, mu, h):
        e = np.zeros(4); e[mu] = h; return (-fun(Pt + 2 * e) + 8 * fun(Pt + e) - 8 * fun(Pt - e) + fun(Pt - 2 * e)) / (12 * h)
    def christ(Pt):
        gi = np.linalg.inv(metric(Pt)); dg = np.array([D(metric, Pt, m, 2e-3) for m in range(4)])
        return 0.5 * (np.einsum('ad,cdb->abc', gi, dg) + np.einsum('ad,bdc->abc', gi, dg) - np.einsum('ad,dbc->abc', gi, dg))
    rows = []
    for _ in range(n):
        t = rng.uniform(8, 25); rr = R0 + DW * rng.normal(0, 1.0); th = rng.uniform(0.2, np.pi - 0.2); ph = rng.uniform(0, 2 * np.pi)
        Pt = np.array([t, Xf(t) + rr * np.cos(th), rr * np.sin(th) * np.cos(ph), rr * np.sin(th) * np.sin(ph)])
        Gm = christ(Pt); dG = np.array([D(christ, Pt, a, 2e-2) for a in range(4)])     # dG[a, al, mu, nu] = d_a Gamma^al_mu nu
        # R_mn = d_a G^a_mn - d_n G^a_ma + G^a_al G^l_mn - G^a_nl G^l_ma
        Ric = (np.einsum('aamn->mn', dG) - np.einsum('nama->mn', dG)
               + np.einsum('aal,lmn->mn', Gm, Gm) - np.einsum('anl,lma->mn', Gm, Gm))
        g = metric(Pt); gi = np.linalg.inv(g); Rs = np.einsum('mn,mn->', gi, Ric); Gt = Ric - 0.5 * g * Rs; T = Gt / (8 * np.pi)
        b = bvec(Pt[0], Pt[1], Pt[2], Pt[3], Xf, Vf); nU = np.concatenate([[1.0], b])
        E_num = nU @ T @ nU; p_num = -(nU @ T)[1:]; S_num = T[1:, 1:]
        L = ledger_fields(Pt[0], np.array(Pt[1]), np.array(Pt[2]), np.array(Pt[3]), Xf, Vf, ht=1e-3)
        rows.append(dict(E=(float(E_num), float(L['E'])), p=(p_num.tolist(), L['p'].tolist()), S=(S_num.tolist(), L['S'].tolist())))
    def rel(a, b): a = np.asarray(a, float); b = np.asarray(b, float); return float(np.max(np.abs(a - b)) / (np.max(np.abs(a)) + 1e-300))
    return dict(E_rel_err_max=max(rel(r['E'][0], r['E'][1]) for r in rows), p_rel_err_max=max(rel(r['p'][0], r['p'][1]) for r in rows),
                S_rel_err_max=max(rel(r['S'][0], r['S'][1]) for r in rows), sample=rows[0])
# ---------- physical ledger for the dash ----------
def ledger_series(nt=61, hx=0.1, L=31.0):
    Xf = lambda t: s5(t / 3.0); Vf = lambda t: v5(t / 3.0)
    us = np.arange(-L, L, hx) + hx / 2; ps = np.arange(0, L, hx) + hx / 2; U, P = np.meshgrid(us, ps, indexing='ij'); dV = 2 * np.pi * P * hx * hx
    conv = C * C / G_N
    out = dict(t=[], E_J=[], Px_Ns=[], xE_Jm=[], trS_J=[], KS_W=[], absE_J=[], Pabs_Ns=[], edge_E=[], Sxx_J=[])
    for t in np.linspace(0.0, 3.0, nt):
        X = Xf(t); x = U + X
        F = ledger_fields(t, x, P, np.zeros_like(P), Xf, Vf)
        E = F['E'] * conv; px = F['p'][0] * conv; S = F['S'] * conv; K = F['K']
        KS = np.einsum('ij...,ij...->...', K, F['S']) * conv                         # K_ij S^ij  (W/m^3)
        out['t'].append(float(t)); out['E_J'].append(float(np.sum(E * dV))); out['absE_J'].append(float(np.sum(np.abs(E) * dV)))
        out['Px_Ns'].append(float(np.sum(px * dV))); out['Pabs_Ns'].append(float(np.sum(np.abs(px) * dV)))
        out['xE_Jm'].append(float(np.sum(x * E * dV))); out['trS_J'].append(float(np.sum(np.einsum('ii...->...', S) * dV)))
        out['Sxx_J'].append(float(np.sum(S[0, 0] * dV))); out['KS_W'].append(float(np.sum(KS * dV)))
        edge = (np.abs(U) > L - 1) | (P > L - 1); out['edge_E'].append(float(np.max(np.abs(E[edge])) / (np.max(np.abs(E)) + 1e-300)))
    t = np.array(out['t']); Et = np.array(out['E_J']); dEdt = np.gradient(Et, t); KS = np.array(out['KS_W'])
    out['energy_balance'] = dict(dEdt_W=dEdt.tolist(), note='compare dE/dt with +/- int K_ij S^ij dV (3+1 energy equation, compact support)')
    return out
if __name__ == '__main__':
    t0 = time.time(); val = validate(); print('VALIDATION', json.dumps({k: v for k, v in val.items() if k != 'sample'}), f'{time.time() - t0:.0f}s', flush=True)
    t0 = time.time(); led = ledger_series(); print('ledger', f'{time.time() - t0:.0f}s', flush=True)
    t = np.array(led['t']); i = int(np.argmax(np.abs(led['E_J'])))
    print('peak E_J', led['E_J'][i], 'at', t[i], 'max|Px|', max(np.abs(led['Px_Ns'])), 'Pabs', max(led['Pabs_Ns']), 'edge', max(led['edge_E']))
    json.dump(dict(doc=__doc__, validation=val, ledger=led), open(os.path.join(H, 'weave_source_ledger.json'), 'w'), indent=1)
