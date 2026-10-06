#!/usr/bin/env python3
"""Designated Build 6E full named-world qualification driver.

The database is a disposable clone of the qualified World Authority snapshot.
World Authority store APIs own all application reads/writes; SQL in this file
is limited to isolated test-database provisioning and hostile role assertions.
"""
from __future__ import annotations

import argparse
import configparser
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Event

ROOT = Path(__file__).resolve().parents[4]
KERNEL = ROOT / 'simulation/offworld_mvp/phase3b/kernel'
sys.path[:0] = [str(KERNEL), str(ROOT / 'src'),
                str(ROOT / 'simulation/offworld_mvp/build6e'),
                str(ROOT / 'simulation/offworld_mvp/build6e/qualification')]

import psycopg
from psycopg import sql
from loom_world_authority import store
from loom_world_authority.etl import SOURCE_SHA, canonical
from offworld_kernel.causal_trace import content_hash, validate_trace
from offworld_kernel.provenance import source_tree_hash
from build6e_fixture import make_kernel, run_case
from named_world import (_artifact_payload, _walk_typed, load_manifest,
                         prepare_named_world,admitted_constraint,
                         fixture_admission_manifest,NamedWorldBlocked)

BASE = ROOT / 'simulation/offworld_mvp/build6e'
PROTOCOL_PATH = BASE / 'inputs/BUILD6E_QUALIFICATION_V2.json'
DEPENDENCY_STANDING = 'WORLD_AUTHORITY_V1_2_RUN_TRANSACTIONS_QUALIFIED'
TRANSIENT_STATES = ('40001', '40P01')


class _RollbackProbe(Exception):
    pass


def qualify_run_epoch_surface(auditor_service: str) -> dict:
    """Exercise V1.2 per-run locks and the closed transaction-session surface."""
    def held_scope(run_id,entered,release):
        try:
            with store.run_epoch('runtime',run_id) as session:
                entered.set()
                if not release.wait(8):raise RuntimeError('TXN_PROBE_RELEASE_TIMEOUT')
                if hasattr(session,'connection') or hasattr(session,'execute') or hasattr(session,'cursor'):
                    raise RuntimeError('TXN_SURFACE_EXPOSES_DATABASE_HANDLE')
                raise _RollbackProbe()
        except _RollbackProbe:
            return 'ROLLED_BACK'
    def acquire_and_abort(run_id,entered):
        release=Event()
        try:
            with store.run_epoch('runtime',run_id) as session:
                entered.set()
                raise _RollbackProbe()
        except _RollbackProbe:return 'ROLLED_BACK'

    same_entered=Event();same_release=Event();same_waiter=Event()
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(held_scope,'B6E_LOCK_SAME_RUN',same_entered,same_release)
        if not same_entered.wait(5):raise RuntimeError('TXN_SAME_RUN_FIRST_ENTRY')
        second=pool.submit(acquire_and_abort,'B6E_LOCK_SAME_RUN',same_waiter)
        if same_waiter.wait(0.5):raise RuntimeError('TXN_SAME_RUN_LOCK_NOT_HELD')
        same_release.set();first.result(timeout=8)
        if not same_waiter.wait(5):raise RuntimeError('TXN_SAME_RUN_WAITER_NOT_RELEASED')
        second.result(timeout=8)

    diff_entered=Event();diff_release=Event();diff_waiter=Event()
    with ThreadPoolExecutor(max_workers=2) as pool:
        first=pool.submit(held_scope,'B6E_LOCK_RUN_A',diff_entered,diff_release)
        if not diff_entered.wait(5):raise RuntimeError('TXN_DIFFERENT_RUN_FIRST_ENTRY')
        second=pool.submit(acquire_and_abort,'B6E_LOCK_RUN_B',diff_waiter)
        if not diff_waiter.wait(5):raise RuntimeError('TXN_DIFFERENT_RUNS_GLOBALLY_SERIALIZED')
        second.result(timeout=8);diff_release.set();first.result(timeout=8)

    # The public session accepts one in-memory stage only and exposes no SQL
    # method, caller connection, transaction control or role-switch method.
    entered=Event();release=Event()
    try:
        with store.run_epoch('runtime','B6E_SURFACE_ROLLBACK') as session:
            entered.set()
            public={'connection','conn','cursor','execute','commit','rollback','set_role'}
            if any(hasattr(session,name) for name in public):
                raise RuntimeError('TXN_BOUNDED_SESSION_PUBLIC_ESCAPE')
            session.stage_epoch('UNCOMMITTED_PROBE',None,(),())
            try:session.stage_epoch('SECOND_STAGE',None,(),())
            except store.IntegrityFailure:pass
            else:raise RuntimeError('TXN_STAGE_ALLOWED_MORE_THAN_ONCE')
            raise _RollbackProbe()
    except _RollbackProbe:pass
    with connect(auditor_service) as db:
        rows=db.execute("SELECT count(*) FROM wa_run.causal_envelope WHERE run_id LIKE 'B6E_LOCK_%' OR run_id='B6E_SURFACE_ROLLBACK'").fetchone()[0]
        if rows:raise RuntimeError('TXN_ROLLBACK_PROBE_PERSISTED_ROWS')
    return {'same_run_lock_serializes':'PASS','different_run_lock_independent':'PASS',
        'raw_connection_sql_and_transaction_controls_unavailable':'PASS',
        'single_stage_enforced':'PASS','exception_rolls_back_without_rows':'PASS'}


def qualify_science_cutoff_controls(*,reference_reader,science_writer,science_governor,
                                    auditor_service,doc,prepared_source):
    """Test source standing, exact provenance/scope and later HOLD cutoffs."""
    source=doc['accepted_source'];aid=uuid.UUID(source['assertion_id'])
    support=uuid.UUID(source['support_id'])
    if prepared_source['initial_standing']!='CANDIDATE' or prepared_source['standing']!='ADMITTED':
        raise RuntimeError('B03_SOURCE_CANDIDACY_OR_SEPARATE_USE_ADMISSION')
    if prepared_source['source_byte_sha256'] is not None or prepared_source['source_artifact_id'] is not None:
        raise RuntimeError('B04_NULL_REMOTE_ARTIFACT_CUSTODY_REWRITTEN')

    drift=deepcopy(doc);drift['accepted_source']['assertion_metadata_sha256']='0'*64
    try:admitted_constraint(reference_reader,drift)
    except NamedWorldBlocked as exc:
        if not str(exc).startswith('BLOCKED_SOURCE_PROVENANCE_OR_SCOPE:metadata_sha256'):
            raise RuntimeError('B04_WRONG_PROVENANCE_DRIFT_BLOCK:'+str(exc))
    else:raise RuntimeError('B04_CHANGED_SOURCE_PROVENANCE_ACCEPTED')

    wrong_support=uuid.UUID('00000000-0000-0000-0000-000000000001')
    try:
        store.read_admitted_constraints(reference_reader,[aid],1,doc['fixture_admission']['use_contract_ref'],
            [wrong_support],consumer='BUILD6E_NAMED_WORLD_V1',context='REAL',perspective='GOVERNANCE')
    except store.IntegrityFailure as exc:
        if 'BLOCKED_SCOPE' not in str(exc):raise
    else:raise RuntimeError('B06_UNSUPPORTED_TARGET_SCOPE_ACCEPTED')
    reference_reader.rollback()

    hold=deepcopy(doc);admission=hold['fixture_admission']
    admission['decision_ordinal']=2;admission['standing']='HOLD'
    admission['authorization_ref']=admission['authorization_ref']+':QUALIFICATION_HOLD_CONTROL'
    admission['effective_availability_lexeme']='3'
    admission['time_support']['time_lexeme']='3'
    time_result=store.install_fixture_time_support(science_writer,fixture_admission_manifest(hold))
    hold_result=store.record_fixture_admission(science_governor,fixture_admission_manifest(hold))
    if time_result not in ('INSERTED','ALREADY_MATCHED') or hold_result!='INSERTED':
        raise RuntimeError('B04_HOLD_AFTER_CUTOFF_FIXTURE_NOT_APPENDED')
    pinned=store.read_admitted_constraints(reference_reader,[aid],1,admission['use_contract_ref'],
        [support],consumer='BUILD6E_NAMED_WORLD_V1',context='REAL',perspective='GOVERNANCE')
    if len(pinned)!=1 or pinned[0]['decision_ordinal']!=1:
        raise RuntimeError('B04_PINNED_CUTOFF_REPLAY_CHANGED')
    reference_reader.rollback()
    try:
        store.read_admitted_constraints(reference_reader,[aid],2,admission['use_contract_ref'],
            [support],consumer='BUILD6E_NAMED_WORLD_V1',context='REAL',perspective='GOVERNANCE')
    except store.IntegrityFailure as exc:
        if 'BLOCKED_SCIENCE_ADMISSION' not in str(exc):raise
    else:raise RuntimeError('SOURCE_HOLD_AFTER_CUTOFF_NOT_ENFORCED')
    reference_reader.rollback()
    with connect(auditor_service) as db:
        standing=db.execute('SELECT initial_standing FROM wa_science.assertion WHERE assertion_id=%s',(aid,)).fetchone()[0]
        if standing!='CANDIDATE':raise RuntimeError('SOURCE_SCIENCE_STANDING_MUTATED')
        admissions=db.execute('SELECT decision_ordinal,standing FROM wa_science.admission WHERE target_assertion_id=%s ORDER BY decision_ordinal',(aid,)).fetchall()
        if admissions!=[(1,'ADMITTED'),(2,'HOLD')]:raise RuntimeError('SOURCE_ADMISSION_HISTORY_NOT_APPEND_ONLY')
    return {'candidate_without_fixture_admission':'BLOCKED','candidate_standing_preserved':'PASS',
        'source_provenance_drift':'BLOCKED','scope_crossing':'BLOCKED',
        'pinned_cutoff_survives_later_hold':'PASS','newer_hold_cutoff':'BLOCKED',
        'admission_history':admissions}


def qualify_candidate_invisibility(reference_reader,doc):
    source=doc['accepted_source']
    try:
        store.read_admitted_constraints(reference_reader,[uuid.UUID(source['assertion_id'])],1,
            doc['fixture_admission']['use_contract_ref'],[uuid.UUID(source['support_id'])],
            consumer='BUILD6E_NAMED_WORLD_V1',context='REAL',perspective='GOVERNANCE')
    except store.IntegrityFailure as exc:
        if 'BLOCKED_SCIENCE_ADMISSION' not in str(exc):raise
        reference_reader.rollback()
        return 'BLOCKED'
    reference_reader.rollback()
    raise RuntimeError('B02_CANDIDATE_SCIENCE_VISIBLE_WITHOUT_ADMISSION')


def qualify_prior_missing_behavior():
    kernel,history=run_case('RICH',{'prior':None})
    blocked=history.get('blocked','')
    if not blocked.startswith('BLOCKED_PARAMETER:') or 'prior' not in blocked.lower():
        raise RuntimeError('B18_MISSING_PRIOR_DID_NOT_BLOCK_EXPLICITLY')
    if any(agent.priors or agent.beliefs for agent in kernel.agents.values()):
        raise RuntimeError('B18_MISSING_PRIOR_COERCED_TO_KNOWN_VALUE')
    if kernel.causal_envelopes or kernel.state.transactions:
        raise RuntimeError('B18_MISSING_PRIOR_CREATED_CONSEQUENCE')
    return {'status':'BLOCKED','reason':blocked,'prior_state':'ABSENT',
        'belief_state':'ABSENT','consequences':0,'default_prior_inserted':False}


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _json_write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2, default=str).encode() + b'\n')


def provision_runtime_database(admin_config: dict, output: Path) -> tuple[str, Path, dict]:
    """Clone the untouched qualified source database and create bounded logins."""
    nonce = secrets.token_hex(5)
    database = 'wa_6e_' + nonce
    logins = {
        'runtime': ('b6e_rt_' + nonce, ('wa_runtime_writer', 'wa_admission_writer')),
        'science_writer': ('b6e_sw_' + nonce, ('wa_science_writer',)),
        'science_governor': ('b6e_sg_' + nonce, ('wa_science_governor',)),
        'world_writer': ('b6e_ww_' + nonce, ('wa_world_writer',)),
        'reference_reader': ('b6e_rr_' + nonce, ('wa_reference_reader',)),
        'auditor': ('b6e_au_' + nonce, ('wa_auditor',)),
        'agent_reader': ('b6e_ar_' + nonce, ('wa_agent_reader',)),
    }
    admin = {k: admin_config[k] for k in ('host', 'port', 'user', 'password')}
    admin['dbname'] = 'postgres'
    with psycopg.connect(**admin, autocommit=True) as conn:
        conn.execute(sql.SQL('CREATE DATABASE {} TEMPLATE {}').format(
            sql.Identifier(database), sql.Identifier(admin_config['dbname'])))
        for service, (login, memberships) in logins.items():
            password = secrets.token_urlsafe(32)
            conn.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(
                sql.Identifier(login), sql.Literal(password)))
            for membership in memberships:
                conn.execute(sql.SQL('GRANT {} TO {}').format(
                    sql.Identifier(membership), sql.Identifier(login)))
            logins[service] = (login, memberships, password)
    service_file = output / 'qualification.pg_service.conf'
    lines = []
    for service, (login, _, password) in logins.items():
        lines.extend((f'[{service}]', f'host={admin_config["host"]}',
            f'port={admin_config["port"]}', f'dbname={database}',
            f'user={login}', f'password={password}', ''))
    service_file.write_text('\n'.join(lines))
    service_file.chmod(0o600)
    os.environ['PGSERVICEFILE'] = str(service_file)
    clean_logins = {k: {'login': v[0], 'memberships': list(v[1])} for k, v in logins.items()}
    return database, service_file, clean_logins


def connect(service: str):
    return psycopg.connect(service=service)


def provision_agent_logins(admin_config: dict, database: str, service_file: Path,
                           run_id: str) -> tuple[dict[str,str],dict[str,str]]:
    """Provision isolated real logins for the exact run/actor projections."""
    cfg={k:admin_config[k] for k in ('host','port','user','password')};cfg['dbname']='postgres'
    logins={actor:'b6e_a_'+sha256((run_id+'\0'+actor).encode()).hexdigest()[:18]
        for actor in ('PUB','SPN','FIN')}
    passwords={actor:secrets.token_urlsafe(32) for actor in logins}
    with psycopg.connect(**cfg,autocommit=True) as conn:
        for actor,login in logins.items():
            exists=conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(login,)).fetchone()
            if exists:
                conn.execute(sql.SQL('ALTER ROLE {} WITH LOGIN PASSWORD {}').format(
                    sql.Identifier(login),sql.Literal(passwords[actor])))
            else:
                conn.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(
                    sql.Identifier(login),sql.Literal(passwords[actor])))
            conn.execute(sql.SQL('GRANT wa_agent_reader TO {}').format(sql.Identifier(login)))
    parser=configparser.ConfigParser(interpolation=None)
    parser.read(service_file)
    services={}
    for actor,login in logins.items():
        service='agent_'+actor.lower();services[actor]=service
        parser[service]={'host':str(admin_config['host']),'port':str(admin_config['port']),
            'dbname':database,'user':login,'password':passwords[actor]}
    with service_file.open('w') as stream:
        for section in parser.sections():
            stream.write(f'[{section}]\n')
            for key,value in parser.items(section):stream.write(f'{key}={value}\n')
            stream.write('\n')
    service_file.chmod(0o600)
    return logins,services


def authority_preflight(admin_config: dict, database: str, expected_source: str) -> dict:
    cfg = {k: admin_config[k] for k in ('host', 'port', 'user', 'password')}
    cfg['dbname'] = database
    with psycopg.connect(**cfg, autocommit=True) as conn:
        server = conn.execute('SELECT version()').fetchone()[0]
        source_rows = conn.execute('SELECT count(*) FROM wa_meta.legacy_row').fetchone()[0]
        columns = conn.execute('SELECT count(*) FROM wa_meta.source_snapshot').fetchone()[0]
        admissions = conn.execute('SELECT count(*) FROM wa_science.admission').fetchone()[0]
        source = conn.execute('SELECT byte_sha256 FROM wa_meta.source_snapshot ORDER BY snapshot_id LIMIT 1').fetchone()[0]
        assert source == expected_source == SOURCE_SHA
        assert source_rows == 2726 and columns == 1 and admissions == 0
        return {'server_version': server, 'forensic_rows': source_rows,
                'source_snapshots': columns, 'source_admissions_before_fixture': admissions,
                'source_sha256': source}


def _case_overrides(name: str) -> tuple[dict, dict]:
    if name == 'BASELINE': return {}, {}
    if name.startswith('BUYER_'): return {'B': name.split('_', 1)[1]}, {}
    if name == 'PUBLIC_LOW': return {'P': '9'}, {}
    if name == 'FINANCIER_LOW': return {'F': '59'}, {}
    if name == 'HABITAT_LOW':
        protocol=json.loads(PROTOCOL_PATH.read_text())
        return {}, {'habitat_capacity':protocol['case_parameters'][name]['habitat_capacity']}
    if name == 'TRANSPORT_MISSING': return {}, {'relationship_registered': 'FALSE'}
    if name == 'POLICY_SEED_ONLY': return {}, {'__policy_seed__': 'B6E-POLICY-ISOLATION-20261006'}
    if name == 'WORLD_SEED_ONLY': return {}, {'__world_seed__': '20261006'}
    if name == 'PRIOR_MISSING': return {'prior': None}, {}
    raise ValueError('UNDECLARED_6E_CASE:' + name)


def witness(kernel, history):
    node = 'OFF:MOON:CABEU:B6E_SITE_01'
    trace = validate_trace(kernel.causal_envelopes, kernel.causal_artifacts)
    return {'status': kernel.state.projects['P'].status,
        'blocked': history.get('blocked'),
        'remote': history.get('REMOTE').signal if 'REMOTE' in history else None,
        'surface': history.get('SURFACE').signal if 'SURFACE' in history else None,
        'draws': {c:str(history[c+'_draw']) for c in ('REMOTE','SURFACE') if c+'_draw' in history},
        'first_output': str(history['first_output'].actual_extracted) if history.get('first_output') else None,
        'second_output': str(history['second_output'].actual_extracted) if history.get('second_output') else None,
        'sale_count': len(kernel.market_clearing_records),
        'sale_value': str(kernel.market_clearing_records[0].transaction_value) if kernel.market_clearing_records else None,
        'remaining': str(kernel.resources['RES'].remaining),
        'people': kernel.population.offworld[node],
        'cohort_total': kernel.population.total(),
        'cash': {aid:str(a.balance) for aid,a in sorted(kernel.state.accounts.items())},
        'all_A1_A9': bool(history['audits']) and all(all(x.values()) for x in history['audits']),
        'infrastructure_plan_capacity': (kernel.settlement_infrastructure_plans['INFRA'].habitat_capacity
            if 'INFRA' in kernel.settlement_infrastructure_plans else None),
        'infrastructure_records': len(kernel.settlement_infrastructure_records),
        'infrastructure_outcomes': [r.outcome for r in kernel.settlement_infrastructure_records],
        'settlement_habitat_capacity': kernel.colonies[node].habitat_capacity,
        'passenger_departures': len(kernel.passenger_transport_departures),
        'passenger_arrivals': len(kernel.passenger_transport_arrivals),
        'settlement_stage': kernel.colonies[node].stage,
        'trace_root': trace, 'envelope_count': len(kernel.causal_envelopes),
        'artifact_count': len(kernel.causal_artifacts),
        'policy_outcomes': {label:result.decision.outcome.value for label,result in history['policies'].items()},
        'policy_fingerprints': {label:content_hash(result.decision) for label,result in history['policies'].items()},
        'snapshot_fingerprints': {label:s.fingerprint() for label,s in history['snapshots'].items()}}


def validate_case_witness(case_name: str, world: str, data: dict) -> dict:
    """Apply the preregistered finite physical and affordability expectations."""
    if not data['all_A1_A9'] or data['cohort_total']!=1000:
        raise RuntimeError('B22_B26_LEDGER_OR_POPULATION_CONSERVATION')
    if data['sale_count']>1:raise RuntimeError('B23_MORE_THAN_ONE_SALE')
    for actor,balance in data['cash'].items():
        if Decimal(balance)<0:raise RuntimeError('B22_NEGATIVE_ACCOUNT:'+actor)
    if case_name=='BASELINE':
        expected={'NULL':('ABANDONED',0,None,None,0),
            'SPARSE':('CLOSED',1,'3','0',10),
            'RICH':('OPERATING',1,'5','5',10)}[world]
        observed=(data['status'],data['sale_count'],data['first_output'],
            data['second_output'],data['people'])
        if observed!=expected:raise RuntimeError('BASELINE_POSITIVE_WITNESS:'+repr((world,observed,expected)))
    elif case_name.startswith('BUYER_'):
        buyer=Decimal(case_name.split('_',1)[1])
        required=Decimal('0') if world=='NULL' else Decimal('60') if world=='SPARSE' else Decimal('100')
        expected_sale=int(world!='NULL' and buyer>=required)
        if data['sale_count']!=expected_sale:
            raise RuntimeError('B23_FINITE_BUYER_BOUNDARY:'+world+':'+str(buyer))
        if expected_sale:
            expected_output=('3','0') if world=='SPARSE' else ('5','5')
            if (data['first_output'],data['second_output'])!=expected_output:
                raise RuntimeError('B22_BUYER_CASE_PHYSICAL_OUTPUT:'+world)
            if data['people']!=10:raise RuntimeError('B23_AFFORDABLE_SALE_SETTLEMENT_WITNESS')
        elif data['people']!=0:
            raise RuntimeError('B23_UNAFFORDABLE_BUYER_CREATED_SETTLEMENT_POPULATION')
    elif case_name=='PUBLIC_LOW':
        if data['sale_count'] or data['people'] or data['first_output'] is not None:
            raise RuntimeError('PUBLIC_LOW_CREATED_UNFUNDED_ACTION')
    elif case_name=='FINANCIER_LOW':
        if data['sale_count'] or data['people']:
            raise RuntimeError('FINANCIER_LOW_CREATED_UNFUNDED_DEVELOPMENT')
    elif case_name=='HABITAT_LOW':
        if world!='NULL' and data['sale_count']!=1:
            raise RuntimeError('HABITAT_LOW_UNEXPECTED_SALE_RESULT')
        if data['people']!=0 or data['passenger_arrivals']!=0:
            raise RuntimeError('B24_INSUFFICIENT_HABITAT_CREATED_RESIDENTS')
        if world!='NULL':
            if data['infrastructure_plan_capacity']!=9 or data['infrastructure_records']!=1:
                raise RuntimeError('B24_VALID_INSUFFICIENT_HABITAT_NOT_EXECUTED')
            if data['infrastructure_outcomes']!=['INSTALLED'] or data['settlement_habitat_capacity']!=9:
                raise RuntimeError('B24_HABITAT_CAPACITY_NOT_PHYSICALLY_REALIZED')
            if data['passenger_departures']!=0 or data['settlement_stage']=='DEPENDENT_SETTLEMENT':
                raise RuntimeError('B24_UNDERCAPACITY_SETTLEMENT_ADVANCED')
    elif case_name=='TRANSPORT_MISSING':
        if data['people']!=0:raise RuntimeError('B25_MISSING_TRANSPORT_CREATED_RESIDENTS')
    return {'accounting_A1_A9':'PASS','cohort_conserved':True,
        'sale_count_at_most_one':True,'finite_case_assertions':'PASS'}


def audit_persisted_case(auditor_service: str, run_id: str, *, minimum_loops: int) -> dict:
    """Read-only relational qualification through the dedicated auditor role."""
    with connect(auditor_service) as db:
        envelope_count=db.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s',(run_id,)).fetchone()[0]
        stock_count=db.execute('SELECT count(*) FROM wa_run.stock_state WHERE run_id=%s',(run_id,)).fetchone()[0]
        access_count=db.execute('SELECT count(*) FROM wa_run.accessibility_assessment WHERE run_id=%s',(run_id,)).fetchone()[0]
        recovery_count=db.execute('SELECT count(*) FROM wa_run.recoverability_assessment WHERE run_id=%s',(run_id,)).fetchone()[0]
        reserve_count=db.execute('SELECT count(*) FROM wa_run.reserve_interpretation WHERE run_id=%s',(run_id,)).fetchone()[0]
        if not envelope_count or (stock_count,access_count,recovery_count,reserve_count)!=(envelope_count,)*4:
            raise RuntimeError('B21_INCOMPLETE_TYPED_RESOURCE_HISTORY')
        bad=db.execute('''SELECT count(*) FROM wa_run.stock_state s
            JOIN wa_run.accessibility_assessment a USING(run_id,deposit_id,event_id)
            JOIN wa_run.recoverability_assessment r USING(run_id,deposit_id,event_id)
            JOIN wa_run.reserve_interpretation z USING(run_id,deposit_id,event_id)
            WHERE s.run_id=%s AND (a.accessible_quantity>s.remaining_in_situ OR
              (r.value_state='KNOWN' AND r.recoverable_quantity>a.accessible_quantity) OR
              z.value_state<>'UNKNOWN' OR z.economic_contract_ref IS NOT NULL)''',(run_id,)).fetchone()[0]
        if bad:raise RuntimeError('B21_RESOURCE_LAYER_SEPARATION')
        population=db.execute('''SELECT count(*) FROM (SELECT event_id,sum(person_count) AS n
            FROM wa_run.population_state WHERE run_id=%s GROUP BY event_id) x
            WHERE x.n<>1000''',(run_id,)).fetchone()[0]
        if population:raise RuntimeError('B26_PERSISTED_POPULATION_CONSERVATION')
        world_row=db.execute('SELECT body_id,world_id FROM wa_run.world_binding WHERE run_id=%s',(run_id,)).fetchone()
        if not world_row:raise RuntimeError('B08_MISSING_NAMED_WORLD_BINDING')
        body_id,world_id=world_row
        site=db.execute('''SELECT l.location_kind,l.origin_kind FROM wa_geo.location l
            JOIN wa_world.site s ON s.location_id=l.location_id WHERE s.world_id=%s''',(world_id,)).fetchone()
        if not site or site[0]!='SITE':raise RuntimeError('B08_NAMED_SITE_KIND')
        cabeus=db.execute("SELECT location_kind,origin_kind FROM wa_geo.location WHERE semantic_key='CABEU'").fetchone()
        if cabeus!=('SITE','EMPIRICALLY_IDENTIFIED'):
            raise RuntimeError('B06_CABEU_LOCAL_SITE_SCOPE')
        loops=db.execute('SELECT count(*) FROM wa_info.epistemic_loop WHERE run_id=%s',(run_id,)).fetchone()[0]
        if loops<minimum_loops:raise RuntimeError('B28_CLOSED_EPISTEMIC_LOOP_MISSING')
        bad_actor=db.execute('''SELECT count(*) FROM wa_info.epistemic_loop l
            JOIN wa_run.causal_envelope e ON e.run_id=l.run_id AND e.envelope_id=l.consequence_envelope_id
            WHERE l.run_id=%s AND e.actor_ref<>l.actor_id''',(run_id,)).fetchone()[0]
        if bad_actor:raise RuntimeError('B28_LOOP_ACTOR_CONTINUITY')
        unknown_reserve=db.execute("SELECT count(*) FROM wa_world.hidden_state WHERE world_id=%s AND property_code='R_RESERVE' AND value_state='UNKNOWN' AND numeric_value IS NULL",(world_id,)).fetchone()[0]
        if unknown_reserve!=1:raise RuntimeError('B21_WORLD_RESERVE_NOT_UNKNOWN')
        return {'run_id':run_id,'world_id':str(world_id),'body_id':str(body_id),
            'causal_envelopes':envelope_count,'stock_states':stock_count,
            'accessibility_assessments':access_count,'recoverability_assessments':recovery_count,
            'reserve_interpretations':reserve_count,'closed_epistemic_loops':loops,
            'cabeus_catalog_kind':'SITE','cabeus_origin_kind':'EMPIRICALLY_IDENTIFIED',
            'resource_layer_guards':'PASS','population_conservation':'PASS'}


def validate_comparison_runs(cases: dict) -> dict:
    """Prove fixed common streams and divergence only after observations."""
    worlds=('NULL','SPARSE','RICH');baseline={}
    for world in worlds:
        key='BASELINE:'+world
        if key not in cases:raise RuntimeError('B43_MISSING_BASELINE:'+world)
        baseline[world]=cases[key]['witness']
    draw_vectors={tuple(sorted(baseline[w]['draws'].items())) for w in worlds}
    if len(draw_vectors)!=1:raise RuntimeError('B11_COMMON_WORLD_STREAM_DIVERGENCE')
    initial_snapshots={baseline[w]['snapshot_fingerprints'].get('REMOTE') for w in worlds}
    initial_decisions={baseline[w]['policy_fingerprints'].get('REMOTE') for w in worlds}
    if len(initial_snapshots)!=1 or None in initial_snapshots or len(initial_decisions)!=1 or None in initial_decisions:
        raise RuntimeError('B12_PRE_OBSERVATION_HIDDEN_WORLD_LEAK')
    later_decisions={baseline[w]['policy_fingerprints'].get('PUBLICATION') for w in worlds}
    later_snapshots={baseline[w]['snapshot_fingerprints'].get('PUBLICATION') for w in worlds}
    if len(later_decisions)<2 or len(later_snapshots)<2:
        raise RuntimeError('B12_NO_POST_OBSERVATION_EPISTEMIC_DIVERGENCE')
    stream={}
    for world in worlds:
        policy=cases.get('POLICY_SEED_ONLY:'+world,{}).get('witness')
        world_seed=cases.get('WORLD_SEED_ONLY:'+world,{}).get('witness')
        if policy is None or world_seed is None:raise RuntimeError('B10_SEED_CASE_MISSING:'+world)
        if policy['draws']!=baseline[world]['draws']:
            raise RuntimeError('B10_POLICY_SEED_CHANGED_WORLD_STREAM:'+world)
        if (world_seed['snapshot_fingerprints'].get('REMOTE')!=baseline[world]['snapshot_fingerprints'].get('REMOTE') or
            world_seed['policy_fingerprints'].get('REMOTE')!=baseline[world]['policy_fingerprints'].get('REMOTE')):
            raise RuntimeError('B10_WORLD_SEED_LEAKED_BEFORE_OBSERVATION:'+world)
        if world_seed['draws']==baseline[world]['draws']:
            raise RuntimeError('B10_WORLD_SEED_DID_NOT_CONTROL_WORLD_STREAM:'+world)
        stream[world]={'common_draws_across_worlds':'PASS',
            'policy_seed_preserved_world_stream':'PASS',
            'world_seed_preserved_pre_observation_agent':'PASS',
            'world_seed_changed_world_stream':'PASS'}
    return {'world_stream_common_before_observation':'PASS',
        'pre_observation_snapshots_and_decisions_identical':'PASS',
        'post_observation_decisions_and_snapshots_diverge':'PASS',
        'per_world_seed_independence':stream}


def qualify_concurrent_fresh_run(*,admin,database,service_file,named,source_row):
    """Run two identical RICH kernels concurrently against one fresh run ID."""
    probe,_=make_kernel('RICH',source_row=source_row)
    if not probe.boundary_manifest.run_id:raise RuntimeError('B32_RUN_ID_MISSING')
    agent_logins,agent_services=provision_agent_logins(admin,database,service_file,
        probe.boundary_manifest.run_id)
    def execute_one():
        kernel,history=run_case('RICH',wa_service='runtime',named_binding=named['binding'],
            agent_logins=agent_logins,source_row=source_row)
        return kernel,history,witness(kernel,history)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(execute_one) for _ in range(2)]
        left,right=(future.result(timeout=600) for future in futures)
    if left[2]!=right[2]:raise RuntimeError('B32_CONCURRENT_SAME_RUN_RESULT_DIVERGENCE')
    if not all(status in ('COMMITTED','ALREADY_MATCHED')
        for _,history,_ in (left,right) for _,status in history.get('epoch_commits',())):
        raise RuntimeError('B32_CONCURRENT_SAME_RUN_COMMIT_STATUS')
    if left[0].state.projects['P'].status!='OPERATING' or left[2]['sale_count']!=1:
        raise RuntimeError('B32_CONCURRENT_POSITIVE_RUN_WITNESS')
    projection=audit_persisted_case('auditor',probe.boundary_manifest.run_id,minimum_loops=1)
    snapshots={obj['agent_id'] for ref,(kind,_) in left[0].causal_artifacts.items()
        if kind=='DECISION_STATE' for obj in _walk_typed(_artifact_payload(left[0],ref))
        if obj.get('__type__')=='DecisionSnapshot'}
    isolation=audit_agent_isolation(agent_services,expected_snapshot_actors=snapshots)
    if projection['causal_envelopes']!=len(left[0].causal_envelopes):
        raise RuntimeError('B32_DUPLICATE_OR_MISSING_CAUSAL_PREFIX')
    return {'run_id':probe.boundary_manifest.run_id,'worker_witnesses_equal':True,
        'single_committed_prefix_envelopes':projection['causal_envelopes'],
        'closed_epistemic_loops':projection['closed_epistemic_loops'],
        'agent_isolation':isolation,'status':'PASS'}


def qualify_fault_reconstructed_retry(*,world,case_name,fault_kind,admin,database,
                                      service_file,named,source_row):
    """Inject one rollback or lost-ack fault, then require a fresh-kernel replay."""
    import psycopg
    import build6e_fixture
    original_persist=store.persist_epoch
    original_builder=build6e_fixture.make_kernel
    fault={'injected':False};kernels=[]
    def tracked_builder(*args,**kwargs):
        result=original_builder(*args,**kwargs);kernels.append(result[0]);return result
    def inject(*args,**kwargs):
        if not fault['injected'] and fault_kind=='BEFORE_COMMIT':
            fault['injected']=True
            raise psycopg.errors.SerializationFailure('qualification-only precommit serialization fault')
        result=original_persist(*args,**kwargs)
        if not fault['injected'] and fault_kind=='AFTER_COMMIT':
            fault['injected']=True
            raise psycopg.errors.ConnectionFailure('qualification-only lost commit acknowledgement')
        return result
    store.persist_epoch=inject
    build6e_fixture.make_kernel=tracked_builder
    try:
        kernel,history,attempts,agent_services,agent_logins,retry_evidence=run_full_case(
            world,case_name,admin=admin,database=database,service_file=service_file,
            named=named,source_row=source_row,retries=3)
    finally:
        store.persist_epoch=original_persist
        build6e_fixture.make_kernel=original_builder
    if not fault['injected'] or attempts!=2 or len(kernels)!=2 or kernels[0] is kernels[1]:
        raise RuntimeError('B30_B31_RETRY_DID_NOT_RECONSTRUCT_FRESH_KERNEL')
    state=retry_evidence[0].get('sqlstate') if retry_evidence else None
    expected='40001' if fault_kind=='BEFORE_COMMIT' else '08006'
    if state!=expected:raise RuntimeError('B30_B31_TRANSIENT_STATE_NOT_RECORDED:'+str(state))
    data=witness(kernel,history);assertions=validate_case_witness(case_name,world,data)
    projection=audit_persisted_case('auditor',kernel.boundary_manifest.run_id,minimum_loops=1)
    if projection['causal_envelopes']!=len(kernel.causal_envelopes):
        raise RuntimeError('B30_B31_RETRY_DUPLICATED_OR_LOST_PREFIX')
    return {'status':'PASS','fault_kind':fault_kind,'sqlstate':state,
        'attempts':attempts,'fresh_kernel_reconstructed':True,
        'retry_evidence':retry_evidence,'witness':data,
        'assertions':assertions,'world_authority_projection':projection}


def qualify_independent_database_export(*,primary_admin,secondary_admin,
        primary_service_file,primary_binding,source_row,output_dir):
    """Execute the same full RICH case in two independent WA PostgreSQL clones."""
    output_dir.mkdir(parents=True,exist_ok=True)
    primary_service_file=Path(primary_service_file)
    primary_service_path=os.environ.get('PGSERVICEFILE',str(primary_service_file))
    second_db,second_service_file,_=provision_runtime_database(secondary_admin,output_dir)
    second_authority=authority_preflight(secondary_admin,second_db,SOURCE_SHA)
    second_prepared={}
    with connect('science_writer') as sw,connect('science_governor') as sg,\
         connect('reference_reader') as rr,connect('world_writer') as ww:
        # The current PGSERVICEFILE is reset to the second clone by provisioning.
        second_prepared=prepare_named_world(science_writer=sw,science_governor=sg,
            reference_reader=rr,world_writer=ww,doc=load_manifest(),world_name='RICH')
    # The canonical run ID is independent of database and credentials.
    probe,_=make_kernel('RICH',source_row=source_row)
    run_id=probe.boundary_manifest.run_id
    def execute_second():
        return run_full_case('RICH','BASELINE',admin=secondary_admin,database=second_db,
            service_file=second_service_file,named={'binding':second_prepared['binding']},
            source_row=second_prepared['source'],retries=3)
    k2,h2,attempts,agent_services,agent_logins,retry=execute_second()
    if attempts!=1:raise RuntimeError('B34_SECOND_DATABASE_UNEXPECTED_RETRY')
    input_ref=probe.boundary_manifest.input_snapshot_id
    contract=probe.boundary_manifest.contract_version
    kernel_hash=source_tree_hash()
    os.environ['PGSERVICEFILE']=primary_service_path
    with connect('auditor') as first:
        export1=store.export_run(first,run_id,input_snapshot_ref=input_ref,
            code_contract=contract,code_tree_sha256=kernel_hash)
    second_services=configparser.ConfigParser(interpolation=None);second_services.read(second_service_file)
    with psycopg.connect(**dict(second_services['auditor'])) as second:
        export2=store.export_run(second,run_id,input_snapshot_ref=input_ref,
            code_contract=contract,code_tree_sha256=kernel_hash)
    os.environ['PGSERVICEFILE']=primary_service_path
    if export1!=export2:
        left=json.loads(export1);right=json.loads(export2)
        changed=[table for table in sorted(left['tables']) if left['tables'][table]!=right['tables'].get(table)]
        raise RuntimeError('B34_INDEPENDENT_DATABASE_EXPORT_DIVERGENCE:'+','.join(changed))
    p1=output_dir/'primary-private-export.json';p2=output_dir/'replica-private-export.json'
    p1.write_bytes(export1 if isinstance(export1,bytes) else export1.encode())
    p2.write_bytes(export2 if isinstance(export2,bytes) else export2.encode())
    return {'status':'PASS','run_id':run_id,'secondary_database':second_db,
        'primary_export_sha256':_digest(p1),'replica_export_sha256':_digest(p2),
        'byte_exact_exports':True,'source_rows':second_authority['forensic_rows'],
        'same_world_binding':str(primary_binding.world_id)==str(second_prepared['binding'].world_id),
        'source_admission_standing':'PRESERVED_CANDIDATE_WITH_SEPARATE_USE_ADMISSION',
        'secondary_witness':witness(k2,h2)}


def run_full_case(world: str, case_name: str, *, admin, database, service_file,
                  named, source_row, retries: int = 3):
    parameter_overrides, meta = _case_overrides(case_name)
    world_seed = meta.pop('__world_seed__', None)
    policy_seed = meta.pop('__policy_seed__', None)
    probe,_=make_kernel(world,{**parameter_overrides,**meta},world_seed=world_seed,policy_seed=policy_seed,source_row=source_row)
    agent_logins,agent_services=provision_agent_logins(admin,database,service_file,probe.boundary_manifest.run_id)
    last = None;retry_evidence=[]
    for attempt in range(retries):
        try:
            k, h = run_case(world, {**parameter_overrides, **meta},
                wa_service='runtime', named_binding=named['binding'],
                agent_logins=agent_logins,source_row=source_row,
                world_seed=world_seed, policy_seed=policy_seed)
            return k, h, attempt + 1, agent_services, agent_logins, retry_evidence
        except Exception as exc:
            last = exc
            state = getattr(exc,'sqlstate',None) or getattr(getattr(exc, 'diag', None), 'sqlstate', None)
            # Class-08 SQLSTATE and psycopg transport failures include an
            # ambiguous commit acknowledgement. The next iteration creates a
            # new kernel and replays the committed prefix; it never resumes
            # this speculative in-memory object.
            transport_failure=isinstance(exc,(ConnectionError,TimeoutError)) or (
                isinstance(state,str) and state.startswith('08'))
            retry_evidence.append({'attempt':attempt+1,'error_type':type(exc).__name__,
                'sqlstate':state,'transport_failure':transport_failure})
            if state not in TRANSIENT_STATES and not transport_failure:
                raise
            # The whole fixture/kernel is reconstructed on each attempt. No
            # speculative in-memory state survives a failed scope/acknowledgement.
    raise last


def audit_agent_isolation(agent_services: dict[str,str], *, expected_snapshot_actors=()):
    expected_snapshot_actors=set(expected_snapshot_actors)
    evidence={}
    for actor,service in sorted(agent_services.items()):
        with connect(service) as conn:
            safe=store.load_current_agent_snapshot(conn)
            denied=False
            try:conn.execute('SELECT * FROM wa_world.hidden_state LIMIT 1').fetchall()
            except psycopg.Error:denied=True
        if not denied:raise RuntimeError('B13_AGENT_HIDDEN_WORLD_QUERY_NOT_DENIED:'+actor)
        if actor in expected_snapshot_actors and safe is None:
            raise RuntimeError('B13_AUTHORIZED_AGENT_SNAPSHOT_MISSING:'+actor)
        if actor not in expected_snapshot_actors and safe is not None:
            raise RuntimeError('B13_UNEXPECTED_AGENT_SNAPSHOT:'+actor)
        if safe is not None:
            if safe['actor_id']!=actor:raise RuntimeError('B13_AGENT_PRINCIPAL_CROSSING:'+actor)
            payload=json.loads(safe['original_snapshot_bytes'])
            snapshot_fields=set(payload.get('fields',{}))
            allowed={'agent_id','agent_kind','node_id','period_key','effective_time',
                'account_balance','capabilities','objectives','information_refs','beliefs',
                'priors','asset_refs','resource_holdings','claim_holdings','admitted_facts'}
            if not snapshot_fields or not snapshot_fields<=allowed:
                raise RuntimeError('B13_AGENT_SAFE_SNAPSHOT_FIELD_LEAK:'+actor)
        evidence[actor]={'safe_current_snapshot_present':safe is not None,
            'hidden_world_query_denied':denied,
            'login_bound_actor_matches':safe is not None and safe['actor_id']==actor,
            'worker_snapshot_allowlist_pass':safe is not None and snapshot_fields<=allowed if safe is not None else False}
    return {'agents':evidence,'agent_database_connection_supplied_to_worker':False}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--admin-services-json', type=Path, required=True)
    ap.add_argument('--dependency-evidence', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--world-authority-db-index', type=int, default=0)
    ap.add_argument('--focused', action='store_true', help='run one BASELINE per world plus exact repeat')
    args = ap.parse_args()
    if args.output.exists():
        raise SystemExit('output path must not exist')
    args.output.mkdir(parents=True)
    admin_rows = json.loads(args.admin_services_json.read_text())
    if args.world_authority_db_index not in (0, 1):
        raise SystemExit('invalid qualified dependency index')
    admin = admin_rows[args.world_authority_db_index]
    protocol = json.loads(PROTOCOL_PATH.read_text())
    doc = load_manifest()
    dependency = json.loads(args.dependency_evidence.read_text())
    # V1.2 is the live authority standing; its sealed report separately records
    # the inherited migration standing. Accept both identities from the same
    # machine evidence rather than treating the inherited V1 label as the
    # current World Authority version.
    if (dependency.get('status') != 'PASS'
            or dependency.get('standing') != DEPENDENCY_STANDING
            or dependency.get('inherited_standing') != 'MIGRATION_QUALIFIED_SCIENCE_CANDIDATE_PRESERVED'
            or dependency.get('source_sha256') != SOURCE_SHA
            or dependency.get('forensic_rows') != 2726
            or dependency.get('source_columns') != 256
            or dependency.get('store_regressions_passed') is not True
            or dependency.get('skipped') != []):
        raise RuntimeError('BLOCKED_WORLD_AUTHORITY_QUALIFICATION_EVIDENCE')
    if (protocol.get('schema')!='BUILD6E_QUALIFICATION_V2'
            or protocol.get('designation')!='BUILD6E_NAMED_WORLD_FULL_V2'
            or protocol.get('supersedes')!='BUILD6E_QUALIFICATION_V1'
            or protocol['world_authority_version_required'] != DEPENDENCY_STANDING
            or protocol['world_authority_main_sha_required'] != '5daa0228ac474bd02de375373456c1d86fe56e2d'):
        raise RuntimeError('BLOCKED_WORLD_AUTHORITY_VERSION_PIN')
    source_path = Path('/home/ubuntu/LOOM_WORLD_SCIENCE_DOC/simulation/offworld_mvp/world_science/lab_v0_1/LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3')
    if _digest(source_path) != SOURCE_SHA:
        raise RuntimeError('BLOCKED_SOURCE_SNAPSHOT_HASH')
    database, service_file, logins = provision_runtime_database(admin, args.output)
    authority = authority_preflight(admin, database, doc['accepted_source']['sqlite_sha256'])
    results = {'status': 'IN_PROGRESS', 'standing': 'BUILD6E_UNQUALIFIED',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'kernel_sha256': source_tree_hash(), 'dependency_evidence_sha256': _digest(args.dependency_evidence),
        'dependency_standing': dependency['standing'], 'authority': authority,
        'qualification_protocol': {'schema':protocol['schema'],'designation':protocol['designation'],
            'sha256':_digest(PROTOCOL_PATH),'governed_corrections':protocol['governed_corrections']},
        'service_roles': logins, 'service_file': str(service_file),
        'inputs': {str(p.relative_to(ROOT)): _digest(p) for p in
            (PROTOCOL_PATH, BASE/'inputs/BUILD6E_NAMED_WORLD_V1.json',
             BASE/'inputs/BUILD6E_EARTH_REFERENCE_SLICE_V1.json')},
        'cases': {}, 'bootstrap': {}, 'security': {}, 'failures': []}
    _json_write(args.output/'BUILD6E_QUALIFICATION.json', results)
    try:
        results['prior_missing']=qualify_prior_missing_behavior()
        results['transaction_surface']=qualify_run_epoch_surface('auditor')
        _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
        prepared_by_world = {}
        with connect('science_writer') as sw, connect('science_governor') as sg, \
             connect('reference_reader') as rr, connect('world_writer') as ww:
            results['science_candidate_without_admission']=qualify_candidate_invisibility(rr,doc)
            for world in protocol['worlds']:
                prepared = prepare_named_world(science_writer=sw,
                    science_governor=sg, reference_reader=rr, world_writer=ww,
                    doc=doc, world_name=world)
                prepared_by_world[world] = prepared
                results['bootstrap'][world] = {
                    'metadata': prepared['metadata_status'],
                    'scoped_admission': prepared['admission_status'],
                    'world': prepared['world_status'],
                    'catalog_kind': prepared['parent']['location_kind'],
                    'catalog_origin': prepared['parent']['origin_kind'],
                    'source_scope': prepared['source']['scope_kind'],
                    'source_initial_standing': prepared['source']['initial_standing'],
                    'source_use_standing': prepared['source']['standing'],
                    'source_artifact_sha256': prepared['source']['source_byte_sha256'],
                    'source_artifact_custody': prepared['source']['custody_kind'],
                    'binding': str(prepared['binding'].world_id)}
            results['science_cutoff_controls']=qualify_science_cutoff_controls(
                reference_reader=rr,science_writer=sw,science_governor=sg,
                auditor_service='auditor',doc=doc,
                prepared_source=prepared_by_world['RICH']['source'])
            authority_after = authority_preflight_after_bootstrap(admin, database)
            results['authority_after_bootstrap'] = authority_after
        results['concurrent_same_run']=qualify_concurrent_fresh_run(
            admin=admin,database=database,service_file=service_file,
            named={'binding':prepared_by_world['RICH']['binding']},
            source_row=prepared_by_world['RICH']['source'])
        secondary_admin=admin_rows[1-args.world_authority_db_index]
        results['independent_database_export']=qualify_independent_database_export(
            primary_admin=admin,secondary_admin=secondary_admin,
            primary_service_file=service_file,
            primary_binding=prepared_by_world['RICH']['binding'],
            source_row=prepared_by_world['RICH']['source'],
            output_dir=args.output/'independent-replay')
        results['crash_before_commit']=qualify_fault_reconstructed_retry(
            world='SPARSE',case_name='POLICY_SEED_ONLY',fault_kind='BEFORE_COMMIT',
            admin=admin,database=database,service_file=service_file,
            named={'binding':prepared_by_world['SPARSE']['binding']},
            source_row=prepared_by_world['SPARSE']['source'])
        results['crash_after_commit_before_ack']=qualify_fault_reconstructed_retry(
            world='NULL',case_name='WORLD_SEED_ONLY',fault_kind='AFTER_COMMIT',
            admin=admin,database=database,service_file=service_file,
            named={'binding':prepared_by_world['NULL']['binding']},
            source_row=prepared_by_world['NULL']['source'])
        _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
        case_names = ['BASELINE'] if args.focused else list(dict.fromkeys((*protocol['baseline_cases'], *protocol['triplet_cases'])))
        for case_name in case_names:
            for world in protocol['worlds']:
                prepared = prepared_by_world[world]
                named = {'binding': prepared['binding']}
                try:
                    k,h,attempts,agent_services,agent_logins,retry_evidence=run_full_case(world,case_name,
                        admin=admin,database=database,service_file=service_file,named=named,
                        source_row=prepared['source'], retries=3)
                    data=witness(k,h)
                    expected=protocol['expected_positive_witness'][world]
                    snapshot_actors={obj['agent_id'] for ref,(kind,_) in k.causal_artifacts.items()
                        if kind=='DECISION_STATE' for obj in _walk_typed(_artifact_payload(k,ref))
                        if obj.get('__type__')=='DecisionSnapshot'}
                    isolation=audit_agent_isolation(agent_services,
                        expected_snapshot_actors=snapshot_actors)
                    results.setdefault('security',{})[case_name+':'+world]=isolation
                    results.setdefault('agent_logins',{})[case_name+':'+world]=agent_logins
                    assertion_evidence=validate_case_witness(case_name,world,data)
                    projection_evidence=audit_persisted_case('auditor',
                        k.boundary_manifest.run_id,
                        minimum_loops=1 if data['remote'] is not None else 0)
                    results['cases'][case_name+':'+world]={'status':'EXECUTED_NOT_YET_ACCEPTED',
                        'attempts':attempts,'retry_evidence':retry_evidence,'witness':data,
                        'assertions':assertion_evidence,'world_authority_projection':projection_evidence,
                        'committed_epochs':len(h.get('epoch_commits',[])),
                        'commit_statuses':h.get('epoch_commits',[])}
                    _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
                    if case_name=='BASELINE':
                        if data['status']!=expected['project_status'] or data['sale_count']!=expected['sale_count']:
                            raise RuntimeError('B_BASELINE_POSITIVE_WITNESS_MISMATCH:'+world)
                        if data['people']!=expected['settlement_population']:
                            raise RuntimeError('B25_NAMED_SETTLEMENT_POPULATION_MISMATCH:'+world)
                        validate_trace(k.causal_envelopes,k.causal_artifacts)
                    results['cases'][case_name+':'+world]={'status':'PASS','attempts':attempts,
                        'retry_evidence':retry_evidence,'witness':data,'assertions':assertion_evidence,
                        'world_authority_projection':projection_evidence,
                        'committed_epochs':len(h.get('epoch_commits',[])),
                        'commit_statuses':h.get('epoch_commits',[])}
                except Exception as exc:
                    prior=results['cases'].get(case_name+':'+world,{})
                    results['cases'][case_name+':'+world]={**prior,'status':'FAIL','error':str(exc),
                        'traceback':traceback.format_exc()}
                    raise
                _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
        if args.focused:
            results['status']='PARTIAL_PASS'
        else:
            expected_keys={name+':'+world for name in case_names for world in protocol['worlds']}
            observed_keys=set(results['cases'])
            if observed_keys!=expected_keys:
                raise RuntimeError('B43_CASE_TUPLE_COVERAGE:'+repr(sorted(expected_keys-observed_keys)))
            results['comparison_evidence']=validate_comparison_runs(results['cases'])
            results['status']='FAIL_INCOMPLETE_REQUIRED_CASES'
            results['failures'].append('single-case, B01-B45 hostile, crash/concurrency, export, and exact historical/successor regression gates remain incomplete')
    except Exception as exc:
        results['failures'].append({'error':str(exc),'traceback':traceback.format_exc()})
        results['status']='FAIL'
    results['completed_utc']=datetime.now(timezone.utc).isoformat()
    _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
    print(results['status'], args.output/'BUILD6E_QUALIFICATION.json')
    return 0 if results['status']=='PASS' else 1


def authority_preflight_after_bootstrap(admin_config, database):
    cfg={k:admin_config[k] for k in ('host','port','user','password')};cfg['dbname']=database
    with psycopg.connect(**cfg,autocommit=True) as conn:
        rows=conn.execute("SELECT a.initial_standing,d.standing,d.use_contract_ref,count(*) FROM wa_science.assertion a JOIN wa_science.admission d ON d.target_assertion_id=a.assertion_id WHERE a.semantic_key='R_MOON_CAB_WATER' GROUP BY 1,2,3").fetchall()
        parent=conn.execute("SELECT location_kind,origin_kind,original_region_type FROM wa_geo.location WHERE semantic_key='CABEU'").fetchone()
        return {'fixture_admission_rows':rows,'cabeus':parent}


if __name__ == '__main__':
    raise SystemExit(main())
