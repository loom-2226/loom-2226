from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_OPPORTUNITY_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='ACTOR_VISIBLE_ANNUAL_OPPORTUNITY_CONSIDERATION_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD7_INCREMENT6_SPONSOR_OPPORTUNITY_V1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'required_capability':'REQUEST_FINANCE',
    'available_financing_fact':'capital.AVAILABLE_F',
    'project_status_fact':'project.STATUS',
    'project_maturity_fact':'study.CURRENT_MATURITY',
    'project_cash_fact':'portfolio.AVAILABLE_CAPITAL',
    'numeric_policy_parameters':[],
}

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor opportunity contract mismatch')
    facts=_facts(snapshot)
    available=D(facts[contract['available_financing_fact']]['value'])
    project_status=str(facts[contract['project_status_fact']]['value'])
    maturity=str(facts[contract['project_maturity_fact']]['value'])
    project_cash=D(facts[contract['project_cash_fact']]['value'])
    metrics={
        'available_financing':str(available),
        'existing_project_status':project_status,
        'existing_project_maturity':maturity,
        'existing_project_cash':str(project_cash),
        'candidate_count':str(len(request['candidates'])),
        'decision_key_hash_material':str(decision_key),
    }
    if (snapshot['agent_kind']!=contract['required_agent_kind']
            or contract['required_objective'] not in snapshot['objectives']
            or contract['required_capability'] not in snapshot['capabilities']):
        return {'outcome':'WAIT','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'selected_opportunity_id':'','selected_body_key':'',
                'reason':'sponsor class, objective, or capability is not admitted',
                'metrics':metrics}
    beliefs={key:D(value) for key,value in snapshot['beliefs']}
    priors={key:D(value) for key,value in snapshot['priors']}
    qualifying=[];underfunded=0
    for candidate in request['candidates']:
        improved=any(beliefs[key]>priors[key] for key in candidate['belief_keys'])
        positive=D(candidate['commercial_opportunity'])==1 and improved
        if positive:
            if available>=D(candidate['required_capital']):qualifying.append(candidate)
            else:underfunded+=1
    if qualifying:
        candidate=sorted(qualifying,key=lambda c:(c['tie_break_key'],c['opportunity_id']))[0]
        metrics['selected_body_key']=candidate['body_key']
        return {'outcome':'CONSIDER_PROSPECTING',
                'reason_code':'VISIBLE_ALTERNATIVE_WITHIN_FINANCING_CAPACITY',
                'selected_opportunity_id':candidate['opportunity_id'],
                'selected_body_key':candidate['body_key'],
                'reason':'admitted characterization supports consideration and the alternative is within remaining financing capacity; a deterministic tie-break selected among equivalent eligible alternatives',
                'metrics':metrics}
    if project_status=='EXPLORING':
        reason_code=('ALTERNATIVE_FINANCING_NOT_AVAILABLE' if underfunded
                     else 'RETAIN_EXISTING_PROJECT')
        reason=('visible alternatives exceed remaining financing capacity; retain the existing prospect'
                if underfunded else
                'no eligible visible alternative is within financing capacity; retain the existing prospect for future consideration')
        return {'outcome':'RETAIN_PROJECT','reason_code':reason_code,
                'selected_opportunity_id':'','selected_body_key':'','reason':reason,
                'metrics':metrics}
    return {'outcome':'WAIT','reason_code':'NO_ACTIONABLE_OPPORTUNITY',
            'selected_opportunity_id':'','selected_body_key':'',
            'reason':'no eligible alternative within financing capacity or active prospect is available',
            'metrics':metrics}
