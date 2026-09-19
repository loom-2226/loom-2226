#!/usr/bin/env python3
"""Require seven actual Ceres browser passes; Node's successful skips fail CI."""
import re
import sys
from pathlib import Path

EXPECTED = {"tests": 7, "suites": 0, "pass": 7, "fail": 0, "cancelled": 0, "skipped": 0, "todo": 0}


def require_seven_passes(report: str) -> dict[str, int]:
    counts = {}
    for key, expected in EXPECTED.items():
        values = re.findall(rf"^# {key} (\d+)$", report, re.MULTILINE)
        if len(values) != 1 or int(values[0]) != expected:
            raise ValueError(f"Expected {key}={expected}; observed {values or 'missing'}")
        counts[key] = int(values[0])
    if re.findall(r"^1\.\.(\d+)$", report, re.MULTILINE) != ["7"]:
        raise ValueError("Expected one complete seven-test TAP plan")
    if re.findall(r"^ok (\d+) - .+$", report, re.MULTILINE) != [str(i) for i in range(1, 8)]:
        raise ValueError("Expected seven ordered successful test results")
    if re.search(r"^\s*(?:not ok\b|Bail out!)|^ok .*#\s*(?:SKIP|TODO)\b", report, re.MULTILINE | re.IGNORECASE):
        raise ValueError("Failure, bailout, skip or todo is not a browser pass")
    return counts


def main() -> None:
    try:
        counts = require_seven_passes(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (IndexError, OSError, ValueError) as error:
        raise SystemExit(f"Ceres browser verification FAIL: {error}") from error
    print("Ceres browser verification PASS: " + ", ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
