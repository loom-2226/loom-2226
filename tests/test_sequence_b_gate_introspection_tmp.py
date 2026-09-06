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
                '_build_leg_timeline',
                '_plan_geometry',
                '_route_local_offset_state',
                '_timeline_contract',
                '_route_parent_system_id',
            )
            print('\n=== ROUTE-SCOPED FLIGHT BUNDLE REQUIREMENTS ===')
            for name in names:
                print(f'--- {name} ---')
                value = getattr(nav, name, None)
                if not callable(value):
                    print('NOT CALLABLE')
                    continue
                try:
                    print(inspect.getsource(value))
                except Exception as exc:
                    print('SOURCE UNAVAILABLE', type(exc).__name__, exc)


if __name__ == '__main__':
    unittest.main()
