from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import unittest
import loom_navigator_core as core


class SequenceBGateIntrospectionTemporaryTest(unittest.TestCase):
    def test_print_sequence_b_gate_surface(self):
        with TemporaryDirectory() as td:
            nav = core._load_core(Path(td) / 'seqh')
            print('\n=== TARGET DETERMINISM GATE ===')
            try:
                print(inspect.getsource(nav.target_determinism_gate))
            except Exception as exc:
                print('SOURCE UNAVAILABLE', type(exc).__name__, exc)
            print('\n=== MATCHING FUNCTIONS ===')
            needle='Sequence B requires direct B1-supported local ephemeris'
            for name in sorted(dir(nav)):
                value=getattr(nav,name)
                if callable(value):
                    try:
                        src=inspect.getsource(value)
                    except Exception:
                        continue
                    if needle in src or 'B1-supported local ephemeris' in src or 'missing_local' in src:
                        print(f'--- {name} ---')
                        print(src)


if __name__ == '__main__':
    unittest.main()
