"""Disposable Build 8 check of country-specific F consumption contract."""
from dataclasses import replace
from decimal import Decimal as D
from offworld_kernel.boundary import ConsumptionRequest,admit_for_use,verify_receipt
from offworld_kernel.policy import FactState
from .opening import build_country_opening
from .two_economy_source_finance_trial import ROOT

def run(root=ROOT):
    k,h,capacities,_=build_country_opening(root)
    k.mobilize_country_capital(1,'AUS',capacities['AUS',2026],D(1),h['prospecting_scenario'],'b8_source:AUS','b8_funds:AUS')
    old=k.boundary_manifest
    contract=next(c for c in old.allowed_use_contracts if c[0]=='SYS:disburse_country_capital' and c[2]=='capital.AVAILABLE_F' and c[3]=='COUNTRY:USA')
    q=ConsumptionRequest('B8:AUS:F','SYS:disburse_country_capital','SYSTEM_TRANSITION','AUS','capital.AVAILABLE_F','COUNTRY:AUS','SIM_TIME','1','1','REALIZED',old.run_id,'WORLD_SIM','','ADMITTED','MODEL_CURRENCY','FINANCIAL_STATE')
    try:
        admit_for_use(k,q)
        raise AssertionError('undeclared AUS use was admitted')
    except Exception as exc:
        assert 'BLOCKED_SCOPE' in str(exc),(type(exc).__name__,str(exc))
    k.boundary_manifest=replace(old,allowed_use_contracts=(*old.allowed_use_contracts,(contract[0],contract[1],contract[2],'COUNTRY:AUS',*contract[4:])))
    v,r=admit_for_use(k,q)
    assert v.value_state==FactState.KNOWN,(v.reason_code,v.value_state)
    assert D(v.value)==k.capital_coupling['AUS']['F']
    assert verify_receipt(k,r)==v
    return str(v.value),r.receipt_id

if __name__=='__main__':
    a=run();b=run();assert a==b
    print('AUS_F_CONTRACT_PASS',a)
