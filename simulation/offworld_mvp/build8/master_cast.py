"""Identity-only access to the noncanon Build 8 master cast.

Scenario parameters, funding participation and service selections stay authored
in the experiment. This module does not select contractors or score capacity.
"""
import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def actors():
    rows=json.loads(Path(__file__).with_name('master_cast_candidate.json').read_text())['actors']
    return {a['name']:a for a in rows}

def actor(name, role=None, category=None):
    entry=actors().get(name)
    if entry is None:
        raise ValueError(f'Build 8 actor not in master cast: {name}')
    if role is not None and role not in entry['roles']:
        raise ValueError(f'Build 8 actor {name} missing role {role}')
    if category is not None and not any(c['category']==category for c in entry['capabilities']):
        raise ValueError(f'Build 8 actor {name} missing capability {category}')
    return entry

def name(value, role=None, category=None):
    return actor(value, role=role, category=category)['name']
