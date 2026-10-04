POLICY_ID='PUBLIC_PUBLISHER_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='OPEN_PUBLIC_INFORMATION_PUBLICATION_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST002B_PUBLIC_PUBLISHER_CONTRACT_V0_1',
    'required_agent_kind':'PUBLIC',
    'required_objective':'PUBLIC_INFORMATION',
    'supported_audience':'PUBLIC_FINANCIERS',
    'numeric_policy_parameters':[],
}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('public publisher contract mismatch')

    metrics={
        'observation_id':str(request['observation_id']),
        'audience':str(request['audience']),
        'decision_key_hash_material':str(decision_key),
    }

    if (snapshot['agent_kind']!=contract['required_agent_kind']
        or contract['required_objective'] not in snapshot['objectives']
        or request['audience']!=contract['supported_audience']):
        return {
            'outcome':'WITHHOLD',
            'reason_code':'OBJECTIVE_OR_CLASS_BLOCK',
            'reason':'public-information publication objective/class/audience is not admitted',
            'metrics':metrics,
        }

    if request['observation_id'] not in snapshot['information_refs']:
        return {
            'outcome':'WITHHOLD',
            'reason_code':'OBSERVATION_NOT_POSSESSED',
            'reason':'requested source observation is not present in admitted publisher information',
            'metrics':metrics,
        }

    return {
        'outcome':'PUBLISH',
        'reason_code':'PUBLISH_PUBLIC_INFORMATION',
        'reason':'public-information mission publishes a legitimately possessed observation',
        'metrics':metrics,
    }
