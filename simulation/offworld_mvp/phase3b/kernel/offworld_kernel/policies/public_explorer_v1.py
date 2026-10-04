from decimal import Decimal

D=Decimal

POLICY_ID='PUBLIC_EXPLORER_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='PUBLIC_INFORMATION_ACQUISITION_STRUCTURAL_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST002A_PUBLIC_EXPLORER_CONTRACT_V0_1',
    'required_agent_kind':'PUBLIC',
    'required_capability':'EXPLORE',
    'required_objective':'PUBLIC_INFORMATION',
    'supported_channel':'REMOTE',
    'required_cost_fact':'exploration.REMOTE_COST',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('public explorer contract mismatch')

    facts=_facts(snapshot)
    cost=_d(facts[contract['required_cost_fact']]['value'])
    balance=_d(snapshot['account_balance'])
    metrics={
        'admitted_cost':str(cost),
        'admitted_balance':str(balance),
        'channel':str(request['channel']),
        'decision_key_hash_material':str(decision_key),
    }

    if request['channel']!=contract['supported_channel']:
        return {
            'outcome':'DEFER',
            'reason_code':'DEFER_UNSUPPORTED_CHANNEL',
            'authorized_cost':'0',
            'reason':'requested exploration channel is outside the bounded Test 002A policy',
            'metrics':metrics,
        }

    if (snapshot['agent_kind']!=contract['required_agent_kind']
        or contract['required_capability'] not in snapshot['capabilities']
        or contract['required_objective'] not in snapshot['objectives']):
        return {
            'outcome':'DECLINE',
            'reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
            'authorized_cost':'0',
            'reason':'public exploration capability or public-information objective is not admitted',
            'metrics':metrics,
        }

    if cost<=0:
        raise ValueError('remote exploration cost must be positive')

    if cost>balance:
        return {
            'outcome':'DECLINE',
            'reason_code':'INSUFFICIENT_BUDGET',
            'authorized_cost':'0',
            'reason':'declared remote-observation cost exceeds admitted public budget',
            'metrics':metrics,
        }

    return {
        'outcome':'AUTHORIZE',
        'reason_code':'APPROVED_PUBLIC_INFORMATION_MISSION',
        'authorized_cost':str(cost),
        'reason':'public-information mission objective, capability, known cost and budget admit remote observation',
        'metrics':metrics,
    }
