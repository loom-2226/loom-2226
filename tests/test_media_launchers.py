import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


class MediaLauncherTest(unittest.TestCase):
    def _run(self,path,env):
        captured={}
        def fake_call(argv,env=None):captured['argv']=list(argv);captured['env']=dict(env or {});return 0
        with patch.dict('os.environ',env,clear=True),patch('pathlib.Path.exists',return_value=True),patch('subprocess.call',side_effect=fake_call):
            with self.assertRaises(SystemExit) as raised:runpy.run_path(str(ROOT/path),run_name='__main__')
        self.assertEqual(raised.exception.code,0);return captured

    def test_android_media_launcher_uses_app_code_and_data_topology(self):
        app='/tmp/app';data='/tmp/loom/data'
        r=self._run('deploy/android/launch_media_library.py',{'LOOM_APP_ROOT':app,'LOOM_DATA_ROOT':data})
        self.assertEqual(Path(r['argv'][1]),Path(app).resolve()/'src/loom_media_library.py')
        self.assertEqual(r['argv'][-2:],[ '--root',str(Path(data).resolve().parent)])
        self.assertEqual(r['env']['LOOM_HOME'],str(Path(app).resolve()))
        self.assertEqual(r['env']['LOOM_DATA_ROOT'],str(Path(data).resolve()))

    def test_windows_media_launcher_uses_explicit_split_roots(self):
        app='/tmp/app';data='/tmp/loom/data'
        r=self._run('deploy/windows/launch_media_library.py',{'LOOM_APP_ROOT':app,'LOOM_DATA_ROOT':data})
        self.assertEqual(Path(r['argv'][1]),Path(app).resolve()/'src/loom_media_library.py')
        self.assertEqual(r['argv'][-2:],[ '--root',str(Path(data).resolve().parent)])


if __name__=='__main__':unittest.main()
