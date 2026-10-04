from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Tuple
from .kernel import InvariantError

D=Decimal

class UnderwritingInputKind(str,Enum):
    PRICE='PRICE'
    EXPLORATION_CAPEX='EXPLORATION_CAPEX'
    DEVELOPMENT_CAPEX='DEVELOPMENT_CAPEX'
    OPERATING_COST='OPERATING_COST'
    LEAD_TIME='LEAD_TIME'

class UnderwritingInputStatus(str,Enum):
    AUTHORED_SCENARIO='AUTHORED_SCENARIO'
    EVIDENCE_DERIVED='EVIDENCE_DERIVED'
    UNKNOWN='UNKNOWN'

@dataclass(frozen=True,slots=True)
class UnderwritingInput:
    input_id:str
    archetype_id:str
    kind:UnderwritingInputKind
    value:D|None
    unit:str
    status:UnderwritingInputStatus
    source_or_rationale_ref:str
    sensitivity_low:D|None=None
    sensitivity_high:D|None=None
    valid_from:int|None=None
    valid_to:int|None=None

    def validate(self):
        if not self.input_id or not self.archetype_id or not self.unit or not self.source_or_rationale_ref:
            raise InvariantError('underwriting input metadata incomplete')
        if self.status==UnderwritingInputStatus.UNKNOWN:
            if self.value is not None: raise InvariantError('UNKNOWN underwriting input may not carry value')
        else:
            if self.value is None: raise InvariantError('known underwriting input requires value')
            if self.value<0: raise InvariantError('negative underwriting input')
        if (self.sensitivity_low is None)!=(self.sensitivity_high is None):
            raise InvariantError('underwriting sensitivity range incomplete')
        if self.sensitivity_low is not None:
            if self.value is None: raise InvariantError('UNKNOWN input cannot carry sensitivity range')
            if self.sensitivity_low>self.value or self.value>self.sensitivity_high:
                raise InvariantError('underwriting value outside sensitivity range')
        if self.valid_from is not None and self.valid_to is not None and self.valid_from>self.valid_to:
            raise InvariantError('invalid underwriting validity interval')
        return self

@dataclass(frozen=True,slots=True)
class UnderwritingTable:
    table_id:str
    version:str
    epistemic_status:str
    inputs:Tuple[UnderwritingInput,...]

    def validate(self):
        if self.epistemic_status!='PRE_CONTRACT_AUTHORED_SCENARIO':
            raise InvariantError('MVP underwriting table must retain PRE_CONTRACT_AUTHORED_SCENARIO status')
        ids=[x.input_id for x in self.inputs]
        if len(ids)!=len(set(ids)): raise InvariantError('duplicate underwriting input id')
        for x in self.inputs: x.validate()
        by_arch={}
        for x in self.inputs: by_arch.setdefault(x.archetype_id,set()).add(x.kind)
        required={UnderwritingInputKind.PRICE,UnderwritingInputKind.EXPLORATION_CAPEX,
                  UnderwritingInputKind.DEVELOPMENT_CAPEX,UnderwritingInputKind.OPERATING_COST,
                  UnderwritingInputKind.LEAD_TIME}
        for arch,kinds in by_arch.items():
            if kinds!=required: raise InvariantError(f'underwriting archetype incomplete: {arch}')
        return self

    def get(self,archetype_id,kind):
        for x in self.inputs:
            if x.archetype_id==archetype_id and x.kind==kind: return x
        raise InvariantError('underwriting input not found')

    def fingerprint(self):
        payload={'table_id':self.table_id,'version':self.version,'epistemic_status':self.epistemic_status,
          'inputs':[(x.input_id,x.archetype_id,x.kind.value,None if x.value is None else str(x.value),x.unit,
                     x.status.value,x.source_or_rationale_ref,
                     None if x.sensitivity_low is None else str(x.sensitivity_low),
                     None if x.sensitivity_high is None else str(x.sensitivity_high),
                     x.valid_from,x.valid_to) for x in self.inputs]}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def mvp_validation_underwriting_table():
    arch='GENERIC_RESOURCE_PROJECT_MVP'
    rationale='AUTHORED:MVP_VALIDATION_NOT_EMPIRICAL'
    return UnderwritingTable(
      'OFFWORLD_MVP_UNDERWRITING_VALIDATION_V0_1','0.1','PRE_CONTRACT_AUTHORED_SCENARIO',(
        UnderwritingInput('price-001',arch,UnderwritingInputKind.PRICE,D('20'),'MODEL_CURRENCY_PER_RESOURCE_UNIT',UnderwritingInputStatus.AUTHORED_SCENARIO,rationale,D('10'),D('40')),
        UnderwritingInput('exp-capex-001',arch,UnderwritingInputKind.EXPLORATION_CAPEX,D('10'),'MODEL_CURRENCY',UnderwritingInputStatus.AUTHORED_SCENARIO,rationale,D('5'),D('20')),
        UnderwritingInput('dev-capex-001',arch,UnderwritingInputKind.DEVELOPMENT_CAPEX,D('60'),'MODEL_CURRENCY',UnderwritingInputStatus.AUTHORED_SCENARIO,rationale,D('30'),D('120')),
        UnderwritingInput('opex-001',arch,UnderwritingInputKind.OPERATING_COST,D('4'),'MODEL_CURRENCY_PER_RESOURCE_UNIT',UnderwritingInputStatus.AUTHORED_SCENARIO,rationale,D('2'),D('8')),
        UnderwritingInput('lead-001',arch,UnderwritingInputKind.LEAD_TIME,D('2'),'YEARS',UnderwritingInputStatus.AUTHORED_SCENARIO,rationale,D('1'),D('5')),
      )).validate()
