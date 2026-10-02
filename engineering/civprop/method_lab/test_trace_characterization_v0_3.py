import io, unittest
from contextlib import redirect_stdout
from engineering.civprop.contracts.mission_knowledge_v1 import CharacterizationObservationRecordV1
class TestCharacterizationTraceV03(unittest.TestCase):
 def test_characterization_observation_has_nonbinary_trace_fields(self):
  row=CharacterizationObservationRecordV1('o','m','NASA','q','CERES::METALS','CERES_ORBITAL',2028,'CHARACTERIZATION_COMPLETED','UNRESOLVED_WITHOUT_AUTHORIZED_OBSERVATION_RESULT','PRIVATE')
  self.assertFalse(hasattr(row,'detected'))
  detail=(f"status={row.characterization_status} resource_result={row.resource_result_status}")
  self.assertEqual(detail,'status=CHARACTERIZATION_COMPLETED resource_result=UNRESOLVED_WITHOUT_AUTHORIZED_OBSERVATION_RESULT')
