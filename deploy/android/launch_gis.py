#!/usr/bin/env python3
"""Android GIS launcher using the LOOM runtime-root contract."""
from pathlib import Path
import os
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

# Post-migration Android defaults. Explicit environment roots always win.
LOOM_ROOT = Path("/storage/emulated/0/Documents/LOOM")
APP = Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or str(LOOM_ROOT / "runtime")).expanduser().resolve()
DATA = Path(os.environ.get("LOOM_DATA_ROOT") or str(LOOM_ROOT / "data")).expanduser().resolve()
CAMPAIGN = Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or str(LOOM_ROOT / "campaign")).expanduser().resolve()
GIS = APP / "src" / "loom_gis.py"
DB = DATA / "LOOM_2226.sqlite3"
CIV = DATA / "LOOM_2226_CIVSTATE.sqlite3"
GIS_URL = str(os.environ.get("LOOM_GIS_URL") or "http://127.0.0.1:8766")

for p in (GIS, DB, CIV):
    if not p.exists():
        raise SystemExit(f"LOOM file missing: {p}")

env = os.environ.copy()
env.update({
    "LOOM_APP_ROOT": str(APP),
    "LOOM_DATA_ROOT": str(DATA),
    "LOOM_CAMPAIGN_ROOT": str(CAMPAIGN),
    "LOOM_HOME": str(APP),
})

argv = [
    sys.executable, str(GIS),
    "--db", str(DB),
    "--civ-db", str(CIV),
    "--nav-runtime-root", str(APP),
]

# Provider-backed acquisition is the Android default. Cache-only planning is
# available explicitly for deterministic/offline qualification runs.
offline = str(os.environ.get("LOOM_NAV_PLANNING_OFFLINE") or "").strip().lower()
if offline in {"1", "true", "yes", "on"}:
    argv.append("--nav-planning-offline")


def _browser_enabled() -> bool:
    value = str(os.environ.get("LOOM_NO_BROWSER") or "").strip().lower()
    return value not in {"1", "true", "yes", "on"}


def _open_browser(url: str) -> None:
    try:
        subprocess.Popen(["termux-open-url", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except OSError:
        pass
    try:
        subprocess.Popen([
            "/system/bin/am", "start", "-a", "android.intent.action.VIEW", "-d", url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        print(f"LOOM browser auto-open unavailable; open {url}", file=sys.stderr)


def _wait_and_open(url: str, timeout_s: float = 20.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=0.5) as response:
                if 200 <= int(getattr(response, "status", 200)) < 500:
                    _open_browser(url)
                    return
        except Exception:
            pass
        time.sleep(0.2)


# Keep the established blocking subprocess.call launcher contract. Browser launch
# happens independently only after the localhost server answers.
if _browser_enabled():
    threading.Thread(target=_wait_and_open, args=(GIS_URL,), name="loom-browser-open", daemon=True).start()

try:
    raise SystemExit(subprocess.call(argv, env=env))
except KeyboardInterrupt:
    # Ctrl+C is the normal interactive Termux shutdown path. The GIS child sees
    # the same terminal interrupt; suppress the wrapper traceback and return the
    # conventional shell interrupt status instead.
    print("\nLOOM stopped.")
    raise SystemExit(130)
