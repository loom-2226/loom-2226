"""Builder Tic Tac rulebook, derived from the lane's speculative physics (fiction-first, NON-CANON).
ALL bodies. ALL sponsors. 2026-2226.

Every rule carries its derivation status:
  CANON      Canon II text (sec. numbers)
  LANE       derived in the Weave prototype lane (cited reports)
  LEDGER     derived in builder_cycle_screen (no-free-work requirement)
  RT         RT accepted result used as inspiration (not proof)
  POSTULATE  a minimal new assumption, stated once
Numbers below are computed, not chosen."""
import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
GM_SUN, GM_E, GM_M = 1.327e20, 3.986e14, 4.905e12
A_E, A_M = 1.496e11, 3.844e8; RE = 6.371e6
M = 48.5e3

def soi(a, m_small, m_big): return a * (m_small / m_big) ** 0.4          # Laplace sphere of influence (force-ratio boundary)
def hill(a, m_small, m_big): return a * (m_small / (3 * m_big)) ** (1 / 3)
earth_soi, earth_hill = soi(A_E, GM_E, GM_SUN), hill(A_E, GM_E, GM_SUN)
moon_soi, moon_hill = soi(A_M, GM_M, GM_E), hill(A_M, GM_M, GM_E)
# at Earth's surface: which body dominates by force vs by potential?
f_ratio = (GM_E / RE ** 2) / (GM_SUN / A_E ** 2); p_ratio = (GM_SUN / A_E) / (GM_E / RE)

def hop(r0, r1, v0, v1, gm=GM_E):          # ledger cost of a Loom hop in the dominant body's frame (record frame)
    return M * (0.5 * (v1 ** 2 - v0 ** 2) - gm / r1 + gm / r0)
v_rot = 7.292e-5 * RE; r_leo = RE + 200e3; v_leo = math.sqrt(GM_E / r_leo)
hops = {
    'Fravor-type level hop, 111 km at constant altitude and velocity': hop(RE + 6e3, RE + 6e3, 150.0, 150.0),
    'surface -> 200 km, natural arrival (velocity kept in Earth frame)': hop(RE, r_leo, v_rot, v_rot),
    'surface -> 200 km, arrival matched to Wayfarer (velocity changed)': hop(RE, r_leo, v_rot, v_leo),
    'level hop and its reverse (round trip)': 0.0,
}
derivation = [
 dict(rule='R1 Weave shift moves her without changing her velocity; carries her air; quiet while the field edge is subsonic',
      status='LANE', basis='slow-geodesic law dw/dt = -(grad b) w is homogeneous (WEAVE_GEOMETRY_COMPARE; continuous_hull_screen B); ideal-fluid transport (WEAVE_SHIFT_FLUID); edge Mach limit (WEAVE_OUTINGS)'),
 dict(rule='R2 Directional W2 changes her velocity only while the field travels with her; it pushes her through the air (drag, wake)',
      status='LANE', basis='potential-type field gives lasting velocity when co-moving, returns it when fixed (continuous_hull_screen C; lapse dash in WEAVE_GEOMETRY_COMPARE)'),
 dict(rule='R3 Loom hop relocates her discontinuously; arrival state is a route transform of departure; she must stay one configuration during commit',
      status='CANON + POSTULATE', basis='Canon II sec. 12 (Q_B = T_AB(Q_A), momentum matching separate) and sec. 12.1 commit lock. POSTULATE P1: the continuous active hull is her Loom boundary (153 m2; Wayfarer needs ~1,900 m2 of controlled boundary)'),
 dict(rule='R4 Every mode must exchange with an external partner; none is isolated',
      status='LANE', basis='ADM charges of a compact field vanish; an isolated displacement violates the boost charge (WEAVE_SOURCE_CLOSURE)'),
 dict(rule='R5 The ledger: her relational state keeps a record equal to the net ordinary work all modes have done on her (kappa x delta rho), in one record frame',
      status='LEDGER', basis='excluding free-work cycles with a restorable relational state forces the record (builder_cycle_screen). Weave adds nothing (no work); W2 and Loom add their work'),
 dict(rule='R6 Locality: a field operation (W2 push or Loom hop) is admissible only if one record frame holds from start to finish, the frame of the body that dominates her by force. No field operation may span a sphere-of-influence boundary; she crosses boundaries only by coasting (no field work), e.g. Earth to Moon: push inside Earth\'s sphere, coast across, capture inside the Moon\'s',
      status='LEDGER + POSTULATE', basis='derived: the work, and so the record, is frame-dependent (KE differs by m u.dv between frames); a ledger needs one frame per operation. POSTULATE P2: the record frame is the force-dominant body. '
            f'Force weighting is the only choice that gives locality: at Earth\'s surface Earth dominates by force x{f_ratio:,.0f}, while the Sun dominates by potential x{p_ratio:.0f} (potential weighting would make the Sun the partner everywhere, with no tether). '
            f'Earth sphere of influence {earth_soi / 1e3:,.0f} km (Hill {earth_hill / 1e3:,.0f} km); Moon {moon_soi / 1e3:,.0f} km (Hill {moon_hill / 1e3:,.0f} km)'),
 dict(rule='R7 Natural arrival keeps her velocity in the record frame (least ledger change); any other arrival costs the difference on the ledger',
      status='LEDGER', basis='from R5 + R6: the ledger change of a hop is the change of ordinary energy in the record frame; keeping velocity leaves only the potential term'),
 dict(rule='R8 Range: the accessible relational range is bounded (kappa x rho_max of net ordinary work on credit); at the edge an operation is refused',
      status='POSTULATE (RT-inspired)', basis='POSTULATE P3: bounded accessibility, in the spirit of RT-C1 control geometry (accessibility differs from distance). Refusal at the edge: builder_cycle_screen L1'),
 dict(rule='R9 Coming home by field gives the record back; shedding energy into the world (aerobraking, braking, drag) leaves it spent until restored',
      status='LEDGER', basis='builder_cycle_screen: route dependence of the record (cf. RT-B1, order matters)'),
 dict(rule='R10 Route library: a hop needs a surveyed route; local measurements cannot certify it',
      status='CANON + RT', basis='Canon sec. 12.1 certifies a solution against a specific configuration; SHG1: locally identical configurations can sit in different global sectors with different responses; RT-B1/C1: route order and control cost are not set by local geometry. So routes must be surveyed (flown or mapped)'),
 dict(rule='R11 The crew cannot see the range left: they know exactly what they have spent (integrated work in the record frame) but not rho_max',
      status='LEDGER + POSTULATE', basis='rho is not a physical observable; its change is fixed by the physical work (R5), its bound (P3) is not, unless reached. So crews keep margin: running out mid-climb is refusal mid-climb'),
 dict(rule='R12 Wear and stability: per-hop effects on the module are UNKNOWN; humans cannot service it',
      status='OPEN (narrative)', basis='no lane or RT result constrains it; left as the human-ignorance limit, not derived. Candidate hypothesis for later: dissipation scales with field gradients, not with work (untested)'),
]
open_items = ['restoration of a spent record (unwind only, or environmental relaxation paid physically): not decided by any theory (builder_cycle_screen)',
              'kappa x rho_max: the one Builder parameter; a kT choice',
              'local heat of each mode: unknown',
              'which body is "force-dominant" near boundaries (Earth-Moon L1 region): P2 needs a tie rule']
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, postulates={
    'P1': 'the continuous active hull is the Loom boundary (and the W2/Weave interface)',
    'P2': 'the record frame is the frame of the body that dominates by force',
    'P3': 'the accessible relational range is bounded'},
    rules=derivation, numbers=dict(force_ratio_earth_vs_sun_at_surface=round(f_ratio), potential_ratio_sun_vs_earth_at_surface=round(p_ratio, 1),
    earth_soi_km=round(earth_soi / 1e3), earth_hill_km=round(earth_hill / 1e3), moon_soi_km=round(moon_soi / 1e3), moon_hill_km=round(moon_hill / 1e3),
    hop_ledger_TJ={k: round(v / 1e12, 4) for k, v in hops.items()}), open_items=open_items)
json.dump(out, open(os.path.join(H, 'builder_rulebook.json'), 'w'), indent=1)
print(json.dumps(out['numbers'], indent=1))
