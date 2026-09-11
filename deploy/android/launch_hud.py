#!/usr/bin/env python3
"""One-command Android launcher for the LOOM HUD test-drive surface.

When run from the Git checkout, this launcher fast-forwards the current tracked
branch before starting the HUD. DATA and CAMPAIGN remain separate and untouched.
Set LOOM_HUD_SKIP_UPDATE=1 to launch without the Git update step.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

LOOM_ROOT = Path("/storage/emulated/0/Documents/LOOM")
CHECKOUT_ROOT = Path(__file__).resolve().parents[2]
APP = Path(
    os.environ.get("LOOM_APP_ROOT")
    or os.environ.get("LOOM_HOME")
    or str(CHECKOUT_ROOT)
).expanduser().resolve()
DATA = Path(os.environ.get("LOOM_DATA_ROOT") or str(LOOM_ROOT / "data")).expanduser().resolve()
CAMPAIGN = Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or str(LOOM_ROOT / "campaign")).expanduser().resolve()
SERVER = APP / "src" / "loom" / "hud" / "server.py"
PAGE = "earth_moon_qualification.html"
BUILD_MARKER="hud-v0.33-orbit-path-cue"


def _truthy(name: str) -> bool:
    return str(os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _git(*args: str, capture: bool = False) -> str:
    proc = subprocess.run(
        ["git", "-C", str(CHECKOUT_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    return (proc.stdout or "").strip()


def _self_update_checkout() -> None:
    if _truthy("LOOM_HUD_SKIP_UPDATE"):
        print("LOOM HUD UPDATE: skipped by LOOM_HUD_SKIP_UPDATE")
        return
    if not (CHECKOUT_ROOT / ".git").exists():
        print("LOOM HUD UPDATE: checkout metadata not present; launching current files")
        return

    dirty = _git("status", "--porcelain", capture=True)
    if dirty:
        raise SystemExit("LOOM HUD refusing auto-update with local Git changes; commit/stash them first")

    branch = _git("symbolic-ref", "--quiet", "--short", "HEAD", capture=True)
    if not branch:
        raise SystemExit("LOOM HUD refusing auto-update from detached HEAD")

    try:
        upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", capture=True)
    except subprocess.CalledProcessError:
        upstream = f"origin/{branch}"

    launcher_path = Path(__file__).resolve()
    before = hashlib.sha256(launcher_path.read_bytes()).hexdigest()
    print(f"LOOM HUD UPDATE: {branch} <- {upstream}")
    print("git fetch --prune origin")
    _git("fetch", "--prune", "origin")
    print(f"git merge --ff-only {upstream}")
    _git("merge", "--ff-only", upstream)
    after = hashlib.sha256(launcher_path.read_bytes()).hexdigest()

    if after != before:
        print("LOOM HUD UPDATE: launcher changed; restarting updated launcher")
        os.execv(sys.executable, [sys.executable, str(launcher_path), *sys.argv[1:]])


_self_update_checkout()

if not SERVER.exists():
    raise SystemExit(f"LOOM file missing: {SERVER}")


def _browser_enabled() -> bool:
    return not _truthy("LOOM_NO_BROWSER")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


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
                if BUILD_MARKER in response.read().decode("utf-8", errors="replace"):
                    _open_browser(url)
                    return
        except Exception:
            pass
        time.sleep(0.2)
    print("HUD preview did not verify the expected build marker; browser not opened.", file=sys.stderr)


port = int(os.environ.get("LOOM_HUD_PORT") or _free_port())
cache_token = str(time.time_ns())
HUD_URL = str(
    os.environ.get("LOOM_HUD_URL")
    or f"http://127.0.0.1:{port}/{PAGE}?build={BUILD_MARKER}&t={cache_token}"
)
env = os.environ.copy()
src_root = str(APP / "src")
existing = str(env.get("PYTHONPATH") or "").strip()
env.update(
    {
        "LOOM_APP_ROOT": str(APP),
        "LOOM_DATA_ROOT": str(DATA),
        "LOOM_CAMPAIGN_ROOT": str(CAMPAIGN),
        "LOOM_HOME": str(APP),
        "PYTHONPATH": src_root if not existing else src_root + os.pathsep + existing,
    }
)

print(f"LOOM HUD APP ROOT: {APP}")
print(f"LOOM HUD DATA ROOT: {DATA}")
print(f"LOOM HUD CAMPAIGN ROOT: {CAMPAIGN}")
print(f"LOOM HUD BUILD: {BUILD_MARKER}")
print(f"LOOM HUD PREVIEW: {HUD_URL}")
if _browser_enabled():
    threading.Thread(
        target=_wait_and_open,
        args=(HUD_URL,),
        name="loom-hud-browser-open",
        daemon=True,
    ).start()

try:
    raise SystemExit(subprocess.call([sys.executable, str(SERVER), "--port", str(port)], env=env))
except KeyboardInterrupt:
    print("\nLOOM HUD stopped.")
    raise SystemExit(130)
