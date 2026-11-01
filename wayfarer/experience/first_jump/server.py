"""First Jump: FQ11 evidence playback for a local Pixel browser.

Standard library only. UI requests presentation state, never flight physics.
No Navigator or mutable simulation state.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
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
    "turn": "cmd_cutaway.png",
    "trim": "ext_departure.png",
    "debrief": "cmd_pov.png",
}
ART_DIR = ROOT / "wayfarer/render/out"
LOG_DIR = Path(os.getenv("FIRST_JUMP_LOG_DIR", str(Path.home() / ".local/state/loom/first_jump")))
CANON_PATH = ROOT / "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md"
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
            {"label": "FLIGHT", "value": "Earth → Mars", "source": t["source"]},
            {"label": "RECORD", "value": "Accepted FQ11 replay; captain GO/HOLD", "source": t["source"]},
            {"label": "COLLAPSE", "value": "Mars approach shell / placeholder", "source": "Earth/Mars Option A decision; no distance"},
            {"label": "PREBURN ΔV", "value": "NOT REPORTED IN FQ11", "source": t["source"]},
        ]
    names = {
        "preburn": [("BURN DURATION", "preburn_s", "s", 1), ("PEAK ACCEL", "preburn_peak_g", "g", 3), ("REMASS USED", "preburn_kg", "kg", 1)],
        "metric": [("METRIC TRANSIT", "metric_s", "s", 1), ("NATURAL MISS", "arrival_mismatch_m_s", "m/s", 2)],
        "turn": [("ARRIVAL MISS", "arrival_mismatch_m_s", "m/s", 2), ("RCS TURN", "turn_s", "s", 1), ("CONTROL RATE", "turn_hz", "Hz", 1), ("POINT TURN", "turn_deg", "deg", 2)],
        "trim": [("TRIM BURN", "trim_s", "s", 3), ("TRIM REMASS", "trim_kg", "kg", 2), ("FINAL MISS", "final_mismatch_m_s", "m/s", 3)],
        "debrief": [("FINAL MISS", "final_mismatch_m_s", "m/s", 3), ("TOTAL REMASS", "total_remass_kg", "kg", 1), ("REMAINING", "remass_remaining_kg", "kg", 1)],
    }
    return [{"label": label, "value": rounded(v(key), precision) + " " + unit, "source": src(key)}
            for label, key, unit, precision in names[phase]]

def allowed_numbers(t):
    nums = set()
    for case in t["cases"].values():
        for evidence in case.values():
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
    words = r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|hundred|thousand|million|billion)\b"
    unsupported.update(w.lower() for w in re.findall(words, clean, flags=re.I))
    return sorted(unsupported)

def local_answer(q, t, case):
    e = values_for(t, case)
    low = q.lower()
    ref = lambda k: e[k]["source"]
    if any(w in low for w in ("mismatch", "miss", "arrival", "recovery", "trim")):
        k = "arrival_mismatch_m_s"
        return f"Natural Mars-relative mismatch: {rounded(e[k]['value'], 2)} m/s. The accepted FQ11 finite trim closes to {rounded(e['final_mismatch_m_s']['value'],3)} m/s. [{ref(k)}; {ref('final_mismatch_m_s')}]"
    if any(w in low for w in ("burn", "fuel", "remass", "accel")):
        k = "preburn_kg"
        return f"Measured preburn remass is {rounded(e[k]['value'],1)} kg; peak acceleration {rounded(e['preburn_peak_g']['value'],3)} g. FQ11 does not report a standalone preburn delta-v. [{ref(k)}; {ref('preburn_peak_g')}]"
    if any(w in low for w in ("physics", "energy", "sun", "canon", "velocity", "how")):
        return "Canon II §7.1a specifies the scoped natural arrival-velocity rule; §7.1b declares solar momentum and angular-momentum exchange as identities by construction, not independent physical proof. [Canon II §7.1a/b]"
    if any(w in low for w in ("shell", "distance", "capture", "orbit", "position")):
        return "Mars approach shell is only declared placeholder geometry. FQ11 does not certify collapse position or orbital capture. [FQ11 limitations; Canon II §7.1a]"
    return "I have FQ11's accepted flight evidence and Canon II §7.1a/b, not an independent physics engine. Ask about the burn, mismatch, trim, or arrival limits. [FQ11; Canon II §7.1a/b]"

def llm_answer(question, t, case, excerpts):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None, "offline"
    payload = {
        "model": os.getenv("FIRST_JUMP_MODEL", "gpt-4.1-mini"),
        "instructions": (
            "You narrate Wayfarer First Jump as MARA, a NON-CANON playable flight-computer role, "
            "not the canonical captain. You have NO physics, calculation or command authority. "
            "Answer only from the supplied accepted FQ11 case evidence and Canon II excerpts. "
            "Every quantitative flight statement MUST cite its exact FQ11 JSON pointer. "
            "Canon claims cite Canon II §7.1a or §7.1b. "
            "No new numbers, inferred distances, speeds, velocities, positions or capture claims. "
            "If evidence is missing, say it is not in FQ11. Speak in under 90 words."
        ),
        "input": json.dumps({
            "captain_question": question,
            "phase": "First Jump Earth to Mars",
            "selected_case": case,
            "numeric_evidence": t["cases"][case],
            "canonical_excerpts": excerpts,
            "unavailable": t["unavailable"],
        }, ensure_ascii=False),
        "max_output_tokens": 260
    }
    request = Request("https://api.openai.com/v1/responses",
                      data=json.dumps(payload).encode(), method="POST",
                      headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=18) as response:
            out = json.load(response)
        chunks = [part.get("text", "")
                  for output in out.get("output", [])
                  for part in output.get("content", [])
                  if part.get("type") == "output_text"]
        return " ".join(chunks).strip() or None, "llm"
    except (OSError, ValueError, URLError, KeyError):
        return None, "llm_error"

class Session:
    def __init__(self, timeline, seed=None):
        self.t = timeline
        self.seed = int(seed) if seed is not None else secrets.randbelow(2**31)
        self.case = random.Random(self.seed).choice(["NOMINAL", "UNDERBURN_1_PERCENT"])
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

    def view(self):
        self.tick()
        phase = self.phase
        display_phase = phase
        if phase == "debrief":
            progress = 100
        elif phase == "briefing":
            progress = 0
        else:
            progress = round(100 * self.spent / PRESENTATION_S[phase], 1)
        return {
            "id": self.id, "seed": self.seed, "phase": phase,
            "mode": self.mode, "progress_percent": progress,
            "scene": ART[display_phase], "case_revealed": self.i >= 2,
            "variant": self.case if self.i >= 2 else "SEALED",
            "facts": evidence_lines(self.t, self.case, phase),
            "physical_phase_s": (self.t["cases"][self.case].get(phase + "_s") or {}).get("value"),
            "viewing_phase_s": round(self.spent, 1),
            "mara_mode": "LLM" if os.getenv("OPENAI_API_KEY") else "OFFLINE EVIDENCE",
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
        self.lock = RLock()
        self.session = Session(self.timeline)
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
                return self.send(self.server.session.view())
        if path == "/api/timeline":
            return self.send(self.server.timeline)
        return self.send({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path not in ("/api/command", "/api/ask", "/api/new"):
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
                    self.server.session = Session(self.server.timeline, seed)
                    return self.send(self.server.session.view())
                if self.path == "/api/command":
                    if body.get("action") not in ("go", "hold", "quit"):
                        raise ValueError("Unknown command")
                    s.command(body["action"])
                    return self.send(s.view())
                question = body.get("question")
                if not isinstance(question, str) or not 0 < len(question.strip()) <= 500:
                    raise ValueError("Question required, max 500 characters")
                s.tick()
                s.questions += 1
                s.log("captain_question", question=question.strip())
                reply, provider = llm_answer(question.strip(), s.t, s.case, self.server.excerpts)
                bad = unsupported_numbers(reply, allowed_numbers(s.t)) if reply else []
                if bad:
                    s.log("unsupported_claim", offending_numbers=bad, rejected_reply=reply, provider=provider)
                    reply = None
                if not reply:
                    reply = local_answer(question, s.t, s.case)
                    provider = "evidence_fallback"
                s.log("mara_reply", provider=provider, reply=reply)
                return self.send({"reply": reply, "mode": provider, "source": "FQ11 + Canon II"})
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
    print("Narration: LLM when OPENAI_API_KEY is present; cited deterministic fallback otherwise", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
