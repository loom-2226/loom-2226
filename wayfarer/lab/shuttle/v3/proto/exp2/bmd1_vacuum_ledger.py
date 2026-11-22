"""BMD-1 vacuum-first ledger: who is the partner, and what does that do to the energy the device must handle?
NON-CANON prototype lane. ALL bodies. ALL sponsors. 2026-2226.
Physics used: for a force F exchanged with a partner of mass M >> m, the energy the coupling must deliver is the work done in the
PARTNER's rest frame, P = F . v_rel (v_rel = domain velocity relative to the partner). Frame choice is not free: it is fixed by the partner."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
G = 9.81; m = 61e3; F = 1.5 * m * G; t = 9.0; a = 0.5 * G; dv = a * t; dh = 0.5 * a * t * t
local = F * dh                                                   # field work in Earth's frame, vertical lift
rows = []
for name, w, note in (('Earth (centre-of-mass frame), vertical lift', 0.0, 'rotation velocity is horizontal, perpendicular to the lift'),
                      ('Earth, lateral push at the equator (rotation 465 m/s)', 465.0, 'sideways W2 manoeuvre, worst alignment'),
                      ('Moon partner while near Earth (Moon 1.02 km/s vs Earth)', 1020.0, 'wrong partner selected'),
                      ('Sun (canon §7.1b partner), lift at dawn/dusk', 29.8e3, 'vertical ~ along Earth orbital velocity'),
                      ('Sun, lift at noon/midnight', 0.0, 'vertical ~ Sun-radial, perpendicular to orbital velocity')):
    extra = F * w * t                                            # |F . w| t, worst-case sign
    rows.append(dict(partner=name, v_rel_ms=w, peak_power_W=F * (w + dv), energy_GJ_range=f'{(local - extra) / 1e9:+.2f} to {(local + extra) / 1e9:+.2f}', note=note))
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) BMD-1',
  lift=dict(mass_t=61, force_MN=round(F / 1e6, 3), time_s=t, height_m=round(dh, 1), speed_ms=round(dv, 1), field_work_earth_frame_MJ=round(local / 1e6),
            impulse_field_MNs=round(F * t / 1e6, 2), impulse_gravity_MNs=round(-m * G * t / 1e6, 2), net_MNs=round(m * dv / 1e6, 2), partner_receives_MNs=round(-F * t / 1e6, 2)),
  partners=rows,
  finding='The ledger closes for any partner, but the device energy is F . v_rel in the partner frame. With the canon Sun partner a 0.9 MN lift near Earth swings by about '
          '+/-240 GJ in 9 s (~27 GW peak, vs 40 MW for the lift itself) depending on local time, ~1,000x the 0.18 GJ of the lift itself. Run in reverse it mines Earth\'s orbital energy, which collides in practice with '
          'the §7.3 no-free-work firewall. A shuttle-scale W2 needs the partner to be the local dominant body (or the source of the local gravitational field).',
  discriminating_observable='device energy draw vs relative velocity to candidate partners: a Sun partner shows a time-of-day swing of +/-27 GW at 0.9 MN; a local partner shows only F . v_local')
json.dump(out, open(os.path.join(H, 'bmd1_vacuum_ledger.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(out['lift'])
    for r in rows: print(f"{r['partner']:58s} v_rel {r['v_rel_ms']:8.0f}  peak {r['peak_power_W']/1e9:10.3f} GW  energy {r['energy_GJ_range']} GJ")
