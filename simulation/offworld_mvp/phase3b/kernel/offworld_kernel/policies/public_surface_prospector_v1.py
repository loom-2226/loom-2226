from decimal import Decimal

D=Decimal

POLICY_ID='PUBLIC_SURFACE_PROSPECTOR_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='PUBLIC_SECOND_STAGE_SURFACE_INFORMATION_ACQUISITION_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST007A_PUBLIC_SURFACE_PROSPECTOR_CONTRACT_V0_1',
    'required_agent_kind':'PUBLIC',
    'required_capabilities':['EXPLORE','SURFACE_PROSPECT'],
    'required_objective':'PUBLIC_INFORMATION',
    'supported_channel':'SURFACE',
    'required_cost_fact':'exploration.SURFACE_COST',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('public surface prospector contract mismatch')

    facts=_facts(snapshot)
    cost=_d(facts[contract['required_cost_fact']]['value'])
    balance=_d(snapshot['account_balance'])
    prerequisite=str(request.get('prerequisite_observation_id',''))
    information=set(snapshot['information_refs'])
    capabilities=set(snapshot['capabilities'])

    metrics={
        'admitted_cost':str(cost),
        'admitted_balance':str(balance),
        'channel':str(request['channel']),
        'prerequisite_observation_id':prerequisite,
        'decision_key_hash_material':str(decision_key),
    }

    if request['channel']!=contract['supported_channel']:
        return {
            'outcome':'DEFER',
            'reason_code':'DEFER_UNSUPPORTED_CHANNEL',
            'authorized_cost':'0',
            'reason':'requested channel is outside the bounded Test 007A surface policy',
            'metrics':metrics,
        }

    if (snapshot['agent_kind']!=contract['required_agent_kind']
        or contract['required_objective'] not in snapshot['objectives']
        or any(c not in capabilities for c in contract['required_capabilities'])):
        return {
            'outcome':'DECLINE',
            'reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
            'authorized_cost':'0',
            'reason':'surface-prospecting capability or public-information objective is not admitted',
            'metrics':metrics,
        }

    if not prerequisite or prerequisite not in information:
        return {
            'outcome':'DEFER',
            'reason_code':'DEFER_PREREQUISITE_OBSERVATION',
            'authorized_cost':'0',
            'reason':'required prior remote observation is not admitted to public-Agent information',
            'metrics':metrics,
        }

    if cost<=0:
        raise ValueError('surface prospecting cost must be positive')

    if cost>balance:
        return {
            'outcome':'DECLINE',
            'reason_code':'INSUFFICIENT_BUDGET',
            'authorized_cost':'0',
            'reason':'declared surface-prospecting cost exceeds admitted public budget',
            'metrics':metrics,
        }

    return {
        'outcome':'AUTHORIZE',
        'reason_code':'APPROVED_SURFACE_INFORMATION_MISSION',
        'authorized_cost':str(cost),
        'reason':'public-information mission, capabilities, prior remote information, known cost and budget admit surface prospecting',
        'metrics':metrics,
    }
