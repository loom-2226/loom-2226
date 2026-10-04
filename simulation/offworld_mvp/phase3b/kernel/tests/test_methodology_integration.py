import unittest
from decimal import Decimal as D
from offworld_kernel.methodology_fixture import *

class MethodologyIntegrationTests(unittest.TestCase):
    def test_scheduled_build4_resolution_and_snapshot(self):
        k,run_result,snapshots=scheduled_resolution_fixture()
        self.assertEqual(k.scheduler.execution_log,['resolve','check','snapshot'])
        self.assertEqual(k.state.accounts['sector_cash'].balance,D('75'))
        self.assertEqual(k.state.accounts['firm_cash'].balance,D('25'))
        self.assertEqual(k.aggregates['FIRM_SECTOR'].member_count,9)
        self.assertEqual(len(snapshots),1)
        self.assertEqual(dict(run_result.event_results)['snapshot'],snapshots[0])
        self.assertEqual(run_result.run_mode,'SCHEDULED_MVP')
        self.assertEqual(run_result.validation_status,'NOT_EMPIRICALLY_VALIDATED')
        self.assertEqual(scheduled_resolution_fixture()[2],snapshots)

    def test_real_kernel_ensemble_replays(self):
        h,a=methodology_ensemble_fixture(); h2,b=methodology_ensemble_fixture()
        self.assertEqual(a,b); self.assertEqual(h.fingerprint(a),h2.fingerprint(b)); self.assertEqual(len(a),4)
        summaries=[dict(r.summary) for r in a]
        self.assertEqual({x['closing_capital'] for x in summaries},{'90.00','95.00'})
        self.assertEqual({x['remaining_resource'] for x in summaries},{'0','100'})
        self.assertTrue(all(r.validation_status=='NOT_EMPIRICALLY_VALIDATED' for r in a))

if __name__=='__main__': unittest.main()
