"""Small AUTHORED / TEST_ONLY / NON-CANON table for Build 8 PR 1."""
from decimal import Decimal as D
from offworld_kernel.named_portfolio import load_build6c_scenario

FIXED_CLAIM_ORDER=('NASA','CNSA')
# Names, body assignments, and lifetime limits are authored trial inputs.
ASSIGNMENTS={
    'NASA':('MOON','MOON-A1-SURFACE','MOON-A2-ASSESS',D('.650')),
    'CNSA':('BENNU','BENNU-A1-RESOURCE','BENNU-A2-CONCEPT',D('.400')),
}

def trial_rules(order=FIXED_CLAIM_ORDER,assignments=None):
    assignments=ASSIGNMENTS if assignments is None else assignments
    order=tuple(order)
    if set(order)!=set(assignments) or len(set(order))!=len(order):
        raise ValueError('recorded claim order must contain each sponsor exactly once')
    scenario=load_build6c_scenario()
    rules={}
    for sponsor,(body,a1,a2,lifetime) in assignments.items():
        first,second=scenario.activity(a1),scenario.activity(a2)
        if first.body_id!=body or second.body_id!=body:
            raise ValueError('activity/body assignment mismatch')
        if first.next_maturity!=second.required_maturity:
            raise ValueError('nonconsecutive authored study maturity')
        rules[sponsor]={'body':body,'a1':a1,'a2':a2,
            'a1_price':str(first.cost/D(100)),
            'a2_price':str(second.cost/D(100)),
            'lifetime_limit':str(D(lifetime))}
    return {'rules':rules,'order':order,'evidence':{},
            'classification':'AUTHORED TEST_ONLY NON-CANON',
            'currency':'AUTHORED 100 native 6C units per 1 Route 1 MODEL_CURRENCY'}
