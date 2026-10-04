from decimal import Decimal

D=Decimal
POLICY_ID='SPONSOR_ENTERPRISE_REVIEW_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='POST_CYCLE_POSITIVE_CONTINUE_ZERO_CLOSE_TEST014A_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST014A_SPONSOR_ENTERPRISE_REVIEW_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'continue_capability':'OPERATE',
    'close_capability':'CLOSE_PROJECT',
    'eligible_project_state':'OPERATING',
    'project_status_fact':'project.STATUS',
    'planned_quantity_fact':'cycle.PLANNED_QUANTITY',
    'actual_output_fact':'cycle.ACTUAL_OUTPUT',
    'numeric_policy_parameters':[],
}

def _d(x): return D(str(x))
def _facts(snapshot): return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor enterprise-review contract mismatch')
    facts=_facts(snapshot)
    status=str(facts[contract['project_status_fact']]['value'])
    planned=_d(facts[contract['planned_quantity_fact']]['value'])
    actual=_d(facts[contract['actual_output_fact']]['value'])
    capabilities=set(snapshot['capabilities'])
    metrics={
        'project_status':status,'planned_quantity':str(planned),'actual_output':str(actual),
        'decision_key_hash_material':str(decision_key),
    }
    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'reason':'sponsor class or return objective is not admitted','metrics':metrics}
    if status!=contract['eligible_project_state']:
        return {'outcome':'DEFER','reason_code':'PROJECT_STATE_BLOCK',
                'reason':'project is not in OPERATING state','metrics':metrics}
    if planned<=0 or actual<0 or actual>planned:
        return {'outcome':'DEFER','reason_code':'OUTPUT_RECORD_INVALID',
                'reason':'admitted realized output is inconsistent with the completed cycle','metrics':metrics}
    if actual==0:
        if contract['close_capability'] not in capabilities:
            return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                    'reason':'zero-output close strategy requires admitted close-project capability','metrics':metrics}
        return {'outcome':'CLOSE','reason_code':'ZERO_OUTPUT_CLOSE',
                'reason':'Test 014A strategy elects closure after admitted zero realized output','metrics':metrics}
    if contract['continue_capability'] not in capabilities:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'reason':'positive-output continuation requires admitted operating capability','metrics':metrics}
    return {'outcome':'CONTINUE','reason_code':'POSITIVE_OUTPUT_CONTINUE',
            'reason':'positive realized output admits continuation under the Test 014A strategy','metrics':metrics}
