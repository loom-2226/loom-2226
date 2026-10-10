"""An unobserved prospecting proposal cannot acquire Sponsor authority."""
import unittest
from pathlib import Path
from offworld_kernel.prospecting import SponsorProspectingRequest, SponsorProspectingOutcome
from offworld_kernel import policy_runner as workers
from simulation.offworld_mvp.build7 import runtime_flow
from .opening import build_country_opening

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'promoted Earth v4 local baseline absent')
class AdmittedProspectingGateTests(unittest.TestCase):
    def test_unobserved_proposal_cannot_be_authorized(self):
        kernel,history,_,_=build_country_opening(ROOT)
        request=SponsorProspectingRequest('B8_UNOBSERVED',1,'SPN','B8_OPPORTUNITY',
            'B8_PROJECT','B8_BODY','B8_REGION','B8_LOCATION',
            tuple('B8_UNOBSERVED_OBS_'+str(i) for i in range(4)),
            tuple('B8_UNOBSERVED_BELIEF_'+str(i) for i in range(4)),2,3)
        decision,_=runtime_flow.policy_epoch(kernel,history,'B8_UNOBSERVED_PROBE','SPN','1',
            request,('prospecting.REQUIRED_CAPITAL','prospecting.INFORMATION_VALUE',
                     'capital.AVAILABLE_F'),workers.run_sponsor_prospecting_policy,
            workers.sponsor_prospecting_policy_version())
        self.assertEqual(decision.outcome,SponsorProspectingOutcome.BLOCKED_UNKNOWN)
        self.assertFalse(kernel.state.projects)
