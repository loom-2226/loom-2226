#!/usr/bin/env python3
"""Designated Build 6E full named-world qualification driver.

The database is a disposable clone of the qualified World Authority snapshot.
World Authority store APIs own all application reads/writes; SQL in this file
is limited to isolated test-database provisioning and hostile role assertions.
"""
from __future__ import annotations

import argparse
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
from build6e_fixture import run_case
from named_world import load_manifest, prepare_named_world

BASE = ROOT / 'simulation/offworld_mvp/build6e'
PROTOCOL_PATH = BASE / 'inputs/BUILD6E_QUALIFICATION_V1.json'
DEPENDENCY_STANDING = 'WORLD_AUTHORITY_V1_2_RUN_TRANSACTIONS_QUALIFIED'
TRANSIENT_STATES = ('40001', '40P01')


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
    if name == 'HABITAT_LOW': return {}, {'habitat_capacity': '0'}
    if name == 'TRANSPORT_MISSING': return {}, {'relationship_registered': 'FALSE'}
    if name == 'POLICY_SEED_ONLY': return {}, {'__policy_seed__': 'B6E-POLICY-ISOLATION-20261006'}
    if name == 'WORLD_SEED_ONLY': return {}, {'__world_seed__': '20261006'}
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
        'trace_root': trace, 'envelope_count': len(kernel.causal_envelopes),
        'artifact_count': len(kernel.causal_artifacts),
        'policy_outcomes': {label:result.decision.outcome.value for label,result in history['policies'].items()},
        'policy_fingerprints': {label:content_hash(result.decision) for label,result in history['policies'].items()},
        'snapshot_fingerprints': {label:s.fingerprint() for label,s in history['snapshots'].items()}}


def run_full_case(world: str, case_name: str, *, services, named, source_row,
                  retries: int = 3):
    parameter_overrides, meta = _case_overrides(case_name)
    world_seed = meta.pop('__world_seed__', None)
    policy_seed = meta.pop('__policy_seed__', None)
    last = None
    for attempt in range(retries):
        try:
            k, h = run_case(world, {**parameter_overrides, **meta},
                wa_service='runtime', named_binding=named['binding'],
                source_row=source_row, world_seed=world_seed, policy_seed=policy_seed)
            return k, h, attempt + 1
        except Exception as exc:
            last = exc
            state = getattr(getattr(exc, 'diag', None), 'sqlstate', None)
            if state not in TRANSIENT_STATES and not isinstance(exc, (ConnectionError, TimeoutError)):
                raise
            # The whole fixture/kernel is reconstructed on each attempt. No
            # speculative in-memory state survives a failed scope/acknowledgement.
    raise last


def audit_agent_isolation():
    with connect('agent_reader') as conn:
        safe = store.load_current_agent_snapshot(conn)
        denied = False
        try:
            conn.execute('SELECT * FROM wa_world.hidden_state LIMIT 1').fetchall()
        except psycopg.Error:
            denied = True
    if not denied:
        raise RuntimeError('B13_AGENT_HIDDEN_WORLD_QUERY_NOT_DENIED')
    return {'safe_current_snapshot': safe, 'hidden_world_query_denied': denied,
            'agent_database_connection_supplied_to_worker': False}


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
    if dependency.get('status') != 'PASS' or dependency.get('standing') != 'MIGRATION_QUALIFIED_SCIENCE_CANDIDATE_PRESERVED':
        raise RuntimeError('BLOCKED_WORLD_AUTHORITY_QUALIFICATION_EVIDENCE')
    if protocol['world_authority_version_required'] != DEPENDENCY_STANDING or protocol['world_authority_main_sha_required'] != '5daa0228ac474bd02de375373456c1d86fe56e2d':
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
        'service_roles': logins, 'service_file': str(service_file),
        'inputs': {str(p.relative_to(ROOT)): _digest(p) for p in
            (PROTOCOL_PATH, BASE/'inputs/BUILD6E_NAMED_WORLD_V1.json',
             BASE/'inputs/BUILD6E_EARTH_REFERENCE_SLICE_V1.json')},
        'cases': {}, 'bootstrap': {}, 'security': {}, 'failures': []}
    _json_write(args.output/'BUILD6E_QUALIFICATION.json', results)
    try:
        prepared_by_world = {}
        with connect('science_writer') as sw, connect('science_governor') as sg, \
             connect('reference_reader') as rr, connect('world_writer') as ww:
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
            authority_after = authority_preflight_after_bootstrap(admin, database)
            results['authority_after_bootstrap'] = authority_after
        case_names = ['BASELINE'] if args.focused else list(dict.fromkeys((*protocol['baseline_cases'], *protocol['triplet_cases'])))
        for case_name in case_names:
            for world in protocol['worlds']:
                prepared = prepared_by_world[world]
                named = {'binding': prepared['binding']}
                try:
                    k,h,attempts=run_full_case(world,case_name,services=None,named=named,
                        source_row=prepared['source'], retries=3)
                    data=witness(k,h)
                    expected=protocol['expected_positive_witness'][world]
                    if case_name=='BASELINE':
                        if data['status']!=expected['project_status'] or data['sale_count']!=expected['sale_count']:
                            raise RuntimeError('B_BASELINE_POSITIVE_WITNESS_MISMATCH:'+world)
                        if data['people']!=expected['settlement_population']:
                            raise RuntimeError('B25_NAMED_SETTLEMENT_POPULATION_MISMATCH:'+world)
                        validate_trace(k.causal_envelopes,k.causal_artifacts)
                    results['cases'][case_name+':'+world]={'status':'PASS','attempts':attempts,
                        'witness':data,'committed_epochs':len(h.get('epoch_commits',[])),
                        'commit_statuses':h.get('epoch_commits',[])}
                except Exception as exc:
                    results['cases'][case_name+':'+world]={'status':'FAIL','error':str(exc),
                        'traceback':traceback.format_exc()}
                    raise
                _json_write(args.output/'BUILD6E_QUALIFICATION.json',results)
        results['security']=audit_agent_isolation()
        results['status']='PARTIAL_PASS' if args.focused else 'FAIL_INCOMPLETE_REQUIRED_CASES'
        results['failures'].append('B01-B45 projection/security/crash/hostile matrix remains incomplete')
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
