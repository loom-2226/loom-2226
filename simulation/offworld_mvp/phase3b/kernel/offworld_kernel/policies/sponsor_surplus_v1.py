from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_SURPLUS_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='BOUNDED_RESERVE_FINANCIER_RETURN_REINVEST_OWNER_RESIDUAL_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST010A_SPONSOR_SURPLUS_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'required_capability':'DISTRIBUTE_SURPLUS',
    'eligible_project_state':'OPERATING',
    'project_status_fact':'project.STATUS',
    'cash_fact':'project.CASH_BALANCE',
    'reserve_fact':'project.RESERVE_REQUIREMENT',
    'financier_claim_fact':'financing.RETURN_CLAIM_REMAINING',
    'reinvestment_fact':'project.REINVESTMENT_REQUIREMENT',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor surplus contract mismatch')
    facts=_facts(snapshot)
    status=str(facts[contract['project_status_fact']]['value'])
    cash=_d(facts[contract['cash_fact']]['value'])
    reserve_req=_d(facts[contract['reserve_fact']]['value'])
    claim_remaining=_d(facts[contract['financier_claim_fact']]['value'])
    reinvest_req=_d(facts[contract['reinvestment_fact']]['value'])
    if min(cash,reserve_req,claim_remaining,reinvest_req)<0:
        raise ValueError('negative admitted surplus-allocation input')

    metrics={
        'project_status':status,'project_cash':str(cash),
        'reserve_requirement':str(reserve_req),
        'financing_return_claim_remaining':str(claim_remaining),
        'reinvestment_requirement':str(reinvest_req),
        'decision_key_hash_material':str(decision_key),
    }
    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'reserve':'0','financier_return':'0','local_reinvestment':'0','owner_distribution':'0',
                'reason':'sponsor class or return objective is not admitted','metrics':metrics}
    if contract['required_capability'] not in set(snapshot['capabilities']):
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'reserve':'0','financier_return':'0','local_reinvestment':'0','owner_distribution':'0',
                'reason':'sponsor lacks admitted DISTRIBUTE_SURPLUS capability','metrics':metrics}
    if status!=contract['eligible_project_state']:
        return {'outcome':'DEFER','reason_code':'PROJECT_STATE_BLOCK',
                'reserve':'0','financier_return':'0','local_reinvestment':'0','owner_distribution':'0',
                'reason':'project is not in OPERATING state','metrics':metrics}
    if cash<=0:
        return {'outcome':'DEFER','reason_code':'NO_DISTRIBUTABLE_CASH',
                'reserve':'0','financier_return':'0','local_reinvestment':'0','owner_distribution':'0',
                'reason':'project has no cash to allocate','metrics':metrics}

    reserve=min(cash,reserve_req)
    remaining=cash-reserve
    financier_return=min(remaining,claim_remaining)
    remaining-=financier_return
    local_reinvestment=min(remaining,reinvest_req)
    remaining-=local_reinvestment
    owner_distribution=remaining
    return {
        'outcome':'DISTRIBUTE','reason_code':'DISTRIBUTION_AUTHORIZED',
        'reserve':str(reserve),'financier_return':str(financier_return),
        'local_reinvestment':str(local_reinvestment),
        'owner_distribution':str(owner_distribution),
        'reason':'project cash allocated by reserve, financing-return claim, reinvestment requirement, then owner residual',
        'metrics':metrics,
    }
