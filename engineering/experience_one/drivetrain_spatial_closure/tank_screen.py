"""Early parametric capacity screen; NOT a collision, dynamics or design qualification.

Run: python engineering/experience_one/drivetrain_spatial_closure/tank_screen.py
No dependencies; no source geometry, canonical database or GLB mutation.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    count: int = 4
    length_m: float = 14.0
    outer_diameter_m: float = 3.0
    center_radius_m: float = 2.7
    shell_allowance_m: float = 0.0  # radial widening beyond 4.5 m nominal radius


def screen(c: Candidate, density_kg_m3: float, usable_fraction: float,
           required_t: float = 250.0, hull_radius_m: float = 4.5) -> dict:
    if c.count != 4 or min(c.length_m, c.outer_diameter_m, density_kg_m3) <= 0:
        raise ValueError('Four tanks and positive dimensions/density required')
    if not 0 < usable_fraction <= 1 or c.shell_allowance_m < 0:
        raise ValueError('Usable fraction must be (0,1]; widening nonnegative')
    gross_m3 = c.count * math.pi * (c.outer_diameter_m / 2)**2 * c.length_m
    usable_m3 = gross_m3 * usable_fraction
    radial_extent_m = c.center_radius_m + c.outer_diameter_m / 2
    radial_margin_m = hull_radius_m + c.shell_allowance_m - radial_extent_m
    # Same-plane quadrature cylinders: centre separation sqrt(2)*R.
    adjacent_gap_m = math.sqrt(2)*c.center_radius_m - c.outer_diameter_m
    return {**asdict(c), 'density_kg_m3': density_kg_m3,
            'usable_fraction': usable_fraction, 'gross_m3': gross_m3,
            'usable_m3': usable_m3, 'normal_capacity_t': usable_m3*density_kg_m3/1000,
            'required_density_kg_m3': required_t*1000/usable_m3,
            'radial_extent_m': radial_extent_m, 'radial_margin_m': radial_margin_m,
            'adjacent_tank_gap_m': adjacent_gap_m,
            'capacity_screen': 'PASS' if usable_m3*density_kg_m3 >= required_t*1000 else 'FAIL',
            'radial_screen': 'PASS' if radial_margin_m >= 0 else 'FAIL',
            'tank_separation_screen': 'PASS' if adjacent_gap_m >= 0 else 'FAIL',
            'cabin_shuttle_clearance': 'HOLD_3D_SWEEP_NOT_RUN',
            'longeron_clearance': 'HOLD_3D_NOT_RUN',
            'rcs_metric_torch_clearance': 'HOLD_3D_NOT_RUN',
            'mass_inertia_attitude': 'HOLD_NOT_RUN',
            'reserve_50t_storage': 'HOLD_NOT_ALLOCATED',
            'physical_storage_feasibility': 'HOLD_FLUID_AND_STRUCTURE_UNSELECTED'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--density', type=float, default=800, help='kg/m3 illustrative input, NOT selected remass')
    parser.add_argument('--usable', type=float, default=.8, help='illustrative net volume fraction')
    args = parser.parse_args()
    candidates = [Candidate('baseline'),
                  Candidate('local_widening_example', outer_diameter_m=3.2,
                            center_radius_m=2.8, shell_allowance_m=.0),
                  Candidate('local_widening_example_with_fairing', outer_diameter_m=3.4,
                            center_radius_m=2.9, shell_allowance_m=.1)]
    print(json.dumps({'warning': 'ILLUSTRATIVE SCREEN ONLY: no reserve, full 3D, mass or dynamics qualification',
                      'candidates': [screen(c, args.density, args.usable) for c in candidates]}, indent=2))


if __name__ == '__main__':
    main()
