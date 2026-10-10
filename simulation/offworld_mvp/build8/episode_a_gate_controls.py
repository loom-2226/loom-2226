"""Disposable negative controls for existing Sponsor policy."""
from decimal import Decimal as D
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner

def evaluate(case):
    obs=tuple('OBS'+str(i) for i in range(4))
    keys=tuple('BEL'+str(i) for i in range(4))
    value=D('.25') if case=='value' else D('.39')
    req=SponsorProspectingRequest('R',1,'SPN','O','P','B','REG','LOC',obs,keys,D('.25'),value).validate_protocol()
    belief=D('.5') if case=='belief' else D('.8')
    available=D('.10') if case=='funds' else D('.60')
    snap=DecisionSnapshot('SPN','PRIVATE_SPONSOR','EARTH:USA','SNAP','1',D(0),('REQUEST_FINANCE',),('RETURN',),obs,
        tuple((k,belief) for k in keys),tuple((k,D('.5')) for k in keys),(),(),(),(
        SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,'.25','SCENARIO'),
        SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,str(value),'SCENARIO'),
        SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,str(available),'CAPITAL')))
    return policy_runner.run_sponsor_prospecting_policy(snap,req,'GATE_'+case).decision

if __name__=='__main__':
    expected={'positive':'INITIATE_PROJECT','value':'DECLINE','belief':'DECLINE','funds':'WAIT'}
    for case,want in expected.items():
        a=evaluate(case);b=evaluate(case)
        assert a==b and a.outcome.value==want,(case,a.outcome,want)
        print('PASS',case,a.outcome.value,a.reason_code.value,flush=True)
