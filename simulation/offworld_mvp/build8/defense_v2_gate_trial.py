"""Isolated, off-by-default Defense V2 accounting gate; no Earth funding authority."""
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
import hashlib
import json

from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import AccountKind, TxPurpose
from .country_capital_input import EARTH_V4, SOURCES
from .opening import EARTH_V4_ROOT, build_country_opening

PINNED_SHA256 = (
    '8524ada09880514088d8293df84b0cd5c4eac30dcf8d694b72192c75096e9f7c',
    '449072d0c18ac09fc9346622d5917ef70efcb7913b5facbbd3517aa800e3e112',
)
BURDEN, SPACE_SHARE, OFFWORLD = D('.034'), D('.04'), D('.05')
UNITS = D('1000000000')
EXPECTED_VA = D('23762479644861.543')


def admitted_value_added(root: Path, kernel):
    """Pin bytes, select the one USA 2026 REAL assertion, and check its value."""
    root = Path(root)
    if root.name != 'earth_long_run_economic_baseline_v4_2026_09_24':
        raise InvariantError('wrong Earth v4 designation')
    payloads = [(root / path).read_bytes() for path in SOURCES]
    hashes = tuple(hashlib.sha256(b).hexdigest() for b in payloads)
    if hashes != PINNED_SHA256:
        raise InvariantError('Earth v4 source hash mismatch')
    rows = [json.loads(line) for line in payloads[0].splitlines()]
    matches = [r for r in rows if r['iso3'] == 'USA' and int(r['year']) == 2026]
    if len(matches) != 1:
        raise InvariantError('expected one USA 2026 Earth value')
    value = D(str(matches[0]['value_added']))
    if not value.is_finite() or value != EXPECTED_VA:
        raise InvariantError('Earth value-added mismatch')
    existing = [a for a in kernel.boundary_manifest.assertions
                if a.subject_id == 'USA' and a.valid_from == '2026'
                and a.concept == 'value_added' and a.world_context == 'REAL']
    if len(existing) != 1:
        raise InvariantError('expected exactly one REAL value-added assertion')
    assertion = replace(existing[0], assertion_id='B8:USA:2026:value_added',
                        value=str(value), source_refs=(EARTH_V4, 'USA:2026'),
                        source_hashes=hashes,
                        authorization_ref='BUILD8_DEFENSE_V2_TEST_ONLY',
                        warrant_refs=('BUILD8_RESEARCH_VALUE_ADDED',))
    kernel.boundary_manifest = replace(
        kernel.boundary_manifest,
        assertions=tuple(assertion if a is existing[0] else a
                         for a in kernel.boundary_manifest.assertions))
    admitted = [a for a in kernel.boundary_manifest.assertions
                if a.subject_id == 'USA' and a.valid_from == '2026'
                and a.concept == 'value_added' and a.world_context == 'REAL']
    if len(admitted) != 1 or admitted[0] != assertion or D(assertion.value) != value:
        raise InvariantError('value-added assertion admission mismatch')
    return value, assertion


def run(*, enabled=False, funded=D(0), requested=None, root=EARTH_V4_ROOT):
    """TEST_ONLY funding is an authored mechanics balance, never sourced from VA."""
    if not enabled:
        return None
    funded = D(funded)
    if not funded.is_finite() or funded < 0:
        raise InvariantError('invalid TEST_ONLY funding')
    kernel, _, _, provenance = build_country_opening(root, world_seed='B8-DEFENSE-V2-GATE')
    if tuple(s['sha256'] for s in provenance['sources']) != PINNED_SHA256:
        raise InvariantError('opening provenance mismatch')
    value, assertion = admitted_value_added(root, kernel)
    ceiling = value * BURDEN * SPACE_SHARE * OFFWORLD / UNITS
    amount = ceiling if requested is None else D(requested)
    if not amount.is_finite() or amount < 0 or amount > ceiling:
        raise InvariantError('invalid or over-ceiling defense request')
    source = kernel.state.accounts['b8_source:USA']
    if source.balance != 0:
        raise InvariantError('expected zero-balance Earth boundary')
    source.balance = funded  # TEST_ONLY initial mechanics balance, NOT an Earth inflow.
    destination = 'defense:funds:USA'
    kernel.add_account(destination, 'DEFENSE:USA', 'EARTH:USA', AccountKind.FUNDS)
    before = source.balance + kernel.state.accounts[destination].balance
    tx = kernel.transfer(1, 'b8_source:USA', destination, amount,
                         TxPurpose.OTHER_INVESTMENT,
                         parent_ids=('DEFENSE_V2_TEST_ONLY', assertion.assertion_id))
    after = source.balance + kernel.state.accounts[destination].balance
    if before != after or source.balance < 0 or tx.amount != amount:
        raise InvariantError('defense conservation failure')
    kernel.assert_invariants()
    return (str(ceiling), str(amount), str(source.balance),
            str(kernel.state.accounts[destination].balance), tx.id,
            assertion.source_hashes)
