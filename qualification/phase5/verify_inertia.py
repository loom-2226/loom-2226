from __future__ import annotations

import hashlib
import json
import platform
import unittest
from pathlib import Path

from wayfarer_inertia_audit import build_audit

ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "phase5b_inertia_verification_result.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromName("test_phase5b_inertia_audit")
    result = unittest.TestResult()
    suite.run(result)

    audit = build_audit(REPO_ROOT)
    d = audit["docked"]
    a = audit["absent"]

    checks = {
        "unit_suite": result.wasSuccessful(),
        "docked_mass_com": d["mass_kg"] == 1158500.0 and d["center_of_mass_B_m"] == [26.676650841605525, 0.0, 0.14812257229175657],
        "absent_mass_com": a["mass_kg"] == 1125500.0 and a["center_of_mass_B_m"] == [26.819635717458908, 0.0, 0.0],
        "parallel_axis_psd": bool(d["parallel_axis_psd"] and a["parallel_axis_psd"]),
        "centroidal_inertia_unresolved": d["unresolved_centroidal_inertia_mass_fraction"] == 1.0 and a["unresolved_centroidal_inertia_mass_fraction"] == 1.0,
        "fail_closed_authority": (not d["flight_dynamics_authority"]) and (not a["flight_dynamics_authority"]),
    }

    payload = {
        "schema": "loom.phase5b_inertia_verification.v0.1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "environment": {
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "offline_required": True,
        },
        "input_sha256": {
            "wayfarer_inertia_audit.py": sha256(ROOT / "wayfarer_inertia_audit.py"),
            "test_phase5b_inertia_audit.py": sha256(ROOT / "test_phase5b_inertia_audit.py"),
            "wayfarer_phase5_adapter.py": sha256(ROOT / "wayfarer_phase5_adapter.py"),
        },
        "audit": audit,
        "unit_suite": {
            "tests_run": result.testsRun,
            "passed": result.wasSuccessful(),
            "failures": [str(t) for t, _ in result.failures],
            "errors": [str(t) for t, _ in result.errors],
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SHA256 phase5b_inertia_verification_result.json", sha256(OUT))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("LOOM_PHASE5B_INERTIA_VERIFY:", payload["status"])
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
