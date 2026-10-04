import inspect
import re
import unittest
from decimal import Decimal as D

from offworld_kernel.build3 import RunIdentity
from offworld_kernel.kernel import InvariantError
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import RuntimeObjectClass, SystemState
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent


class ScheduledRuntimeTests(unittest.TestCase):
    def fixture(self):
        rid=RunIdentity('STRICT','v1','SYNTH_STRICT','BUILD4_MVP_METHODOLOGY_R1',())
        k=MethodologyHardenedBuild4Kernel(rid)
        k.add_node('EARTH:X',NodeKind.EARTH)
        k.add_account('source','SRC','EARTH:X',AccountKind.FUNDS,D('10'))
        k.add_account('dest','DST','EARTH:X',AccountKind.FUNDS,D('0'))
        k.add_system(SystemState('PAYMENT_SYSTEM','PAYMENT',{'accounts','transactions'}))
        k.scheduler.register_coupling(CouplingSpec(
            'PAYMENT_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions'),('accounts',),('accounts','transactions'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.schedule(ScheduledEvent('pay-1',D('1'),Phase.OPERATIONS,0,'pay-1','PAYMENT_SYSTEM'))
        rt=ScheduledSimulationRuntime(k)
        rt.register_handler('PAYMENT_SYSTEM',lambda kernel,event:
            kernel.transfer(1,'source','dest',D('4'),TxPurpose.OPEX).id)
        return k,rt

    def test_runtime_is_only_supported_mutation_path_after_seal(self):
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            k.transfer(1,'source','dest',D('1'),TxPurpose.OPEX)
        with self.assertRaises(InvariantError):
            k.scheduler.run(lambda e:k.transfer(1,'source','dest',D('1'),TxPurpose.OPEX))

        result=rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('6'))
        self.assertEqual(k.state.accounts['dest'].balance,D('4'))
        self.assertEqual(result.execution_log,('pay-1',))
        self.assertEqual(result.run_mode,'SCHEDULED_MVP')
        self.assertEqual(result.verification_status,'SCHEDULED_EXECUTION_VERIFIED')
        self.assertEqual(result.validation_status,'NOT_EMPIRICALLY_VALIDATED')

        with self.assertRaises(InvariantError):
            k.transfer(2,'source','dest',D('1'),TxPurpose.OPEX)

    def test_every_public_kernel_method_is_classified_and_every_mutator_blocks_directly(self):
        rid=RunIdentity('SURFACE','v1','SYNTH_SURFACE','BUILD4_MVP_METHODOLOGY_R1',())
        k=MethodologyHardenedBuild4Kernel(rid)

        public={name for name,value in inspect.getmembers(MethodologyHardenedBuild4Kernel,inspect.isfunction)
                if not name.startswith('_')}
        classified=(set(k.SCHEDULED_MUTATION_METHODS)
                    | set(k.SCHEDULED_READONLY_METHODS)
                    | set(k.SCHEDULED_CONTROL_METHODS))
        self.assertEqual(
            public,classified,
            msg=f'unclassified public kernel methods: {sorted(public-classified)}; '
                f'stale classifications: {sorted(classified-public)}')

        rt=ScheduledSimulationRuntime(k)
        rt.seal()

        blocked=[]
        for name in sorted(k.SCHEDULED_MUTATION_METHODS):
            with self.subTest(mutator=name):
                method=getattr(k,name)
                with self.assertRaisesRegex(
                    InvariantError,
                    rf'^direct mutation blocked in scheduled-run mode: {name}$'):
                    method()
                blocked.append(name)

        self.assertEqual(set(blocked),set(k.SCHEDULED_MUTATION_METHODS))


    def test_replay_manifest_pins_git_code_inputs_parameters_tables_and_execution(self):
        k,rt=self.fixture()
        rt.seal()
        result=rt.run()
        self.assertRegex(result.git_commit,r'^[0-9a-f]{40}
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
)
        self.assertRegex(result.code_tree_sha256,r'^[0-9a-f]{64}
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
)
        self.assertEqual(result.repository,'loom-2226/loom-2226')
        self.assertEqual(result.input_snapshot_ids,('SYNTH_STRICT',))
        self.assertEqual(len(result.parameter_manifest_ids),1)
        self.assertTrue(result.parameter_manifest_ids[0].startswith('PARAMS_SHA256:'))
        self.assertEqual(result.table_manifest_ids,('NO_EXTERNAL_TABLES',))
        self.assertRegex(result.provenance_fingerprint,r'^[0-9a-f]{64}
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
)
        self.assertRegex(result.execution_fingerprint,r'^[0-9a-f]{64}
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
)
        self.assertRegex(result.result_fingerprint,r'^[0-9a-f]{64}
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
)

    def test_runtime_context_token_cannot_be_omitted(self):
        k,rt=self.fixture()
        rt.seal()
        with self.assertRaises(InvariantError):
            with k.scheduled_event_context('fake',None):
                pass

    def test_missing_handler_blocks_seal(self):
        k,rt=self.fixture()
        rt2=ScheduledSimulationRuntime(k)
        with self.assertRaises(InvariantError):
            rt2.seal()

    def test_plan_mutation_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.scheduler.schedule(ScheduledEvent('pay-2',D('2'),Phase.OPERATIONS,0,'pay-2','PAYMENT_SYSTEM'))
        with self.assertRaises(InvariantError):
            rt.run()
        self.assertEqual(k.state.accounts['source'].balance,D('10'))

    def test_raw_state_tamper_after_seal_blocks_run(self):
        k,rt=self.fixture()
        rt.seal()
        k.state.accounts['source'].balance+=D('1')
        with self.assertRaises(InvariantError):
            rt.run()

    def test_runtime_single_use_and_replay(self):
        k1,r1=self.fixture()
        r1.seal()
        a=r1.run()

        k2,r2=self.fixture()
        r2.seal()
        b=r2.run()

        self.assertEqual(a.result_fingerprint,b.result_fingerprint)
        self.assertEqual(a.final_fingerprint,b.final_fingerprint)
        with self.assertRaises(InvariantError):
            r1.run()


if __name__=='__main__':
    unittest.main()
