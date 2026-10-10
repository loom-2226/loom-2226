"""Read-only Build 8 Experiment A country investment boundary; no finance created."""
from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import hashlib
import json

EARTH_V4 = 'EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24'
SOURCES = ('qualified_inputs/countries_2026_2031.ndjson',
           'stage_2031_2060/countries_2031_2060.ndjson')


def load_investment_capacity(baseline_root: Path) -> tuple[dict[tuple[str, int], Decimal], dict]:
    """Return 80 x 10 read-only capacities and exact source provenance.

    Qualified 2026-2031 inputs win the 2031 overlap; stage data starts 2032.
    """
    root = Path(baseline_root)
    if root.name != 'earth_long_run_economic_baseline_v4_2026_09_24':
        raise ValueError('expected promoted Earth v4 baseline directory')
    capacities = {}
    sources = []
    for index, relative in enumerate(SOURCES):
        path = root / relative
        payload = path.read_bytes()
        sources.append({'path': relative, 'sha256': hashlib.sha256(payload).hexdigest()})
        for line in payload.splitlines():
            record = json.loads(line)
            year = int(record['year'])
            if not (2026 <= year <= 2031 if index == 0 else 2032 <= year <= 2035):
                continue
            country = record['iso3']
            key = (country, year)
            if key in capacities:
                raise ValueError(f'duplicate country-year: {key}')
            value = Decimal(str(record['investment']))
            if not value.is_finite() or value < 0:
                raise ValueError(f'invalid investment: {key}')
            capacities[key] = value
    countries = {c for c, _ in capacities}
    if len(countries) != 80 or len(capacities) != 800 or any(
        (country, year) not in capacities for country in countries for year in range(2026, 2036)
    ):
        raise ValueError('incomplete 80-economy x 10-year investment boundary')
    return capacities, {'designation': EARTH_V4, 'sources': sources,
                        'overlap_rule': 'qualified_inputs wins 2031',
                        'standing': 'MODELED_INVESTMENT_CAPACITY_NOT_SPENDABLE_CASH'}
