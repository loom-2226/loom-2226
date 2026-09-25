#!/usr/bin/env python3
"""Build explicit post-NAIF-horizon Solar propagation SPKs.

The initial state is read from the last accepted NAIF satellite kernel.  The
system is then integrated in barycentric coordinates with fixed-step RK4,
mutual gravity, and the DE440 external-body tidal field.  The output is a
NAIF type-9 SPK, explicitly marked as propagated rather than direct JPL
authority by the repository manifest and database migration.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import spiceypy as spice

AU_KM = 149_597_870.700
FRAME = "ECLIPJ2000"
GMS = {
    10: 132_712_440_017.99,
    599: 126_686_531.900,
    501: 5_959.916,
    502: 3_202.739,
    503: 9_887.834,
    504: 7_179.289,
    999: 872.4,
    901: 101.4,
}


def et(iso: str) -> float:
    return float(spice.str2et(iso.replace("Z", "")))


def iso_et(value: float) -> str:
    return spice.et2utc(value, "ISOC", 3).replace(" ", "") + "Z"


def external_table(center: int, start: float, end: float, step: float = 86_400.0):
    bodies = [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    times = np.arange(start, end + step * 0.5, step, dtype=float)
    values = np.empty((len(times), len(bodies), 3), dtype=float)
    for i, t in enumerate(times):
        for j, body in enumerate(bodies):
            values[i, j] = spice.spkgeo(body, float(t), FRAME, center)[0][:3]
    return times, bodies, values


def external_positions(table, t: float) -> np.ndarray:
    times, bodies, values = table
    idx = int(np.searchsorted(times, t, side="right") - 1)
    idx = max(0, min(idx, len(times) - 2))
    f = (t - times[idx]) / (times[idx + 1] - times[idx])
    return values[idx] * (1.0 - f) + values[idx + 1] * f


def acceleration(state: np.ndarray, t: float, center: int, table) -> np.ndarray:
    pos = state[:, :3]
    masses = np.asarray([GMS[b] for b in TARGETS[center]], dtype=float)
    delta = pos[None, :, :] - pos[:, None, :]
    distance = np.linalg.norm(delta, axis=2)
    inv_r3 = np.divide(1.0, distance ** 3, out=np.zeros_like(distance), where=distance > 0)
    out = np.sum(delta * inv_r3[:, :, None] * masses[None, :, None], axis=1)
    # External DE440 bodies contribute their differential acceleration relative
    # to the selected system barycenter.  The central body is omitted when it
    # is the system itself.
    ext = external_positions(table, t)
    external_bodies = np.asarray([10, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    ext_masses = np.asarray([0.0 if body == center else GMS.get(int(body), 0.0)
                             for body in external_bodies], dtype=float)
    d1 = ext[None, :, :] - pos[:, None, :]
    r1 = np.linalg.norm(d1, axis=2)
    inv_r1_3 = np.divide(1.0, r1 ** 3, out=np.zeros_like(r1), where=r1 > 0)
    r0 = np.linalg.norm(ext, axis=1)
    inv_r0_3 = np.divide(1.0, r0 ** 3, out=np.zeros_like(r0), where=r0 > 0)
    out += np.sum((d1 * inv_r1_3[:, :, None]
                   - ext[None, :, :] * inv_r0_3[None, :, None])
                  * ext_masses[None, :, None], axis=1)
    return out


def rk4_step(state: np.ndarray, t: float, h: float, center: int, table) -> np.ndarray:
    def rhs(x, tt):
        result = np.empty_like(x)
        result[:, :3] = x[:, 3:]
        result[:, 3:] = acceleration(x, tt, center, table)
        return result
    k1 = rhs(state, t)
    k2 = rhs(state + 0.5 * h * k1, t + 0.5 * h)
    k3 = rhs(state + 0.5 * h * k2, t + 0.5 * h)
    k4 = rhs(state + h * k3, t + h)
    return state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


TARGETS = {5: (599, 501, 502, 503, 504), 9: (999, 901)}

# Phase-4D small-body extension of the same fixed-step RK4 architecture. The
# propagated body is heliocentric; planetary perturbations are taken from the
# authoritative DE440 backbone and the omitted small-body/non-gravitational
# terms remain part of the declared uncertainty rather than hidden precision.
SMALL_BODY_GMS = {
    10: 132_712_440_017.99,
    1: 2.203186855140000e4,
    2: 3.248585920000000e5,
    3: 3.986004354360959e5,
    4: 4.282837362069909e4,
    5: 1.266865349118000e8,
    6: 3.793118793817000e7,
    7: 5.793939e6,
    8: 6.836529e6,
    9: 9.717000e2,
}


def small_body_acceleration(state: np.ndarray, t: float, table) -> np.ndarray:
    position = state[:3]
    radius = float(np.linalg.norm(position))
    result = -SMALL_BODY_GMS[10] * position / radius ** 3
    ext = external_positions(table, t)
    bodies = np.asarray(table[1], dtype=int)
    for index, body in enumerate(bodies):
        if int(body) == 10:
            continue
        gm = SMALL_BODY_GMS.get(int(body), 0.0)
        if gm == 0.0:
            continue
        delta = ext[index] - position
        delta_radius = float(np.linalg.norm(delta))
        ext_radius = float(np.linalg.norm(ext[index]))
        result += gm * (delta / delta_radius ** 3 - ext[index] / ext_radius ** 3)
    return result


def small_body_rk4_step(state: np.ndarray, t: float, h: float, table) -> np.ndarray:
    def rhs(value, epoch):
        result = np.empty_like(value)
        result[:3] = value[3:]
        result[3:] = small_body_acceleration(value, epoch, table)
        return result
    k1 = rhs(state, t)
    k2 = rhs(state + 0.5 * h * k1, t + 0.5 * h)
    k3 = rhs(state + 0.5 * h * k2, t + 0.5 * h)
    k4 = rhs(state + h * k3, t + h)
    return state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def build_small_body(predecessor: Path, de440: Path, lsk: Path, target: int,
                     start_iso: str, end_iso: str, output: Path,
                     sample_step: float = 43_200.0,
                     integration_step: float = 3_600.0):
    spice.furnsh(str(lsk))
    spice.furnsh(str(de440))
    spice.furnsh(str(predecessor))
    start, end = et(start_iso), et(end_iso)
    state = np.asarray(spice.spkgeo(target, start, FRAME, 10)[0], dtype=float)
    table = external_table(10, start, end, 86_400.0)
    epochs = [start]
    states = [state.copy()]
    next_sample = start + sample_step
    t = start
    while t < end - 1e-6:
        h = min(integration_step, end - t)
        state = small_body_rk4_step(state, t, h, table)
        t += h
        if t + 1e-6 >= next_sample or t >= end - 1e-6:
            epochs.append(t)
            states.append(state.copy())
            next_sample += sample_step
    epochs_np = np.asarray(epochs, dtype=float)
    states_np = np.asarray(states, dtype=float)
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = spice.spkopn(str(output), "LOOM PHASE4D PROPAGATED SPK", 1024)
    spice.spkw09(handle, target, 10, FRAME, epochs_np[0], epochs_np[-1],
                 f"LOOM PHASE4D PROPAGATED {target} REL SUN", 7,
                 len(epochs_np), np.ascontiguousarray(states_np),
                 np.ascontiguousarray(epochs_np))
    spice.spkcls(handle)
    print(target, output, output.stat().st_size, iso_et(epochs_np[0]), iso_et(epochs_np[-1]))


def build(predecessor: Path, de440: Path, lsk: Path, center: int, start_iso: str,
          end_iso: str, output_dir: Path, sample_step: float = 43_200.0,
          integration_step: float = 3_600.0):
    spice.furnsh(str(lsk))
    spice.furnsh(str(de440))
    spice.furnsh(str(predecessor))
    start, end = et(start_iso), et(end_iso)
    target_ids = TARGETS[center]
    state = np.vstack([spice.spkgeo(body, start, FRAME, center)[0] for body in target_ids])
    table = external_table(center, start, end, 86_400.0)
    epochs = [start]
    states = [state.copy()]
    next_sample = start + sample_step
    t = start
    while t < end - 1e-6:
        h = min(integration_step, end - t)
        state = rk4_step(state, t, h, center, table)
        t += h
        if t + 1e-6 >= next_sample or t >= end - 1e-6:
            epochs.append(t)
            states.append(state.copy())
            next_sample += sample_step
    epochs_np = np.asarray(epochs, dtype=float)
    states_np = np.asarray(states, dtype=float)
    output_dir.mkdir(parents=True, exist_ok=True)
    for col, body in enumerate(target_ids):
        path = output_dir / f"propagated_{body}_from_{center}_2251.bsp"
        handle = spice.spkopn(str(path), "LOOM PHASE4B PROPAGATED SPK", 1024)
        spice.spkw09(handle, body, center, FRAME, epochs_np[0], epochs_np[-1],
                     f"LOOM PHASE4B PROPAGATED {body} REL {center}", 7,
                     len(epochs_np), np.ascontiguousarray(states_np[:, col, :]),
                     np.ascontiguousarray(epochs_np))
        spice.spkcls(handle)
        print(body, path, path.stat().st_size, iso_et(epochs_np[0]), iso_et(epochs_np[-1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=int, choices=(5, 9), required=True)
    parser.add_argument("--predecessor", type=Path, required=True)
    parser.add_argument("--de440", type=Path, required=True)
    parser.add_argument("--lsk", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-step-hours", type=float, default=12.0)
    parser.add_argument("--integration-step-seconds", type=float, default=3600.0)
    parser.add_argument("--small-body", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.small_body is not None:
        if args.output is None:
            parser.error("--output is required with --small-body")
        build_small_body(args.predecessor, args.de440, args.lsk, args.small_body,
                         args.start, args.end, args.output,
                         args.sample_step_hours * 3600.0,
                         args.integration_step_seconds)
        return
    build(args.predecessor, args.de440, args.lsk, args.center, args.start, args.end,
          args.output_dir, args.sample_step_hours * 3600.0,
          args.integration_step_seconds)


if __name__ == "__main__":
    main()
