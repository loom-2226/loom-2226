from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import unittest

import loom_navigator_core as core


class SequenceHIntrospectionTemporaryTest(unittest.TestCase):
    def test_print_acquisition_surface(self):
        with TemporaryDirectory() as td:
            nav = core._load_core(Path(td) / "seqh")
            print("\n=== SEQUENCE H ACQUISITION SURFACE ===")
            for name in sorted(dir(nav)):
                upper = name.upper()
                if any(token in upper for token in ("ACQU", "TARGET", "ROUTE", "OBJECT", "DEPEND", "BODY")):
                    value = getattr(nav, name)
                    if callable(value):
                        try:
                            sig = inspect.signature(value)
                        except Exception:
                            sig = "<?>"
                        print(f"CALLABLE {name}{sig}")
                    elif isinstance(value, (dict, list, tuple, set)):
                        text = repr(value)
                        if len(text) > 3000:
                            text = text[:3000] + "..."
                        print(f"VALUE {name}={text}")
            print("=== run_acquisition SOURCE ===")
            try:
                print(inspect.getsource(nav.run_acquisition))
            except Exception as exc:
                print("SOURCE UNAVAILABLE", type(exc).__name__, exc)
            print("=== build_canonical_dependency_index SOURCE ===")
            try:
                print(inspect.getsource(nav.build_canonical_dependency_index))
            except Exception as exc:
                print("SOURCE UNAVAILABLE", type(exc).__name__, exc)


if __name__ == "__main__":
    unittest.main()
