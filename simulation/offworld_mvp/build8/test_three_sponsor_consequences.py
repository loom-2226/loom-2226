"""Noncanon: same seeded observations and policy, with bounded capital consequences."""
import unittest
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.build3 import Build3Kernel, RunIdentity
from offworld_kernel.mvp_state import AgentState, AgentKind, BODY_MATERIAL_FAMILIES
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner
from .sponsor_evidence_setup import sponsor_setup,KEYS


def episode(private_positive=False):
    k,public,obs,private,_=sponsor_setup('POSITIVE' if private_positive else 'NEGATIVE',projects=True)
    outcomes={}
    for name in ('A','B','C'):
        a=k.agents[name]
        ids=tuple(sorted(i for i in a.information if i in k.observations))
        req=SponsorProspectingRequest('req:'+name,2,name,'opp:'+name,'project:'+name,
            'MOON','REG','LOC',tuple(o.id for o in public),KEYS,D('.25'),D('.39')).validate_protocol()
        snap=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:X','snap:'+name,'2',D(0),
            ('REQUEST_FINANCE',),('RETURN',),ids,
            tuple((key,a.beliefs[key]) for key in KEYS),
            tuple((key,a.priors[key]) for key in KEYS),(),(),(),(
            SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,'.25','SYNTHETIC'),
            SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'.39','SYNTHETIC'),
            SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'1','SYNTHETIC')))
        decision=policy_runner.run_sponsor_prospecting_policy(snap,req,'decision:'+name).decision
        if decision.outcome.value=='INITIATE_PROJECT':
            k.transfer(2,name,'cash:'+name,D('.25'),TxPurpose.OTHER_INVESTMENT,
                parent_ids=('decision:'+name,))
            k.transition_project_status(2,name,'project:'+name,'DEVELOPMENT','decision:'+name)
        else:
            k.transition_project_status(2,name,'project:'+name,'ABANDONED','decision:'+name)
        outcomes[name]=(decision.outcome.value,k.state.projects['project:'+name].status,
            str(k.state.accounts['cash:'+name].balance),str(k.state.accounts[name].balance))
    k.assert_invariants()
    return outcomes,tuple((t.source_account,t.destination_account,str(t.amount),t.purpose.value)
        for t in k.state.transactions)


class ThreeSponsorConsequences(unittest.TestCase):
    def test_decision_drives_bounded_capital_and_projects(self):
        negative,flows=episode(False)
        positive,flows_positive=episode(True)
        self.assertEqual((negative,flows),episode(False))
        self.assertEqual((positive,flows_positive),episode(True))
        self.assertEqual(negative['A'],negative['C'])
        self.assertEqual(negative['A'],positive['A'])
        self.assertEqual(negative['C'],positive['C'])
        self.assertEqual(negative['A'],('INITIATE_PROJECT','DEVELOPMENT','0.25','0.75'))
        self.assertEqual(negative['B'],('DECLINE','ABANDONED','0','1'))
        self.assertEqual(positive['B'],('INITIATE_PROJECT','DEVELOPMENT','0.25','0.75'))
        self.assertEqual(sum(D(t[2]) for t in flows if t[3]=='OTHER_INVESTMENT'),D('.50'))
        self.assertEqual(sum(D(t[2]) for t in flows_positive if t[3]=='OTHER_INVESTMENT'),D('.75'))
        print('SPONSOR_CONSEQUENCES',negative,positive)


if __name__=='__main__':
    unittest.main()
