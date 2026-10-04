from decimal import Decimal

D=Decimal

POLICY_ID='SPONSOR_SALE_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='BOUNDED_INVENTORY_OFFER_AGAINST_EXOGENOUS_MARKET_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST009A_SPONSOR_SALE_CONTRACT_V0_1',
    'required_agent_kind':'PRIVATE_SPONSOR',
    'required_objective':'RETURN',
    'sell_capability':'SELL',
    'eligible_project_state':'OPERATING',
    'required_project_status_fact':'project.STATUS',
    'required_inventory_fact':'inventory.AVAILABLE',
    'required_price_fact':'market.UNIT_PRICE',
    'required_demand_fact':'market.REMAINING_DEMAND',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('sponsor sale contract mismatch')
    facts=_facts(snapshot)
    status=str(facts[contract['required_project_status_fact']]['value'])
    inventory=_d(facts[contract['required_inventory_fact']]['value'])
    price=_d(facts[contract['required_price_fact']]['value'])
    demand=_d(facts[contract['required_demand_fact']]['value'])
    visible=set(snapshot['information_refs'])
    capabilities=set(snapshot['capabilities'])

    metrics={
        'project_status':status,'inventory_available':str(inventory),
        'unit_price':str(price),'remaining_demand':str(demand),
        'decision_key_hash_material':str(decision_key),
    }

    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'offered_quantity':'0','reason':'sponsor class or return objective is not admitted',
                'metrics':metrics}
    if status!=contract['eligible_project_state']:
        return {'outcome':'DEFER','reason_code':'PROJECT_STATE_BLOCK',
                'offered_quantity':'0','reason':'project is not in OPERATING state',
                'metrics':metrics}
    if not request['observation_id'] or request['observation_id'] not in visible:
        return {'outcome':'DEFER','reason_code':'NO_RELEVANT_INFORMATION',
                'offered_quantity':'0','reason':'relevant resource information is not admitted',
                'metrics':metrics}
    if contract['sell_capability'] not in capabilities:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'offered_quantity':'0','reason':'sponsor lacks admitted SELL capability',
                'metrics':metrics}
    if inventory<=0:
        return {'outcome':'DEFER','reason_code':'NO_SELLABLE_INVENTORY',
                'offered_quantity':'0','reason':'no realized resource inventory is available for sale',
                'metrics':metrics}
    if price<=0:
        return {'outcome':'DEFER','reason_code':'NO_POSITIVE_PRICE',
                'offered_quantity':'0','reason':'admitted market price is not positive',
                'metrics':metrics}
    if demand<=0:
        return {'outcome':'DEFER','reason_code':'NO_MARKET_DEMAND',
                'offered_quantity':'0','reason':'no admitted market demand remains',
                'metrics':metrics}
    return {'outcome':'OFFER','reason_code':'MARKET_OFFER_AUTHORIZED',
            'offered_quantity':str(inventory),
            'reason':'realized inventory and positive admitted exogenous market state authorize an offer',
            'metrics':metrics}
