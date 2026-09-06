from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import unittest
import loom_navigator_core as core


class SequenceBGateIntrospectionTemporaryTest(unittest.TestCase):
    def test_print_sequence_b_gate_surface(self):
        with TemporaryDirectory() as td:
            nav = core._load_core(Path(td) / 'seqh')
            names = (
                '_all_dependency_rows',
                '_build_local_geometry_models',
                '_route_rows_from_ep_aux',
                'compile_ephemeris_payload',
                'compile_route_payload',
                'compile_flight_payload',
                'compile_local_route_payload',
            )
            print('\n=== SEQUENCE-B DEPENDENCY CONSUMERS ===')
            for name in names:
                value = getattr(nav, name, None)
                print(f'--- {name} ---')
                if not callable(value):
                    print('NOT CALLABLE')
                    continue
                try:
                    print(inspect.getsource(value))
                except Exception as exc:
                    print('SOURCE UNAVAILABLE', type(exc).__name__, exc)


if __name__ == '__main__':
    unittest.main()
