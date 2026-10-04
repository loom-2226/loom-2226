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


    def test_stochastic_spread_is_variability_not_uncertainty(self):
        h=EnsembleHarness('BASE',[ExperimentAxis('seed',AxisKind.STOCHASTIC_KEY,('1','2'))])
        results=(
          EnsembleResult(h.cases()[0].case_id,'a',(('metric','1'),)),
          EnsembleResult(h.cases()[1].case_id,'b',(('metric','3'),)))
        rep=EnsembleReporter(h).spread(results,'metric','seed')
        self.assertEqual(rep.meaning,'STOCHASTIC_VARIABILITY')
        self.assertFalse(rep.probability_weighted)

    def test_scenario_spread_is_not_probability(self):
        h=EnsembleHarness('BASE',[ExperimentAxis('scenario',AxisKind.SCENARIO,('A','B'))])
        results=(
          EnsembleResult(h.cases()[0].case_id,'a',(('metric','1'),)),
          EnsembleResult(h.cases()[1].case_id,'b',(('metric','3'),)))
        rep=EnsembleReporter(h).spread(results,'metric','scenario')
        self.assertEqual(rep.meaning,'SCENARIO_SPREAD_NOT_PROBABILITY')

    def test_weighted_summary_requires_explicit_authority(self):
        h=EnsembleHarness('BASE',[ExperimentAxis('scenario',AxisKind.SCENARIO,('A','B'))])
        cases=h.cases()
        results=(EnsembleResult(cases[0].case_id,'a',(('metric','1'),)),
                 EnsembleResult(cases[1].case_id,'b',(('metric','3'),)))
        reporter=EnsembleReporter(h)
        with self.assertRaisesRegex(ValueError,'forbidden without explicit authority'):
            reporter.weighted_mean(results,'metric')
        auth=ProbabilityWeightAuthority('AUTH:SCENARIO_WEIGHTS',
            ((cases[0].case_id,'0.25'),(cases[1].case_id,'0.75')))
        out=reporter.weighted_mean(results,'metric',auth)
        self.assertEqual(out['weighted_mean'],2.5)
        self.assertEqual(out['authority_ref'],'AUTH:SCENARIO_WEIGHTS')

    def test_mean_interval_forbidden_without_authority_and_unimplemented_with_it(self):
        h=EnsembleHarness('BASE',[ExperimentAxis('scenario',AxisKind.SCENARIO,('A','B'))])
        reporter=EnsembleReporter(h)
        with self.assertRaisesRegex(ValueError,'forbidden without explicit probability authority'):
            reporter.mean_with_interval((),metric='m')
        cases=h.cases()
        auth=ProbabilityWeightAuthority('AUTH:X',((cases[0].case_id,'0.5'),(cases[1].case_id,'0.5')))
        with self.assertRaises(NotImplementedError):
            reporter.mean_with_interval((),metric='m',authority=auth)

if __name__=='__main__': unittest.main()
