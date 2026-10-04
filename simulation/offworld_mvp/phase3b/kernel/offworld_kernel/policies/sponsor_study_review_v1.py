POLICY_ID='SPONSOR_STUDY_REVIEW_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='TEST_ONLY_STUDY_RESULT_GATE_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD6B_TEST001A_SPONSOR_STUDY_REVIEW_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'required_capability':'REVIEW_STUDY',
    'eligible_project_state':'EXPLORING',
    'numeric_policy_parameters':[],
}

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor study review contract mismatch')
    facts=_facts(snapshot)
    metrics={
        'current_maturity':str(facts['study.CURRENT_MATURITY']['value']),
        'next_maturity':str(facts['study.NEXT_MATURITY']['value']),
        'result_standing':str(facts['study.RESULT_STANDING']['value']),
        'decision_key_hash_material':str(decision_key),
    }

    if (snapshot['agent_kind']!=contract['required_agent_kind']
            or contract['required_objective'] not in snapshot['objectives']
            or contract['required_capability'] not in snapshot['capabilities']
            or str(facts['project.STATUS']['value'])!=contract['eligible_project_state']):
        return {
            'outcome':'DEFER',
            'reason_code':'PROJECT_OR_CAPABILITY_BLOCK',
            'reason':'project state or sponsor study-review authority is not admitted',
            'metrics':metrics,
        }

    standing=str(facts['study.RESULT_STANDING']['value'])
    if standing=='SUPPORTS_ADVANCE':
        return {
            'outcome':'ADVANCE',
            'reason_code':'SUPPORTS_DECLARED_ADVANCE',
            'reason':'admitted completed study result supports exactly the declared next maturity',
            'metrics':metrics,
        }
    if standing=='INSUFFICIENT':
        return {
            'outcome':'DEFER',
            'reason_code':'INSUFFICIENT_EVIDENCE',
            'reason':'admitted completed study result is insufficient to earn the declared next maturity',
            'metrics':metrics,
        }
    if standing=='NEGATIVE':
        return {
            'outcome':'ABANDON',
            'reason_code':'NEGATIVE_EVIDENCE',
            'reason':'admitted completed study result is negative under the Test-only structural strategy',
            'metrics':metrics,
        }
    return {
        'outcome':'DEFER',
        'reason_code':'INSUFFICIENT_EVIDENCE',
        'reason':'unrecognized non-advancing study standing',
        'metrics':metrics,
    }
