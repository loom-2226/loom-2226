from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_OPERATING_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='BOUNDED_OPERATING_CAPACITY_AND_WORKING_CAPITAL_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST008A_SPONSOR_OPERATING_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'finance_capability':'REQUEST_FINANCE',
    'operate_capability':'OPERATE',
    'extract_capability':'EXTRACT',
    'eligible_project_state':'OPERATING',
    'required_project_status_fact':'project.STATUS',
    'required_project_cash_fact':'project.CASH_BALANCE',
    'required_asset_capacity_fact':'asset.CAPACITY',
    'required_operating_cost_fact':'underwriting.OPERATING_COST',
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
        raise ValueError('sponsor operating contract mismatch')
    facts=_facts(snapshot)
    beliefs={k:_d(v) for k,v in snapshot['beliefs']}
    priors={k:_d(v) for k,v in snapshot['priors']}
    status=str(facts[contract['required_project_status_fact']]['value'])
    cash=_d(facts[contract['required_project_cash_fact']]['value'])
    capacity=_d(facts[contract['required_asset_capacity_fact']]['value'])
    unit_opex=_d(facts[contract['required_operating_cost_fact']]['value'])
    belief=beliefs[contract['belief_key']]
    prior=priors[contract['prior_key']]
    visible=set(snapshot['information_refs'])
    capabilities=set(snapshot['capabilities'])

    metrics={
        'project_status':status,'project_cash':str(cash),'asset_capacity':str(capacity),
        'unit_opex':str(unit_opex),'belief':str(belief),'prior':str(prior),
        'decision_key_hash_material':str(decision_key),
    }

    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'sponsor class or return objective is not admitted','metrics':metrics}

    if status!=contract['eligible_project_state']:
        return {'outcome':'DEFER','reason_code':'PROJECT_STATE_BLOCK',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'project is not in OPERATING state','metrics':metrics}

    if not request['observation_id'] or request['observation_id'] not in visible:
        return {'outcome':'DEFER','reason_code':'NO_RELEVANT_INFORMATION',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'relevant observation is not admitted to sponsor information','metrics':metrics}

    if belief<=prior:
        return {'outcome':'DEFER','reason_code':'NONPOSITIVE_EVIDENCE',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'admitted evidence does not improve resource belief above sponsor prior','metrics':metrics}

    if capacity<=0 or unit_opex<0:
        return {'outcome':'DEFER','reason_code':'ASSET_OR_CAPACITY_BLOCK',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'admitted productive capacity or operating-cost basis is invalid','metrics':metrics}

    cycle_cost=capacity*unit_opex
    metrics['cycle_cost']=str(cycle_cost)

    if cash<cycle_cost:
        if contract['finance_capability'] not in capabilities:
            return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                    'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                    'reason':'operating cycle requires finance but sponsor lacks financing-request capability','metrics':metrics}
        return {'outcome':'REQUEST_FINANCE','reason_code':'POSITIVE_EVIDENCE_FINANCE_REQUIRED',
                'requested_financing':str(cycle_cost-cash),'planned_quantity':'0','authorized_opex':'0',
                'reason':'positive admitted evidence and operating cash below full declared cycle cost','metrics':metrics}

    if contract['operate_capability'] not in capabilities or contract['extract_capability'] not in capabilities:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'requested_financing':'0','planned_quantity':'0','authorized_opex':'0',
                'reason':'sponsor lacks admitted operating/extraction capability','metrics':metrics}

    return {'outcome':'OPERATE','reason_code':'OPERATING_CYCLE_AUTHORIZED',
            'requested_financing':'0','planned_quantity':str(capacity),'authorized_opex':str(cycle_cost),
            'reason':'positive admitted evidence, productive capacity and funded operating cycle authorize operation',
            'metrics':metrics}
