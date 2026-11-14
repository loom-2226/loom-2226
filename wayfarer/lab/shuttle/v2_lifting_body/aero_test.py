"""ROM aerodynamic test of shuttle v1 (biconic, reference) and v2 B2/B3/B4
across solar-system atmospheres. NON-CANON engineering screen.
ALL bodies. ALL sponsors. 2026-2226.

Methods (all ROM, stated so):
  Hypersonic: modified Newtonian impact on the actual meshes (wings stowed),
    Cp_max from the stagnation limit for an effective gamma per gas, plus a
    flat skin-friction term Cf=0.002 on wetted area. Reference = planform.
  Subsonic: low-aspect-ratio lifting surface, Helmbold lift slope + Polhamus
    vortex lift (sharp chines), drag CD0 + CL*tan(alpha) (no LE suction);
    CD0 = 0.004 * Swet/S + 0.15 * Abase/S. Wings deployed for B3/B4.
  Entry: 3-D point mass over a spherical non-rotating planet, from circular
    orbit at entry interface: deorbit ellipse whose vacuum periapsis is where
    rho = 3e-4 kg/m3 (Earth ~60 km, Shuttle-like), constant alpha and
    constant bank 60 deg. Sutton-Graves stagnation heating.
  Atmospheres: Venus VIRA table from shuttle_inputs.json (<=70 km), all others
    approximate tabulated profiles (log-interpolated). APPROXIMATE.
"""
import numpy as np, json, os, struct
import build_v2b as B, variants as VA
HERE = os.path.dirname(os.path.abspath(__file__)); SH = os.path.join(HERE, '..')
G0 = 9.80665

# ---------------- atmospheres ----------------
venus_tab = [(p['altitude_km'], p['density_kg_m3']) for p in json.load(open(os.path.join(SH, 'shuttle_inputs.json')))['venus']['atmosphere_profile']]
venus_tab += [(80, 1.5e-2), (90, 2.4e-3), (100, 3.0e-4), (110, 3.6e-5), (120, 5e-6), (140, 1e-7), (150, 2e-8)]
WORLDS = {
 'Venus': dict(R=6051.8e3, GM=3.2486e14, gas='CO2', k=1.896e-4, gam=1.15, EI=150e3, kit=True,
               tab=venus_tab),
 'Earth': dict(R=6371e3, GM=3.986e14, gas='N2/O2', k=1.7415e-4, gam=1.2, EI=120e3, kit=False,
               tab=[(0, 1.225), (10, .4135), (20, .0889), (30, .0184), (40, 4.0e-3), (50, 1.03e-3), (60, 3.1e-4), (70, 8.3e-5), (80, 1.85e-5), (90, 3.4e-6), (100, 5.6e-7), (120, 2.2e-8)]),
 'Mars':  dict(R=3389.5e3, GM=4.2828e13, gas='CO2', k=1.9027e-4, gam=1.15, EI=125e3, kit=False,
               tab=[(0, .020), (10, .0098), (20, .0045), (30, .0019), (40, 7.4e-4), (50, 2.9e-4), (60, 1.0e-4), (80, 1.1e-5), (100, 7e-7), (125, 2e-8)]),
 'Titan': dict(R=2574.7e3, GM=8.978e12, gas='N2/CH4', k=1.7407e-4, gam=1.25, EI=800e3, kit=True,
               tab=[(0, 5.43), (10, 3.4), (20, 2.1), (40, .70), (60, .22), (80, .075), (100, .030), (150, 3.0e-3), (200, 3.5e-4), (300, 2e-5), (400, 3e-6), (500, 6e-7), (700, 4e-8), (1000, 5e-10)]),
}
THIN = {  # landing-only check: surface density from p/(R_specific T)
 'Pluto':  dict(R=1188.3e3, GM=8.696e11, rho0=1.0 * 0.028 / (8.314 * 40)),
 'Triton': dict(R=1353.4e3, GM=1.428e12, rho0=1.4 * 0.028 / (8.314 * 38))}
def rho(w, h):
    t = np.array(w['tab'], float); hk = h / 1e3
    if hk >= t[-1, 0]: return float(t[-1, 1] * np.exp(-(hk - t[-1, 0]) / 8.0))
    return float(np.exp(np.interp(hk, t[:, 0], np.log(t[:, 1]))))

# ---------------- vehicles ----------------
def v1_mesh():
    d = open(os.path.join(HERE, '..', '..', '..', 'print', 'shuttle_1to100', 'parts', 'shuttle_v1_1to100.stl'), 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    F = np.frombuffer(d[84:], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')], count=n)['v'].astype(float) * 0.1
    T = np.stack([-F[..., 2], -F[..., 0], F[..., 1]], -1)       # x aft? check below
    T = T - T.reshape(-1, 3).min(0) * [1, 0, 0]
    # make x run nose(0) -> tail: put the blunter end aft by area-weighted check is not needed; length axis only
    c = T.reshape(-1, 3).mean(0); T = T - [0, c[1], c[2]]
    return T
def v2_tris(var):
    P = VA.model(var, deployed=False)   # entry config: wings & fins stowed
    keep = ('hull', 'belly_tps', 'glazing', 'kit_pod', 'body_flap', 'torch_nozzle', 'fin_stbd', 'fin_port') + tuple(k for k in P if k.startswith('wing'))
    return np.vstack([P[k][0][P[k][1]] for k in keep if k in P])
def geom(T):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]; nv = np.cross(b - a, c - a); A = 0.5 * np.linalg.norm(nv, axis=1)
    n = nv / (2 * A[:, None] + 1e-15); return n, A
def planform(T, nx=400, ny=200):
    P = T.reshape(-1, 3); x0, x1 = P[:, 0].min(), P[:, 0].max(); y0, y1 = P[:, 1].min(), P[:, 1].max()
    from matplotlib.path import Path
    gx, gy = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny)); pts = np.c_[gx.ravel(), gy.ravel()]
    hit = np.zeros(len(pts), bool)
    for t in T[np.abs(geom(T)[0][:, 2]) > 0.05][:, :, :2]:
        bb = (pts[:, 0] >= t[:, 0].min()) & (pts[:, 0] <= t[:, 0].max()) & (pts[:, 1] >= t[:, 1].min()) & (pts[:, 1] <= t[:, 1].max())
        if bb.any(): hit[bb] |= Path(t).contains_points(pts[bb])
    return hit.mean() * (x1 - x0) * (y1 - y0)
def cpmax(g): return ((g + 1) ** 2 / (4 * g)) ** (g / (g - 1)) * 4 / (g + 1)
def newtonian(T, S, Swet, alpha_deg, gam):
    n, A = geom(T); a = np.radians(alpha_deg)
    d = np.array([np.cos(a), 0, np.sin(a)]); l = np.array([-np.sin(a), 0, np.cos(a)])
    cs = n @ d; w = cs < 0
    Fv = -(cpmax(gam) * cs[w] ** 2 * A[w])[:, None] * n[w]
    Fsum = Fv.sum(0) / S
    CD = Fsum @ d + 0.002 * Swet / S; CL = Fsum @ l
    return CL, CD

VEH = {}
def build():
    Tv1 = v1_mesh()
    # orient v1 so the nose is at min x: the nose end has the smaller section
    P = Tv1.reshape(-1, 3); L = P[:, 0].max() - P[:, 0].min(); xm = P[:, 0].min()
    near = lambda f: P[np.abs(P[:, 0] - (xm + f * L)) < 0.2 * 1]
    if np.ptp(near(0.03)[:, 1]) > np.ptp(near(0.97)[:, 1]): Tv1[..., 0] = xm + L - (Tv1[..., 0] - xm)
    Tv1[..., 0] -= Tv1[..., 0].min(); Tv1[..., 2] -= 0
    for name, T, extra, dm in (('v1 biconic', Tv1, (0.0, 3.8), 0.0), ('B2 angular', v2_tris('B2'), VA.wing_geom('B2'), 0.4),
                               ('B3 fold wing', v2_tris('B3'), VA.wing_geom('B3'), 0.4 + VA.WING['B3']['mass_t']),
                               ('B4 double fold', v2_tris('B4'), VA.wing_geom('B4'), 0.4 + VA.WING['B4']['mass_t'])):
        n, A = geom(T); Swet = A.sum(); Sb = planform(T)
        xs = T[..., 0]; aft = T[(xs > xs.max() - 0.15).all(1)]; Abase = geom(aft)[1].sum() if len(aft) else 0
        if Abase < 1: Abase = 6.0
        VEH[name] = dict(T=T, S_body=Sb, S_wing=extra[0], span=max(extra[1], np.ptp(T[..., 1])), Swet=Swet, Abase=Abase, dm=dm,
                         sharp=name != 'v1 biconic', rn=0.6 if name == 'v1 biconic' else 0.25)

def subsonic(v, alpha_deg):
    S = v['S_body'] + v['S_wing']; A = v['span'] ** 2 / S
    a = np.radians(alpha_deg); CLa = 2 * np.pi * A / (2 + np.sqrt(A * A + 4))
    Kv = np.pi if v['sharp'] else 0.4 * np.pi
    CL = CLa * np.sin(a) * np.cos(a) ** 2 + Kv * np.sin(a) ** 2 * np.cos(a)
    CD0 = 0.004 * (v['Swet'] + 2 * v['S_wing']) / S + 0.15 * v['Abase'] / S
    CD = CD0 + CL * np.tan(a)
    return CL, CD, S, A, CD0

def entry(v, wname, mass, alpha, bank=60.0):
    w = WORLDS[wname]; S = v['S_body']   # wings stowed in entry
    CL, CD = newtonian(v['T'], S, v['Swet'], alpha, w['gam'])
    # deorbit from a low circular orbit at entry interface: start at apoapsis (EI), vacuum periapsis where rho = 3e-4 kg/m3
    hs = np.linspace(0, w['EI'], 4000); hp = float(hs[np.argmin(np.abs(np.log([rho(w, h) for h in hs]) - np.log(3e-4)))])
    r0 = w['R'] + w['EI']; rp = w['R'] + hp; a_ = (r0 + rp) / 2; v0 = np.sqrt(w['GM'] * (2 / r0 - 1 / a_))
    y = np.array([r0, 0.0, 0.0, v0, 0.0, 0.0]); sb, cb = np.sin(np.radians(bank)), np.cos(np.radians(bank))
    def f(y):
        r, th, ph, V, gm, ps = y; h = r - w['R']; g = w['GM'] / r ** 2; q = 0.5 * rho(w, h) * V * V
        Lf, Df = q * S * CL / mass, q * S * CD / mass
        return np.array([V * np.sin(gm), V * np.cos(gm) * np.cos(ps) / (r * np.cos(ph)), V * np.cos(gm) * np.sin(ps) / r,
                         -Df - g * np.sin(gm), (Lf * cb - (g - V * V / r) * np.cos(gm)) / V,
                         (Lf * sb / np.cos(gm) - V * V / r * np.cos(gm) * np.cos(ps) * np.tan(ph)) / V]), Lf, Df
    dt = 0.5; t = 0; pk_g = pk_q = Q = 0; vend = min(400.0, 0.2 * v0)
    while t < 20000:
        k1, Lf, Df = f(y); k2 = f(y + dt / 2 * k1)[0]; k3 = f(y + dt / 2 * k2)[0]; k4 = f(y + dt * k3)[0]
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
        h = y[0] - w['R']; qd = w['k'] * np.sqrt(rho(w, h) / v['rn']) * y[3] ** 3
        pk_g = max(pk_g, np.hypot(Lf, Df) / G0); pk_q = max(pk_q, qd); Q += qd * dt
        if y[3] < vend or h < 5e3 or (h > w['EI'] + 50e3 and t > 60): break
    skipped = (y[0] - w['R']) > w['EI']
    return dict(periapsis_target_km=hp / 1e3, alpha=alpha, CL=CL, CD=CD, LD=CL / CD, beta=mass / (CD * S), v_entry=v0, peak_g=pk_g, peak_q_Wcm2=pk_q / 1e4,
                heat_load_MJm2=Q / 1e6, downrange_km=y[1] * w['R'] / 1e3, crossrange_km=y[2] * w['R'] / 1e3,
                end_alt_km=(y[0] - w['R']) / 1e3, end_v=y[3], time_min=t / 60, skipped=bool(skipped))

def landing(v, rho0, g, mass, alpha_td=15.0):
    CL, CD, S, A, CD0 = subsonic(v, alpha_td); W = mass * g
    vt = np.sqrt(2 * W / (rho0 * S * CL)); al = np.linspace(2, 30, 141)
    LD = [subsonic(v, a)[0] / subsonic(v, a)[1] for a in al]
    return dict(v_td=vt, sink=vt / (CL / CD), LDmax=max(LD), alpha_LDmax=float(al[int(np.argmax(LD))]), AR=A, S=S, CD0=CD0)

if __name__ == '__main__':
    build()
    MASS = {True: 45.0, False: 35.0}   # entry mass t: kit aboard (Venus/Titan) vs core (Earth/Mars)
    out = dict(method=__doc__, vehicles={}, entry={}, landing={}, hyper_polar={})
    for vn, v in VEH.items():
        out['vehicles'][vn] = {k: (round(float(x), 3) if not isinstance(x, (bool, np.ndarray)) else (bool(x) if isinstance(x, bool) else None))
                               for k, x in v.items() if k != 'T'}
        out['hyper_polar'][vn] = [dict(alpha=a, LD=round(float(np.divide(*newtonian(v['T'], v['S_body'], v['Swet'], a, 1.2))), 3)) for a in range(5, 61, 5)]
    for wn in WORLDS:
        out['entry'][wn] = {}; out['landing'][wn] = {}
        for vn, v in VEH.items():
            m = (MASS[WORLDS[wn]['kit']] + v['dm']) * 1e3
            pol = out['hyper_polar'][vn]; a_best = max([p for p in pol if 15 <= p['alpha'] <= 45], key=lambda p: p['LD'])['alpha']
            a_fly = 40 if v['sharp'] else a_best
            e = entry(v, wn, m, a_fly); out['entry'][wn][vn] = {k: (round(float(x), 3) if not isinstance(x, bool) else x) for k, x in e.items()}
            g0 = WORLDS[wn]['GM'] / WORLDS[wn]['R'] ** 2
            out['landing'][wn][vn] = {k: round(float(x), 3) for k, x in landing(v, rho(WORLDS[wn], 0), g0, m).items()}
    for wn, w in THIN.items():
        out['landing'][wn] = {}
        for vn, v in VEH.items():
            m = (35.0 + v['dm']) * 1e3; g0 = w['GM'] / w['R'] ** 2
            out['landing'][wn][vn] = {k: round(float(x), 3) for k, x in landing(v, w['rho0'], g0, m).items()}
    json.dump(out, open(os.path.join(HERE, 'aero_results.json'), 'w'), indent=1)
    for vn in VEH: print(vn, out['vehicles'][vn])
    print('hyper L/D', {vn: [(p['alpha'], p['LD']) for p in out['hyper_polar'][vn]] for vn in VEH})
    for wn in out['entry']:
        for vn, e in out['entry'][wn].items(): print(wn, vn, {k: e[k] for k in ('alpha', 'LD', 'beta', 'v_entry', 'peak_g', 'peak_q_Wcm2', 'heat_load_MJm2', 'crossrange_km', 'downrange_km', 'end_alt_km', 'skipped')})
    for wn in out['landing']:
        for vn, l in out['landing'][wn].items(): print('LAND', wn, vn, l)
