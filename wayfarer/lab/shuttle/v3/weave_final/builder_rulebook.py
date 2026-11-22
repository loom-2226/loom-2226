"""Builder Tic Tac rulebook, derived from the lane's speculative physics (fiction-first, NON-CANON).
ALL bodies. ALL sponsors. 2026-2226.

Every rule carries its status (corrected after Sol's review of 0db5da0):
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
def equal_pull(a, m_small, m_big): q = math.sqrt(m_small / m_big); return a * q / (1 + q)
earth_eq, moon_eq = equal_pull(A_E, GM_E, GM_SUN), equal_pull(A_M, GM_M, GM_E)
sun_vs_earth_on_moon = (GM_SUN / A_E ** 2) / (GM_E / A_M ** 2)
D_ = 'DERIVED within the adopted field model'; NB = 'NEW BUILDER PERMISSION'; CH = 'CONDITIONAL HYPOTHESIS'; OR = 'CHOSEN OPERATING RULE'
derivation = [
 dict(rule='R1 The Weave shift moves her without changing her velocity; carries her air; quiet while the field edge is subsonic', status=D_,
      basis='slow-geodesic law dw/dt = -(grad b) w is homogeneous (WEAVE_GEOMETRY_COMPARE; continuous_hull_screen B); ideal-fluid transport; edge Mach limit'),
 dict(rule='R2 Directional W2 changes her velocity only while the field travels with her; it pushes her through the air (drag, wake)', status=D_,
      basis='potential-type field: lasting velocity when co-moving, returned when fixed (continuous_hull_screen C; lapse dash). Directional use itself is the experimental grant (Sol, after b99d437)'),
 dict(rule='R3 The hull can perform local Loom hops (relocation with a route-transformed arrival state, configuration locked during commit)', status=NB,
      basis="canon sec. 12 gives the human Loom (Q_B = T_AB(Q_A), sec. 12.1 commit lock, interstellar role in sec. 18A). A local Builder hop through a 153 m2 hull boundary is a new permission; the area comparison with Wayfarer's ~1,900 m2 does not establish it"),
 dict(rule='R4 Every mode exchanges with an external partner; none is isolated', status=D_,
      basis='ADM charges of a compact field vanish; an isolated displacement violates the boost charge (WEAVE_SOURCE_CLOSURE)'),
 dict(rule='R5 A ledger: her relational state records the net ordinary work done on her, linearly (kappa x delta rho), in one record frame', status=CH,
      basis='one accounting model that excludes free-work cycles (builder_cycle_screen L1). Not forced: a partner supplying the energy (e.g. the Sun-partner route), a global field state, a nonlinear cost or a finite environmental exchange would also exclude them'),
 dict(rule='R6 Locality: no field operation spans a change of partner frame; she crosses such boundaries by coasting', status=OR,
      basis='frame-dependence of work does NOT require the field to stop where the partner changes; this is an adopted restriction. Its boundary depends on the partner criterion, not yet chosen (P2: equal pull and Laplace give different boundaries)'),
 dict(rule='R7 Natural arrival keeps her velocity in the partner frame', status=OR,
      basis='canon leaves T_AB unspecified; this arrival rule is a choice, not a consequence of minimum energy'),
 dict(rule='R8 Bounded accessible range; operations refused at the edge', status=CH,
      basis='postulate P3 (RT-C1-inspired), conditional on the R5 ledger model. Its size is NOT set: a one-number budget would be an invisible tank (Sol)'),
 dict(rule='R9 Coming home by field restores the record; shedding energy into the world leaves it displaced', status=CH,
      basis='true within the R5 ledger model (route dependence, cf. RT-B1); not a general consequence'),
 dict(rule='R10 Route library: a hop needs a surveyed route', status=OR,
      basis='motivated by canon sec. 12.1 (certification against a specific configuration) and RT SHG1 (locally identical, globally different); requiring a survey is a design rule'),
 dict(rule='R11 The crew knows what has been spent, not what is left', status=CH, basis='follows within the R5 ledger plus P3'),
 dict(rule='R12 Wear and stability per hop unknown; humans cannot service the module', status='OPEN (narrative)', basis='no model constrains it'),
]
open_items = ['restoration of a spent record (unwind only, or environmental relaxation paid physically): not decided by any theory (builder_cycle_screen)',
              'kappa x rho_max: the one Builder parameter; a kT choice',
              'local heat of each mode: unknown',
              'which body is "force-dominant" near boundaries (Earth-Moon L1 region): P2 needs a tie rule']
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, postulates={
    'P1': 'the continuous active hull is the W2/Weave interface (design hypothesis); as a Loom boundary it is part of the R3 new permission',
    'P2': 'partner/record frame selection: NOT YET CHOSEN. 0db5da0 conflated two criteria: equal pull (Earth-Sun boundary 259,000 km from Earth; Earth-Moon 38,400 km from the Moon; the Sun pulls the Moon 2.2x harder than Earth, so the Moon region is Sun-frame) versus Laplace sphere of influence (patched-conic perturbation ratio: Earth 924,700 km, Moon 66,200 km)',
    'P3': 'the accessible relational range is bounded'},
    rules=derivation, numbers=dict(force_ratio_earth_vs_sun_at_surface=round(f_ratio), potential_ratio_sun_vs_earth_at_surface=round(p_ratio, 1),
    earth_soi_km=round(earth_soi / 1e3), earth_equal_pull_km=round(earth_eq / 1e3), moon_equal_pull_km=round(moon_eq / 1e3), sun_vs_earth_pull_on_moon=round(sun_vs_earth_on_moon, 2), earth_hill_km=round(earth_hill / 1e3), moon_soi_km=round(moon_soi / 1e3), moon_hill_km=round(moon_hill / 1e3),
    hop_ledger_TJ={k: round(v / 1e12, 4) for k, v in hops.items()}, hop_ledger_note='CONDITIONAL EXAMPLES: endpoint change of ordinary mechanical energy under the R5 ledger and the R7 arrival rule; not the cost of forming or controlling a Loom transition, and not local dissipation'), open_items=open_items)
json.dump(out, open(os.path.join(H, 'builder_rulebook.json'), 'w'), indent=1)
print(json.dumps(out['numbers'], indent=1))
