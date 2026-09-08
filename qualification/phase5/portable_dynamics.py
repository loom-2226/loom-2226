from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable, Sequence, Tuple
import math

Vector3 = Tuple[float, float, float]
Matrix3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
Quaternion = Tuple[float, float, float, float]


class DynamicsError(ValueError):
    pass


def vadd(a: Vector3, b: Vector3) -> Vector3:
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def vsub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


def vscale(s: float, a: Vector3) -> Vector3:
    return (s*a[0], s*a[1], s*a[2])


def cross(a: Vector3, b: Vector3) -> Vector3:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def matvec(m: Matrix3, v: Vector3) -> Vector3:
    return tuple(sum(m[i][j]*v[j] for j in range(3)) for i in range(3))  # type: ignore[return-value]


def det3(m: Matrix3) -> float:
    return (
        m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
        - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
        + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0])
    )


def inv3(m: Matrix3) -> Matrix3:
    d = det3(m)
    if not math.isfinite(d) or abs(d) < 1e-15:
        raise DynamicsError("Inertia tensor is singular/non-finite")
    a,b,c = m[0]; d1,e,f = m[1]; g,h,i = m[2]
    adj = (
        (e*i-f*h, c*h-b*i, b*f-c*e),
        (f*g-d1*i, a*i-c*g, c*d1-a*f),
        (d1*h-e*g, b*g-a*h, a*e-b*d1),
    )
    return tuple(tuple(x/d for x in row) for row in adj)  # type: ignore[return-value]


def qmul(a: Quaternion, b: Quaternion) -> Quaternion:
    aw,ax,ay,az = a; bw,bx,by,bz = b
    return (
        aw*bw-ax*bx-ay*by-az*bz,
        aw*bx+ax*bw+ay*bz-az*by,
        aw*by-ax*bz+ay*bw+az*bx,
        aw*bz+ax*by-ay*bx+az*bw,
    )


def qnorm(q: Quaternion) -> Quaternion:
    n = math.sqrt(sum(x*x for x in q))
    if not math.isfinite(n) or n <= 0:
        raise DynamicsError("Invalid quaternion")
    return tuple(x/n for x in q)  # type: ignore[return-value]


def qrot(q_BN: Quaternion, v_B: Vector3) -> Vector3:
    q = qnorm(q_BN)
    p = (0.0, *v_B)
    qc = (q[0], -q[1], -q[2], -q[3])
    r = qmul(qmul(q, p), qc)
    return (r[1], r[2], r[3])


@dataclass(frozen=True)
class MassProperties:
    mass_kg: float
    com_B_m: Vector3
    inertia_B_kg_m2: Matrix3
    inertia_dot_B_kg_m2_s: Matrix3 = ((0.0,0.0,0.0),(0.0,0.0,0.0),(0.0,0.0,0.0))


@dataclass(frozen=True)
class VehicleState:
    t_s: float
    r_N_m: Vector3
    v_N_m_s: Vector3
    q_BN: Quaternion
    omega_B_rad_s: Vector3
    resource_kg: float = 0.0
    configuration: str = "DEFAULT"


@dataclass(frozen=True)
class EffectorCommand:
    force_B_N: Vector3 = (0.0,0.0,0.0)
    force_N_N: Vector3 = (0.0,0.0,0.0)
    application_B_m: Vector3 = (0.0,0.0,0.0)
    intrinsic_torque_B_Nm: Vector3 = (0.0,0.0,0.0)
    mass_flow_kg_s: float = 0.0


MassProvider = Callable[[VehicleState], MassProperties]
EffectorProvider = Callable[[VehicleState, MassProperties], Iterable[EffectorCommand]]


@dataclass(frozen=True)
class Derivative:
    dr: Vector3
    dv: Vector3
    dq: Quaternion
    domega: Vector3
    dresource: float


def _validate_mp(mp: MassProperties) -> None:
    if not math.isfinite(mp.mass_kg) or mp.mass_kg <= 0:
        raise DynamicsError("Mass must be finite and positive")
    if not all(math.isfinite(x) for x in mp.com_B_m):
        raise DynamicsError("CoM must be finite")
    inv3(mp.inertia_B_kg_m2)


def derivative(state: VehicleState, mass_provider: MassProvider, effector_provider: EffectorProvider) -> Derivative:
    mp = mass_provider(state)
    _validate_mp(mp)
    force_N: Vector3 = (0.0,0.0,0.0)
    torque_B: Vector3 = (0.0,0.0,0.0)
    mdot = 0.0
    for e in effector_provider(state, mp):
        if e.mass_flow_kg_s < 0 or not math.isfinite(e.mass_flow_kg_s):
            raise DynamicsError("mass_flow_kg_s must be finite and nonnegative")
        if e.mass_flow_kg_s > 0 and state.resource_kg <= 0:
            continue
        force_N = vadd(force_N, vadd(qrot(state.q_BN, e.force_B_N), e.force_N_N))
        torque_B = vadd(torque_B, vadd(cross(vsub(e.application_B_m, mp.com_B_m), e.force_B_N), e.intrinsic_torque_B_Nm))
        mdot += e.mass_flow_kg_s
    a_N = vscale(1.0/mp.mass_kg, force_N)
    Iw = matvec(mp.inertia_B_kg_m2, state.omega_B_rad_s)
    Idotw = matvec(mp.inertia_dot_B_kg_m2_s, state.omega_B_rad_s)
    rhs = vsub(vsub(torque_B, cross(state.omega_B_rad_s, Iw)), Idotw)
    domega = matvec(inv3(mp.inertia_B_kg_m2), rhs)
    dq = qmul(state.q_BN, (0.0, *state.omega_B_rad_s))
    dq = tuple(0.5*x for x in dq)  # type: ignore[assignment]
    return Derivative(state.v_N_m_s, a_N, dq, domega, -mdot)


def _advance_state(s: VehicleState, d: Derivative, h: float) -> VehicleState:
    return VehicleState(
        t_s=s.t_s+h,
        r_N_m=vadd(s.r_N_m, vscale(h,d.dr)),
        v_N_m_s=vadd(s.v_N_m_s, vscale(h,d.dv)),
        q_BN=qnorm(tuple(s.q_BN[i]+h*d.dq[i] for i in range(4))),
        omega_B_rad_s=vadd(s.omega_B_rad_s, vscale(h,d.domega)),
        resource_kg=max(0.0, s.resource_kg+h*d.dresource),
        configuration=s.configuration,
    )


def rk4_step(state: VehicleState, dt: float, mass_provider: MassProvider, effector_provider: EffectorProvider, *, pre_event_left_limit: bool=False) -> VehicleState:
    if dt <= 0 or not math.isfinite(dt):
        raise DynamicsError("dt must be finite and positive")
    def deval(s: VehicleState) -> Derivative:
        if pre_event_left_limit and s.resource_kg <= 0:
            s = replace(s, resource_kg=1e-12)
        return derivative(s, mass_provider, effector_provider)
    k1 = deval(state)
    k2 = deval(_advance_state(state,k1,dt/2))
    k3 = deval(_advance_state(state,k2,dt/2))
    k4 = deval(_advance_state(state,k3,dt))
    def comb(a,b,c,d): return (a+2*b+2*c+d)/6
    return VehicleState(
        t_s=state.t_s+dt,
        r_N_m=tuple(state.r_N_m[i]+dt*comb(k1.dr[i],k2.dr[i],k3.dr[i],k4.dr[i]) for i in range(3)),
        v_N_m_s=tuple(state.v_N_m_s[i]+dt*comb(k1.dv[i],k2.dv[i],k3.dv[i],k4.dv[i]) for i in range(3)),
        q_BN=qnorm(tuple(state.q_BN[i]+dt*comb(k1.dq[i],k2.dq[i],k3.dq[i],k4.dq[i]) for i in range(4))),
        omega_B_rad_s=tuple(state.omega_B_rad_s[i]+dt*comb(k1.domega[i],k2.domega[i],k3.domega[i],k4.domega[i]) for i in range(3)),
        resource_kg=max(0.0, state.resource_kg+dt*comb(k1.dresource,k2.dresource,k3.dresource,k4.dresource)),
        configuration=state.configuration,
    )


def propagate(state: VehicleState, duration_s: float, dt_s: float, mass_provider: MassProvider, effector_provider: EffectorProvider) -> Sequence[VehicleState]:
    if duration_s < 0 or not math.isfinite(duration_s):
        raise DynamicsError("duration must be finite and nonnegative")
    n_float = duration_s/dt_s if dt_s else float('inf')
    n = int(round(n_float))
    if abs(n*dt_s-duration_s) > 1e-12:
        raise DynamicsError("duration_s must be an integer multiple of dt_s for deterministic qualification")
    trace = [state]
    cur = state
    for _ in range(n):
        d0 = derivative(cur, mass_provider, effector_provider)
        if cur.resource_kg > 0 and d0.dresource < 0:
            h_event = cur.resource_kg / (-d0.dresource)
        else:
            h_event = math.inf
        if h_event <= dt_s + 1e-12:
            h1 = min(dt_s, max(0.0, h_event))
            if h1 > 1e-15:
                cur = rk4_step(cur, h1, mass_provider, effector_provider, pre_event_left_limit=True)
                cur = replace(cur, resource_kg=0.0)
            h2 = dt_s - h1
            if h2 > 1e-15:
                cur = rk4_step(cur, h2, mass_provider, effector_provider)
        else:
            cur = rk4_step(cur,dt_s,mass_provider,effector_provider)
        trace.append(cur)
    return trace
