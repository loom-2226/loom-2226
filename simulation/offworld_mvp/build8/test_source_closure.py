"""Guard Build 8 tracked-module import closure against undeclared local files."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class SourceClosureTests(unittest.TestCase):
    def test_clean_checkout_imports_all_build8_modules(self):
        repo = Path(__file__).resolve().parents[3]
        names = subprocess.check_output(
            ['git', 'ls-files', 'simulation/offworld_mvp/build8/*.py'],
            cwd=repo, text=True).splitlines()
        self.assertTrue(names, 'No tracked Build 8 Python modules')
        with tempfile.TemporaryDirectory(prefix='b8-import-closure-') as tmp:
            # Only tracked files are present; untracked scripts cannot mask omissions.
            subprocess.run(['git', 'archive', 'HEAD', '-o', str(Path(tmp)/'tree.tar')],
                           cwd=repo, check=True, capture_output=True)
            import tarfile
            with tarfile.open(Path(tmp)/'tree.tar') as archive:
                archive.extractall(Path(tmp)/'checkout', filter='data')
            root = Path(tmp)/'checkout'
            env = dict(os.environ)
            env['PYTHONPATH'] = os.pathsep.join(str(root / path) for path in
                ('src', 'simulation/offworld_mvp/phase3b/kernel', '.'))
            modules = ['.'.join(Path(name).with_suffix('').parts) for name in names]
            script = '''import importlib,sys
skipped=[]
for name in sys.argv[1:]:
    if name.endswith('.lunar_2027_continuation_trial'):
        try:
            import psycopg
        except ImportError:
            skipped.append(name)
            continue
    importlib.import_module(name)
expected=['simulation.offworld_mvp.build8.lunar_2027_continuation_trial']
assert not skipped or skipped==expected, ('unexpected skipped modules',skipped)
print('CLEAN_TRACKED_IMPORT_PASS',len(sys.argv)-1-len(skipped),'SKIPPED',len(skipped),'SKIPPED_MODULES',skipped,flush=True)
'''
            result = subprocess.run([sys.executable, '-c', script, *modules],
                                    cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main()
