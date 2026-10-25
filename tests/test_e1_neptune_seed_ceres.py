from __future__ import annotations

import importlib.util
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SEED_PATH = REPO / 'engineering' / 'experience_one' / 'e1_neptune_seed_ceres.py'
NAV_PATH = REPO / 'src' / 'loom_navigator_core.py'


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retime_fresh_state_uses_navigator_state_authority():
    seed = load(SEED_PATH, 'e1_neptune_seed_test')
    nav = load(NAV_PATH, 'e1_neptune_nav_test')
    original = nav._new_state('E1_TEST', 'WAYFARER')
    target = '2226-08-22T00:00:00Z'

    retimed = seed.retime_fresh_state(nav, original, target)

    assert original['epoch_utc'] == '2027-06-15T02:00:00Z'
    assert retimed['epoch_utc'] == target
    assert retimed['location_token'] == 'CERES'
    assert retimed['revision'] == original['revision']
    assert retimed['state_id'] != original['state_id']
    nav._validate_state(retimed)


def test_retime_rejects_non_utc_epoch():
    seed = load(SEED_PATH, 'e1_neptune_seed_test_bad_epoch')
    nav = load(NAV_PATH, 'e1_neptune_nav_test_bad_epoch')
    original = nav._new_state('E1_TEST', 'WAYFARER')

    try:
        seed.retime_fresh_state(nav, original, '2226-08-22T10:00:00+10:00')
    except RuntimeError as exc:
        assert 'explicit UTC' in str(exc)
    else:
        raise AssertionError('non-UTC E1 qualification epoch must fail closed')
