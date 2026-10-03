from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from itertools import product
import json
from typing import Callable, Iterable, Tuple

class AxisKind(str,Enum):
    SCENARIO='SCENARIO'
    PARAMETER='PARAMETER'
    UNCERTAINTY='UNCERTAINTY'
    STOCHASTIC_KEY='STOCHASTIC_KEY'

@dataclass(frozen=True)
class ExperimentAxis:
    name: str
    kind: AxisKind
    values: Tuple[str,...]

@dataclass(frozen=True)
class EnsembleCase:
    case_id: str
    coordinates: Tuple[Tuple[str,str,str],...]

@dataclass(frozen=True)
class EnsembleResult:
    case_id: str
    outcome_fingerprint: str
    summary: Tuple[Tuple[str,str],...]
    verification_status: str='VERIFIED_FIXTURE'
    validation_status: str='NOT_EMPIRICALLY_VALIDATED'

class EnsembleHarness:
    """Deterministic scenario/uncertainty cartesian harness. It assigns no probabilities."""
    version='PHASE3B_ENSEMBLE_0_1'

    def __init__(self,base_manifest_id:str,axes:Iterable[ExperimentAxis]):
        self.base_manifest_id=base_manifest_id
        axes=list(axes)
        names=[a.name for a in axes]
        if len(names)!=len(set(names)): raise ValueError('duplicate ensemble axis')
        if any(not a.values for a in axes): raise ValueError('empty ensemble axis')
        self.axes=tuple(sorted(axes,key=lambda a:a.name))

    def cases(self)->Tuple[EnsembleCase,...]:
        value_sets=[tuple(sorted(a.values)) for a in self.axes]
        out=[]
        for combo in product(*value_sets):
            coords=tuple((a.name,a.kind.value,v) for a,v in zip(self.axes,combo))
            raw=json.dumps({'base':self.base_manifest_id,'coords':coords},sort_keys=True,separators=(',',':'))
            cid='case-'+sha256(raw.encode()).hexdigest()[:16]
            out.append(EnsembleCase(cid,coords))
        return tuple(out)

    def run(self,runner:Callable[[EnsembleCase],tuple[str,dict]])->Tuple[EnsembleResult,...]:
        results=[]
        for case in self.cases():
            fp,summary=runner(case)
            results.append(EnsembleResult(case.case_id,fp,tuple(sorted((str(k),str(v)) for k,v in summary.items()))))
        return tuple(results)

    def fingerprint(self,results:Iterable[EnsembleResult]=())->str:
        payload={'version':self.version,'base':self.base_manifest_id,
          'axes':[(a.name,a.kind.value,a.values) for a in self.axes],
          'cases':[(c.case_id,c.coordinates) for c in self.cases()],
          'results':[(r.case_id,r.outcome_fingerprint,r.summary,r.verification_status,r.validation_status) for r in results]}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
