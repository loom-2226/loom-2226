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


class SpreadMeaning(str,Enum):
    SCENARIO_SPREAD_NOT_PROBABILITY='SCENARIO_SPREAD_NOT_PROBABILITY'
    PARAMETER_SENSITIVITY='PARAMETER_SENSITIVITY'
    UNCERTAINTY_SPREAD='UNCERTAINTY_SPREAD'
    STOCHASTIC_VARIABILITY='STOCHASTIC_VARIABILITY'

@dataclass(frozen=True)
class ProbabilityWeightAuthority:
    authority_ref: str
    weights: Tuple[Tuple[str,str],...]

    def normalized(self,case_ids):
        if not self.authority_ref: raise ValueError('probability weights require explicit authority reference')
        d={cid:float(w) for cid,w in self.weights}
        if set(d)!=set(case_ids): raise ValueError('probability weights must cover exactly all cases')
        if any(v<0 for v in d.values()): raise ValueError('negative probability weight')
        total=sum(d.values())
        if abs(total-1.0)>1e-12: raise ValueError('probability weights must sum to one')
        return d

@dataclass(frozen=True)
class EnsembleSpreadReport:
    metric: str
    axis_name: str
    axis_kind: str
    meaning: str
    minimum: str
    maximum: str
    values: Tuple[str,...]
    probability_weighted: bool=False
    authority_ref: str=''

class EnsembleReporter:
    def __init__(self,harness:'EnsembleHarness'):
        self.harness=harness

    def _axis(self,name):
        for a in self.harness.axes:
            if a.name==name: return a
        raise ValueError('unknown ensemble axis')

    def spread(self,results:Iterable[EnsembleResult],metric,axis_name):
        axis=self._axis(axis_name)
        rs=tuple(results)
        vals=[]
        for r in rs:
            d=dict(r.summary)
            if metric not in d: raise ValueError('metric missing from ensemble result')
            vals.append(d[metric])
        nums=[float(v) for v in vals]
        meaning={
          AxisKind.SCENARIO:SpreadMeaning.SCENARIO_SPREAD_NOT_PROBABILITY,
          AxisKind.PARAMETER:SpreadMeaning.PARAMETER_SENSITIVITY,
          AxisKind.UNCERTAINTY:SpreadMeaning.UNCERTAINTY_SPREAD,
          AxisKind.STOCHASTIC_KEY:SpreadMeaning.STOCHASTIC_VARIABILITY}[axis.kind]
        return EnsembleSpreadReport(metric,axis.name,axis.kind.value,meaning.value,
                                    str(min(nums)),str(max(nums)),tuple(vals),False,'')

    def weighted_mean(self,results:Iterable[EnsembleResult],metric,authority:ProbabilityWeightAuthority|None=None):
        if authority is None:
            raise ValueError('probability-weighted summary forbidden without explicit authority')
        rs=tuple(results)
        weights=authority.normalized([r.case_id for r in rs])
        total=0.0
        for r in rs:
            d=dict(r.summary)
            if metric not in d: raise ValueError('metric missing from ensemble result')
            total+=weights[r.case_id]*float(d[metric])
        return {'metric':metric,'weighted_mean':total,'probability_weighted':True,'authority_ref':authority.authority_ref}

    def mean_with_interval(self,*args,authority:ProbabilityWeightAuthority|None=None,**kwargs):
        if authority is None:
            raise ValueError('mean-with-interval forbidden without explicit probability authority')
        raise NotImplementedError('authorized probability interval method not yet implemented')
