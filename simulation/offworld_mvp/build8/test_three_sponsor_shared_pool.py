"""Noncanon control: one finite funding account, three competing Sponsor requests."""
import unittest
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner
from .sponsor_evidence_setup import sponsor_setup, KEYS


def shared_pool(private_positive):
    k,public,_,_,_=sponsor_setup('POSITIVE' if private_positive else 'NEGATIVE',projects=True)
    k.add_account('shared_pool','CAPITAL_POOL','EARTH:X',AccountKind.FUNDS,D('.50'))
    results={}
    # Explicit fixed queue is the experimental control, not a claim of fair allocation.
    for name in ('B','A','C'):
        a=k.agents[name]
        ids=tuple(sorted(i for i in a.information if i in k.observations))
        req=SponsorProspectingRequest('pool_req:'+name,2,name,'pool_opp:'+name,'project:'+name,
            'MOON','REG','LOC',tuple(o.id for o in public),KEYS,D('.25'),D('.39')).validate_protocol()
        snap=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:X','pool_snap:'+name,'2',D(0),
            ('REQUEST_FINANCE',),('RETURN',),ids,
            tuple((key,a.beliefs[key]) for key in KEYS),
            tuple((key,a.priors[key]) for key in KEYS),(),(),(),(
            SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,'.25','SYNTHETIC'),
            SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'.39','SYNTHETIC'),
            SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'1','SYNTHETIC')))
        decision=policy_runner.run_sponsor_prospecting_policy(snap,req,'pool_decision:'+name).decision.outcome.value
        funded=decision=='INITIATE_PROJECT' and k.state.accounts['shared_pool'].balance>=D('.25')
        if funded:
            k.transfer(2,'shared_pool','cash:'+name,D('.25'),TxPurpose.OTHER_INVESTMENT,
                parent_ids=('pool_decision:'+name,))
            k.transition_project_status(2,name,'project:'+name,'DEVELOPMENT','pool_decision:'+name)
        elif decision=='DECLINE':
            k.transition_project_status(2,name,'project:'+name,'ABANDONED','pool_decision:'+name)
        results[name]=(decision,'FUNDED' if funded else 'DECLINED' if decision=='DECLINE' else 'UNFUNDED',
                       k.state.projects['project:'+name].status)
    k.assert_invariants()
    return results,str(k.state.accounts['shared_pool'].balance),tuple(
        (t.source_account,t.destination_account,str(t.amount)) for t in k.state.transactions
        if t.source_account=='shared_pool')


class SharedPoolCompetition(unittest.TestCase):
    def test_one_sponsor_changes_anothers_funding(self):
        negative=shared_pool(False)
        positive=shared_pool(True)
        self.assertEqual(negative,shared_pool(False))
        self.assertEqual(positive,shared_pool(True))
        self.assertEqual(negative[0]['B'],('DECLINE','DECLINED','ABANDONED'))
        self.assertEqual(positive[0]['B'],('INITIATE_PROJECT','FUNDED','DEVELOPMENT'))
        self.assertEqual(negative[0]['C'],('INITIATE_PROJECT','FUNDED','DEVELOPMENT'))
        self.assertEqual(positive[0]['C'],('INITIATE_PROJECT','UNFUNDED','PROPOSED'))
        self.assertEqual(negative[0]['A'],positive[0]['A'])
        self.assertEqual(negative[1],positive[1])
        self.assertEqual(negative[1],'0.00')
        self.assertEqual(sum(D(t[2]) for t in negative[2]),D('.50'))
        self.assertEqual(sum(D(t[2]) for t in positive[2]),D('.50'))
        print('SHARED_POOL',negative,positive)
