#!/usr/bin/env python3
"""Android launcher for the LOOM HUD qualification/live synthetic-vision surface."""
from __future__ import annotations
from pathlib import Path
import os,socket,subprocess,sys,threading,time
from urllib.request import urlopen
LOOM_ROOT=Path("/storage/emulated/0/Documents/LOOM")
APP=Path(os.environ.get("LOOM_APP_ROOT") or os.environ.get("LOOM_HOME") or str(LOOM_ROOT/"runtime")).expanduser().resolve()
DATA=Path(os.environ.get("LOOM_DATA_ROOT") or str(LOOM_ROOT/"data")).expanduser().resolve()
CAMPAIGN=Path(os.environ.get("LOOM_CAMPAIGN_ROOT") or str(LOOM_ROOT/"campaign")).expanduser().resolve()
SERVER=APP/"src"/"loom"/"hud"/"server.py"; PAGE="earth_moon_qualification.html"; BUILD_MARKER="hud-v0.22-wayfarer-engineering"
if not SERVER.exists(): raise SystemExit(f"LOOM file missing: {SERVER}")
def _browser_enabled(): return str(os.environ.get("LOOM_NO_BROWSER") or "").strip().lower() not in {"1","true","yes","on"}
def _free_port():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock: sock.bind(("127.0.0.1",0)); return int(sock.getsockname()[1])
def _open_browser(url):
    try: subprocess.Popen(["termux-open-url",url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return
    except OSError: pass
    try: subprocess.Popen(["/system/bin/am","start","-a","android.intent.action.VIEW","-d",url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except OSError: print(f"LOOM browser auto-open unavailable; open {url}",file=sys.stderr)
def _wait_and_open(url,timeout_s=20.0):
    deadline=time.monotonic()+timeout_s
    while time.monotonic()<deadline:
        try:
            with urlopen(url,timeout=.5) as response:
                if BUILD_MARKER in response.read().decode("utf-8",errors="replace"): _open_browser(url); return
        except Exception: pass
        time.sleep(.2)
    print("HUD preview did not verify the expected build marker; browser not opened.",file=sys.stderr)
port=int(os.environ.get("LOOM_HUD_PORT") or _free_port()); cache_token=str(time.time_ns()); HUD_URL=str(os.environ.get("LOOM_HUD_URL") or f"http://127.0.0.1:{port}/{PAGE}?build={BUILD_MARKER}&t={cache_token}")
env=os.environ.copy(); src_root=str(APP/"src"); existing=str(env.get("PYTHONPATH") or "").strip(); env.update({"LOOM_APP_ROOT":str(APP),"LOOM_DATA_ROOT":str(DATA),"LOOM_CAMPAIGN_ROOT":str(CAMPAIGN),"LOOM_HOME":str(APP),"PYTHONPATH":src_root if not existing else src_root+os.pathsep+existing})
print(f"LOOM HUD APP ROOT: {APP}"); print(f"LOOM HUD DATA ROOT: {DATA}"); print(f"LOOM HUD CAMPAIGN ROOT: {CAMPAIGN}"); print(f"LOOM HUD BUILD: {BUILD_MARKER}"); print(f"LOOM HUD PREVIEW: {HUD_URL}")
if _browser_enabled(): threading.Thread(target=_wait_and_open,args=(HUD_URL,),name="loom-hud-browser-open",daemon=True).start()
try: raise SystemExit(subprocess.call([sys.executable,str(SERVER),"--port",str(port)],env=env))
except KeyboardInterrupt: print("\nLOOM HUD stopped."); raise SystemExit(130)