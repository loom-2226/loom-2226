from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from loom.runtime_trace import RuntimeTrace, TRACE_CONTRACT


class RuntimeTraceTest(unittest.TestCase):
    def test_emit_writes_correlated_jsonl(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "logs" / "loom-trace.jsonl"
            trace = RuntimeTrace(path)
            trace_id = trace.new_trace_id("flight")
            row = trace.emit("discover.accepted", trace_id=trace_id, subsystem="gis", destination="MARS")
            saved = json.loads(path.read_text(encoding="utf-8").strip())
            self.assertEqual(saved["contract"], TRACE_CONTRACT)
            self.assertEqual(saved["trace_id"], trace_id)
            self.assertEqual(saved["event_id"], row["event_id"])
            self.assertEqual(saved["destination"], "MARS")

    def test_parent_event_is_preserved(self):
        with TemporaryDirectory() as tmp:
            trace = RuntimeTrace(Path(tmp) / "trace.jsonl")
            root = trace.emit("request", trace_id="tr-1", subsystem="http")
            child = trace.emit("execute", trace_id="tr-1", subsystem="campaign", parent_event_id=root["event_id"])
            self.assertEqual(child["parent_event_id"], root["event_id"])


if __name__ == "__main__":
    unittest.main()
