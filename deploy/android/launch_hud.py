#!/usr/bin/env python3
"""Android launcher for the LOOM HUD qualification surface."""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

LOOM_ROOT = Path("/storage/emulated/0/Documents/LOOM")
APP = Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or str(LOOM_ROOT / "runtime")).expanduser().resolve()
SERVER = APP / "src" / "loom" / "hud" / "server.py"
HUD_URL = str(os.environ.get("LOOM_HUD_URL") or "http://127.0.0.1:8767/hud_mock_v0_1.html")

if not SERVER.exists():
    raise SystemExit(f"LOOM file missing: {SERVER}")


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
        subprocess.Popen(
            ["/system/bin/am", "start", "-a", "android.intent.action.VIEW", "-d", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
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


env = os.environ.copy()
env.update({"LOOM_APP_ROOT": str(APP), "LOOM_HOME": str(APP)})

if _browser_enabled():
    threading.Thread(target=_wait_and_open, args=(HUD_URL,), name="loom-hud-browser-open", daemon=True).start()

try:
    raise SystemExit(subprocess.call([sys.executable, str(SERVER)], env=env))
except KeyboardInterrupt:
    print("\nLOOM HUD stopped.")
    raise SystemExit(130)
