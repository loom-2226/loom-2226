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

# PR 2: authored eight-sponsor / four-body scenario, without modifying 6C.
FOUR_BODY_ORDER=('NASA','CNSA','ESA','ISRO','JAXA','CNES','DLR','ispace')
FOUR_BODY_ASSIGNMENTS={
    **ASSIGNMENTS,
    'ESA':('CERES','CERES-A1-SURFACE','CERES-A2-ASSESS',D('.950')),
    'ISRO':('MARS','MARS-A1-REMOTE','MARS-A2-SURFACE',D('.200')),
    'JAXA':('BENNU','BENNU-A1-RESOURCE','BENNU-A2-CONCEPT',D('.180')),
    'CNES':('CERES','CERES-A1-SURFACE','CERES-A2-ASSESS',D('.100')),
    'DLR':('MOON','MOON-A1-SURFACE','MOON-A2-ASSESS',D('.100')),
    'ispace':('MARS','MARS-A1-REMOTE','MARS-A2-SURFACE',D('.100')),
}
# Only test-only overrides: these are NOT new Gate 1 canonical ceilings.
TRIAL_CEILING_OVERRIDES={'ESA':'0.700','ISRO':'0.200'}

def four_body_rules(order=FOUR_BODY_ORDER,overrides=True):
    trial=trial_rules(order,FOUR_BODY_ASSIGNMENTS)
    trial['expanded']=True
    trial['ceilings']=dict(TRIAL_CEILING_OVERRIDES) if overrides else {}
    trial['overrides_enabled']=bool(overrides)
    scenario=load_build6c_scenario()
    for r in trial['rules'].values():
        for stage in ('a1','a2'):
            spec=scenario.activity(r[stage])
            r[stage+'_earliest']=str(spec.earliest_start)
            r[stage+'_window_open']=str(spec.window_open) if spec.window_open is not None else None
            r[stage+'_window_close']=str(spec.window_close) if spec.window_close is not None else None
    return trial
