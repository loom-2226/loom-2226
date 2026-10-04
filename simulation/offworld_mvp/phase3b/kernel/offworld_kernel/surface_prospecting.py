from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal as D
from hashlib import sha256
import json


@dataclass(frozen=True)
class SurfaceProspectingModel:
    model_id: str
    world_false_positive: D
    world_false_negative: D
    agent_detection_rate: D
    agent_false_positive_rate: D
    remote_world_false_positive_reference: D
    remote_world_false_negative_reference: D
    epistemic_status: str
    source_ref: str
    model_version: str='SURFACE_PROSPECTING_MODEL_V1'

    def validate(self):
        vals=(
            D(self.world_false_positive),D(self.world_false_negative),
            D(self.agent_detection_rate),D(self.agent_false_positive_rate),
            D(self.remote_world_false_positive_reference),
            D(self.remote_world_false_negative_reference),
        )
        if any(v<D('0') or v>D('1') for v in vals):
            raise ValueError('surface prospecting probability outside [0,1]')
        if not D(self.world_false_positive)<D(self.remote_world_false_positive_reference):
            raise ValueError('surface false-positive rate must be lower than remote reference')
        if not D(self.world_false_negative)<D(self.remote_world_false_negative_reference):
            raise ValueError('surface false-negative rate must be lower than remote reference')
        if not D(self.agent_detection_rate)>D(self.agent_false_positive_rate):
            raise ValueError('agent surface likelihood model must discriminate signal')
        if not self.model_id or not self.epistemic_status or not self.source_ref:
            raise ValueError('surface prospecting model lineage incomplete')
        return self

    def fingerprint(self):
        payload={
            'model_id':self.model_id,
            'world_false_positive':str(self.world_false_positive),
            'world_false_negative':str(self.world_false_negative),
            'agent_detection_rate':str(self.agent_detection_rate),
            'agent_false_positive_rate':str(self.agent_false_positive_rate),
            'remote_world_false_positive_reference':str(self.remote_world_false_positive_reference),
            'remote_world_false_negative_reference':str(self.remote_world_false_negative_reference),
            'epistemic_status':self.epistemic_status,
            'source_ref':self.source_ref,
            'model_version':self.model_version,
        }
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class SurfaceProspectingWorldRecord:
    year: int
    actor_id: str
    resource_id: str
    prerequisite_observation_id: str
    observation_id: str
    world_model_id: str
    world_false_positive: D
    world_false_negative: D
    deterministic_draw: D
    signal: str
    expenditure_transaction_id: str
    exploration_asset_id: str
    record_version: str='SURFACE_PROSPECTING_WORLD_RECORD_V1'


@dataclass(frozen=True)
class ObservationBeliefUpdateRecord:
    year: int
    agent_id: str
    observation_id: str
    belief_key: str
    prior: D
    posterior: D
    detection_rate: D
    false_positive_rate: D
    model_id: str
    source_ref: str
    event_id: str
    record_version: str='OBSERVATION_BELIEF_UPDATE_RECORD_V1'
