from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_PORTFOLIO_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='TEST_ONLY_PRIORITY_AFFORDABILITY_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD6A_TEST001A_SPONSOR_PORTFOLIO_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'required_capability':'AUTHORIZE_ACTIVITY',
    'eligible_project_states':['PROPOSED','EXPLORING'],
    'eligible_activity_status':'PROPOSED',
    'numeric_policy_parameters':[],
}

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def _d(x):
    return D(str(x))

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor portfolio contract mismatch')
    facts=_facts(snapshot)
    available=_d(facts['portfolio.AVAILABLE_CAPITAL']['value'])
    metrics={
        'available_capital':str(available),
        'decision_key_hash_material':str(decision_key),
        'candidate_count':str(len(request['candidate_activity_ids'])),
    }

    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives'] or contract['required_capability'] not in snapshot['capabilities']:
        return {
            'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
            'selected_activity_id':'','reserved_capital':'0',
            'reason':'sponsor class, objective or activity-authorization capability is not admitted',
            'metrics':metrics,
        }

    candidates=[]
    state_eligible=0
    unaffordable=0
    for aid in request['candidate_activity_ids']:
        prefix='activity.'+str(aid)+'.'
        project_id=str(facts[prefix+'PROJECT_ID']['value'])
        project_status=str(facts[prefix+'PROJECT_STATUS']['value'])
        status=str(facts[prefix+'STATUS']['value'])
        commitment=_d(facts[prefix+'COMMITMENT']['value'])
        priority=int(facts[prefix+'PRIORITY']['value'])
        window_valid=str(facts[prefix+'WINDOW_VALID']['value'])=='1'
        eligible=(project_status in contract['eligible_project_states']
                  and status==contract['eligible_activity_status'] and window_valid)
        if eligible:
            state_eligible+=1
            if commitment<=available:
                candidates.append((priority,project_id,str(aid),commitment))
            else:
                unaffordable+=1

    if candidates:
        candidates.sort(key=lambda x:(x[0],x[1],x[2]))
        priority,project_id,aid,commitment=candidates[0]
        metrics.update({'selected_priority':str(priority),'selected_project_id':project_id})
        return {
            'outcome':'AUTHORIZE','reason_code':'SELECTED_PRIORITY_AFFORDABLE',
            'selected_activity_id':aid,'reserved_capital':str(commitment),
            'reason':'highest-priority stable candidate is eligible and affordable from admitted uncommitted capital',
            'metrics':metrics,
        }

    if state_eligible and unaffordable:
        return {
            'outcome':'DEFER','reason_code':'INSUFFICIENT_AVAILABLE_CAPITAL',
            'selected_activity_id':'','reserved_capital':'0',
            'reason':'eligible candidate activities exceed admitted uncommitted sponsor capital',
            'metrics':metrics,
        }

    return {
        'outcome':'DEFER','reason_code':'NO_ELIGIBLE_ACTIVITY',
        'selected_activity_id':'','reserved_capital':'0',
        'reason':'no requested project activity is currently eligible for authorization',
        'metrics':metrics,
    }
