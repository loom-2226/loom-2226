"""Opt-in descriptive tiers and independent authored fallbacks, not capacity scores."""
import json
from decimal import Decimal
from pathlib import Path
from .master_cast import actor

HERE = Path(__file__).parent


def descriptive_tier(name, category, *, tiers=False):
    if not tiers:
        return None
    entry = actor(name, 'executor', category)
    rows = json.loads((HERE / 'capacity_tiers_descriptive.json').read_text())['capabilities']
    matches = [row for row in rows if row['actor_id'] == entry['id'] and row['category'] == category]
    if len(matches) != 1:
        return None  # An absent research entry is not an invented capability.
    row = matches[0]
    return {'tier': row['tier'], 'basis': row['basis'],
            'inference': 'INFERRED_TIER', 'note': row['note']}


def authored_fallbacks(name, category, *, authored_quote=None, authored_slots=None,
                       slots=False, prices=False):
    """Preserve explicit authored values. Switches are independent and default off."""
    actor(name, 'executor', category)
    defaults = json.loads((HERE / 'capacity_authored_defaults.json').read_text())
    price = authored_quote
    capacity = authored_slots
    if prices and price is None and category in defaults['price_units_if_no_authored_quote']:
        price = Decimal(defaults['price_units_if_no_authored_quote'][category])
    if slots and capacity is None:
        capacity = defaults['flat_slots']
    return price, capacity
