import unittest
from hashlib import sha256
from offworld_kernel.ensemble import *

class EnsembleTests(unittest.TestCase):
    def test_cartesian_and_axis_order_independence(self):
        a=ExperimentAxis('universe',AxisKind.SCENARIO,('RICH','NULL'))
        b=ExperimentAxis('allocation',AxisKind.PARAMETER,('0.05','0.10'))
        x=EnsembleHarness('BASE',[a,b]); y=EnsembleHarness('BASE',[b,a])
        self.assertEqual(x.cases(),y.cases()); self.assertEqual(len(x.cases()),4)
        self.assertEqual(x.fingerprint(),y.fingerprint())

    def test_results_are_conditional_not_empirical_validation(self):
        h=EnsembleHarness('BASE',[ExperimentAxis('u',AxisKind.SCENARIO,('NULL','RICH'))])
        def run(case):
            raw=str(case.coordinates).encode()
            return sha256(raw).hexdigest(),{'trajectory':'conditional'}
        results=h.run(run)
        self.assertTrue(all(r.validation_status=='NOT_EMPIRICALLY_VALIDATED' for r in results))
        self.assertNotEqual(results[0].case_id,results[1].case_id)
        self.assertEqual(h.fingerprint(results),h.fingerprint(h.run(run)))

if __name__=='__main__': unittest.main()
