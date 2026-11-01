"""Opt-in, NON-CANON single-leg Metric Arrival Law v1 (ENERGY + orbit-frame B).
Only used when a flight experiment explicitly sets enable_metric_arrival_law_v1.
Frozen endpoint potential is an assumption, NOT a time-dependent Killing law.
The Metric miracle is the declared E/p/L exchange; no local coupler is claimed.
"""
import math
# CCR-2026-0003: default selection for NEW lab Metric experiments only.
# Existing source-pinned qualifications and canonical HOLD remain untouched.
NEW_LAB_METRIC_ARRIVAL_DEFAULT = "ENERGY_ORBIT_RELATIVE_B"

def new_lab_metric_arrival_rule(experiment=None):
    """Resolve a NEW lab experiment's explicit rule or the scoped ENERGY-B default.

    Deliberately not used to reinterpret old FQ1-FQ10 fixtures or Navigator.
    """
    return (experiment or {}).get("arrival_rule", NEW_LAB_METRIC_ARRIVAL_DEFAULT)

import numpy as np
from scipy.integrate import solve_ivp

AU_KM=149597870.7
DAY_S=86400.0
C_KM_S=299792.458
G0=9.80665
FROZEN_CAVEAT=("FROZEN POTENTIAL, NOT AN EXACT KILLING ENERGY in a moving Sun/planet system. "
               "Sun-only moving ephemerides; approximate Sun-barycentric counting frame. "
               "Lab accounting is not a qualified physical momentum/torque coupler.")
def norm(v):return float(np.linalg.norm(v))
def unit(v):
    n=norm(v)
    if n<1e-12:raise ValueError("undefined zero-velocity heading")
    return np.asarray(v,dtype=float)/n
def frame(r,v):
    e_r=unit(r)
    e_t=unit(v-np.dot(v,e_r)*e_r)
    return np.column_stack((e_r,e_t,unit(np.cross(e_r,e_t))))
def planetary_state(src,gm_sun,t):
    y=np.array(src["position_au"]+src["velocity_au_day"],float)
    y[:3]*=AU_KM
    y[3:]*=AU_KM/DAY_S
    if t==0:return y[:3],y[3:]
    def dynamics(_,q):
        r=q[:3];rr=norm(r)
        return np.r_[q[3:],-gm_sun*r/(rr**3)]
    solution=solve_ivp(dynamics,(0.,t),y,rtol=3e-12,atol=2e-9,method="DOP853")
    if not solution.success:raise RuntimeError(solution.message)
    return solution.y[:3,-1],solution.y[3:,-1]
def hill_half(p,gm,gm_sun):
    return .5*norm(p)*(gm/(3*gm_sun))**(1./3.)
def phi(p,gm_body,gm_sun):
    return -gm_sun/norm(p)-gm_body/hill_half(p,gm_body,gm_sun)
def metric_elapsed(p0,dst,mu,mode):
    beta=mode["beta"];ramp=mode["ramp_s"]
    if not 0<beta<1:raise ValueError("metric card beta invalid")
    t=norm(np.array(dst["position_au"])*AU_KM-p0)/(beta*C_KM_S)+ramp
    for _ in range(14):
        q,_=planetary_state(dst,mu,t)
        new=norm(q-p0)/(beta*C_KM_S)+ramp
        if abs(new-t)<1e-9:break
        t=new
    return t
def calculate_fq11(ship,experiment):
    """CALC ONLY: inverse-arrival analytic preview, not a flightlab qualification.
    Impulsive paid torch preburn; Metric NORMAL moves endpoint in time.
    Matching arrival and balancing E/p/L are algebraic identities by construction.
    """
    if not experiment.get("enable_metric_arrival_law_v1",False):
        raise ValueError("FQ11 may not execute without explicit opt-in")
    phase=experiment.get("phases",[])
    if [p["kind"] for p in phase]!=["torch","metric","arrival_match"]:
        raise ValueError("FQ11 requires torch, metric, arrival_match in order")
    if phase[0].get("mode")!="CRUISE" or phase[1].get("mode")!="NORMAL":
        raise ValueError("FQ11 only validates CRUISE/NORMAL")
    if phase[1].get("model")!="lab_energy_v1" or phase[1].get("arrival_rule")!="ENERGY_ORBIT_RELATIVE_B":
        raise ValueError("FQ11 must explicitly select the ENERGY B lab card")
    card=ship["metric"].get("lab_energy_v1")
    if not card or card["law"]!="energy_orbit_relative_v1" or card.get("enabled_by_default") is not False:
        raise ValueError("FQ11 requires a separate default-off lab Metric card")
    if ship["metric"]["canonical"]["law"]!="canonical_envelope":
        raise ValueError("canonical Metric HOLD may not be replaced")
    env=experiment["metric_arrival_v1"]
    if env.get("source_id")!="EA" or env.get("destination_id")!="MA":
        raise ValueError("FQ11 is scoped to Earth->Mars only")
    src=env["source_snapshot"]
    if src["geometry_sha256"]!=ship["provenance"]["geometry_sha256"]:
        raise ValueError("geometry mismatch")
    if src["main_commit"]!=env["main_commit"]:
        raise ValueError("main mismatch")
    mu=float(src["sun_gm_km3_s2"]);sun_mass=float(src["sun_mass_kg"])
    Earth=src["bodies"]["EA"];Mars=src["bodies"]["MA"]
    p0,v0h=planetary_state(Earth,mu,0.)
    t=metric_elapsed(p0,Mars,mu,card["modes"]["NORMAL"])
    p1,v1h=planetary_state(Mars,mu,t)
    ref=np.asarray(src["solar_reflex_approx_km_s"],float)
    v0=v0h+ref;v_target=v1h+ref
    phi0=phi(p0,Earth["gm_km3_s2"],mu)
    phi1=phi(p1,Mars["gm_km3_s2"],mu)
    F0=frame(p0,v0h);F1=frame(p1,v1h)
    needed_speed2=norm(v_target)**2+2*(phi1-phi0)
    if needed_speed2<=0:raise ValueError("ENERGY forbids this endpoint without more preburn")
    before_dir=unit(F0@F1.T@v_target)
    v_pre=math.sqrt(needed_speed2)*before_dir
    # Paid vector torch burn, exact rocket remass with existing source card.
    dv_out=norm(v_pre-v0)
    mode=ship["torch"][0]["modes"]["CRUISE"]
    ve=float(mode["ve_m_s"])/1000
    m0=float(ship["base"]["mass_kg"])+sum(float(tk["initial_kg"]) for tk in ship["tanks"])
    # FQ11 uses the already-source-fixed S1 fixture with no extra dry components.
    if ship.get("components"):raise ValueError("FQ11 fixture must have fixed original mass")
    m1=m0*math.exp(-dv_out/ve)
    consumed=m0-m1
    remass0=float(ship["tanks"][0]["initial_kg"])
    floor=float(env["rcs_reserve_kg"])
    remass1=remass0-consumed
    if remass1<floor:raise ValueError("FQ11 torch would breach 5t RCS floor")
    burn_s=consumed/float(mode["working_card_mdot_kg_s"])
    # Orbit-relative heading transport, energy magnitude; actual arrival velocity.
    q=F0.T@unit(v_pre)
    s2=norm(v_pre)**2+2*(phi0-phi1)
    if s2<=0:raise ValueError("ENERGY arrival speed not positive")
    v_post=math.sqrt(s2)*(F1@q)
    dv_in=norm(v_post-v_target)

    # E/p/L conservation for ideal impulsive torch plume and Metric transition.
    # Torch energy is sourced from a declared fusion reservoir, not closed hardware.
    U=unit(v_pre-v0)
    dp_torch_ship=(m1*v_pre-m0*v0)*1000.
    dp_torch_exhaust=-dp_torch_ship
    # Kinetic energy in ideal exhaust; midpoint quadrature, only for energy budget.
    N=1000
    dm=consumed/N
    exhaust_K=0.
    for i in range(N):
        mass=m0-(i+.5)*dm
        vjet=v0+ve*math.log(m0/mass)*U-ve*U
        exhaust_K+=.5*dm*norm(vjet*1000.)**2
    delta_ship_K_torch=.5*(m1*norm(v_pre*1000.)**2-m0*norm(v0*1000.)**2)
    fusion_source_debit=delta_ship_K_torch+exhaust_K
    torch_energy_residual=delta_ship_K_torch+exhaust_K-fusion_source_debit

    dp_metric=m1*(v_post-v_pre)*1000.
    sun_dp=-dp_metric
    sun_recoil=sun_dp/sun_mass
    recoil_E=norm(sun_dp)**2/(2*sun_mass)
    r0=p0*1000.;r1=p1*1000.
    dL_ship=np.cross(r1,m1*v_post*1000.)-np.cross(r0,m1*v_pre*1000.)
    sun_spin_dL=-np.cross(r0,dp_metric)
    sun_orbit_dL=-np.cross((r1-r0),m1*v_post*1000.)
    sun_dL=sun_spin_dL+sun_orbit_dL
    delta_ship_E_metric=m1*(.5*(norm(v_post*1000.)**2-norm(v_pre*1000.)**2)+(phi1-phi0)*1e6)
    sun_field_energy=-(delta_ship_E_metric+recoil_E)
    # Exact signed ledger sums (per the declared nonlocal mechanism).
    p_error=norm(dp_metric+sun_dp)
    L_error=norm(dL_ship+sun_dL)
    E_error=delta_ship_E_metric+recoil_E+sun_field_energy
    torch_p_error=norm(dp_torch_ship+dp_torch_exhaust)
    torch_L_error=norm(np.cross(r0,dp_torch_ship+dp_torch_exhaust))
    mass_error=m0-(m1+consumed)
    limits={"remass_residual_kg":1e-6,"arrival_error_m_s":float(env["arrival_match_tolerance_m_s"]),
            "energy_residual_J":1e-4,"momentum_residual_N_s":1e-3,
            "angular_residual_N_m_s":1e7}
    # Angular momenta are ~1e27 N m s; absolute residual is from floating cancellation.
    tests={"remass_closes":abs(mass_error)<=limits["remass_residual_kg"] and remass1>=floor,
           "arrival_matches":dv_in*1000<=limits["arrival_error_m_s"],
           "energy_ledger_closes":abs(E_error)<=limits["energy_residual_J"] and abs(torch_energy_residual)<=limits["energy_residual_J"],
           "momentum_ledger_closes":p_error<=limits["momentum_residual_N_s"] and torch_p_error<=limits["momentum_residual_N_s"],
           "angular_ledger_closes":L_error<=limits["angular_residual_N_m_s"] and torch_L_error<=limits["angular_residual_N_m_s"]}
    # Preview only: do not claim algebraically forced closure is a measured pass.
    identities={k:tests[k] for k in ("arrival_matches","energy_ledger_closes","momentum_ledger_closes","angular_ledger_closes")}
    measurements={"remass_budget":tests["remass_closes"]}
    return {
        "fq":"FQ11-CALC","name":"Earth -> Mars inverse-map preview; NOT a flight qualification",
        "classification":"LAB_ONLY_NON_CANON_NOT_NAVIGATOR",
        "enabled":True,"status":"CALC_IDENTITY_PREVIEW","qualified":False,
        "measurements":measurements,"identities_by_construction":identities,"thresholds":limits,
        "provenance":{"main_commit":src["main_commit"],"geometry_sha256":src["geometry_sha256"],
                      "epoch":src["epoch_utc"],"ephemeris_source":src["ephemeris_source"]},
        "phases":[{"kind":"torch","card":"CRUISE","impulsive_dv_km_s":dv_out,"nominal_burn_duration_s":burn_s,
                   "remass_used_kg":consumed,"mass_before_kg":m0,"mass_after_kg":m1},
                  {"kind":"metric","mode":"NORMAL","arrival_rule":"ENERGY_ORBIT_RELATIVE_B",
                   "duration_s":t,"pre_velocity_km_s":v_pre.tolist(),"post_velocity_km_s":v_post.tolist()},
                  {"kind":"arrival_match","target":"Mars","dv_km_s":dv_in,
                   "velocity_error_m_s":dv_in*1000}],
        "state":{"final_remass_kg":remass1,"reserve_margin_kg":remass1-floor,
                 "target_velocity_km_s":v_target.tolist(),"arrival_velocity_km_s":v_post.tolist()},
        "ledger":{
           "torch":{"remass_used_kg":consumed,"mass_residual_kg":mass_error,
                    "exhaust_momentum_N_s":dp_torch_exhaust.tolist(),
                    "momentum_residual_N_s":torch_p_error,"angular_residual_N_m_s":torch_L_error,
                    "declared_fusion_source_energy_J":fusion_source_debit,
                    "energy_residual_J":torch_energy_residual},
           "metric":{"frozen_phi_depart_km2_s2":phi0,"frozen_phi_arrive_km2_s2":phi1,
                     "ship_energy_change_J":delta_ship_E_metric,
                     "sun_recoil_energy_J":recoil_E,"sun_field_energy_work_J":sun_field_energy,
                     "energy_residual_J":E_error,"ship_impulse_N_s":dp_metric.tolist(),
                     "sun_impulse_N_s":sun_dp.tolist(),"momentum_residual_N_s":p_error,
                     "sun_recoil_m_s":sun_recoil.tolist(),
                     "sun_recoil_magnitude_m_s":norm(sun_recoil),
                     "sun_spin_dL_N_m_s":sun_spin_dL.tolist(),
                     "sun_orbit_dL_N_m_s":sun_orbit_dL.tolist(),
                     "sun_total_dL_N_m_s":sun_dL.tolist(),
                     "sun_spin_dL_magnitude_N_m_s":norm(sun_spin_dL),
                     "sun_orbit_dL_magnitude_N_m_s":norm(sun_orbit_dL),
                     "sun_total_dL_magnitude_N_m_s":norm(sun_dL),
                     "angular_residual_N_m_s":L_error}},
        "limitations":[FROZEN_CAVEAT,"Sun's E/p/L transfer is bookkeeping for the Metric miracle, not a local coupling mechanism.",
                       "Transport term is required when source and destination position differ.",
                       "Pre-jump vector burn is ideal impulsive; duration informational only; full fusion/plume hardware not qualified.",
                       "0.5 Hill is a diagnostic boundary, not Metric admissibility policy.",
                       "Planetary propagation Sun-only; no N-body gravitational work ledger or orbital capture."]}
