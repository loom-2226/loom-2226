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
                holders={actor for _,actor,_,_ in who_knows(k,private.id)}
                self.assertEqual(holders,{'Axiom','Interlune'} if share else {'Axiom'})
                for name in ('Interlune','Axiom'):
                    self.assertEqual(D(next(e['posterior'] for e in k.event_log
                                      if e.get('kind')=='BUILD8_EVIDENCE_BASIS' and e['sponsor']==name)),
                                     k.agents[name].beliefs['BODY:MOON:VOLATILES_PRESENT'])
                    self.assertEqual(who_knows(k,'belief:VOLATILES:'+name),
                                     ((2026,'SCREEN_FINANCIER','DISCLOSED',name),))
                self.assertTrue(all(o.id in k.observations for o in k.observations.values()))
                self.assertEqual(len(deal_records(work,decisions,k)),2)

    def test_deal_terms_only_parties_and_replay(self):
        a,da,k,_=run_screened()
        b,db,kb,_=run_screened()
        self.assertEqual(k.build8_knowledge,kb.build8_knowledge)
        deals=deal_records(a,da,k)
        for deal in deals:
            name=deal['sponsor']
            finance=next(r for r in deal['deal_terms'] if ':FINANCE:' in r[1])
            self.assertEqual({x[2] for x in deal['deal_terms'] if x[1]==finance[1]},
                             {name,'SCREEN_FINANCIER'})
            for category,executor in deal['executors']:
                term=next(r[1] for r in deal['deal_terms'] if ':'+category+':' in r[1])
                self.assertEqual({x[2] for x in deal['deal_terms'] if x[1]==term},
                                 {name,executor})
            other=({'Interlune','Axiom'}-{name}).pop()
            self.assertFalse(any(x[2]==other for x in deal['deal_terms']))

    def test_event_years_outcomes_and_private_visibility(self):
        for signal in ('NEGATIVE','POSITIVE'):
            rows,decisions,k,_=run_screened(private_signal=signal)
            funded={d[0]:d[4] for d in decisions}
            for name in ('Interlune','Axiom'):
                recipients=who_knows(k,'outcome:'+name+':FUNDED:1.525000')
                self.assertEqual({actor for _,actor,_,_ in recipients},
                                 {name,'SCREEN_FINANCIER'})
                self.assertEqual({year for year,_,_,_ in recipients},{funded[name]})
                if funded[name]==2027:
                    deferred=who_knows(k,'outcome:'+name+':DEFERRED:INSUFFICIENT_CASH')
                    self.assertEqual({year for year,_,_,_ in deferred},{2026})
                    self.assertEqual({actor for _,actor,_,_ in deferred},
                                     {name,'SCREEN_FINANCIER'})
                for row in (r for r in rows if r.project==name):
                    event=who_knows(k,'outcome:'+name+':'+row.outcome+':'+row.category)
                    self.assertEqual({year for year,_,_,_ in event},{row.finish})
                    self.assertEqual({actor for _,actor,_,_ in event},
                                     {name,dict(deal_records(rows,decisions,k)[0]['executors'])[row.category]})
                    term=next(r for r in k.build8_knowledge
                              if r[1].startswith('deal:'+name+':'+row.category+':'))
                    self.assertEqual(term[0],row.start)
            self.assertEqual([(e['year'],e['fact'],e['actor'],e['route'],e['source'])
                              for e in k.event_log if e.get('kind')=='BUILD8_KNOWLEDGE'],
                             k.build8_knowledge)
