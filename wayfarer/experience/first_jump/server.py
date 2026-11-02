"""First Jump: FQ11 evidence playback for a local Pixel browser.

Standard library only. UI requests presentation state, never flight physics.
No Navigator or mutable simulation state.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import bisect
from urllib.request import Request, urlopen
from urllib.error import URLError
from threading import RLock
from datetime import datetime, timezone
import argparse
import json
import os
import random
import re
import secrets
import time

from build_timeline import HERE, build

ROOT = HERE.parents[2]
PHASES = ("briefing", "preburn", "metric", "turn", "trim", "debrief")
# Human viewing time only. None of these values are physics inputs or outputs.
PRESENTATION_S = {"preburn": 115, "metric": 565, "turn": 42, "trim": 12}
ART = {
    "briefing": "cmd_pov.png",
    "preburn": "ext_burn.png",
    "metric": "ext_metric.png",
    "turn": "cmd_pov.png",
    "trim": "ext_departure.png",
    "debrief": "cmd_pov.png",
}
ART_DIR = ROOT / "wayfarer/render/out"
LOG_DIR = Path(os.getenv("FIRST_JUMP_LOG_DIR", str(Path.home() / ".local/state/loom/first_jump")))
CANON_PATH = ROOT / "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md"
MAP_PATH = HERE / "map_display.json"
FQ11_INPUT = ROOT / "wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101/FQ11_INPUT.json"
FQ11_RESULT = ROOT / "wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/FQ11_RESULT.json"

def load_map(timeline):
    """Only an already compiled, source-bound ephemeris display. No Navigator."""
    mapdata = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    if mapdata.get("schema") != "FIRST_JUMP_SOLAR_DISPLAY_v0.3":
        raise ValueError("Invalid map display schema")
    if mapdata.get("metric_path") is not None or mapdata.get("mars_approach_range") is not None:
        raise ValueError("Map must not invent a Metric path or collapse radius")
    if mapdata["source_input_sha256"] != hashlib.sha256(FQ11_INPUT.read_bytes()).hexdigest():
        raise ValueError("FQ11 ephemeris source changed")
    if mapdata["source_fq11_result_sha256"] != timeline["source_sha256"]:
        raise ValueError("Map frame set does not match accepted FQ11")
    if mapdata["epoch_utc"] != json.loads(FQ11_INPUT.read_text())["epoch_utc"]:
        raise ValueError("Map source epoch mismatch")
    for case, evidence in mapdata["cases"].items():
        q=timeline["cases"][case]
        expected = {"preburn": q["preburn_s"]["value"] +
                        sum(p["duration_s"] for p in json.loads(FQ11_RESULT.read_text())["measured_cases"][
                        0 if case=="NOMINAL" else 1]["phase_evidence"]["preburn"] if p["kind"]=="coast"),
                    "metric":q["metric_s"]["value"],
                    "turn":q["turn_s"]["value"],"trim":q["trim_s"]["value"]}
        if any(abs(evidence["phase_durations_s"][k] - v)>1e-7 for k,v in expected.items()):
            raise ValueError("Map phase times are not accepted FQ11")
    samples=mapdata["samples"]
    if not samples or not all(samples[i]["elapsed_s"] < samples[i+1]["elapsed_s"] for i in range(len(samples)-1)):
        raise ValueError("Invalid map time axis")
    return mapdata

# Verbatim bounded canonical excerpts, not independent physical claims.
def canon_excerpt():
    text = CANON_PATH.read_text(encoding="utf-8")
    a = text.index("### 7.1a Scoped Solar System")
    b = text.index("### 7.1b Declared Sun")
    c = text.index("Desired arrival state remains separate:", b)
    return {"Canon II §7.1a": text[a:b], "Canon II §7.1b": text[b:c]}

def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def values_for(timeline, case):
    return timeline["cases"][case]

def rounded(v, digits=1):
    return f"{v:,.{digits}f}"

def evidence_lines(t, case, phase):
    q = values_for(t, case)
    v = lambda k: q[k]["value"]
    src = lambda k: q[k]["source"]
    if phase == "briefing":
        return [
            {"label": "DESTINATION", "value": "Mars", "source": None, "earned": False},
            {"label": "FLIGHT PLAN", "value": "Loaded", "source": None, "earned": False},
            {"label": "CREW", "value": "At stations", "source": None, "earned": False},
        ]
    names = {
        "preburn": [("BURN DURATION", "preburn_s", "s", 1), ("PEAK ACCEL", "preburn_peak_g", "g", 3), ("REMASS USED", "preburn_kg", "kg", 1)],
        "metric": [("METRIC TRANSIT", "metric_s", "s", 1), ("NATURAL MISS", "arrival_mismatch_m_s", "m/s", 2)],
        "turn": [("ARRIVAL MISS", "arrival_mismatch_m_s", "m/s", 2), ("RCS TURN", "turn_s", "s", 1), ("CONTROL RATE", "turn_hz", "Hz", 1), ("POINT TURN", "turn_deg", "deg", 2)],
        "trim": [("TRIM BURN", "trim_s", "s", 3), ("TRIM REMASS", "trim_kg", "kg", 2), ("FINAL MISS", "final_mismatch_m_s", "m/s", 3)],
        "debrief": [("FINAL MISS", "final_mismatch_m_s", "m/s", 3), ("TOTAL REMASS", "total_remass_kg", "kg", 1), ("REMAINING", "remass_remaining_kg", "kg", 1)],
    }
    return [{"label": label, "value": rounded(v(key), precision) + " " + unit, "source": src(key), "earned": True, "field": key}
            for label, key, unit, precision in names[phase]]

def allowed_numbers(t, selected_case):
    nums = set()
    for evidence in t["cases"][selected_case].values():
            val = evidence["value"]
            nums.add(str(val))
            nums.update(f"{val:.{n}f}" for n in range(5))
            nums.update(f"{val:,.{n}f}" for n in range(5))
    # Both named FQ11 cases record a 1% deliberately shortened burn.
    nums.add("1")
    return nums

def unsupported_numbers(answer, permitted):
    # Canon section references are citations, not flight numbers.
    clean = re.sub(r"Canon\s+II\s+§?7\.1[ab]?(?:/b)?", "CANONREF", answer, flags=re.I)
    unsupported = {m.group() for m in re.finditer(r"(?<![\w])\d+(?:[,.]\d+)*(?!\w)", clean)
                   if m.group().replace(",", "") not in permitted}
    words = r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|trillion|half|quarter|third|dozen)\b"
    unsupported.update(w.lower() for w in re.findall(words, clean, flags=re.I))
    return sorted(unsupported)

def local_answer(question, timeline, selected_case):
    """Source-backed, in-world dialogue when a live channel is unavailable."""
    low = question.lower()
    if any(w in low for w in ("mismatch", "miss", "arrival", "recovery", "trim")):
        return "The mismatch is on your board, Captain. The attitude change and trim are loaded. Give the order when you're ready.", ["arrival_mismatch_m_s", "final_mismatch_m_s"]
    if any(w in low for w in ("burn", "fuel", "remass", "accel", "delta")):
        return "The pre-jump burn is on the record. Fins are deployed; the mass and acceleration readings are on your board. Anything beyond those, I won't guess.", ["preburn_s", "preburn_kg", "preburn_peak_g"]
    if any(w in low for w in ("physics", "energy", "sun", "velocity", "canon", "how")):
        return "We carry our departure into the weave and meet Mars with the velocity it gives us. Any correction after that comes from our own engines.", []
    if any(w in low for w in ("shell", "distance", "capture", "orbit", "position")):
        return "Mars approach shell, Captain. Traffic has the handoff. We'll take the next leg one clearance at a time.", []
    return "I'm here, Captain. Ask what the burn, the weave, or the approach needs from us.", []

def llm_answer(question, timeline, selected_case, excerpts):
    """Return an in-character JSON answer; provider diagnostics stay in logs."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None, [], "missing_api_key"
    payload = {
        "model": os.getenv("FIRST_JUMP_MODEL", "gpt-4.1-mini"),
        "instructions": (
            "You voice MARA aboard Wayfarer during the Earth to Mars First Jump. "
            "The player holds captain authority in this non-canon playtest. "
            "Stay entirely IN CHARACTER: short natural spoken lines, warmth, tension, judgment. "
            "Never mention FQ11, lab, evidence, data, tests, canon, source paths, limitations, caveats or audit, "
            "and NEVER include citations or footnotes in spoken words. "
            "You must not invent physical events, numerical quantities, distances, speeds, "
            "positions, orbital capture, traffic details or outcomes. "
            "Use ONLY the accepted selected FQ11 numbers supplied, with Canon II §§7.1a/b as "
            "your world-physics constraints. Never calculate new physics or issue commands. "
            "If the captain asks something unrecorded, answer naturally without numbers. "
            "Output a JSON object ONLY: "
            "{\"line\":\"spoken line, at most 65 words\","
            "\"facts\":[\"keys of numeric_evidence actually used in the line\"],"
            "\"canon\":[\"7.1a\" or \"7.1b\" if used]}. "
            "Do not include numbers unless each appears unchanged or conventionally rounded "
            "from one of those declared evidence keys."
        ),
        "input": json.dumps({
            "player_question": question,
            "phase": "Earth to Mars First Jump",
            "selected_case": selected_case,
            "numeric_evidence": timeline["cases"][selected_case],
            "canon_7_1a_7_1b": excerpts,
            "unknown_flight_values": timeline["unavailable"],
        }, ensure_ascii=False),
        "max_output_tokens": 260
    }
    req = Request("https://api.openai.com/v1/responses",
                  data=json.dumps(payload).encode(), method="POST",
                  headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=22) as resp:
            output = json.load(resp)
        chunks = [part.get("text", "")
                  for item in output.get("output", [])
                  for part in item.get("content", [])
                  if part.get("type") == "output_text"]
        raw = " ".join(chunks).strip()
        parsed = json.loads(raw)
        line = parsed.get("line")
        facts = parsed.get("facts")
        canon = parsed.get("canon")
        if not isinstance(line, str) or not (0 < len(line.strip()) <= 600):
            return None, [], "invalid_model_line"
        if not isinstance(facts, list) or not all(isinstance(k, str) and k in timeline["cases"][selected_case] for k in facts):
            return None, [], "invalid_model_supports"
        if not isinstance(canon, list) or not all(k in ("7.1a", "7.1b") for k in canon):
            return None, [], "invalid_model_canon_refs"
        # No model-only numerics or naked audit references in the player voice.
        rejects = unsupported_numbers(line, allowed_numbers_for_fields(timeline, selected_case, facts))
        if rejects:
            return None, facts, "unsupported_numbers:" + ",".join(rejects) + " | rejected_line=" + line
        if re.search(r"FQ11|Canon II|JSON|evidence|lab(?:oratory)?|source path|certif|\btest\b", line, re.I):
            return None, facts, "audit_tone_rejected"
        return line.strip(), facts, "live_llm"
    except Exception as e:
        # Log only exception type and HTTP status, never token/headers/content.
        status = getattr(e, "code", None)
        return None, [], f"api_{type(e).__name__}" + (f"_{status}" if status is not None else "")

def allowed_numbers_for_fields(t, selected_case, fields):
    nums = set()
    for field in fields:
        v = t["cases"][selected_case][field]["value"]
        nums.add(str(v))
        nums.update(f"{v:.{n}f}" for n in range(5))
        nums.update(f"{v:,.{n}f}" for n in range(5))
    return nums

class Session:
    def __init__(self, timeline, seed=None, first=False, requested_case=None):
        self.t = timeline
        self.seed = int(seed) if seed is not None else secrets.randbelow(2**31)
        if requested_case is not None and requested_case not in ("NOMINAL", "UNDERBURN_1_PERCENT"):
            raise ValueError("Unknown scenario")
        self.case = requested_case or ("NOMINAL" if first else random.Random(self.seed).choice(["NOMINAL", "UNDERBURN_1_PERCENT"]))
        self.id = secrets.token_hex(6)
        self.i = 0
        self.mode = "awaiting"
        self.spent = 0.0
        self.since = None
        self.questions = 0
        self.logs = LOG_DIR / f"{self.id}.jsonl"
        self.log("start", seed=self.seed, case=self.case, source_sha256=timeline["source_sha256"])

    @property
    def phase(self):
        return PHASES[self.i]

    def log(self, event, **extras):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        row = {"utc": stamp(), "session": self.id, "phase": self.phase, "event": event, **extras}
        with self.logs.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def tick(self):
        if self.mode != "active":
            return
        now = time.monotonic()
        self.spent += now - self.since
        self.since = now
        if self.spent >= PRESENTATION_S[self.phase]:
            self.spent = float(PRESENTATION_S[self.phase])
            self.finish()

    def finish(self):
        self.log("phase_end", wall_viewing_s=round(self.spent, 3),
                 source_physical_s=(self.t["cases"][self.case].get(self.phase + "_s") or {}).get("value"))
        self.i += 1
        self.spent = 0
        self.since = None
        self.mode = "complete" if self.phase == "debrief" else "awaiting"
        self.log("complete" if self.mode == "complete" else "gate_open")

    def scrub(self, progress):
        """Captain-controlled viewing cursor, never physical flight execution."""
        if self.phase not in PRESENTATION_S or self.mode not in ("active", "held"):
            raise ValueError("No active phase to scrub")
        if not isinstance(progress, (int,float)) or isinstance(progress, bool) or not 0 <= progress <= 99.9:
            raise ValueError("Viewing percent must be 0..99.9")
        self.tick()
        if self.mode not in ("active", "held"):
            raise ValueError("Phase ended while seeking")
        self.spent = PRESENTATION_S[self.phase] * float(progress)/100.
        self.since = None
        self.mode = "held"
        self.log("captain_scrub", viewing_progress_percent=progress,
                 viewing_s=round(self.spent,3))

    def command(self, action):
        self.tick()
        if action == "quit":
            self.log("quit", quit_point=self.phase, phase_viewing_s=round(self.spent, 3))
            self.mode = "quit"
        elif action == "hold" and self.mode == "active":
            self.mode = "held"
            self.since = None
            self.log("captain_hold", phase_viewing_s=round(self.spent, 3))
        elif action == "go" and self.mode in ("awaiting", "held"):
            if self.phase == "briefing":
                self.log("captain_go", phase_viewing_s=round(self.spent, 3))
                self.i = 1
                self.spent = 0
            else:
                self.log("captain_go" if self.mode == "awaiting" else "captain_resume",
                         phase_viewing_s=round(self.spent, 3))
            self.mode = "active"
            self.since = time.monotonic()
        else:
            raise ValueError("Command not available in current phase")

    def view(self, mapdata=None):
        self.tick()
        phase = self.phase
        display_phase = phase
        if phase == "debrief":
            progress = 100
        elif phase == "briefing":
            progress = 0
        else:
            progress = round(100 * self.spent / PRESENTATION_S[phase], 1)
        # Presentation time from accepted FQ11 phase durations. Map frames are
        # precomputed by FQ11's source-epoch ephemeris, not the browser.
        map_elapsed=0.0
        map_index=0
        if mapdata is not None:
            phase_times=mapdata["cases"][self.case]["phase_durations_s"]
            if phase == "debrief":
                map_elapsed=sum(phase_times.values())
            elif phase in phase_times:
                order=("preburn","metric","turn","trim")
                map_elapsed=sum(phase_times[k] for k in order[:order.index(phase)])
                map_elapsed+=phase_times[phase]*self.spent/PRESENTATION_S[phase]
            map_index=max(0,bisect.bisect_right(
                [row["elapsed_s"] for row in mapdata["samples"]],map_elapsed)-1)
            map_index=min(map_index,len(mapdata["samples"])-1)
        return {
            "map_index": map_index, "map_epoch_elapsed_s":round(map_elapsed,4),
            "id": self.id, "seed": self.seed, "phase": phase,
            "mode": self.mode, "progress_percent": progress,
            "scene": ART[display_phase], "case_revealed": self.i >= 2,
            "variant": self.case if self.i >= 2 else "SEALED",
            "facts": evidence_lines(self.t, self.case, phase),
            "physical_phase_s": (self.t["cases"][self.case].get(phase + "_s") or {}).get("value"),
            "viewing_phase_s": round(self.spent, 1),
            "question_count": self.questions,
            "log_file": str(self.logs)
        }

class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, handler):
        self.timeline = build()
        recorded = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
        if recorded != self.timeline:
            raise ValueError("Timeline differs from authoritative FQ11; regenerate & review")
        self.excerpts = canon_excerpt()
        self.mapdata = load_map(self.timeline)
        self.lock = RLock()
        self.session = Session(self.timeline, first=True)
        super().__init__(address, handler)

class Handler(BaseHTTPRequestHandler):
    def send(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def page(self, path, mime):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        from urllib.parse import urlsplit
        path = urlsplit(self.path).path
        if path == "/":
            return self.page(HERE / "index.html", "text/html; charset=utf-8")
        if path.startswith("/art/") and path.split("/")[-1] in ART.values() and path.count("/") == 2:
            return self.page(ART_DIR / path.rsplit("/", 1)[1], "image/png")
        if path == "/api/state":
            with self.server.lock:
                return self.send(self.server.session.view(self.server.mapdata))
        if path == "/api/timeline":
            return self.send(self.server.timeline)
        if path == "/api/map":
            return self.send(self.server.mapdata)
        if path == "/api/diagnostics":
            with self.server.lock:
                return self.send({"narration": "live_available" if os.getenv("OPENAI_API_KEY", "").strip() else "missing_api_key",
                                  "last_question_channel": "see session JSONL",
                                  "source_sha256": self.server.timeline["source_sha256"],
                                  "log_file": str(self.server.session.logs)})
        return self.send({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path not in ("/api/command", "/api/ask", "/api/new", "/api/evidence"):
            return self.send({"error": "Not found"}, 404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 4096 or size < 2:
                raise ValueError("Invalid request size")
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError("JSON object required")
            with self.server.lock:
                s = self.server.session
                if self.path == "/api/new":
                    seed = body.get("seed")
                    if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed < 2**31):
                        raise ValueError("Seed out of range")
                    if s.mode not in ("quit", "complete"):
                        s.tick()
                        s.log("quit", quit_point=s.phase, reason="restart")
                    self.server.session = Session(self.server.timeline, seed, requested_case=body.get("case"))
                    return self.send(self.server.session.view(self.server.mapdata))
                if self.path == "/api/command":
                    action=body.get("action")
                    if action == "scrub":
                        s.scrub(body.get("percent"))
                    elif action in ("go", "hold", "quit"):
                        s.command(action)
                    else:
                        raise ValueError("Unknown command")
                    return self.send(s.view(self.server.mapdata))
                if self.path == "/api/evidence":
                    field = body.get("field")
                    fact = s.t["cases"][s.case].get(field) if isinstance(field, str) else None
                    if fact is None:
                        raise ValueError("Unknown evidence field")
                    s.log("evidence_open", field=field, source=fact["source"])
                    return self.send({"field": field, "value": fact["value"], "source": fact["source"], "earned": True})
                question = body.get("question")
                if not isinstance(question, str) or not 0 < len(question.strip()) <= 500:
                    raise ValueError("Question required, max 500 characters")
                s.tick()
                s.questions += 1
                s.log("captain_question", question=question.strip())
                line, facts, channel = llm_answer(question.strip(), s.t, s.case, self.server.excerpts)
                if not line:
                    s.log("narration_fallback", reason=channel, requested_live=True)
                    if channel.startswith("unsupported_numbers:"):
                        s.log("unsupported_claim", reason=channel)
                    line, facts = local_answer(question, s.t, s.case)
                    channel = "scripted"
                supports = [s.t["cases"][s.case][k]["source"] for k in facts]
                s.log("mara_reply", channel=channel, reply=line, fact_keys=facts, evidence_paths=supports)
                return self.send({"reply": line})
        except (ValueError, KeyError, TypeError) as exc:
            return self.send({"error": str(exc)}, 400)

    def log_message(self, fmt, *args):
        # No flight or question content on stdout.
        pass

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8877)
    opts = p.parse_args()
    server = Server(("127.0.0.1", opts.port), Handler)
    print(f"FIRST JUMP | FQ11 {server.timeline['source_sha256'][:12]} | http://127.0.0.1:{opts.port}", flush=True)
    print(f"SESSION LOG: {server.session.logs}", flush=True)
    print("Mara channel: " + ("LIVE MODEL READY" if os.getenv("OPENAI_API_KEY", "").strip() else "MISSING_API_KEY / SCRIPTED BACKUP"), flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
