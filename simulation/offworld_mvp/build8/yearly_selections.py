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
    'esa_build_quote_trial': {
        'sponsors': ('ESA',), 'country': 'DEU',
        'executors': {'BUILD': 'Airbus Defence and Space', 'LAND': 'ispace'},
        'stages': {'ESA': ('BUILD',)},
        'quotes': {'BUILD': {'Thales Alenia Space': D('.0270'),
                             'Airbus Defence and Space': D('.0240')}},
        'ceiling': D('.030'), 'readiness_probability': D('.5'),
        'private_observer': 'ESA', 'private_recipient': 'ESA',
        'motives': {'ESA': ('SCIENTIFIC', D('2.20'))},
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
        actor(sponsor, 'agency_sponsor' if sponsor == 'ESA' else 'private_sponsor')
    if set(item['motives']) != set(item['sponsors']):
        raise ValueError('each sponsor requires authored policy inputs')
    if item['private_observer'] not in item['sponsors'] or item['private_recipient'] not in item['sponsors']:
        raise ValueError('private evidence must belong to a selected sponsor')
    for category in ('BUILD', 'LAND'):
        actor(item['executors'][category], 'executor', category)
    for sponsor, stages in item.get('stages', {}).items():
        if sponsor not in item['sponsors'] or not stages or any(c not in ('BUILD','LAND') for c in stages):
            raise ValueError('invalid project stage list')
    for category, offers in item.get('quotes', {}).items():
        for executor in offers:
            actor(executor, 'executor', category)
    return item
