#!/usr/bin/env python3
"""Build explicit spacecraft post-source empirical propagation SPKs.

The input is an authoritative mission SPK.  States are propagated in
heliocentric ECLIPJ2000 coordinates with Sun gravity, differential DE440
planetary perturbations, and fixed-step RK4.  The resulting kernels are
derived LOOM products, never direct mission authority.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import spiceypy as spice

from build_solar_phase4b_propagation import (
    FRAME, SMALL_BODY_GMS, et, external_table, iso_et, small_body_acceleration,
    small_body_rk4_step,
)


def build_spacecraft(predecessor: Path, de440: Path, lsk: Path, target: int,
                     source_end: str, output_start: str, end: str,
                     output: Path, sample_step: float = 43_200.0,
                     integration_step: float = 21_600.0) -> None:
    spice.furnsh(str(lsk))
    spice.furnsh(str(de440))
    spice.furnsh(str(predecessor))
    source_et, start, finish = et(source_end), et(output_start), et(end)
    state = np.asarray(spice.spkgeo(target, source_et, FRAME, 10)[0], dtype=float)
    table = external_table(10, source_et, finish, 86_400.0)
    t = source_et
    epochs = [t]
    states = [state.copy()]
    next_sample = max(start, source_et) + sample_step
    while t < finish - 1e-6:
        h = min(integration_step, finish - t)
        state = small_body_rk4_step(state, t, h, table)
        t += h
        if t + 1e-6 >= next_sample or t >= finish - 1e-6:
            epochs.append(t)
            states.append(state.copy())
            next_sample += sample_step
    output.parent.mkdir(parents=True, exist_ok=True)
    epochs_np = np.asarray(epochs, dtype=float)
    states_np = np.asarray(states, dtype=float)
    handle = spice.spkopn(str(output), "LOOM PHASE4E SPACECRAFT PROPAGATION", 1024)
    spice.spkw09(handle, target, 10, FRAME, epochs_np[0], epochs_np[-1],
                 f"LOOM PHASE4E PROPAGATED SPACECRAFT {target}", 7,
                 len(epochs_np), np.ascontiguousarray(states_np),
                 np.ascontiguousarray(epochs_np))
    spice.spkcls(handle)
    print(target, output, output.stat().st_size, iso_et(epochs_np[0]), iso_et(epochs_np[-1]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predecessor", type=Path, required=True)
    parser.add_argument("--de440", type=Path, required=True)
    parser.add_argument("--lsk", type=Path, required=True)
    parser.add_argument("--target", type=int, required=True)
    parser.add_argument("--source-end", required=True)
    parser.add_argument("--output-start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-step-hours", type=float, default=12.0)
    parser.add_argument("--integration-step-seconds", type=float, default=21600.0)
    args = parser.parse_args()
    build_spacecraft(args.predecessor, args.de440, args.lsk, args.target,
                     args.source_end, args.output_start, args.end, args.output,
                     args.sample_step_hours * 3600.0,
                     args.integration_step_seconds)


if __name__ == "__main__":
    main()
