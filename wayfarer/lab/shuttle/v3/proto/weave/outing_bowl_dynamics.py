"""Cushion activation and departure over calm water: does the bowl form, how much does it lag, what happens after a jink (SOL, after 1ba4d27).
NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Coarse linear free-surface response, deep water. The cushion is represented by the equivalent surface pressure that would hold the
static equilibrium bowl eta_eq (outing_nimitz_view.bowl, field centre Z = 10 m). Each Fourier mode relaxes toward the forcing:
   a_k'' = -omega_k^2 (a_k - f_k(t)),   omega_k^2 = g |k|   (exact step for piecewise-constant forcing).
Periodic 512 m x 512 m domain, 1 m grid. Inviscid, no breaking, no foam. Small-slope theory applied to a bowl with 30 deg rims:
timing is meaningful, amplitudes are coarse.
Cases: cushion switched on at t = 0 (0.2 s ramp), hover 0.5 s or 5 s, then 30 m dodge in 0.5 s (quintic), then hover at the new spot."""
import os, json
import numpy as np
import outing_nimitz_view as nv
H = os.path.dirname(os.path.abspath(__file__))
g0, RW, Z, L, N = 9.81, 1000.0, 10.0, 512.0, 512
sg = np.linspace(0, 80, 1601); prof = nv.bowl(Z, sg)
x = (np.arange(N) - N / 2) * (L / N); X, Y = np.meshgrid(x, x, indexing='ij')
k1 = 2 * np.pi * np.fft.fftfreq(N, d=L / N); KX, KY = np.meshgrid(k1, k1, indexing='ij'); K = np.hypot(KX, KY); W = np.sqrt(g0 * K)
def eq_field(xc, amp):
    return amp * np.interp(np.hypot(X - xc, Y), sg, prof, right=0.0)
def run(hover, dodge=30.0, Td=0.5, Tend=25.0, dt=0.01, snaps=(), ramp=0.2):
    def craft(t):
        if t < hover: return 0.0
        s = np.clip((t - hover) / Td, 0, 1); return dodge * (6 * s ** 5 - 15 * s ** 4 + 10 * s ** 3)
    def amp(t): s = np.clip(t / ramp, 0, 1); return 6 * s ** 5 - 15 * s ** 4 + 10 * s ** 3
    a = np.zeros((N, N), complex); ad = np.zeros((N, N), complex); log = dict(t=[], under_craft=[], old_site=[], eq_depth=[], max_rise=[], max_slope_deg=[], wave_E=[])
    out_snaps = {}; c = np.cos(W * dt); s_ = np.sin(W * dt); Wsafe = np.where(W > 0, W, 1.0)
    ix0 = np.argmin(np.abs(x - 0.0)); iy0 = np.argmin(np.abs(x))
    for n in range(int(Tend / dt) + 1):
        t = n * dt; xc = craft(t); f = np.fft.fft2(eq_field(xc, amp(t)))
        q = a - f; qn = q * c + ad / Wsafe * s_; adn = -q * W * s_ + ad * c
        qn = np.where(W > 0, qn, 0); adn = np.where(W > 0, adn, 0); a = qn + f; ad = adn
        if n % 5 == 0 or any(abs(t - sv) < dt / 2 for sv in snaps):
            eta = np.real(np.fft.ifft2(a)); gx, gy = np.gradient(eta, L / N)
            ixc = np.argmin(np.abs(x - xc))
            pe = 0.5 * RW * g0 * np.sum(eta ** 2) * (L / N) ** 2
            ke = 0.5 * RW * g0 * np.sum(np.abs(ad[W > 0]) ** 2 / W[W > 0] ** 2) * (L / N) ** 2 / N ** 2
            log['t'].append(t); log['under_craft'].append(float(eta[ixc, iy0])); log['old_site'].append(float(eta[ix0, iy0]))
            log['eq_depth'].append(float(prof[0] * amp(t))); log['max_rise'].append(float(eta.max())); log['max_slope_deg'].append(float(np.degrees(np.arctan(np.hypot(gx, gy).max()))))
            log['wave_E'].append(float(pe + ke))
            for sv in snaps:
                if abs(t - sv) < dt / 2: out_snaps[f'{sv:g}'] = eta[N // 2 - 80:N // 2 + 120, N // 2 - 70:N // 2 + 70].astype(np.float32)
    return log, out_snaps
if __name__ == '__main__':
    res = dict(doc=__doc__, equilibrium_depth_m=float(-prof[0])); snapset = {}
    for hv, rp, tag in ((0.5, 0.2, '0.5s'), (5.0, 0.2, '5s'), (5.0, 2.0, '5s_ramp2s')):
        snaps = (hv, hv + 0.5, hv + 2.0, hv + 5.0, hv + 12.0)
        log, sn = run(hv, snaps=snaps, ramp=rp); hv_key = tag; t = np.array(log['t']); uc = np.array(log['under_craft']); old = np.array(log['old_site'])
        pre = t <= hv
        frac = float(uc[pre][-1] / prof[0]) if pre.any() else 0.0
        t63 = float(t[np.argmax(uc <= 0.63 * prof[0])]) if np.any(uc <= 0.63 * prof[0]) else None
        after = t > hv + 0.5
        res[f'hover_{hv_key}'] = dict(ramp_s=rp, max_overshoot_depth_m=float(-uc[pre].min()) if pre.any() else 0.0, bowl_fraction_at_departure=frac, depth_at_departure_m=float(-uc[pre][-1]), time_to_63pct_s=t63,
            old_site_rebound_max_m=float(old[after].max()), old_site_rebound_time_s=float(t[after][np.argmax(old[after])] - hv),
            max_rise_after_departure_m=float(np.array(log['max_rise'])[after].max()), max_slope_deg=float(max(log['max_slope_deg'])),
            new_site_depth_5s_after_m=float(-uc[np.argmin(np.abs(t - (hv + 5.5)))]), wave_E_end_J=float(log['wave_E'][-1]))
        res[f'series_{hv_key}'] = log; snapset[f'h{hv_key}'] = sn
        print(hv_key, json.dumps(res[f'hover_{hv_key}']), flush=True)
    json.dump(res, open(os.path.join(H, 'outing_bowl_dynamics.json'), 'w'), indent=1)
    np.savez_compressed(os.path.join(H, 'outing_bowl_dynamics_snaps.npz'), **{f'{k}_{s}': v for k, d in snapset.items() for s, v in d.items()})
