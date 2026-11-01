"""Focused playback tests: source-only numbers, gates, logging and HTTP."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen, Request
import hashlib
import json
import threading
import time
import unittest

import build_timeline as source
import server as game

class FirstJumpTests(unittest.TestCase):
    def test_exact_fq11_source_and_pointers(self):
        timeline = source.build()
        raw = source.SOURCE.read_bytes()
        self.assertEqual(timeline["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(timeline, json.loads(source.OUTPUT.read_text()))
        self.assertEqual(set(timeline["cases"]), {"NOMINAL", "UNDERBURN_1_PERCENT"})
        fq = json.loads(raw)
        for i, case in enumerate(fq["measured_cases"]):
            facts = timeline["cases"][case["case"]]
            for label, pointer in source.FIELDS.items():
                value = case
                for part in pointer.split("/"):
                    value = value[int(part)] if part.isdecimal() else value[part]
                self.assertEqual(facts[label]["value"], value)
                self.assertTrue(facts[label]["source"].endswith(
                    f"#/measured_cases/{i}/{pointer}"))
        self.assertIn("preburn_delta_v_km_s", timeline["unavailable"])
        self.assertNotIn("4.83", json.dumps(timeline))

    def test_seed_go_hold_completion_quit(self):
        with TemporaryDirectory() as d, patch.object(game, "LOG_DIR", Path(d)):
            session = game.Session(source.build(), seed=42)
            self.assertEqual(session.mode, "awaiting")
            session.command("go")
            self.assertEqual(session.phase, "preburn")
            session.command("hold")
            self.assertEqual(session.mode, "held")
            session.command("go")
            for phase in ("preburn", "metric", "turn", "trim"):
                self.assertEqual(session.phase, phase)
                session.since = time.monotonic() - game.PRESENTATION_S[phase] - 1
                session.tick()
                if phase != "trim":
                    self.assertEqual(session.mode, "awaiting")
                    session.command("go")
            self.assertEqual(session.mode, "complete")
            events = [json.loads(x) for x in session.logs.read_text().splitlines()]
            self.assertEqual(len([x for x in events if x["event"] == "phase_end"]), 4)
            self.assertTrue(any(x["event"] == "captain_hold" for x in events))
            other = game.Session(source.build(), seed=42)
            self.assertEqual(other.case, session.case)
            other.command("quit")
            self.assertTrue(any(json.loads(x)["event"] == "quit"
                                for x in other.logs.read_text().splitlines()))

    def test_numerical_claim_guard(self):
        permitted = game.allowed_numbers(source.build())
        self.assertIn("1234567", game.unsupported_numbers("Mara says 1234567 m/s", permitted))
        self.assertIn("million", game.unsupported_numbers("A million kilometres", permitted))
        self.assertFalse(game.unsupported_numbers("Canon II §7.1a", permitted))
        reply = game.local_answer("mismatch", source.build(), "NOMINAL")
        self.assertIn("19.43", reply)
        self.assertIn("#/measured_cases/0/forward_arrival_mismatch_m_s", reply)

    def test_http_and_no_flight_calculation(self):
        with TemporaryDirectory() as d, patch.object(game, "LOG_DIR", Path(d)):
            http = game.Server(("127.0.0.1", 0), game.Handler)
            thread = threading.Thread(target=http.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{http.server_address[1]}"
            try:
                def get(path):
                    with urlopen(base + path, timeout=4) as r:
                        return json.load(r)
                def post(path, body):
                    req = Request(base + path, data=json.dumps(body).encode(),
                                  headers={"Content-Type":"application/json"}, method="POST")
                    with urlopen(req, timeout=4) as r:
                        return json.load(r)
                state = get("/api/state")
                self.assertEqual(state["phase"], "briefing")
                self.assertFalse(state["case_revealed"])
                self.assertEqual(post("/api/command", {"action": "go"})["phase"], "preburn")
                self.assertEqual(post("/api/command", {"action": "hold"})["mode"], "held")
                with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
                    answer = post("/api/ask", {"question": "What is the mismatch?"})
                self.assertIn("FQ11", answer["source"])
                self.assertTrue(Path(http.session.logs).exists())
                self.assertEqual(get("/api/timeline")["source_sha256"], source.build()["source_sha256"])
                with urlopen(base + "/", timeout=4) as r:
                    self.assertIn(b"FIRST JUMP", r.read())
                with urlopen(base + "/art/cmd_pov.png", timeout=4) as r:
                    self.assertEqual(r.headers["Content-Type"], "image/png")
            finally:
                http.shutdown()
                http.server_close()

if __name__ == "__main__":
    unittest.main()
