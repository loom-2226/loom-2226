"""Build 8 disposable admission probe; no transition or money movement."""
from dataclasses import replace
from decimal import Decimal as D
from offworld_kernel.boundary import ConsumptionRequest,admit_for_use,verify_receipt,validate_opening
from offworld_kernel.policy import FactState
from offworld_kernel.causal_trace import content_hash,canonical
from .opening import build_country_opening
from .two_economy_source_finance_trial import ROOT

def run(root=ROOT):
    k,h,_,_=build_country_opening(root)
    old=k.boundary_manifest
    template=next(a for a in old.assertions if a.concept=='investment' and a.world_context=='SCENARIO' and a.subject_id=='USA')
    prefs=(('USA','SPN','0.6'),('USA','B8_COMPETITOR','0.4'),('AUS','B8_COMMERCIAL','0.5'))
    assertions=[];contracts=[]
    for country,sponsor,share in prefs:
        assertions.append(replace(template,assertion_id=f'B8:PREF:{country}:{sponsor}',subject_id=f'{country}:{sponsor}',
            concept='allocation.PREFERENCE',scope=f'COUNTRY:{country}:SPONSOR:{sponsor}',value=share,unit='PROBABILITY',
            proposition_role='POLICY_PARAMETER',source_refs=('BUILD8_AUTHORED_ALLOCATION_EXPERIMENT',),
            authorization_ref='BUILD8_AUTHORED_ALLOCATION_EXPERIMENT'))
        contracts.append(('SYS:allocate_country_capital','SYSTEM_TRANSITION','allocation.PREFERENCE',
            f'COUNTRY:{country}:SPONSOR:{sponsor}','SCENARIO','WORLD_SIM','PROBABILITY','POLICY_PARAMETER'))
    k.boundary_manifest=replace(old,assertions=(*old.assertions,*assertions),
        allowed_use_contracts=(*old.allowed_use_contracts,*contracts))
    validate_opening(k)
    from offworld_kernel.mvp_state import SystemState
    k.add_system(SystemState("SYS:allocate_country_capital","EXISTING_TRANSITION",set()))
    outcomes=[]
    for country,sponsor,share in prefs:
        q=ConsumptionRequest(f'B8:PREF:USE:{country}:{sponsor}','SYS:allocate_country_capital','SYSTEM_TRANSITION',
            f'{country}:{sponsor}','allocation.PREFERENCE',f'COUNTRY:{country}:SPONSOR:{sponsor}',
            'SIM_TIME','1','1','SCENARIO',k.boundary_manifest.scenario_id,'WORLD_SIM','','ADMITTED','PROBABILITY','POLICY_PARAMETER')
        v,r=admit_for_use(k,q)
        assert v.value_state==FactState.KNOWN,(v.reason_code,v.value_state)
        assert D(v.value)==D(share)
        assert verify_receipt(k,r)==v
        outcomes.append((country,sponsor,share,r.receipt_id))
    return tuple(outcomes)

if __name__=='__main__':
    a=run();b=run();assert a==b
    print('PREFERENCE_ADMISSION_PASS',a)
