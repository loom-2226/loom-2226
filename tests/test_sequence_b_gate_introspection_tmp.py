from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import re
import unittest
import loom_navigator_core as core


class SequenceBGateIntrospectionTemporaryTest(unittest.TestCase):
    def test_print_sequence_b_gate_surface(self):
        with TemporaryDirectory() as td:
            nav = core._load_core(Path(td) / 'seqh')

            def source(name):
                value = getattr(nav, name, None)
                if not callable(value):
                    return None
                try:
                    return inspect.getsource(value)
                except Exception:
                    return None

            print('\n=== EXPLICIT PIPELINE FUNCTIONS ===')
            for name in ('build_sequence_d_once', '_all_dependency_rows'):
                src = source(name)
                if src:
                    print(f'--- {name} ---')
                    print(src)

            print('\n=== ALL FUNCTIONS TOUCHING DEPENDENCY ROWS / LOCAL DICT ===')
            matches = []
            for name in sorted(dir(nav)):
                src = source(name)
                if not src:
                    continue
                if (
                    '_all_dependency_rows(' in src
                    or re.search(r'\blocal\s*\[', src)
                    or re.search(r'\blocal\.get\s*\(', src)
                    or re.search(r'\bfor\s+.*\s+in\s+local(?:\.|\b)', src)
                    or 'required_local' in src
                ):
                    matches.append((name, src))
            for name, src in matches:
                print(f'--- {name} ---')
                print(src)

            print('\n=== BUILD_SEQUENCE_D_ONCE DIRECT CALLEES ===')
            bsrc = source('build_sequence_d_once') or ''
            names = sorted(set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', bsrc)))
            for name in names:
                if name in {'if', 'for', 'len', 'dict', 'list', 'set', 'str', 'int', 'float', 'tuple', 'sorted', 'range', 'enumerate', 'zip', 'min', 'max', 'abs', 'round'}:
                    continue
                src = source(name)
                if src:
                    print(f'--- {name} ---')
                    print(src)


if __name__ == '__main__':
    unittest.main()
