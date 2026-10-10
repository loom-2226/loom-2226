"""Noncanon synthetic lunar information-asymmetry experiment; no World Authority admission."""
import unittest
from decimal import Decimal as D
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner
from .sponsor_evidence_setup import sponsor_setup,SEED,KEY,KEYS

def run(private_signal='NEGATIVE', share_private=False):
    k,public,obs,private,public_draw=sponsor_setup(private_signal,share_private)
    public_ids=tuple(o.id for o in public)
    results={}
    for name in ('A','B','C'):
        agent=k.agents[name]
        ids=tuple(sorted(i for i in agent.information if i in k.observations))
        request=SponsorProspectingRequest('REQ:'+name,2,name,'OPP','PROJECT','MOON','REG','LOC',
            public_ids,KEYS,D('.25'),D('.39')).validate_protocol()
        snapshot=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:X','SNAP:'+name,'2',D(0),
            ('REQUEST_FINANCE',),('RETURN',),ids,tuple((key,agent.beliefs[key]) for key in KEYS),
            tuple((key,agent.priors[key]) for key in KEYS),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,'.25','SYNTHETIC'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'.39','SYNTHETIC'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'1','SYNTHETIC')))
        decision=policy_runner.run_sponsor_prospecting_policy(snapshot,request,'DEC:'+name).decision
        results[name]=(str(agent.beliefs[KEY]),decision.outcome.value,ids)
    k.assert_invariants()
    return results,(obs.signal,private.signal,str(public_draw[0]),SEED)


class ThreeSponsorObservationTests(unittest.TestCase):
    def test_access_and_isolation(self):
        base,source=run('NEGATIVE')
        flipped,_=run('POSITIVE')
        shared,_=run('NEGATIVE',share_private=True)
        self.assertEqual((base,source),run('NEGATIVE'))
        self.assertEqual(base['A'][:2],base['C'][:2])
        self.assertEqual(base['A'],flipped['A'])
        self.assertEqual(base['C'],flipped['C'])
        self.assertNotEqual(base['B'][0],flipped['B'][0])
        self.assertNotEqual(base['B'][1],flipped['B'][1])
        self.assertEqual(shared['A'][:2],shared['B'][:2])
        self.assertEqual(shared['C'][:2],shared['B'][:2])
        print('SYNTHETIC_ACCESS_CONTROL',base,flipped,shared,source)


if __name__=='__main__':
    unittest.main()
