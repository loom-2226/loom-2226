import unittest
from decimal import Decimal as D
from offworld_kernel.scheduler import *
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.kernel import InvariantError

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

    def test_unowned_write_rejected(self):
        with self.assertRaises(InvariantError):
            self.spec('bad',Phase.OPERATIONS,owned=('mine',),write=('earth_reference',)).validate()

    def test_agent_policy_not_scheduler_process(self):
        with self.assertRaises(InvariantError):
            self.spec('agent',Phase.DECISION_WINDOW,runtime=RuntimeObjectClass.AGENT).validate()

if __name__=='__main__': unittest.main()
