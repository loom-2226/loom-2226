"""Wrap the PR #567 B4-S candidate GLB (stowed, rolled 90 deg) for the review viewer. Visual reference only.
ALL bodies. ALL sponsors. 2026-2226. The hull node is renamed dry:shuttle so the viewer skips the v1 shuttle in the
exterior file (first file wins); other parts become dry:shuttle_b4s_<part>. Output: <out>/shuttle_b4s.json."""
import base64, json, struct, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
SRC = R / 'render/out/b4s_candidates/wayfarer_b4s_rolled90_standard.glb'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else R / 'render/review_viewer/glb'
b = SRC.read_bytes(); L = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + L]); rest = b[20 + L:]
for n in j['nodes']:
    n['name'] = 'dry:shuttle' if n.get('name') == 'hull' else 'dry:shuttle_b4s_' + n.get('name', '')
js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + len(rest)) + struct.pack('<II', len(js), 0x4E4F534A) + js + rest
OUT.mkdir(parents=True, exist_ok=True); (OUT / 'shuttle_b4s.json').write_text(json.dumps({'glb_base64': base64.b64encode(glb).decode()}))
print(len(glb), 'bytes')
