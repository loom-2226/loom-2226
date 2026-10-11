import unittest
from decimal import Decimal as D
from .deal_record import deal_records
from .trial_knowledge import who_knows
from .screened_delivery import run_screened

class DealRecordTests(unittest.TestCase):
    def test_single_world_observation_and_decision_beliefs(self):
        for signal in ('NEGATIVE','POSITIVE'):
            for share in (False,True):
                work,decisions,k,_=run_screened(private_signal=signal,share_private=share)
                private=next(o for o in k.observations.values()
                             if o.question_ref=='WATER_BEARING_MATERIAL_PRESENT')
                self.assertEqual(private.signal,signal)
                holders={actor for actor,_,_ in who_knows(k,private.id)}
                self.assertEqual(holders,{'Axiom','Interlune'} if share else {'Axiom'})
                for name in ('Interlune','Axiom'):
                    self.assertEqual(D(next(e['posterior'] for e in k.event_log
                                      if e.get('kind')=='BUILD8_EVIDENCE_BASIS' and e['sponsor']==name)),
                                     k.agents[name].beliefs['BODY:MOON:VOLATILES_PRESENT'])
                    self.assertEqual(who_knows(k,'belief:VOLATILES:'+name),
                                     (('SCREEN_FINANCIER','DISCLOSED',name),))
                self.assertTrue(all(o.id in k.observations for o in k.observations.values()))
                self.assertEqual(len(deal_records(work,decisions,k)),2)

    def test_deal_terms_only_parties_and_replay(self):
        a,da,k,_=run_screened()
        b,db,kb,_=run_screened()
        self.assertEqual(k.build8_knowledge,kb.build8_knowledge)
        deals=deal_records(a,da,k)
        for deal in deals:
            name=deal['sponsor']
            finance=next(r for r in deal['deal_terms'] if ':FINANCE:' in r[0])
            self.assertEqual({x[1] for x in deal['deal_terms'] if x[0]==finance[0]},
                             {name,'SCREEN_FINANCIER'})
            for category,executor in deal['executors']:
                term=next(r[0] for r in deal['deal_terms'] if ':'+category+':' in r[0])
                self.assertEqual({x[1] for x in deal['deal_terms'] if x[0]==term},
                                 {name,executor})
            other=({'Interlune','Axiom'}-{name}).pop()
            self.assertFalse(any(x[1]==other for x in deal['deal_terms']))
