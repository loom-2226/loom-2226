"""First Jump v0.2: locked FQ11 source, in-world story, evidence, live-model seam."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen, Request
import hashlib
import io
import json
import threading
import time
import unittest

import build_timeline as source
import server as game

class MockResponse:
    def __init__(self, body):
        self.body = io.BytesIO(json.dumps(body).encode())
    def __enter__(self):
        return self.body
    def __exit__(self, *args):
        return False

class FirstJumpTests(unittest.TestCase):
    def test_exact_fq11_evidence(self):
        timeline = source.build()
        raw = source.SOURCE.read_bytes()
        self.assertEqual(timeline["source_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(timeline, json.loads(source.OUTPUT.read_text()))
        self.assertEqual(set(timeline["cases"]), {"NOMINAL", "UNDERBURN_1_PERCENT"})
        fq = json.loads(raw)
        for i, case in enumerate(fq["measured_cases"]):
            for label, pointer in source.FIELDS.items():
                value = case
                for part in pointer.split("/"):
                    value = value[int(part)] if part.isdecimal() else value[part]
                fact = timeline["cases"][case["case"]][label]
                self.assertEqual(fact["value"], value)
                self.assertEqual(fact["source"], f"{timeline['source']}#/measured_cases/{i}/{pointer}")
        self.assertNotIn("4.83", json.dumps(timeline))
        self.assertIn("preburn_delta_v_km_s", timeline["unavailable"])

    def test_first_nominal_replay_variant_and_go_hold(self):
        with TemporaryDirectory() as d, patch.object(game, "LOG_DIR", Path(d)):
            t = source.build()
            m = game.load_map(t)
            first = game.Session(t,m,seed=42,first=True)
            self.assertEqual(first.case,"NOMINAL")
            other = game.Session(t,m,seed=42,requested_case="UNDERBURN_1_PERCENT")
            self.assertEqual(other.case,"UNDERBURN_1_PERCENT")
            self.assertEqual(first.phase,"briefing")
            self.assertEqual(first.view()["next_gate"],"burn")
            first.command("go")
            self.assertEqual(first.phase,"preburn")
            self.assertEqual(first.mode,"active")
            # Complete burn via stage pacing, gate JUMP only.
            first.since = time.monotonic()-game.PRESENTATION_S["preburn"]-1
            first.tick()
            self.assertEqual(first.mode,"awaiting")
            self.assertEqual(first.view()["next_gate"],"jump")
            first.command("go")
            self.assertEqual(first.phase,"metric")
            # Metric automatically advances into the turn, with no gate.
            first.since = time.monotonic()-game.PRESENTATION_S["metric"]-5
            first.tick()
            self.assertEqual(first.mode,"active")
            self.assertEqual(first.phase,"turn")
            first.command("hold")
            self.assertEqual(first.mode,"held")
            first.command("go")
            first.since = time.monotonic()-game.PRESENTATION_S["turn"]-1
            first.tick()
            self.assertEqual(first.mode,"awaiting")
            self.assertEqual(first.view()["next_gate"],"trim")
            first.command("go")
            self.assertEqual(first.phase,"trim")
            first.since=time.monotonic()-game.PRESENTATION_S["trim"]-1
            first.tick()
            self.assertEqual(first.mode,"complete")
            self.assertEqual(first.phase,"debrief")
            events=[json.loads(x) for x in first.logs.read_text().splitlines()]
            self.assertEqual([x["gate"] for x in events if x["event"]=="captain_authorise"],["burn","jump","trim"])
            self.assertEqual(sum(x["event"]=="phase_end" for x in events),4)
            other.command("quit")
            self.assertTrue(any(json.loads(x)["event"]=="quit" for x in other.logs.read_text().splitlines()))

    def test_numerical_claims_and_model_in_world(self):
        timeline=source.build()
        permitted=game.allowed_numbers(timeline,"NOMINAL")
        self.assertIn("1234567",game.unsupported_numbers("1234567 m/s",permitted))
        self.assertIn("million",game.unsupported_numbers("A million kilometres",permitted))
        self.assertFalse(game.unsupported_numbers("Canon II §7.1a",permitted))
        packet={"output":[{"content":[{"type":"output_text","text":json.dumps({
            "line":"Captain, the departure burn lasted 497.7 seconds. Time to cross the weave.",
            "facts":["preburn_s"],"canon":["7.1a"]})}]}]}
        reqs=[]
        def fake_open(req,timeout=0):
            reqs.append(json.loads(req.data.decode()))
            return MockResponse(packet)
        with patch.dict("os.environ",{"OPENAI_API_KEY":"test-only-redacted"}),patch.object(game,"urlopen",side_effect=fake_open):
            line,facts,status=game.llm_answer("Burn duration?",timeline,"NOMINAL",{"Canon II §7.1a":"canon passage"})
        self.assertEqual(status,"live_llm")
        self.assertEqual(facts,["preburn_s"])
        self.assertNotIn("FQ11",line)
        self.assertNotIn("Canon",line)
        self.assertIn("preburn_s",reqs[0]["input"])
        self.assertIn("canon passage",reqs[0]["input"])
        packet["output"][0]["content"][0]["text"]=json.dumps({"line":"We made 987654 km in a moment.","facts":["preburn_s"],"canon":[]})
        with patch.dict("os.environ",{"OPENAI_API_KEY":"test-only-redacted"}),patch.object(game,"urlopen",side_effect=fake_open):
            line,facts,status=game.llm_answer("How far?",timeline,"NOMINAL",{"Canon II §7.1a":"canon"})
        self.assertIsNone(line)
        self.assertTrue(status.startswith("unsupported_numbers:"))

    def test_http_evidence_tap_logging_and_story_reply(self):
        with TemporaryDirectory() as d,patch.object(game,"LOG_DIR",Path(d)):
            server=game.Server(("127.0.0.1",0),game.Handler)
            worker=threading.Thread(target=server.serve_forever,daemon=True)
            worker.start()
            base=f"http://127.0.0.1:{server.server_address[1]}"
            def get(path):
                with urlopen(base+path,timeout=5) as r:return json.load(r)
            def post(path,body):
                request=Request(base+path,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
                with urlopen(request,timeout=5) as r:return json.load(r)
            try:
                s=get("/api/state")
                self.assertEqual(s["phase"],"briefing")
                self.assertEqual(server.session.case,"NOMINAL")
                self.assertNotIn("mara_mode",s)
                s=post("/api/command",{"action":"go"})
                fact=next(f for f in s["facts"] if f["field"]=="preburn_kg")
                self.assertTrue(fact["earned"])
                trace=post("/api/evidence",{"field":"preburn_kg"})
                self.assertEqual(trace["source"],fact["source"])
                with patch.dict("os.environ",{"OPENAI_API_KEY":""}):
                    answer=post("/api/ask",{"question":"What is the burn doing?"})
                self.assertIn("reply",answer)
                self.assertNotIn("mode",answer)
                self.assertNotIn("FQ11",answer["reply"])
                self.assertNotIn("Canon",answer["reply"])
                logs=[json.loads(l) for l in server.session.logs.read_text().splitlines()]
                self.assertTrue(any(x["event"]=="evidence_open" for x in logs))
                self.assertTrue(any(x["event"]=="narration_fallback" and x["reason"]=="missing_api_key" for x in logs))
                self.assertTrue(any(x["event"]=="mara_reply" and x["channel"]=="scripted" for x in logs))
                self.assertEqual(get("/api/diagnostics")["source_sha256"],source.build()["source_sha256"])
                with urlopen(base+"/",timeout=5) as response:
                    html=response.read().decode()
                self.assertIn('/clock.js',html)
                with urlopen(base+"/clock.js",timeout=5) as r:
                    script=r.read().decode()
                self.assertIn("Holding at Mars approach shell. Mars Traffic has us from here.",script)
                self.assertIn("requestAnimationFrame",script)
                self.assertIn("earned",script)
                with urlopen(base+"/art/cmd_pov.png",timeout=5) as response:
                    self.assertEqual(response.headers["Content-Type"],"image/png")
            finally:
                server.shutdown();server.server_close()

if __name__=="__main__":
    unittest.main()
