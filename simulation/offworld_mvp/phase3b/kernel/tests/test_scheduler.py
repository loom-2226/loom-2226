import unittest
from decimal import Decimal as D
from offworld_kernel.scheduler import *
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.kernel import InvariantError
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel

class SchedulerTests(unittest.TestCase):
    def spec(self,pid,phase,owned=('x',),read=(),write=('x',),runtime=RuntimeObjectClass.SYSTEM,interfaces=()):
        return CouplingSpec(pid,'v1',runtime,tuple(owned),tuple(read),tuple(write),'ANNUAL',phase,transition_interfaces=tuple(interfaces))

    def test_phase_order_and_ties(self):
        s=DeterministicScheduler()
        for sp in [self.spec('obs',Phase.OBSERVATION),self.spec('close',Phase.ACCOUNTING_CLOSE),self.spec('snap',Phase.SNAPSHOT_CLOSE)]:
            s.register_coupling(sp)
        # deliberately inserted in the wrong order
        s.schedule(ScheduledEvent('z',D('1'),Phase.SNAPSHOT_CLOSE,0,'z','snap'))
        s.schedule(ScheduledEvent('b',D('1'),Phase.OBSERVATION,0,'B','obs'))
        s.schedule(ScheduledEvent('a',D('1'),Phase.OBSERVATION,0,'A','obs'))
        s.schedule(ScheduledEvent('c',D('1'),Phase.ACCOUNTING_CLOSE,0,'c','close'))
        self.assertEqual([e.event_id for e in s.ordered_events()],['a','b','c','z'])

    def test_insertion_order_independence(self):
        def make(order):
            s=DeterministicScheduler(); s.register_coupling(self.spec('ops',Phase.OPERATIONS))
            ev=[ScheduledEvent('e1',D('1.2'),Phase.OPERATIONS,0,'K1','ops'),ScheduledEvent('e2',D('1.1'),Phase.OPERATIONS,0,'K2','ops')]
            for i in order: s.schedule(ev[i])
            return s
        self.assertEqual(make([0,1]).fingerprint(),make([1,0]).fingerprint())



    def test_period_end_adjustments_precede_accounting_close(self):
        s=DeterministicScheduler()
        s.register_coupling(self.spec('dep',Phase.DEPRECIATION_AMORTIZATION))
        s.register_coupling(self.spec('close',Phase.ACCOUNTING_CLOSE))
        s.register_coupling(self.spec('snap',Phase.SNAPSHOT_CLOSE))
        s.schedule(ScheduledEvent('snap',D('1'),Phase.SNAPSHOT_CLOSE,0,'snap','snap'))
        s.schedule(ScheduledEvent('close',D('1'),Phase.ACCOUNTING_CLOSE,0,'close','close'))
        s.schedule(ScheduledEvent('dep',D('1'),Phase.DEPRECIATION_AMORTIZATION,0,'dep','dep'))
        self.assertEqual([e.event_id for e in s.ordered_events()],['dep','close','snap'])

    def test_decision_window_requires_pinned_snapshot(self):
        s=DeterministicScheduler(); s.register_coupling(self.spec('decision_orchestrator',Phase.DECISION_WINDOW))
        with self.assertRaises(InvariantError):
            s.schedule(ScheduledEvent('d0',D('1'),Phase.DECISION_WINDOW,0,'D','decision_orchestrator'))
        snap=s.open_decision_window('1','STATE-ABC')
        s.schedule(ScheduledEvent('d1',D('1'),Phase.DECISION_WINDOW,0,'D','decision_orchestrator',snapshot_ref=snap))
        self.assertEqual(s.ordered_events()[0].snapshot_ref,snap)
        with self.assertRaises(InvariantError): s.open_decision_window('1','OTHER')

    def test_keyed_randomness_independent_of_queue_insertion(self):
        rid=RunIdentity('SCHED','v1','SYNTH','SCHED_TEST',())
        a=MethodologyHardenedBuild4Kernel(rid); b=MethodologyHardenedBuild4Kernel(rid)
        for k,order in ((a,['e1','e2']),(b,['e2','e1'])):
            k.scheduler.register_coupling(self.spec('ops',Phase.OPERATIONS))
            events={
              'e1':ScheduledEvent('e1',D('1.2'),Phase.OPERATIONS,0,'K1','ops'),
              'e2':ScheduledEvent('e2',D('1.1'),Phase.OPERATIONS,0,'K2','ops')}
            for eid in order: k.scheduler.schedule(events[eid])
        draws_a={e.event_id:a.keyed_draw('SCHEDULED',e.process_id,e.stable_key,e.effective_time) for e in a.scheduler.ordered_events()}
        draws_b={e.event_id:b.keyed_draw('SCHEDULED',e.process_id,e.stable_key,e.effective_time) for e in b.scheduler.ordered_events()}
        self.assertEqual(draws_a,draws_b)
        self.assertEqual(a.scheduler.fingerprint(),b.scheduler.fingerprint())

    def test_unowned_write_rejected(self):
        with self.assertRaises(InvariantError):
            self.spec('bad',Phase.OPERATIONS,owned=('mine',),write=('earth_reference',)).validate()

    def test_agent_policy_not_scheduler_process(self):
        with self.assertRaises(InvariantError):
            self.spec('agent',Phase.DECISION_WINDOW,runtime=RuntimeObjectClass.AGENT).validate()

if __name__=='__main__': unittest.main()
