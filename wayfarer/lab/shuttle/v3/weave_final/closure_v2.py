"""Weave shuttle closure v2 (SOL revised direction after 34fc20c). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Kept fixed: 12.8 m #2643 airframe, 6 couches at 3.5 m3, 6 m3 cargo well, wings/fans/floats/torch, 8 t relational module (+1.0 t
install allowance), lane cushion model (fast 20 s lift to 2 km) and its flywheel, 23.1 t tank.
Prototype assumptions explored (explicit, not established Builder properties):
  - module packaging density 2-4 t/m3: dense central core + field network distributed in the hull wall. The distributed part
    still occupies volume: it thickens the wall INWARD (no outward growth: bay fit headroom is 0.02 m), so it is charged to the interior.
    Mass is NOT reduced anywhere for integration (no double counting).
  - thermal management integrated with the fan-reactor loop and the 23 t water tank as heat sink: cooling hardware 0.2 m3 (was 0.5).
  - floats 32 m3 (31 + 1 m3 margin), +0.03 t per m3.
  - W1 programmable wing: field-off lift uplift = the smallest CLmax factor that brings the heavy field-off touchdown to <= 50 m/s.
Reported: residual interior volume for each density; the minimum adjustment if it does not close."""
import os, json, math
import numpy as np
import closure_screen as cs
H = os.path.dirname(os.path.abspath(__file__))
def run(rho_module, cool_m3=0.2, floats=32.0, length=None, tank=23.1, uplift=None):
    cfg = dict(cs.by[2643]['params'], wildcard='osteon_cautious+programmable', span=17.0, chord=1.8, water_t=tank, floats_m3=floats)
    if length: cfg['length'] = length
    cs.CFG = cfg; r, M = cs.mass_close(); g = cs.gates(r, M)
    mod_m3 = cs.MODULE['core_t'] / rho_module; fly_m3 = M['flywheel_t'] / 2.0; inst_m3 = 0.1 + cool_m3        # mounts/power 0.1 m3
    need = r['interior_need_m3'] + mod_m3 + fly_m3 + inst_m3; resid = r['inner_m3'] - need
    S, clmax, stat = r['land']['S'], r['land']['clmax'], r['land']['static_kN']
    m_heavy = M['dry_t'] + M['payload_t'] + g['earth_water_t']['value']
    def vtd(mm, cl): return math.sqrt(2 * max(mm * 1e3 * cs.G - stat * 1e3, 1.0) / (1.225 * S * cl))
    need_up = 1.0
    while vtd(m_heavy, clmax * need_up) > 50.0: need_up += 0.001
    up = uplift if uplift else need_up
    return dict(rho_module=rho_module, module_m3=round(mod_m3, 2), flywheel_m3=round(fly_m3, 2), install_m3=round(inst_m3, 2), interior_usable=r['inner_m3'], need=round(need, 2), residual_m3=round(resid, 2),
                dry_t=M['dry_t'], margin_t=M['margin_t'], water_cushion_t=g['earth_and_hot_egress_with_cushion_t']['value'], tank_t=tank, water_ok=g['earth_and_hot_egress_with_cushion_t']['ok'],
                buoy=(g['buoyancy_total_m3']['value'], g['buoyancy_total_m3']['limit']), buoy_ok=g['buoyancy_total_m3']['ok'], clmax=clmax, uplift=round(up, 3),
                heavy_td_ms=round(vtd(m_heavy, clmax * up), 1), heavy_td_no_uplift=round(vtd(m_heavy, clmax), 1), light_td_ms=round(vtd(M['dry_t'] + M['payload_t'] + 2.0, clmax * up), 1),
                length=cfg.get('length', 12.8))
if __name__ == '__main__':
    out = dict(doc=__doc__, by_density={}, adjustments={})
    for rho in (2.0, 3.0, 4.0):
        out['by_density'][f'{rho:g}'] = run(rho); print(rho, out['by_density'][f'{rho:g}'])
    # smallest parallel-body stretch that closes the interior at each density (keeps everything else)
    for rho in (3.0, 4.0):
        L = 12.8
        while run(rho, length=L)['residual_m3'] < 0 and L < 14.3: L = round(L + 0.02, 2)
        out['adjustments'][f'stretch_rho{rho:g}'] = run(rho, length=L); print('stretch', rho, out['adjustments'][f'stretch_rho{rho:g}'])
    json.dump(out, open(os.path.join(H, 'closure_v2.json'), 'w'), indent=1)
