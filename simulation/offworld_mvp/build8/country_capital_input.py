"""Read-only Build 8 Experiment A country investment boundary; no finance created."""
from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import hashlib
import json

EARTH_V4 = 'EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24'
SOURCES = ('qualified_inputs/countries_2026_2031.ndjson',
           'stage_2031_2060/countries_2031_2060.ndjson')
SUCCESSOR_SOURCE = 'successor_80_2226/results/countries_2060_2226.ndjson'


def load_investment_capacity(baseline_root: Path, end_year: int = 2035) -> tuple[dict[tuple[str, int], Decimal], dict]:
    """Return read-only 80-economy annual capacities, 2026 through end_year.

    Qualified data owns 2031; stage data owns 2032..2060;
    successor data owns 2061..2226. Never blend overlapping source rows.
    """
    if type(end_year) is not int or not 2035 <= end_year <= 2226:
        raise ValueError('Earth v4 trial horizon must be 2035..2226')
    root = Path(baseline_root)
    if root.name != 'earth_long_run_economic_baseline_v4_2026_09_24':
        raise ValueError('expected promoted Earth v4 baseline directory')
    capacities = {}
    sources = []
    for index, relative in enumerate((*SOURCES, SUCCESSOR_SOURCE) if end_year > 2060 else SOURCES):
        path = root / relative
        payload = path.read_bytes()
        sources.append({'path': relative, 'sha256': hashlib.sha256(payload).hexdigest()})
        lower, upper = ((2026, min(end_year, 2031)) if index == 0
                        else (2032, min(end_year, 2060)) if index == 1
                        else (2061, end_year))
        for lineno, line in enumerate(payload.splitlines(), 1):
            try:
                record = json.loads(line)
                year = record['year']
                if type(year) is not int:
                    raise ValueError('non-integer year')
                if not lower <= year <= upper:
                    continue
                country = record['iso3']
                if type(country) is not str or len(country) != 3:
                    raise ValueError('invalid country identity')
                value = Decimal(str(record['investment']))
                if not value.is_finite() or value < 0:
                    raise ValueError('negative or nonfinite investment')
            except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
                raise ValueError(f'malformed Earth v4 record: {relative}:{lineno}: {exc}') from exc
            key = (country, year)
            if key in capacities:
                raise ValueError(f'duplicate country-year: {key}')
            capacities[key] = value
    countries = {c for c, _ in capacities}
    expected = 80 * (end_year - 2026 + 1)
    if len(countries) != 80 or len(capacities) != expected or any(
        (country, year) not in capacities for country in countries
        for year in range(2026, end_year + 1)
    ):
        raise ValueError(f'incomplete 80-economy x {end_year-2025}-year investment boundary')
    provenance = {'designation': EARTH_V4, 'sources': sources,
                  'overlap_rule': 'qualified_inputs wins 2031',
                  'standing': 'MODELED_INVESTMENT_CAPACITY_NOT_SPENDABLE_CASH'}
    if end_year > 2035:
        provenance['overlap_rule'] = 'qualified owns 2031; stage owns 2032-2060; successor owns 2061-2226'
    return capacities, provenance
