import json, math
exec(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'node_map.py')).read().split("CL = [")[0])           # loads G, HW, nf, hw_hit, az, ad, LONG
exec("CL = [" + open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'node_map.py')).read().split("CL = [")[1].split("C = [cls(f)")[0])
STRK = [40, 140, 220, 320]
def snap_strake(a):
    for s in STRK:
        if ad(a, s) <= 12.7: return s, True
    return a, False
out = []
for f in nf:
    x, a = f['pos'][0], az(f['pos']); r = math.hypot(f['pos'][1], f['pos'][2]); c = cls(f)
    out.append(dict(x=round(x, 3), a=round(a, 3), r=round(r, 3), c=c, ring=f['ring']))
# after
after = []
door_rings = sorted({o['x'] for o in out if o['c'] == 'door'})
for o in out:
    x, a, r, c = o['x'], o['a'], o['r'], o['c']
    if c == 'torch':      # into the four hot-fin root trusses: 4 per fin per ring, nothing new outside the hull line (F1)
        j = int(round(a / 22.5)) % 16; fin = [40, 140, 220, 320][j // 4]; rr = [3.25, 3.75, 4.25, 4.7][j % 4]
        after.append(dict(x=x, a=fin, r=rr, c='finroot')); continue
    if c == 'bow': after.append(dict(x=2.35, a=a, r=4.5, c='bowframe')); continue
    if o['x'] in door_rings: continue                      # whole ring re-spaced below
    if c == 'strake': s, _ = snap_strake(a); after.append(dict(x=x, a=s, r=4.5, c='strakeroot')); continue
    after.append(dict(x=x, a=a, r=4.5, c='hwmove' if c == 'hw' else 'ok'))
for x in door_rings:          # 16 nodes evenly over the arc outside the doors (122.23 .. 57.77 + 360), 1.8 deg margins
    a0, a1 = 122.23 + 1.8, 57.77 + 360 - 1.8
    for k in range(16):
        a = (a0 + (a1 - a0) * k / 15) % 360; s, hit = snap_strake(a)
        after.append(dict(x=x, a=round(s if hit else a, 3), r=4.5, c='strakeroot' if hit else 'respaced'))
from collections import Counter
print(len(out), Counter(o['c'] for o in out)); print(len(after), Counter(o['c'] for o in after))
json.dump(dict(before=out, after=after), open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'nodes_before_after.json'), 'w'))
