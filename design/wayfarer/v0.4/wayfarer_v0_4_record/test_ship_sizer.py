"""Regression: the sizer must rebuild Wayfarer from Wayfarer's own drivers.

Expected values are read from the repo (seed + canon torch card), never typed in.
Usage: python test_ship_sizer.py REPO_DIR
"""
import re
import sqlite3
import sys
from pathlib import Path

import ship_sizer as ss


def canon_torch_card(repo):
    text = (Path(repo) / "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md").read_text()
    rows = re.findall(r"^\| (\w+) \| [\d,]+ km/s \| ~([\d,]+) km/s \|$", text, re.M)
    return {m: float(v.replace(",", "")) for m, v in rows}


def main(repo):
    db = sqlite3.connect(":memory:")
    db.executescript((Path(repo) / "geometry/wayfarer_geometry_seed.sql").read_text())
    p = dict(db.execute("SELECT key, value_real FROM geometry_parameters"))
    seed_ledger = dict(db.execute("SELECT id, mass_t FROM mass_elements"))

    res = ss.size(ss.wayfarer_requirement(repo), repo)
    checks = []

    def check(name, got, want, tol):
        ok = abs(got - want) <= tol
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got:.3f}, want {want:.3f} (tol {tol})")

    check("dry mass t", res["dry_t"], p["mass.dry_reference_t"], 1e-6)
    check("wet mass t", res["wet_t"], p["mass.wet_reference_t"], 1e-6)
    check("normal remass t", res["remass_t"], p["mass.normal_remass_t"], 1e-6)
    check("protected water t", res["protected_water_t"], p["mass.protected_water_t"], 1e-6)
    check("torch scale", res["torch_scale"], 1.0, 1e-9)
    for line, mass in seed_ledger.items():
        check(f"ledger {line}", res["ledger_t"][line], mass, 1e-6)
    card = canon_torch_card(repo)
    if len(card) != 6:
        print(f"FAIL  canon torch card parse found {len(card)} rows")
        checks.append(False)
    for mode, dv in card.items():
        check(f"canon dv {mode} km/s", res["modes"][mode]["dv_km_s"], dv, 1.0)
    check("CRUISE accel at wet g", res["modes"]["CRUISE"]["accel_wet_g"], 1.0, 1e-9)

    print(f"\n{sum(checks)}/{len(checks)} checks passed")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
