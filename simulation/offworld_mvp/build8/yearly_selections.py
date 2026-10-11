"""Named, authored participation choices; not a policy or capacity score."""
from decimal import Decimal as D
from .master_cast import actor

# Motivation and information values are scenario-authored policy inputs,
# not claims about real companies' private beliefs or investment plans.
SELECTIONS = {
    'legacy_usa': {
        'sponsors': ('Interlune', 'Axiom'), 'country': 'USA',
        'executors': {'BUILD': 'Northrop Grumman', 'LAND': 'Firefly Aerospace'},
        'private_observer': 'Axiom', 'private_recipient': 'Interlune',
        'motives': {'Interlune': ('RESOURCE_RETURN', D('2.00')),
                    'Axiom': ('LUNAR_INFRASTRUCTURE', D('2.20'))},
    },
    'japan_lunar': {
        'sponsors': ('Axiom', 'ispace'), 'country': 'JPN',
        'executors': {'BUILD': 'Thales Alenia Space', 'LAND': 'ispace'},
        'private_observer': 'Axiom', 'private_recipient': 'ispace',
        # AUTHORED MODEL QUOTES, not offers by these companies.
        'authored_costs': {'BUILD': D('1.20'), 'LAND': D('1.50')},
        'motives': {'Axiom': ('LUNAR_INFRASTRUCTURE', D('2.20')),
                    'ispace': ('RESOURCE_RETURN', D('2.00'))},
    },
}

def select(name):
    if name not in SELECTIONS:
        raise ValueError('unknown named yearly selection: '+str(name))
    item = SELECTIONS[name]
    if len(set(item['sponsors'])) != len(item['sponsors']) or not item['sponsors']:
        raise ValueError('duplicate/empty sponsor selection')
    for sponsor in item['sponsors']:
        actor(sponsor, 'private_sponsor')
    if set(item['motives']) != set(item['sponsors']):
        raise ValueError('each sponsor requires authored policy inputs')
    if item['private_observer'] not in item['sponsors'] or item['private_recipient'] not in item['sponsors']:
        raise ValueError('private evidence must belong to a selected sponsor')
    for category in ('BUILD', 'LAND'):
        actor(item['executors'][category], 'executor', category)
    return item
