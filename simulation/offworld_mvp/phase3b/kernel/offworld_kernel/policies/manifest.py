from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Tuple

D=Decimal

class PolicyParameterStatus(str,Enum):
    AUTHORIZED='AUTHORIZED'
    TEST_ONLY='TEST_ONLY'

class ObservationKnowledgeRelation(str,Enum):
    PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION='PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION'
    INDEPENDENT_AGENT_LIKELIHOOD_MODEL='INDEPENDENT_AGENT_LIKELIHOOD_MODEL'

@dataclass(frozen=True,slots=True)
class PolicyParameter:
    parameter_id:str
    semantic_name:str
    value:D
    unit:str
    authorization_ref:str
    status:PolicyParameterStatus
    sensitivity_low:D
    sensitivity_high:D
    local_perturbation:D
    valid_from_version:str
    valid_to_version:str

    def validate(self):
        if not all((self.parameter_id,self.semantic_name,self.unit,self.authorization_ref,
                    self.valid_from_version,self.valid_to_version)):
            raise ValueError('policy parameter metadata incomplete')
        if self.sensitivity_low>self.value or self.value>self.sensitivity_high:
            raise ValueError(f'policy parameter outside sensitivity range: {self.semantic_name}')
        if self.local_perturbation<=0:
            raise ValueError(f'policy parameter perturbation must be positive: {self.semantic_name}')
        return self

@dataclass(frozen=True,slots=True)
class FinancierPolicyManifest:
    manifest_id:str
    policy_id:str
    semantic_version:str
    parameters:Tuple[PolicyParameter,...]
    observation_knowledge_relation:ObservationKnowledgeRelation
    world_observation_model_ref:str
    world_detection_rate:D|None
    world_false_positive_rate:D|None
    manifest_status:PolicyParameterStatus

    REQUIRED_PARAMETERS=(
        'hurdle_rate',
        'horizon_years',
        'agent_detection_rate',
        'agent_false_positive_rate',
        'normalized_throughput',
        'max_concentration_fraction',
    )

    def validate(self,require_authorized:bool=True):
        if not self.manifest_id or not self.policy_id or not self.semantic_version:
            raise ValueError('policy manifest identity incomplete')
        if not self.world_observation_model_ref:
            raise ValueError('world observation-model reference missing')
        by_name={}
        for p in self.parameters:
            p.validate()
            if p.semantic_name in by_name:
                raise ValueError(f'duplicate policy parameter: {p.semantic_name}')
            by_name[p.semantic_name]=p
        if tuple(sorted(by_name))!=tuple(sorted(self.REQUIRED_PARAMETERS)):
            raise ValueError('policy manifest parameter set differs from Test 001 contract')
        if require_authorized:
            if self.manifest_status!=PolicyParameterStatus.AUTHORIZED:
                raise ValueError('policy manifest is not authorized')
            if any(p.status!=PolicyParameterStatus.AUTHORIZED for p in self.parameters):
                raise ValueError('one or more policy parameters are not authorized')
        for name in ('agent_detection_rate','agent_false_positive_rate','hurdle_rate','max_concentration_fraction'):
            v=by_name[name].value
            if v<0 or v>1:
                raise ValueError(f'probability/rate parameter outside [0,1]: {name}')
        if by_name['horizon_years'].value<=0 or by_name['normalized_throughput'].value<=0:
            raise ValueError('horizon and normalized throughput must be positive')
        if self.observation_knowledge_relation==ObservationKnowledgeRelation.PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION:
            if self.world_detection_rate is None or self.world_false_positive_rate is None:
                raise ValueError('perfect observation-model knowledge requires world likelihood values')
            if by_name['agent_detection_rate'].value!=self.world_detection_rate:
                raise ValueError('agent detection rate differs from world under declared equality')
            if by_name['agent_false_positive_rate'].value!=self.world_false_positive_rate:
                raise ValueError('agent false-positive rate differs from world under declared equality')
        return self

    def parameter(self,name:str)->PolicyParameter:
        for p in self.parameters:
            if p.semantic_name==name:
                return p
        raise KeyError(name)

    def canonical_dict(self):
        return {
            'manifest_id':self.manifest_id,
            'policy_id':self.policy_id,
            'semantic_version':self.semantic_version,
            'manifest_status':self.manifest_status.value,
            'observation_knowledge_relation':self.observation_knowledge_relation.value,
            'world_observation_model_ref':self.world_observation_model_ref,
            'world_detection_rate':None if self.world_detection_rate is None else str(self.world_detection_rate),
            'world_false_positive_rate':None if self.world_false_positive_rate is None else str(self.world_false_positive_rate),
            'parameters':[{
                'parameter_id':p.parameter_id,
                'semantic_name':p.semantic_name,
                'value':str(p.value),
                'unit':p.unit,
                'authorization_ref':p.authorization_ref,
                'status':p.status.value,
                'sensitivity_low':str(p.sensitivity_low),
                'sensitivity_high':str(p.sensitivity_high),
                'local_perturbation':str(p.local_perturbation),
                'valid_from_version':p.valid_from_version,
                'valid_to_version':p.valid_to_version,
            } for p in sorted(self.parameters,key=lambda x:x.semantic_name)]
        }

    def parameter_manifest_hash(self):
        raw=json.dumps(self.canonical_dict(),sort_keys=True,separators=(',',':')).encode()
        return sha256(raw).hexdigest()

    def wire_dict(self):
        return self.canonical_dict()

    def policy_version_hash(self,policy_source:bytes):
        h=sha256()
        h.update(policy_source)
        h.update(self.parameter_manifest_hash().encode())
        return f'{self.policy_id}:{self.semantic_version}:{h.hexdigest()}'

def policy_source_bytes()->bytes:
    return (Path(__file__).resolve().parent/'financier_v1.py').read_bytes()

def test_only_manifest()->FinancierPolicyManifest:
    """Synthetic validation fixture. These values are not an authorized policy baseline."""
    status=PolicyParameterStatus.TEST_ONLY
    auth='TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE'
    def p(pid,name,value,unit,low,high,pert):
        return PolicyParameter(pid,name,D(value),unit,auth,status,D(low),D(high),D(pert),'TEST001','TEST001')
    return FinancierPolicyManifest(
        'BUILD5_TEST001_SYNTHETIC_PARAMS_V0_1',
        'FINANCIER_SCREENING_V1',
        '0.1',
        (
            p('p-hurdle','hurdle_rate','0.20','DIMENSIONLESS_ANNUAL_RATE','0.05','0.40','0.01'),
            p('p-horizon','horizon_years','10','YEARS','5','20','1'),
            p('p-detection','agent_detection_rate','0.80','PROBABILITY','0.60','0.95','0.02'),
            p('p-fp','agent_false_positive_rate','0.20','PROBABILITY','0.05','0.40','0.02'),
            p('p-throughput','normalized_throughput','10','MODEL_RESOURCE_UNIT_PER_YEAR','5','20','1'),
            p('p-concentration','max_concentration_fraction','0.80','DIMENSIONLESS_SHARE','0.50','1.00','0.05'),
        ),
        ObservationKnowledgeRelation.PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION,
        'WORLD_OBSERVATION_MODEL:BUILD3_VALIDATION_FP0.20_DETECTION0.80',
        D('0.80'),D('0.20'),
        status,
    ).validate(require_authorized=False)
