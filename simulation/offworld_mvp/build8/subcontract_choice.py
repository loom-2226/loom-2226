"""Opt-in authored subcontract choice demonstration, not used by existing trials."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from .master_cast import name as cast_name

SEED = 'BUILD8_SUB_CHOICE_V1'  # Authored deterministic tie-break seed.

@dataclass(frozen=True)
class Request:
    prime: str
    sub: str
    category: str
    year: int
    quote: Decimal
    slots: int = 1


def allocate(requests, capacities, seed=SEED):
    """Cheapest quote first; then seeded hash. Shared (sub,category,year) slots."""
    used = {}
    results = []
    def priority(r):
        return (r.quote, sha256(f'{seed}|{r.year}|{r.prime}|{r.sub}|{r.category}'.encode()).hexdigest())
    for r in sorted(requests, key=priority):
        prime = cast_name(r.prime, 'executor')
        sub = cast_name(r.sub, 'executor', r.category)
        if prime == sub or r.slots < 1 or r.quote < 0:
            raise ValueError('invalid authored subcontract request')
        key = (sub, r.category, r.year)
        capacity = capacities.get(key)
        if capacity is None or capacity < 0:
            raise ValueError('missing authored capacity slots')
        accepted = used.get(key, 0) + r.slots <= capacity
        if accepted:
            used[key] = used.get(key, 0) + r.slots
        results.append((prime, sub, r.year, 'ALLOCATED' if accepted else 'DEFERRED_NO_SLOT'))
    return tuple(results), used
