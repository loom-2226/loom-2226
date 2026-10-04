import unittest
from offworld_kernel.accounting_property_fixture import scheduler_valid_accounting_property_fixture

class SchedulerAccountingPropertyTests(unittest.TestCase):
    def test_many_seeded_scheduler_valid_sequences_hold_A1_A9_after_every_step(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                k,result,actions,checks=scheduler_valid_accounting_property_fixture(1000+seed,80)
                self.assertEqual(len(actions),80)
                self.assertEqual(len(checks),80)
                self.assertTrue(all(names==('A1','A2','A3','A4','A5','A6','A7','A8','A9') for _,names in checks))
                self.assertEqual(result.validation_status,'NOT_EMPIRICALLY_VALIDATED')

    def test_property_sequence_replays(self):
        a=scheduler_valid_accounting_property_fixture(2226,120)
        b=scheduler_valid_accounting_property_fixture(2226,120)
        self.assertEqual(a[1].result_fingerprint,b[1].result_fingerprint)
        self.assertEqual(a[2],b[2])
        self.assertEqual(a[3],b[3])

if __name__=='__main__': unittest.main()
