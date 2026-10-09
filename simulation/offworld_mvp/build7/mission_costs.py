"""Public lookup and authored scenario normalization for Build 7 mission costs.

USD-million amounts are normalized by the explicitly authorized scenario
proxy: USD millions / 1000 MODEL_CURRENCY. This is not an exchange rate.
"""
from __future__ import annotations

import csv
from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent / 'inputs/BUILD7_MISSION_COSTS_2026_2035_PROVISIONAL_V1.csv'
REMOTE_EXPLORATION_MISSION_TYPE = 'ORBITAL_RECON'
USD_MILLION_TO_MODEL_CURRENCY = Decimal('0.001')


class MissionCost(NamedTuple):
    year: int
    body_id: str
    mission_type: str
    usd_millions: Decimal
    model_currency: Decimal
    source_ref: str
    source_sha256: str


class MissionCostLookup:
    """Read-only keyed access; absent/NO_TRAJECTORY rows are unavailable."""

    def __init__(self, path: Path = INPUT):
        self.path = Path(path)
        raw = self.path.read_bytes()
        self.source_sha256 = sha256(raw).hexdigest()
        rows: dict[tuple[int, str, str], MissionCost | None] = {}
        with self.path.open(newline='') as stream:
            reader = csv.DictReader(stream)
            required = {'year', 'body_id', 'mission_type', 'one_way_cost_usd_millions', 'method'}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError('mission cost input missing required columns')
            for row in reader:
                key = (int(row['year']), row['body_id'].strip(), row['mission_type'].strip())
                if key in rows:
                    raise ValueError(f'duplicate mission cost key: {key}')
                amount = row['one_way_cost_usd_millions'].strip()
                method = row['method'].strip()
                if method == 'NO_TRAJECTORY':
                    if amount:
                        raise ValueError(f'NO_TRAJECTORY row carries cost: {key}')
                    rows[key] = None
                    continue
                if not amount:
                    raise ValueError(f'mission cost missing without NO_TRAJECTORY: {key}')
                usd_millions = Decimal(amount)
                if not usd_millions.is_finite() or usd_millions < 0:
                    raise ValueError(f'invalid mission cost: {key}')
                model_currency = usd_millions * USD_MILLION_TO_MODEL_CURRENCY
                rows[key] = MissionCost(*key, usd_millions, model_currency,
                    f'{self.path.name}:{key[0]}:{key[1]}:{key[2]}', self.source_sha256)
        self.rows = rows

    def lookup(self, year: int, body_id: str, mission_type: str) -> MissionCost | None:
        """Return ``None`` for missing or explicitly unavailable trajectories."""
        if year not in range(2026, 2036):
            raise ValueError('mission cost year outside 2026-2035')
        return self.rows.get((year, body_id, mission_type))

    def has_record(self, year: int, body_id: str, mission_type: str) -> bool:
        """Distinguish an explicit unavailable row from a missing key."""
        return (year, body_id, mission_type) in self.rows


_DEFAULT_LOOKUP: MissionCostLookup | None = None


def public_mission_cost(year: int, body_id: str, mission_type: str) -> MissionCost | None:
    """Look up one public mission row; no hidden generated state is consulted."""
    global _DEFAULT_LOOKUP
    if _DEFAULT_LOOKUP is None:
        _DEFAULT_LOOKUP = MissionCostLookup()
    return _DEFAULT_LOOKUP.lookup(year, body_id, mission_type)


def policy_cost_assertion(cost: MissionCost | None, *, scenario_id: str, year: int,
                          body_id: str, source_sha256: str, source_ref: str):
    """Build an immutable scenario fact for the existing public cost contract."""
    from dataclasses import replace
    from .generated_campaign import _source

    sim_year=str(year-2025)
    amount=None if cost is None else str(cost.model_currency)
    fact=_source(f'BUILD7_MISSION_COST:{year}:{body_id}:ORBITAL_RECON',body_id,
        'exploration.REMOTE_COST','MISSION:REMOTE','SCENARIO',scenario_id,
        'AGENT','PUB',amount,'MODEL_CURRENCY',source_sha256,
        source_ref=source_ref)
    return replace(fact,reason_code='NO_TRAJECTORY' if amount is None else 'ADMITTED',
        valid_from=sim_year,valid_to=sim_year,source_time=sim_year,
        transformation_ref='USD_MILLIONS_TO_MODEL_CURRENCY_SCENARIO_V1',
        transformation_version='USD_MILLIONS_DIV_1000',
        dependency_refs=(source_ref,),
        exception_flags=(('empirical_exchange_rate','NOT_CLAIMED'),
                         ('normalization','1E9_EARTH_PROXY_UNITS_PER_MODEL_CURRENCY')))
