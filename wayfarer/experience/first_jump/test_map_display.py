"""First Jump v0.3 display-only invariants and HTTP control checks."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import Request, urlopen
import hashlib
import json
import threading
import unittest
import server as game
import build_timeline

class MapDisplayTests(unittest.TestCase):
    def test_source_ephemeris_and_no_metric_ship_path(self):
        timeline=build_timeline.build()
        mapdata=game.load_map(timeline)
        self.assertEqual(mapdata["epoch_utc"],"2226-08-29T05:00:00Z")
        self.assertEqual(mapdata["source_fq11_result_sha256"],timeline["source_sha256"])
        self.assertEqual(mapdata["source_input_sha256"],hashlib.sha256(game.FQ11_INPUT.read_bytes()).hexdigest())
        self.assertIsNone(mapdata["metric_path"])
        self.assertIsNone(mapdata["mars_approach_range"])
        self.assertEqual(set(mapdata["body_labels"]),{"EA","MA"})
        self.assertGreater(len(mapdata["samples"]),100)
        self.assertEqual(mapdata["samples"][0]["elapsed_s"],0)
        self.assertNotEqual(mapdata["samples"][0]["EA"],mapdata["samples"][-1]["EA"])
        self.assertNotEqual(mapdata["samples"][0]["MA"],mapdata["samples"][-1]["MA"])
        self.assertEqual(len(mapdata["orbit_context"]["EA"]),121)
        self.assertEqual(len(mapdata["orbit_context"]["MA"]),121)

    def test_scrub_held_and_precompiled_frame_selection(self):
        with TemporaryDirectory() as d, patch.object(game,"LOG_DIR",Path(d)):
            t=build_timeline.build()
            m=game.load_map(t)
            s=game.Session(t,m,seed=42,first=True)
            s.command("go")
            self.assertEqual(s.phase,"preburn")
            s.scrub(s.ends[0]*.75)
            self.assertEqual(s.mode,"held")
            view=s.view(m)
            self.assertAlmostEqual(view["progress_percent"],75,places=1)
            self.assertGreater(view["map_index"],0)
            before=view["mission_clock_s"]
            self.assertGreater(before,0)
            s.command("go")
            self.assertEqual(s.mode,"active")
            self.assertTrue(any(json.loads(line)["event"]=="captain_scrub" for line in s.logs.read_text().splitlines()))
            s.command("hold")
            self.assertEqual(s.mode,"held")

    def test_map_http_readonly_and_scrub(self):
        with TemporaryDirectory() as d,patch.object(game,"LOG_DIR",Path(d)):
            srv=game.Server(("127.0.0.1",0),game.Handler)
            worker=threading.Thread(target=srv.serve_forever,daemon=True);worker.start()
            root="http://127.0.0.1:"+str(srv.server_address[1])
            def get(path):
                with urlopen(root+path,timeout=4) as r:return json.load(r)
            def post(path,body):
                req=Request(root+path,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
                with urlopen(req,timeout=4) as r:return json.load(r)
            try:
                m=get("/api/map")
                self.assertEqual(m["schema"],"FIRST_JUMP_SOLAR_DISPLAY_v0.3")
                self.assertIsNone(m["metric_path"])
                a=post("/api/command",{"action":"go"})
                self.assertEqual(a["phase"],"preburn")
                a=post("/api/command",{"action":"scrub","clock_s":srv.session.ends[0]*.5})
                self.assertEqual(a["mode"],"held")
                self.assertGreater(a["map_index"],0)
                self.assertEqual(post("/api/command",{"action":"go"})["mode"],"active")
                logs=[json.loads(line) for line in srv.session.logs.read_text().splitlines()]
                self.assertTrue(any(x["event"]=="captain_scrub" for x in logs))
            finally:
                srv.shutdown();srv.server_close()

if __name__=="__main__":unittest.main()
