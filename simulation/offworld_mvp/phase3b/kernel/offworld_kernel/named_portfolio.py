from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import io
import json
from typing import Dict, Tuple

from .kernel import InvariantError
from .project_study import ProjectStudyMaturity, ProjectStudyResultStanding, MATURITY_INDEX

D=Decimal

BUILD6C_SCENARIO_VERSION='BUILD6C_PORTFOLIO_SCENARIO_V0_1'
BUILD6C_SCENARIO_STANDING='PRE_CONTRACT_AUTHORED_STRUCTURAL_SCENARIO_NOT_EMPIRICALLY_VALIDATED'


@dataclass(frozen=True)
class NamedBodyEvidenceRecord:
    evidence_id: str
    body_id: str
    project_id: str
    source_path: str
    evidence_class: str
    confidence_class: str
    abundance_semantics: str
    scope: str
    admitted_claim: str
    source_blob_sha: str
    record_version: str='BUILD6C_NAMED_BODY_EVIDENCE_V0_1'

    def validate(self):
        required=(
            self.evidence_id,self.body_id,self.project_id,self.source_path,
            self.evidence_class,self.confidence_class,self.abundance_semantics,
            self.scope,self.admitted_claim,self.source_blob_sha,
        )
        if not all(str(x).strip() for x in required):
            raise ValueError('named body evidence record incomplete')
        if len(self.source_blob_sha)!=40:
            raise ValueError('named body evidence blob SHA invalid')
        return self


@dataclass(frozen=True)
class BodyPortfolioBinding:
    body_id: str
    node_id: str
    project_id: str
    opportunity_family: str
    opening_maturity: ProjectStudyMaturity
    evidence_ids: Tuple[str,...]
    record_version: str='BUILD6C_BODY_PORTFOLIO_BINDING_V0_1'

    def validate(self):
        if not self.body_id or not self.node_id or not self.project_id or not self.opportunity_family:
            raise ValueError('body portfolio binding incomplete')
        ProjectStudyMaturity(self.opening_maturity)
        if not self.evidence_ids or len(set(self.evidence_ids))!=len(self.evidence_ids):
            raise ValueError('body portfolio evidence IDs invalid')
        return self


@dataclass(frozen=True)
class Build6CActivitySpec:
    activity_id: str
    body_id: str
    project_id: str
    required_maturity: ProjectStudyMaturity
    next_maturity: ProjectStudyMaturity
    activity_type: str
    priority: int
    cost: D
    earliest_start: D
    duration_years: D
    result_standing: ProjectStudyResultStanding
    rationale: str
    opportunity_window_id: str=''
    window_open: D|None=None
    window_close: D|None=None
    spec_version: str='BUILD6C_ACTIVITY_SPEC_V0_1'

    @property
    def planned_completion_if_started_at_earliest(self):
        start=max(
            self.earliest_start,
            self.window_open if self.window_open is not None else self.earliest_start
        )
        return start+self.duration_years

    def validate(self):
        if not self.activity_id or not self.body_id or not self.project_id or not self.activity_type:
            raise ValueError('Build 6C activity identity incomplete')
        if self.priority<0 or self.cost<0 or self.earliest_start<D('2026') or self.duration_years<=0:
            raise ValueError('Build 6C activity numeric field invalid')
        required=ProjectStudyMaturity(self.required_maturity)
        nxt=ProjectStudyMaturity(self.next_maturity)
        if MATURITY_INDEX[nxt]!=MATURITY_INDEX[required]+1:
            raise ValueError('Build 6C activity maturity edge invalid')
        ProjectStudyResultStanding(self.result_standing)
        if not self.rationale:
            raise ValueError('Build 6C activity rationale required')
        has_window=bool(self.opportunity_window_id)
        if has_window!=(self.window_open is not None and self.window_close is not None):
            raise ValueError('Build 6C opportunity-window metadata incomplete')
        if has_window and (self.window_close<self.window_open or self.window_close<D('2026')):
            raise ValueError('Build 6C opportunity window invalid')
        return self


@dataclass(frozen=True)
class Build6CPortfolioScenario:
    path: str
    schema_version: str
    standing: str
    reference_calendar: str
    horizon_start: D
    horizon_end: D
    opening_capital: D
    sponsor_id: str
    authority: Tuple[Tuple[str,str],...]
    body_bindings: Tuple[BodyPortfolioBinding,...]
    evidence_records: Tuple[NamedBodyEvidenceRecord,...]
    activity_specs: Tuple[Build6CActivitySpec,...]
    scenario_sha256: str

    def binding_for_body(self,body_id):
        hits=[x for x in self.body_bindings if x.body_id==body_id]
        if len(hits)!=1:
            raise InvariantError('Build 6C body binding not unique')
        return hits[0]

    def activity(self,activity_id):
        hits=[x for x in self.activity_specs if x.activity_id==activity_id]
        if len(hits)!=1:
            raise InvariantError('Build 6C activity spec not unique')
        return hits[0]

    def validate(self):
        if self.schema_version!=BUILD6C_SCENARIO_VERSION or self.standing!=BUILD6C_SCENARIO_STANDING:
            raise ValueError('Build 6C scenario authority/version drift')
        if self.reference_calendar!='2026-01-01' or self.horizon_start!=D('2026.0') or self.horizon_end<D('2041'):
            raise ValueError('Build 6C calendar contract drift')
        if self.opening_capital<=0 or not self.sponsor_id:
            raise ValueError('Build 6C capital contract invalid')
        bodies={x.body_id for x in self.body_bindings}
        if bodies!={'MOON','MARS','CERES','BENNU'}:
            raise ValueError('Build 6C body set drift')
        if len({x.node_id for x in self.body_bindings})!=4 or len({x.project_id for x in self.body_bindings})!=4:
            raise ValueError('Build 6C node/project identity collision')
        ev_ids={x.evidence_id for x in self.evidence_records}
        if len(ev_ids)!=len(self.evidence_records):
            raise ValueError('Build 6C duplicate evidence identity')
        for x in self.body_bindings:
            x.validate()
            if not set(x.evidence_ids)<=ev_ids:
                raise ValueError('Build 6C body binding references missing evidence')
        for x in self.evidence_records:
            x.validate()
            binding=self.binding_for_body(x.body_id)
            if x.project_id!=binding.project_id or x.evidence_id not in binding.evidence_ids:
                raise ValueError('Build 6C evidence/body/project drift')
        ids=set()
        for x in self.activity_specs:
            x.validate()
            if x.activity_id in ids:
                raise ValueError('Build 6C duplicate activity spec')
            ids.add(x.activity_id)
            binding=self.binding_for_body(x.body_id)
            if x.project_id!=binding.project_id:
                raise ValueError('Build 6C activity body/project drift')
            if x.earliest_start>self.horizon_end:
                raise ValueError('Build 6C activity begins after horizon')
        if len(self.scenario_sha256)!=64:
            raise ValueError('Build 6C scenario SHA invalid')
        return self


def default_build6c_scenario_path():
    return Path(__file__).resolve().parents[3] / 'build6' / 'inputs' / 'BUILD6C_2026_2041_PORTFOLIO_SCENARIO_V0_1.json'


def _git_blob_sha(path:Path):
    data=path.read_bytes()
    header=f'blob {len(data)}\0'.encode()
    return hashlib.sha1(header+data).hexdigest()


def _read_source_assertion(repo_root:Path,source_path:str,evidence_id:str):
    path=repo_root/source_path
    if not path.is_file():
        raise ValueError(f'Build 6C evidence source missing: {source_path}')
    if path.suffix=='.json':
        data=json.loads(path.read_text())
        for row in data.get('evidence_assertions',[]):
            if str(row.get('key'))==evidence_id:
                return row
        raise ValueError(f'Build 6C evidence ID absent from JSON source: {evidence_id}')
    if path.suffix=='.csv':
        for row in csv.DictReader(io.StringIO(path.read_text())):
            if str(row.get('assertion_key'))==evidence_id:
                return row
        raise ValueError(f'Build 6C evidence ID absent from CSV source: {evidence_id}')
    raise ValueError('Build 6C evidence source type unsupported')


def load_build6c_scenario(path:Path|str|None=None,validate_repository_sources=True):
    path=Path(path) if path is not None else default_build6c_scenario_path()
    raw=path.read_bytes()
    data=json.loads(raw)
    source_blob_by_path={
        'dev/solar_civprop_m4b/campaign_assertions.json':data['authority']['campaign_assertions_blob'],
        'dev/solar_civprop_m4b/reports/M4B_ASSERTION_PROVENANCE_LEDGER.csv':data['authority']['assertion_ledger_blob'],
    }

    body_bindings=[]
    evidence=[]
    for b in data['bodies']:
        ev_ids=[]
        for e in b['evidence']:
            source_path=str(e['source_path'])
            if source_path not in source_blob_by_path:
                raise ValueError('Build 6C evidence source is not pinned')
            rec=NamedBodyEvidenceRecord(
                str(e['evidence_id']),str(b['body_id']),str(b['project_id']),
                source_path,str(e['evidence_class']),str(e['confidence_class']),
                str(e['abundance_semantics']),str(e['scope']),str(e['admitted_claim']),
                str(source_blob_by_path[source_path])
            ).validate()
            evidence.append(rec); ev_ids.append(rec.evidence_id)
        body_bindings.append(BodyPortfolioBinding(
            str(b['body_id']),str(b['node_id']),str(b['project_id']),
            str(b['opportunity_family']),ProjectStudyMaturity(b['opening_maturity']),
            tuple(ev_ids)
        ).validate())

    specs=[]
    for a in data['activities']:
        w=a.get('opportunity_window')
        spec=Build6CActivitySpec(
            str(a['activity_id']),str(a['body_id']),str(a['project_id']),
            ProjectStudyMaturity(a['required_maturity']),
            ProjectStudyMaturity(a['next_maturity']),
            str(a['activity_type']),int(a['priority']),D(str(a['cost'])),
            D(str(a['earliest_start'])),D(str(a['duration_years'])),
            ProjectStudyResultStanding(a['result_standing']),str(a['rationale']),
            '' if not w else str(w['id']),
            None if not w else D(str(w['open'])),
            None if not w else D(str(w['close'])),
        ).validate()
        specs.append(spec)

    scenario=Build6CPortfolioScenario(
        str(path),str(data['schema_version']),str(data['standing']),
        str(data['calendar']['reference']),
        D(str(data['calendar']['horizon_start'])),D(str(data['calendar']['horizon_end'])),
        D(str(data['capital']['opening_model_currency'])),str(data['capital']['sponsor_id']),
        tuple(sorted((str(k),str(v)) for k,v in data['authority'].items())),
        tuple(body_bindings),tuple(evidence),tuple(specs),hashlib.sha256(raw).hexdigest()
    ).validate()

    if validate_repository_sources:
        repo_root=Path(__file__).resolve().parents[5]
        authority=dict(scenario.authority)
        expected_blobs={
            'dev/solar_civprop_m4b/campaign_assertions.json':authority['campaign_assertions_blob'],
            'dev/solar_civprop_m4b/reports/M4B_ASSERTION_PROVENANCE_LEDGER.csv':authority['assertion_ledger_blob'],
            'dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv':authority['coverage_matrix_blob'],
            'docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md':authority['technology_timeline_blob'],
        }
        for rel,expected in expected_blobs.items():
            actual=_git_blob_sha(repo_root/rel)
            if actual!=expected:
                raise ValueError(f'Build 6C pinned source blob drift: {rel}')
        for rec in scenario.evidence_records:
            row=_read_source_assertion(repo_root,rec.source_path,rec.evidence_id)
            body=str(row.get('body_id',''))
            if body!=rec.body_id:
                raise ValueError(f'Build 6C evidence body drift: {rec.evidence_id}')
            # Require source facts to be no stronger than the preserved input declaration.
            if str(row.get('evidence_class'))!=rec.evidence_class:
                raise ValueError(f'Build 6C evidence class drift: {rec.evidence_id}')
            if str(row.get('abundance_semantics'))!=rec.abundance_semantics:
                raise ValueError(f'Build 6C abundance semantics drift: {rec.evidence_id}')
    return scenario
