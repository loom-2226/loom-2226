from decimal import Decimal

D=Decimal

POLICY_ID='FINANCIER_SCREENING_V1'
POLICY_SEMANTICS='MVP_VALIDATION_RETURN_PROXY_V1'

def _d(x):
    return D(str(x))

def _clamp01(x):
    x=_d(x)
    if x<D('0'): return D('0')
    if x>D('1'): return D('1')
    return x

def posterior_from_signal(prior,signal,detection_rate,false_positive_rate):
    prior=_clamp01(prior)
    detection=_clamp01(detection_rate)
    fp=_clamp01(false_positive_rate)
    if signal=='POSITIVE':
        num=detection*prior
        den=num+fp*(D('1')-prior)
    elif signal=='NEGATIVE':
        num=(D('1')-detection)*prior
        den=num+(D('1')-fp)*(D('1')-prior)
    else:
        raise ValueError('unsupported observation signal')
    if den==0:
        raise ValueError('degenerate observation likelihood')
    return num/den

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def _params(manifest):
    return {p['semantic_name']:_d(p['value']) for p in manifest['parameters']}

def evaluate(snapshot,request,manifest,decision_key):
    """Pure policy evaluation over serialized admitted inputs only."""
    facts=_facts(snapshot)
    params=_params(manifest)
    beliefs={k:_d(v) for k,v in snapshot['beliefs']}
    priors={k:_d(v) for k,v in snapshot['priors']}

    price=_d(facts['underwriting.PRICE']['value'])
    exploration=_d(facts['underwriting.EXPLORATION_CAPEX']['value'])
    development=_d(facts['underwriting.DEVELOPMENT_CAPEX']['value'])
    opex=_d(facts['underwriting.OPERATING_COST']['value'])
    lead=_d(facts['underwriting.LEAD_TIME']['value'])

    belief=beliefs['resource_exists']
    prior=priors['resource_exists']
    balance=_d(snapshot['account_balance'])
    amount=_d(request['amount'])

    if amount>balance:
        return {
            'outcome':'REJECT','reason_code':'CEILING','amount':'0','instrument':'',
            'reason':'requested exposure exceeds admitted financier cash ceiling',
            'metrics':{'belief':str(belief),'prior':str(prior)}
        }

    if balance<=0:
        return {
            'outcome':'REJECT','reason_code':'CEILING','amount':'0','instrument':'',
            'reason':'financier has no admitted deployable cash',
            'metrics':{'belief':str(belief),'prior':str(prior)}
        }

    concentration=amount/balance
    if concentration>params['max_concentration_fraction']:
        return {
            'outcome':'REJECT','reason_code':'CONCENTRATION','amount':'0','instrument':'',
            'reason':'request exceeds admitted single-project concentration limit',
            'metrics':{'concentration':str(concentration),'belief':str(belief)}
        }

    disclosed=set(request['disclosed_observation_ids'])
    visible=set(snapshot['information_refs'])
    if not disclosed or not disclosed.issubset(visible):
        return {
            'outcome':'DEFER','reason_code':'DEFER_MORE_INFORMATION','amount':'0','instrument':'',
            'reason':'no complete disclosed observation set is admitted to the financier',
            'metrics':{'belief':str(belief),'prior':str(prior)}
        }

    margin=price-opex
    if margin<D('0'):
        margin=D('0')
    capital=exploration+development
    if capital<=0:
        raise ValueError('nonpositive project capital denominator')
    horizon=params['horizon_years']
    productive_years=horizon-lead
    if productive_years<D('0'):
        productive_years=D('0')
    utilization=productive_years/horizon
    annual_margin=margin*params['normalized_throughput']
    annual_return_proxy=belief*(annual_margin/capital)*utilization

    metrics={
        'belief':str(belief),
        'prior':str(prior),
        'margin':str(margin),
        'capital':str(capital),
        'utilization':str(utilization),
        'annual_return_proxy':str(annual_return_proxy),
        'hurdle_rate':str(params['hurdle_rate']),
        'decision_key_hash_material':str(decision_key),
    }

    if annual_return_proxy<params['hurdle_rate']:
        return {
            'outcome':'REJECT','reason_code':'BELOW_RETURN','amount':'0','instrument':'',
            'reason':'admitted expected annual return proxy is below the policy hurdle',
            'metrics':metrics,
        }

    return {
        'outcome':'APPROVE','reason_code':'APPROVED_POLICY_RULE',
        'amount':str(amount),'instrument':'EQUITY',
        'reason':'admitted expected annual return proxy meets the policy hurdle and exposure controls',
        'metrics':metrics,
    }
