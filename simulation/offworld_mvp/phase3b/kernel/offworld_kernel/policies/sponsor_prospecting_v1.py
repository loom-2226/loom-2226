from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_PROSPECTING_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='ACTOR_VISIBLE_PROSPECTING_INITIATION_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD7_INCREMENT4_SPONSOR_PROSPECTING_V1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'required_capability':'REQUEST_FINANCE',
    'required_capital_fact':'prospecting.REQUIRED_CAPITAL',
    'information_value_fact':'prospecting.INFORMATION_VALUE',
    'available_financing_fact':'capital.AVAILABLE_F',
    'numeric_policy_parameters':[],
}

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor prospecting contract mismatch')
    facts=_facts(snapshot)
    beliefs={key:D(value) for key,value in snapshot['beliefs']}
    priors={key:D(value) for key,value in snapshot['priors']}
    required=D(facts[contract['required_capital_fact']]['value'])
    information_value=D(facts[contract['information_value_fact']]['value'])
    available=D(facts[contract['available_financing_fact']]['value'])
    metrics={
        'opportunity_id':request['opportunity_id'],
        'required_capital':str(required),
        'prospective_information_value':str(information_value),
        'available_financing':str(available),
        'decision_key_hash_material':str(decision_key),
    }
    if (snapshot['agent_kind']!=contract['required_agent_kind']
            or contract['required_objective'] not in snapshot['objectives']
            or contract['required_capability'] not in snapshot['capabilities']):
        return {'outcome':'WAIT','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'reason':'sponsor class, objective, or capability is not admitted','metrics':metrics}
    if required!=D(request['amount']) or information_value!=D(request['prospective_information_value']):
        raise ValueError('prospecting request/scenario economics mismatch')
    if information_value<=required:
        return {'outcome':'DECLINE','reason_code':'NONPOSITIVE_PROSPECTING_ECONOMICS',
                'reason':'authored characterization value does not exceed its required capital','metrics':metrics}
    if not any(beliefs[key]>priors[key] for key in request['belief_keys']):
        return {'outcome':'DECLINE','reason_code':'NONPOSITIVE_CHARACTERIZATION',
                'reason':'public evidence did not improve any sponsor material-family belief','metrics':metrics}
    if available<required:
        return {'outcome':'WAIT','reason_code':'FINANCING_NOT_AVAILABLE',
                'reason':'finite available Offworld financing cash is below required prospecting capital','metrics':metrics}
    return {'outcome':'INITIATE_PROJECT','reason_code':'POSITIVE_CHARACTERIZATION_FUNDED',
            'reason':'actor-visible characterization and finite cash support regional prospecting','metrics':metrics}
