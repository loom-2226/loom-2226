"""The sole physical-realization owner. Audit output is evaluator-only, never actor input."""
from dataclasses import dataclass
import hashlib
import json
from .model import Scenario, Observation


def draw(*parts) -> float:
    key = json.dumps(parts, separators=(',', ':'), allow_nan=False).encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], 'big') / 2**64


@dataclass(frozen=True)
class _PhysicalRealization:
    ice_present: bool


class Instrument:
    def __init__(self, seed: int, scenario: Scenario, evidence_id: str):
        scenario.validate()
        self._scenario = scenario
        self._key = (scenario.generator, scenario.prior_version, evidence_id, seed,
                     scenario.body_id, scenario.site_id, scenario.prior)
        self._physical = _PhysicalRealization(draw('physical', *self._key) < scenario.prior)

    def observe(self, mission_id: str, time: str) -> Observation:
        s = self._scenario
        probability = s.sensitivity if self._physical.ice_present else s.false_positive
        # Independent keyed stream, independent of simulation insertion order/run ID.
        detected = draw('instrument', *self._key, mission_id, time) < probability
        return Observation(mission_id + ':observation', mission_id, s.site_id,
                           detected, s.sensitivity, s.false_positive, time)

    def audit(self) -> dict:
        return {'truth': self._physical.ice_present, 'site_id': self._scenario.site_id,
                'authority_class': 'HIDDEN_SCENARIO_REALIZATION_EVALUATOR_ONLY',
                'generator': self._scenario.generator, 'key': list(self._key)}
