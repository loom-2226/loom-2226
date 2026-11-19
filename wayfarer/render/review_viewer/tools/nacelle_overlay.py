"""Extract the 20 nacelle solids from the PR #561 candidate GLBs into small overlay GLBs for the review viewer.
Visual reference only. ALL bodies. ALL sponsors. 2026-2226.
Output: glb wrappers {"glb_base64": ...} at <out>/nacelles_tucked.json (torch state) and nacelles_deployed.json (Metric state)."""
import base64, json, struct, sys
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[3]   # wayfarer/
SRC = {'tucked': R / 'render/candidates/wayfarer_nacelle_torch_f173094b.glb', 'deployed': R / 'candidates/wayfarer_nacelle_Metric_f173094b.glb'}
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else R / 'render/review_viewer/glb'
CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

def subset(path):
    b = path.read_bytes(); L = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + L]); b0 = 20 + L
    BL = struct.unpack('<I', b[b0:b0 + 4])[0]; buf = b[b0 + 8:b0 + 8 + BL]
    def acc(i):
        a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        return a, np.frombuffer(buf, CT[a['componentType']], count=a['count'] * NC[a['type']], offset=off).copy()
    root = j['scenes'][0]['nodes'][0]; keep = [c for c in j['nodes'][root].get('children', []) if (j['nodes'][c].get('name') or '').startswith('candidate:')]
    assert len(keep) == 20, len(keep)
    out = dict(asset=dict(version='2.0', generator='nacelle_overlay.py from ' + path.name), scene=0, scenes=[dict(nodes=[0])],
               nodes=[dict(name=j['nodes'][root].get('name'), **{k: j['nodes'][root][k] for k in ('rotation', 'translation', 'scale', 'matrix') if k in j['nodes'][root]}, children=[])],
               meshes=[], accessors=[], bufferViews=[], materials=[], buffers=[])
    if 'extensionsUsed' in j: out['extensionsUsed'] = j['extensionsUsed']
    blob = bytearray(); matmap = {}
    def put(a, arr, target):
        nonlocal blob
        while len(blob) % 4: blob += b'\0'
        off = len(blob); raw = arr.tobytes(); blob += raw
        out['bufferViews'].append(dict(buffer=0, byteOffset=off, byteLength=len(raw), **({'target': target} if target else {})))
        na = {k: a[k] for k in ('componentType', 'count', 'type', 'min', 'max', 'normalized') if k in a}; na['bufferView'] = len(out['bufferViews']) - 1
        out['accessors'].append(na); return len(out['accessors']) - 1
    for k in keep:
        n = j['nodes'][k]; m = j['meshes'][n['mesh']]; prims = []
        for p in m['primitives']:
            q = dict(attributes={})
            for an, ai in p['attributes'].items():
                if an in ('POSITION', 'NORMAL'): a, arr = acc(ai); q['attributes'][an] = put(a, arr, 34962)
            a, arr = acc(p['indices']); q['indices'] = put(a, arr, 34963)
            if 'material' in p:
                if p['material'] not in matmap: matmap[p['material']] = len(out['materials']); out['materials'].append(j['materials'][p['material']])
                q['material'] = matmap[p['material']]
            prims.append(q)
        out['meshes'].append(dict(name=n['name'][len('candidate:'):], primitives=prims))
        nn = dict(name=n['name'][len('candidate:'):], mesh=len(out['meshes']) - 1, extras=n.get('extras', {}))
        nn.update({kk: n[kk] for kk in ('rotation', 'translation', 'scale', 'matrix') if kk in n})
        out['nodes'].append(nn); out['nodes'][0]['children'].append(len(out['nodes']) - 1)
    while len(blob) % 4: blob += b'\0'
    out['buffers'] = [dict(byteLength=len(blob))]
    js = json.dumps(out, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
    glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(blob), 0x004E4942) + bytes(blob)
    return glb

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for state, p in SRC.items():
        g = subset(p); (OUT / f'nacelles_{state}.json').write_text(json.dumps({'glb_base64': base64.b64encode(g).decode()}))
        print(state, len(g), 'bytes')
