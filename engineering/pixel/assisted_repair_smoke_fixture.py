#!/usr/bin/env python3
from pathlib import Path


def main() -> int:
    marker = Path("/tmp/loom-assisted-repair-smoke.txt")
    marker.write_text("ok\n", encoding="utf-8")
    print("ASSISTED_REPAIR_SMOKE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
