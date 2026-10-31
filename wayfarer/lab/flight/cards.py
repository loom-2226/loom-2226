"""Propulsion cards for the flight lab. ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING. A ship entry may name a card with "card": "<id>". The card's
"fields" are merged into the entry; a field set in both places is an error,
so a card can never be silently overridden. Only "fields" reach flightlab;
"declared" is documentation. Ship-side limits (tank, heat ceiling, crew g
cap, trim) stay on the ship entry."""
import json,hashlib
from pathlib import Path
CARDS=Path(__file__).resolve().parent/'cards'
def _h(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load_cards(root=CARDS):
    out={}
    for p in sorted(Path(root).glob('*/*.json')):
        c=json.loads(p.read_text())
        if c['id'] in out:raise ValueError('duplicate card id '+c['id'])
        if p.parent.name!=c['kind']:raise ValueError(f"{p}: kind {c['kind']} not in folder {p.parent.name}")
        out[c['id']]=c
    return out
def _merge(entry,cards,kind,used):
    if 'card' not in entry:return entry
    cid=entry['card'];c=cards.get(cid)
    if c is None:raise ValueError('unknown card '+cid)
    if c['kind']!=kind:raise ValueError(f'card {cid} is {c["kind"]}, used as {kind}')
    rest={k:v for k,v in entry.items() if k!='card'}
    clash=set(rest)&set(c['fields'])
    if clash:raise ValueError(f'card {cid}: field(s) set on ship entry too: {sorted(clash)}')
    used[cid]={'id':cid,'kind':kind,'sha256':_h(c)}
    return {**json.loads(json.dumps(c['fields'])),**rest}
def resolve(ship,root=CARDS):
    """Return (ship with cards expanded, list of cards used with hashes)."""
    cards=load_cards(root);used={};s=json.loads(json.dumps(ship))
    for key,kind in (('rcs','rcs'),('torch','torch')):
        s[key]=[_merge(e,cards,kind,used) for e in s.get(key,[])]
    if 'metric' in s:s['metric']={k:_merge(v,cards,'metric',used) for k,v in s['metric'].items()}
    return s,sorted(used.values(),key=lambda x:x['id'])
