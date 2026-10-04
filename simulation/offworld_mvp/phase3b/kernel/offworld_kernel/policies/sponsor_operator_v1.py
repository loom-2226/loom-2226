from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_OPERATOR_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='DIRECTIONAL_EVIDENCE_PROJECT_ADVANCEMENT_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST005A_SPONSOR_OPERATOR_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'finance_capability':'REQUEST_FINANCE',
    'develop_capability':'DEVELOP',
    'eligible_project_states':['PROPOSED','EXPLORING'],
    'required_project_status_fact':'project.STATUS',
    'required_project_cash_fact':'project.CASH_BALANCE',
    'required_development_cost_fact':'underwriting.DEVELOPMENT_CAPEX',
    'belief_key':'resource_exists',
    'prior_key':'resource_exists',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor operator contract mismatch')

    facts=_facts(snapshot)
    beliefs={k:_d(v) for k,v in snapshot['beliefs']}
    priors={k:_d(v) for k,v in snapshot['priors']}
    status=str(facts[contract['required_project_status_fact']]['value'])
    project_cash=_d(facts[contract['required_project_cash_fact']]['value'])
    development_cost=_d(facts[contract['required_development_cost_fact']]['value'])
    belief=beliefs[contract['belief_key']]
    prior=priors[contract['prior_key']]
    visible=set(snapshot['information_refs'])
    capabilities=set(snapshot['capabilities'])

    metrics={
        'project_status':status,
        'project_cash':str(project_cash),
        'development_cost':str(development_cost),
        'belief':str(belief),
        'prior':str(prior),
        'decision_key_hash_material':str(decision_key),
    }

    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {
            'outcome':'DEFER',
            'reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
            'requested_financing':'0',
            'reason':'sponsor class or return objective is not admitted',
            'metrics':metrics,
        }

    if status not in contract['eligible_project_states']:
        return {
            'outcome':'DEFER',
            'reason_code':'PROJECT_STATE_BLOCK',
            'requested_financing':'0',
            'reason':'project lifecycle state is outside the bounded sponsor decision window',
            'metrics':metrics,
        }

    if not request['observation_id'] or request['observation_id'] not in visible:
        return {
            'outcome':'DEFER',
            'reason_code':'NO_RELEVANT_INFORMATION',
            'requested_financing':'0',
            'reason':'relevant observation is not admitted to sponsor information',
            'metrics':metrics,
        }

    if belief<=prior:
        return {
            'outcome':'ABANDON',
            'reason_code':'NONPOSITIVE_EVIDENCE',
            'requested_financing':'0',
            'reason':'admitted evidence does not improve resource belief above the sponsor prior',
            'metrics':metrics,
        }

    shortfall=development_cost-project_cash
    if shortfall>D('0'):
        if contract['finance_capability'] not in capabilities:
            return {
                'outcome':'DEFER',
                'reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'requested_financing':'0',
                'reason':'project requires financing but sponsor lacks admitted financing-request capability',
                'metrics':metrics,
            }
        return {
            'outcome':'REQUEST_FINANCE',
            'reason_code':'POSITIVE_EVIDENCE_FINANCE_REQUIRED',
            'requested_financing':str(shortfall),
            'reason':'admitted evidence improves belief and project cash is below known development cost',
            'metrics':metrics,
        }

    if contract['develop_capability'] not in capabilities:
        return {
            'outcome':'DEFER',
            'reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
            'requested_financing':'0',
            'reason':'project is funded but sponsor lacks admitted development capability',
            'metrics':metrics,
        }

    return {
        'outcome':'DEVELOP',
        'reason_code':'POSITIVE_EVIDENCE_FUNDED',
        'requested_financing':'0',
        'reason':'admitted evidence improves belief and project cash meets known development cost',
        'metrics':metrics,
    }
