"""Neutral PostgreSQL access primitives for LOOM World Authority.

No Offworld imports. No caller-built SQL. No dynamic registries.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import uuid
from typing import Iterable, Sequence

WORLD_AUTHORITY_VERSION = "LOOM_WORLD_AUTHORITY_V1"
UUID_NAMESPACE = uuid.UUID("fc7bc6cd-f41f-5293-ab79-312760b5cedc")

class WorldAuthorityError(RuntimeError): pass
class IntegrityFailure(WorldAuthorityError): pass
class CollisionFailure(IntegrityFailure): pass
class RoleViolation(WorldAuthorityError): pass

def _lp_utf8(value: str) -> bytes:
    if not isinstance(value, str): raise TypeError("length-prefixed values must be str")
    raw=value.encode("utf-8")
    return str(len(raw)).encode("ascii") + b":" + raw

def length_prefixed(*values: str) -> bytes:
    return b"".join(_lp_utf8(v) for v in values)

def stable_uuid(kind: str, authority: str, semantic_key: str, revision: str) -> uuid.UUID:
    # UUIDv5 semantics over the exact byte-length-prefixed four-string profile.
    name=length_prefixed(kind, authority, semantic_key, revision)
    # RFC 4122 UUIDv5 hashes namespace bytes plus the UTF-8 name bytes.
    digest=hashlib.sha1(UUID_NAMESPACE.bytes+name).digest()
    raw=bytearray(digest[:16]); raw[6]=(raw[6]&0x0F)|0x50; raw[8]=(raw[8]&0x3F)|0x80
    return uuid.UUID(bytes=bytes(raw))

def sha256_bytes(value: bytes) -> str:
    if not isinstance(value, (bytes, bytearray, memoryview)): raise TypeError("bytes required")
    return hashlib.sha256(bytes(value)).hexdigest()

def require_sha256(value: str) -> str:
    if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
        raise IntegrityFailure("expected lowercase SHA-256 hex")
    return value

@dataclass(frozen=True)
class ServiceRoute:
    name: str
    expected_role: str

SERVICE_ROUTES={
 "science_writer":ServiceRoute("science_writer","wa_science_writer"),
 "science_governor":ServiceRoute("science_governor","wa_science_governor"),
 "world_writer":ServiceRoute("world_writer","wa_world_writer"),
 "runtime_writer":ServiceRoute("runtime_writer","wa_runtime_writer"),
 "admission_writer":ServiceRoute("admission_writer","wa_admission_writer"),
 "reference_reader":ServiceRoute("reference_reader","wa_reference_reader"),
 "auditor":ServiceRoute("auditor","wa_auditor"),
 "agent_reader":ServiceRoute("agent_reader","wa_agent_reader"),
}

def assert_service_role(conn, route: ServiceRoute) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT current_user")
        got=cur.fetchone()[0]
    if got != route.expected_role:
        raise RoleViolation(f"service {route.name} requires {route.expected_role}, got {got}")

def serializable(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")

def _fetch_one_fixed(conn, sql: str, params: Sequence[object]):
    # Internal-only helper: callers of the public module never supply SQL.
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row=cur.fetchone()
        if cur.fetchone() is not None: raise IntegrityFailure("expected at most one row")
        return row

# Closed import tables/PKs; never accept names discovered from caller SQL.
TABLE_KEYS={
 'wa_meta.source_snapshot':('snapshot_id',), 'wa_meta.legacy_row':('snapshot_id','table_name','source_key'),
 'wa_meta.unit':('unit_key',),'wa_geo.time_support':('time_id',),'wa_geo.vertical_support':('vertical_id',),
 'wa_geo.body':('body_id',),'wa_geo.body_identifier':('body_id','authority','identifier_type','identifier_value'),
 'wa_geo.location':('location_id',),'wa_geo.location_relation':('from_location_id','to_location_id','relation_kind'),
 'wa_science.source':('source_id',),'wa_science.source_artifact':('artifact_id',),'wa_science.sample':('sample_id',),
 'wa_science.support':('support_id',),'wa_science.spatial_product':('product_id',),'wa_science.observation':('observation_id',),
 'wa_science.assertion':('assertion_id',),'wa_science.material_evidence':('evidence_id',),'wa_science.coverage':('coverage_id',),
 'wa_science.reconciliation':('reconciliation_id',),'wa_nav.product':('product_id',),'wa_nav.coverage':('product_id','body_id','coverage_key'),
}


def _table_identifier(table):
    from psycopg import sql
    if table not in TABLE_KEYS:raise IntegrityFailure('UNDECLARED_IMPORT_TABLE')
    return sql.Identifier(*table.split('.'))


def _values(row):
    from psycopg.types.json import Jsonb
    return [Jsonb(v) if isinstance(v,dict) else v for v in row.values.values()]


def _insert_row(conn,row):
    from psycopg import sql
    checks={'wa_science.assertion':('metadata_bytes','metadata_sha256'),'wa_run.artifact':('payload_bytes','payload_sha256'),'wa_run.causal_envelope':('original_envelope_bytes','original_envelope_sha256'),'wa_info.agent_snapshot':('original_snapshot_bytes','original_snapshot_sha256'),'wa_world.generation_policy':('policy_bytes','policy_sha256')}
    if row.table in checks:
        payload,sha=checks[row.table];verify_original_bytes(row.values[payload],row.values[sha])
    q=sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(_table_identifier(row.table),sql.SQL(',').join(map(sql.Identifier,row.values)),sql.SQL(',').join(sql.Placeholder() for _ in row.values))
    conn.execute(q,_values(row))


def verify_source_projection(conn,plan):
    """Verify every planned typed cell and every preserved raw cell, not counts alone."""
    from psycopg import sql
    for table in TABLE_KEYS:
        planned=[r for r in plan.rows if r.table==table]
        if not planned:continue
        columns=tuple(planned[0].values)
        if any(tuple(r.values)!=columns for r in planned):raise IntegrityFailure('INCONSISTENT_COLUMN_PROFILE')
        q=sql.SQL('SELECT {} FROM {}').format(sql.SQL(',').join(map(sql.Identifier,columns)),_table_identifier(table))
        got=conn.execute(q).fetchall();keys=TABLE_KEYS[table];ix=[columns.index(k) for k in keys]
        actual={tuple(row[i] for i in ix):row for row in got}
        for r in planned:
            k=tuple(r.values[n] for n in keys)
            if k not in actual or any(a!=b for a,b in zip(actual[k],r.values.values(),strict=True)):raise CollisionFailure('IMPORT_COLLISION:'+table+':'+str(k))
        # The source-scoped closure must contain no unexpected raw/scientific rows.
        if table=='wa_meta.legacy_row':
            if sum(row[columns.index('snapshot_id')]==plan.snapshot_id for row in got)!=len(planned):raise CollisionFailure('UNEXPECTED_SOURCE_MEMBERS')
    if conn.execute('SELECT count(*) FROM wa_meta.legacy_row WHERE snapshot_id=%s',(plan.snapshot_id,)).fetchone()[0]!=2726:raise IntegrityFailure('FORENSIC_ROW_COUNT')
    return {'source_rows':2726,'source_columns':256,'planned_target_rows':len(plan.rows),'plan_sha256':plan.plan_hash}


def import_exact_snapshot(conn,plan,*,failure_after_table=None,commit_ack_failure=False):
    """One source transaction; repeat is read+match, never upsert or partial repair.

    Fault-injection arguments are deterministic qualification seams, not recovery
    actions; they never disable constraints or mutate input.
    """
    import hashlib
    from .etl import SOURCE_SHA
    from psycopg.errors import SerializationFailure,DeadlockDetected
    if conn.info.transaction_status.value!=0:raise IntegrityFailure('IMPORT_REQUIRES_IDLE_CONNECTION')
    lock=int.from_bytes(hashlib.sha256(('WORLD_AUTHORITY_ETL_V1:'+SOURCE_SHA).encode()).digest()[:8],'big',signed=True)
    for attempt in range(3):
        try:
            with conn.transaction():
                serializable(conn)
                conn.execute('SET LOCAL ROLE wa_science_writer')
                assert_service_role(conn,SERVICE_ROUTES['science_writer'])
                conn.execute('SET LOCAL search_path=pg_catalog')
                conn.execute('SELECT pg_advisory_xact_lock(%s)',(lock,))
                present=conn.execute('SELECT count(*) FROM wa_meta.source_snapshot WHERE snapshot_id=%s',(plan.snapshot_id,)).fetchone()[0]
                if present:
                    verify_source_projection(conn,plan);status='ALREADY_MATCHED'
                else:
                    previous=None
                    for r in plan.rows:
                        if previous and previous!=r.table and failure_after_table==previous:raise IntegrityFailure('QUALIFICATION_INJECTED_FAILURE:'+previous)
                        _insert_row(conn,r);previous=r.table
                    if failure_after_table==previous:raise IntegrityFailure('QUALIFICATION_INJECTED_FAILURE:'+previous)
                    conn.execute('SET CONSTRAINTS ALL IMMEDIATE');verify_source_projection(conn,plan);status='IMPORTED'
                if hashlib.sha256(plan.source_file.read_bytes()).hexdigest()!=SOURCE_SHA:raise IntegrityFailure('SOURCE_CHANGED_DURING_IMPORT')
            if commit_ack_failure:raise ConnectionError('QUALIFICATION_LOST_COMMIT_ACK')
            return status
        except (SerializationFailure,DeadlockDetected):
            if attempt==2:raise
    raise IntegrityFailure('TRANSACTION_RETRY_EXHAUSTED')


def export_source(conn,plan,directory):
    """Canonical logical scientific export with original full source membership."""
    from pathlib import Path
    from psycopg import sql
    from .etl import canonical
    p=Path(directory);p.mkdir(parents=True,exist_ok=True);manifest=[]
    with conn.transaction():
        conn.execute('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ ONLY')
        verify_source_projection(conn,plan)
        for table,keys in TABLE_KEYS.items():
            planned=[r for r in plan.rows if r.table==table]
            if not planned:continue
            cols=tuple(planned[0].values);out=[]
            types=dict(conn.execute('SELECT attname,format_type(atttypid,atttypmod) FROM pg_attribute WHERE attrelid=%s::regclass AND attnum>0 AND NOT attisdropped',(table,)).fetchall())
            for r in planned:
                q=sql.SQL('SELECT {} FROM {} WHERE {}').format(sql.SQL(',').join(map(sql.Identifier,cols)),_table_identifier(table),sql.SQL(' AND ').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in keys))
                record=conn.execute(q,[r.values[k] for k in keys]).fetchone()
                out.append((tuple(r.values[k] for k in keys),{k:{'sql_type':types[k],'value':v} for k,v in zip(cols,record)}))
            out.sort(key=lambda r:canonical(r[0]))
            data=canonical({'profile':'WA_LOGICAL_EXPORT_V1','table':table,'columns':cols})+b'\n'+b''.join(canonical(r)+b'\n' for _,r in out)
            name=table+'.jsonl';(p/name).write_bytes(data);manifest.append({'path':name,'bytes':len(data),'sha256':sha256_bytes(data),'rows':len(out)})
    m={'profile':'WA_LOGICAL_EXPORT_V1','source_sha256':plan.source_sha256,'plan_sha256':plan.plan_hash,'files':manifest}
    (p/'manifest.json').write_bytes(canonical(m)+b'\n');return m


def verify_original_bytes(payload,expected_hash):
    """Neutral original-byte integrity; never a consumer fingerprint algorithm."""
    require_sha256(expected_hash)
    if sha256_bytes(payload)!=expected_hash:raise IntegrityFailure('ORIGINAL_BYTES_MISMATCH')
    return bytes(payload)


def _require_session_group(conn,group):
    # SET ROLE does not change the authenticated principal. Group membership is
    # checked without treating superuser/owner credentials as worker credentials.
    role=conn.execute('SELECT session_user').fetchone()[0]
    allowed=conn.execute('SELECT pg_has_role(session_user,%s,\'MEMBER\')',(group,)).fetchone()[0]
    flags=conn.execute('SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=session_user').fetchone()
    if not allowed or flags[0] or flags[1]:raise RoleViolation('SERVICE_PRINCIPAL_MISMATCH:'+group)
    return role


def load_current_agent_snapshot(conn):
    """Only the login-bound safe surface. No caller actor/run/time parameters."""
    _require_session_group(conn,'wa_agent_reader')
    rows=conn.execute('SELECT actor_id,snapshot_ref,period_key,effective_time,original_snapshot_bytes FROM wa_agent_api.current_snapshot').fetchall()
    if not rows:return None
    if len(rows)!=1:raise IntegrityFailure('AMBIGUOUS_CURRENT_SNAPSHOT')
    actor,ref,period,t,payload=rows[0]
    facts=conn.execute('SELECT actor_id,snapshot_ref,fact_key,effective_time,value_state,value_lexeme,worker_source_ref FROM wa_agent_api.snapshot_facts ORDER BY fact_key COLLATE "C"').fetchall()
    if any((f[0],f[1],f[3])!=(actor,ref,t) for f in facts):raise IntegrityFailure('SAFE_SNAPSHOT_BINDING_MISMATCH')
    return dict(actor_id=actor,snapshot_ref=ref,period_key=period,effective_time=t,original_snapshot_bytes=bytes(payload),facts=tuple(facts))


def read_catalog_location(conn,body_key,location_key):
    """Trusted reference projection, never Agent knowledge/admission."""
    _require_session_group(conn,'wa_reference_reader')
    return _fetch_one_fixed(conn,'''SELECT b.body_id,b.semantic_key,b.canonical_name,b.body_class,b.original_ref,
        l.location_id,l.semantic_key,l.name,l.location_kind,l.origin_kind,l.geometry_id,l.source_ref
        FROM wa_geo.body b JOIN wa_geo.location l ON l.body_id=b.body_id
        WHERE b.semantic_key=%s AND l.semantic_key=%s''',(body_key,location_key))


def record_fixture_admission(conn,manifest):
    """One immutable use-scoped fixture decision. ETL never invokes this.

    The caller supplies a pinned neutral manifest, not scientific interpretation.
    Time metadata must already exist under the independent science-writer route.
    """
    from .etl import canonical
    from psycopg import sql
    required={'profile','assertion_id','assertion_metadata_sha256','support_id','source_snapshot_sha256','initial_standing','use_contract_ref','authorization_ref','decision_ordinal','standing','effective_availability_lexeme','time_support'}
    if set(manifest)!=required or manifest['profile']!='WA_FIXTURE_ADMISSION_MANIFEST_V1':raise IntegrityFailure('FIXTURE_MANIFEST_FIELDS')
    if manifest['standing'] not in ('ADMITTED','HOLD') or manifest['initial_standing']!='CANDIDATE':raise IntegrityFailure('FIXTURE_MANIFEST_STANDING')
    if type(manifest['decision_ordinal']) is not int or manifest['decision_ordinal']<1:raise IntegrityFailure('FIXTURE_MANIFEST_ORDINAL')
    for k in ('assertion_metadata_sha256','source_snapshot_sha256'):require_sha256(manifest[k])
    for k in ('assertion_id','support_id'):uuid.UUID(manifest[k])
    time=manifest['time_support'];columns=('kind','time_lexeme','start_lexeme','end_lexeme','calendar_ref','timescale_ref','instant_utc','interval_utc','parsing_warrant_ref')
    if set(time)!=set(columns) or time['kind']!='LEXICAL' or time['timescale_ref']!='SIM_TIME' or time['time_lexeme']!=manifest['effective_availability_lexeme'] or any(time[k] is not None for k in columns if k not in ('kind','time_lexeme','timescale_ref')):raise IntegrityFailure('FIXTURE_TIME_METADATA')
    if conn.info.transaction_status.value!=0:raise IntegrityFailure('FIXTURE_ADMISSION_REQUIRES_IDLE_CONNECTION')
    mh=sha256_bytes(canonical(manifest));ordinal=str(manifest['decision_ordinal'])
    tid=stable_uuid('TIME_SUPPORT','LOOM_WORLD_AUTHORITY_V1','BUILD6E_FIXTURE_ADMISSION:'+ordinal,mh)
    aid=stable_uuid('SCIENCE_ADMISSION','LOOM_WORLD_AUTHORITY_V1',length_prefixed(manifest['assertion_id'],manifest['use_contract_ref'],ordinal).decode(),mh)
    with conn.transaction():
        serializable(conn);_require_session_group(conn,'wa_science_governor');conn.execute('SET LOCAL ROLE wa_science_governor');assert_service_role(conn,SERVICE_ROUTES['science_governor'])
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('WA_FIXTURE_ADMISSION:'+ordinal,))
        got=conn.execute('SELECT '+','.join(columns)+' FROM wa_geo.time_support WHERE time_id=%s',(tid,)).fetchone()
        if got is None or tuple(time[k] for k in columns)!=got:raise IntegrityFailure('FIXTURE_TIME_METADATA_MISMATCH')
        a=conn.execute('''SELECT a.metadata_sha256,a.support_id,a.initial_standing,s.byte_sha256
            FROM wa_science.assertion a JOIN wa_science.source so ON so.source_id=a.source_id
            JOIN wa_meta.source_snapshot s ON s.snapshot_id=so.snapshot_id WHERE a.assertion_id=%s''',(manifest['assertion_id'],)).fetchone()
        if a!=(manifest['assertion_metadata_sha256'],uuid.UUID(manifest['support_id']),manifest['initial_standing'],manifest['source_snapshot_sha256']):raise IntegrityFailure('FIXTURE_SOURCE_PROVENANCE_MISMATCH')
        v=dict(admission_id=aid,target_assertion_id=uuid.UUID(manifest['assertion_id']),target_material_id=None,target_warrant_id=None,decision_ordinal=manifest['decision_ordinal'],standing=manifest['standing'],use_contract_ref=manifest['use_contract_ref'],authorization_ref=manifest['authorization_ref'],decision_time_id=tid,decision_sha256=mh)
        old=conn.execute('SELECT '+','.join(v)+' FROM wa_science.admission WHERE decision_ordinal=%s',(manifest['decision_ordinal'],)).fetchone()
        if old is not None:
            if old!=tuple(v.values()):raise CollisionFailure('FIXTURE_ADMISSION_COLLISION')
            return 'ALREADY_MATCHED'
        q=sql.SQL('INSERT INTO wa_science.admission ({}) VALUES ({})').format(sql.SQL(',').join(map(sql.Identifier,v)),sql.SQL(',').join(sql.Placeholder() for _ in v))
        conn.execute(q,list(v.values()))
    return 'INSERTED'

# Closed V1 SQL-column profile, qualified against the pinned migration catalog.
SQL_COLUMN_PROFILE = {
    'wa_geo.body': (('body_id', True), ('semantic_key', True), ('canonical_name', True), ('body_class', True), ('parent_body_id', False), ('status_lexeme', True), ('original_ref', False)),
    'wa_geo.body_identifier': (('body_id', True), ('authority', True), ('identifier_type', True), ('identifier_value', True), ('status_lexeme', True)),
    'wa_geo.body_system': (('system_id', True), ('semantic_key', True), ('name', True), ('authority_ref', True), ('characterization_ref', True)),
    'wa_geo.frame': (('frame_id', True), ('semantic_key', True), ('body_id', False), ('system_id', False), ('frame_kind', True), ('authority', True), ('authority_frame_id', False), ('definition_ref', True), ('definition_sha256', False), ('length_unit_key', False), ('angular_unit_key', False), ('epoch_id', False)),
    'wa_geo.geometry': (('geometry_id', True), ('body_id', False), ('system_id', False), ('frame_id', True), ('geometry_kind', True), ('encoding_ref', True), ('product_locator', False), ('product_sha256', False), ('coordinate_1', False), ('coordinate_2', False), ('coordinate_3', False), ('coordinate_semantics', True), ('coordinate_unit_key', False), ('angular_unit_key', False), ('vertical_id', False), ('epoch_id', False), ('characterization_ref', True)),
    'wa_geo.location': (('location_id', True), ('body_id', False), ('system_id', False), ('semantic_key', True), ('name', True), ('location_kind', True), ('original_region_type', False), ('origin_kind', True), ('geometry_id', False), ('source_ref', True), ('notes', False)),
    'wa_geo.location_relation': (('from_location_id', True), ('to_location_id', True), ('relation_kind', True), ('warrant_ref', True)),
    'wa_geo.system_member': (('system_id', True), ('body_id', True), ('role_lexeme', True)),
    'wa_geo.time_support': (('time_id', True), ('kind', True), ('time_lexeme', False), ('start_lexeme', False), ('end_lexeme', False), ('calendar_ref', False), ('timescale_ref', False), ('instant_utc', False), ('interval_utc', False), ('parsing_warrant_ref', False)),
    'wa_geo.vertical_support': (('vertical_id', True), ('coordinate_kind', True), ('lower_value', False), ('upper_value', False), ('unit_key', False), ('datum_ref', False), ('original_coordinate_lexeme', False)),
    'wa_info.action_authorization': (('run_id', True), ('authorization_id', True), ('decision_id', False), ('actor_id', True), ('authorization_time', True), ('rule_origin_kind', True), ('rule_ref', True), ('planned_action_ref', True)),
    'wa_info.agent_fact': (('run_id', True), ('actor_id', True), ('snapshot_ref', True), ('fact_key', True), ('receipt_id', True), ('effective_time', True), ('value_state', True), ('value_lexeme', False), ('worker_source_ref', True), ('producer_contract_ref', True), ('sanitizer_attestation_sha256', True)),
    'wa_info.agent_snapshot': (('run_id', True), ('snapshot_ref', True), ('actor_id', True), ('period_key', True), ('effective_time', True), ('effective_time_lexeme', True), ('original_snapshot_bytes', True), ('original_snapshot_sha256', True), ('original_artifact_ref', True), ('worker_fingerprint', True), ('producer_contract_ref', True), ('sanitizer_attestation_sha256', True)),
    'wa_info.belief': (('run_id', True), ('actor_id', True), ('belief_key', True), ('event_id', True), ('source_information_id', False), ('value_state', True), ('original_belief_ref', True), ('update_rule_ref', True)),
    'wa_info.consumption_request': (('run_id', True), ('request_id', True), ('consumer_id', True), ('use_ref', True), ('subject_ref', True), ('concept', True), ('scope_ref', True), ('time_basis', True), ('effective_time', True), ('knowledge_cutoff', True), ('world_context', True), ('context_id', True), ('perspective', True), ('perspective_actor_id', True), ('assertion_set', True), ('required_unit', True), ('required_role', True), ('original_artifact_ref', True)),
    'wa_info.context_value': (('run_id', True), ('value_ref', True), ('assertion_ref', True), ('subject_ref', True), ('concept', True), ('scope_ref', True), ('world_context', True), ('context_id', True), ('perspective', True), ('perspective_actor_id', True), ('value_state', True), ('value_lexeme', False), ('unit_lexeme', True), ('reason_code', True), ('proposition_kind', True), ('proposition_role', True), ('epistemic_mode', True), ('admission_state', True), ('uncertainty_state', True), ('uncertainty_ref', True), ('time_basis', True), ('valid_from', True), ('valid_to', True), ('available_from', True), ('source_time', True), ('source_refs', True), ('source_hashes', True), ('warrant_refs', True), ('support_conflict_refs', True), ('dependency_refs', True), ('transformation_ref', True), ('transformation_version', True), ('authorization_ref', True), ('reference_role', True), ('record_version', True), ('original_artifact_ref', True), ('fingerprint', True)),
    'wa_info.decision': (('run_id', True), ('decision_id', True), ('actor_id', True), ('decision_time', True), ('original_snapshot_ref', True), ('worker_snapshot_ref', True), ('original_decision_ref', True), ('policy_version_ref', True)),
    'wa_info.epistemic_loop': (('run_id', True), ('loop_key', True), ('actor_id', True), ('receipt_id', True), ('belief_event_id', False), ('belief_key', False), ('decision_id', True), ('authorization_id', True), ('consequence_envelope_id', True), ('subsequent_information_id', False), ('subsequent_possession_key', False)),
    'wa_info.information_artifact': (('run_id', True), ('information_id', True), ('source_observation_id', False), ('source_context_value_ref', False), ('created_time', True), ('source_time_lexeme', True), ('source_time_basis', True), ('payload_schema_ref', True), ('original_artifact_ref', True), ('publication_contract_ref', True)),
    'wa_info.possession': (('run_id', True), ('actor_id', True), ('information_id', True), ('possession_key', True), ('available_from', True), ('event_id', True), ('access_contract_ref', True)),
    'wa_info.principal_binding': (('login_name', True), ('run_id', True), ('actor_id', True), ('authorized_snapshot_ref', True), ('effective_time', True), ('authorization_ref', True)),
    'wa_info.receipt': (('run_id', True), ('receipt_id', True), ('request_id', True), ('value_ref', True), ('resolved_value_hash', True), ('state', True), ('reason_code', True), ('consumer_contract_ref', True), ('consumer_contract_version', True), ('receipt_version', True), ('original_artifact_ref', True)),
    'wa_meta.design_version': (('version_key', True), ('ddl_sha256', True), ('contract_sha256', True), ('authority_main_sha', True), ('qualified_6d_sha', True), ('installed_by', True), ('installed_at', True)),
    'wa_meta.legacy_row': (('snapshot_id', True), ('table_name', True), ('source_key', True), ('original_columns', True), ('row_digest', True)),
    'wa_meta.source_snapshot': (('snapshot_id', True), ('semantic_key', True), ('repository', True), ('git_commit', True), ('source_path', True), ('byte_sha256', True), ('byte_count', True), ('schema_ref', True), ('authority_class', True), ('original_manifest', True)),
    'wa_meta.unit': (('unit_key', True), ('source_lexeme', True), ('dimension_ref', False), ('canonical_unit_ref', False), ('conversion_profile_ref', False), ('interpretation_state', True)),
    'wa_nav.coverage': (('product_id', True), ('body_id', True), ('coverage_key', True), ('valid_time_id', True), ('frame_id', False), ('original_frame_lexeme', False), ('units_lexeme', False), ('coverage_class', True), ('status_lexeme', True)),
    'wa_nav.product': (('product_id', True), ('semantic_key', True), ('provider', True), ('product_name', True), ('product_version', False), ('asset_filename', False), ('byte_sha256', False), ('byte_count', False), ('source_url', False), ('acquired_time_id', False), ('status_lexeme', True)),
    'wa_run.accessibility_assessment': (('run_id', True), ('deposit_id', True), ('world_id', True), ('body_id', True), ('assessment_key', True), ('event_id', True), ('value_state', True), ('accessible_quantity', False), ('unit_key', False), ('capability_ref', True), ('environment_ref', True), ('method_ref', True), ('original_assessment_ref', True)),
    'wa_run.actor_reference': (('run_id', True), ('actor_id', True), ('original_runtime_class', True), ('original_artifact_ref', True)),
    'wa_run.artifact': (('run_id', True), ('artifact_ref', True), ('record_kind', True), ('serializer_ref', True), ('payload_bytes', True), ('payload_sha256', True)),
    'wa_run.asset': (('run_id', True), ('asset_id', True), ('asset_class_ref', True), ('runtime_class', True), ('original_asset_ref', True), ('installed_event_id', False)),
    'wa_run.asset_location': (('run_id', True), ('asset_id', True), ('placement_key', True), ('world_id', False), ('body_id', False), ('location_id', True), ('effective_period', True), ('placement_mode', True), ('trajectory_product_ref', False), ('event_id', True)),
    'wa_run.causal_envelope': (('run_id', True), ('envelope_id', True), ('event_ordinal', True), ('record_version', True), ('scheduled_event_id', True), ('epoch_id', True), ('actor_ref', True), ('process_ref', True), ('action_ref', True), ('world_context', True), ('context_id', True), ('perspective', True), ('time_basis', True), ('effective_time', True), ('decision_time', False), ('authorization_time', False), ('realized_time', True), ('effective_time_lexeme', True), ('decision_time_lexeme', False), ('authorization_time_lexeme', False), ('realized_time_lexeme', True), ('reason_code', True), ('original_envelope_bytes', True), ('original_envelope_sha256', True), ('original_hash_material', True), ('envelope_hash', True), ('previous_trace_hash', True), ('pre_domain_hash', True), ('post_domain_hash', True)),
    'wa_run.execution': (('run_id', True), ('scenario_id', True), ('original_run_identity', True), ('identity_sha256', True), ('code_contract', True), ('code_tree_sha256', True), ('input_snapshot_ref', True), ('boundary_manifest_bytes', True), ('boundary_manifest_sha256', True), ('policy_seed_lexeme', True), ('world_seed_manifest_ref', True), ('world_seed_lexeme', True), ('comparison_group_ref', True), ('comparison_key_schema_ref', True), ('random_algorithm_ref', True), ('decimal_precision', True), ('decimal_rounding_ref', True), ('clock_mapping_ref', True), ('qualification_protocol_ref', True)),
    'wa_run.mission': (('run_id', True), ('mission_id', True), ('project_id', False), ('world_id', True), ('body_id', True), ('target_location_id', True), ('planned_activity_artifact_ref', True), ('interaction_contract_ref', True)),
    'wa_run.observation': (('run_id', True), ('observation_id', True), ('mission_id', False), ('world_id', True), ('body_id', True), ('location_id', True), ('event_id', True), ('effective_time', True), ('source_time_lexeme', True), ('source_time_basis', True), ('geometry_id', False), ('vertical_id', False), ('method_ref', True), ('measurement_schema_ref', True), ('original_observation_ref', True), ('world_context', True)),
    'wa_run.organization_reference': (('run_id', True), ('organization_id', True), ('original_ref', True), ('name', True)),
    'wa_run.population_origin': (('run_id', True), ('cohort_id', True), ('origin_location_id', False), ('external_origin_ref', False), ('initial_person_count', True), ('source_admission_artifact_ref', True), ('genesis_event_id', True)),
    'wa_run.population_state': (('run_id', True), ('cohort_id', True), ('event_id', True), ('position_key', True), ('location_id', False), ('settlement_id', False), ('position_class', True), ('person_count', True), ('original_state_ref', True)),
    'wa_run.project': (('run_id', True), ('project_id', True), ('name', True), ('original_project_artifact_ref', True)),
    'wa_run.project_location': (('run_id', True), ('project_id', True), ('binding_key', True), ('world_id', False), ('body_id', False), ('site_id', False), ('location_id', True), ('effective_period', True), ('purpose_ref', True), ('origin_artifact_ref', True)),
    'wa_run.project_party': (('run_id', True), ('project_id', True), ('organization_id', True), ('relationship_ref', True), ('effective_period', True), ('original_artifact_ref', True)),
    'wa_run.recoverability_assessment': (('run_id', True), ('deposit_id', True), ('project_id', True), ('assessment_key', True), ('accessibility_key', True), ('event_id', True), ('value_state', True), ('recoverable_quantity', False), ('unit_key', False), ('realized_capability_ref', True), ('method_ref', True), ('original_assessment_ref', True)),
    'wa_run.reserve_interpretation': (('run_id', True), ('deposit_id', True), ('project_id', True), ('interpretation_key', True), ('recovery_key', True), ('event_id', True), ('value_state', True), ('reason_code', True), ('economic_contract_ref', False), ('institutional_contract_ref', False), ('original_interpretation_ref', True)),
    'wa_run.settlement': (('run_id', True), ('settlement_id', True), ('name', True), ('runtime_class', True), ('original_state_ref', True)),
    'wa_run.settlement_asset': (('run_id', True), ('settlement_id', True), ('asset_id', True), ('relationship_ref', True), ('organization_id', False), ('effective_period', True), ('event_id', True)),
    'wa_run.settlement_location': (('run_id', True), ('settlement_id', True), ('occupation_key', True), ('world_id', False), ('body_id', False), ('location_id', True), ('effective_period', True), ('event_id', True)),
    'wa_run.settlement_state': (('run_id', True), ('settlement_id', True), ('event_id', True), ('stage_ref', True), ('habitation_state', True), ('habitation_capacity', False), ('original_state_ref', True)),
    'wa_run.stock_state': (('run_id', True), ('world_id', True), ('body_id', True), ('deposit_id', True), ('event_id', True), ('remaining_state', True), ('remaining_in_situ', False), ('cumulative_extracted', False), ('unit_key', False), ('original_physical_state_ref', True)),
    'wa_run.trace_artifact_edge': (('run_id', True), ('envelope_id', True), ('edge_role', True), ('edge_ordinal', True), ('artifact_ref', True)),
    'wa_run.trace_parent': (('run_id', True), ('child_envelope_id', True), ('parent_envelope_id', True)),
    'wa_run.world_binding': (('run_id', True), ('scenario_id', True), ('world_id', True), ('body_id', True), ('binding_key', True)),
    'wa_science.admission': (('admission_id', True), ('target_assertion_id', False), ('target_material_id', False), ('target_warrant_id', False), ('decision_ordinal', True), ('standing', True), ('use_contract_ref', True), ('authorization_ref', True), ('decision_time_id', False), ('decision_sha256', True)),
    'wa_science.assertion': (('assertion_id', True), ('semantic_key', True), ('revision', True), ('body_id', True), ('support_id', True), ('property_code', True), ('ontology', True), ('world_context', True), ('observation_id', False), ('sample_id', False), ('product_id', False), ('value_kind', True), ('value_numeric', False), ('value_text', False), ('value_min', False), ('value_max', False), ('bound_operator', False), ('unit_key', False), ('uncertainty_numeric', False), ('uncertainty_text', False), ('unit_state', True), ('epistemic_class_lexeme', True), ('measurement_method', False), ('confidence_lexeme', False), ('knowledge_time_id', False), ('source_id', True), ('source_artifact_id', False), ('source_locator', False), ('lineage_lexeme', False), ('initial_standing', True), ('preferred_lexeme', True), ('origin_lexeme', True), ('notes', False), ('metadata_bytes', True), ('metadata_sha256', True)),
    'wa_science.assertion_input': (('body_id', True), ('assertion_id', True), ('input_key', True), ('input_assertion_id', False), ('input_observation_id', False), ('input_product_id', False), ('input_material_id', False), ('role_lexeme', True)),
    'wa_science.coverage': (('coverage_id', True), ('body_id', True), ('domain_lexeme', True), ('property_or_class_lexeme', True), ('state_lexeme', True), ('origin_lexeme', True), ('reason', True)),
    'wa_science.extrapolation': (('warrant_id', True), ('assertion_id', True), ('from_body_id', True), ('to_body_id', True), ('from_support_id', True), ('to_support_id', True), ('property_code', True), ('model_family_ref', True), ('method_ref', True), ('uncertainty_ref', True), ('knowledge_ordinal', True), ('initial_standing', True), ('admission_id', True), ('authorization_ref', True), ('scientific_warrant_artifact_id', True)),
    'wa_science.knowledge_event': (('event_id', True), ('semantic_key', True), ('event_type', True), ('event_time_id', False), ('target_assertion_id', False), ('target_observation_id', False), ('target_product_id', False), ('target_source_id', False)),
    'wa_science.material_evidence': (('evidence_id', True), ('body_id', True), ('support_id', True), ('observation_id', False), ('sample_id', False), ('material_family', True), ('material_species', False), ('phase_lexeme', False), ('physical_form_lexeme', False), ('evidence_class_lexeme', True), ('abundance_semantics_lexeme', True), ('value', False), ('value_min', False), ('value_max', False), ('unit_key', False), ('legacy_depth_min', False), ('legacy_depth_max', False), ('legacy_depth_unit_key', False), ('source_id', True), ('initial_standing', True), ('origin_lexeme', True), ('notes', False)),
    'wa_science.observation': (('observation_id', True), ('body_id', True), ('support_id', True), ('product_id', False), ('semantic_key', True), ('measurement_method', True), ('observation_time_id', False), ('source_id', True), ('horizontal_resolution_value', False), ('horizontal_resolution_unit_key', False), ('vertical_sensitivity_min', False), ('vertical_sensitivity_max', False), ('vertical_sensitivity_unit_key', False), ('notes', False)),
    'wa_science.reconciliation': (('reconciliation_id', True), ('body_id', True), ('property_code', True), ('assertion_a', True), ('assertion_b', True), ('classification_lexeme', True), ('reason', True), ('status_lexeme', True)),
    'wa_science.sample': (('sample_id', True), ('body_id', True), ('location_id', False), ('semantic_key', True), ('sample_name', True), ('collection_site_lexeme', False), ('collection_method', False), ('collection_time_id', False), ('mass_value', False), ('mass_unit_key', False), ('source_id', True), ('notes', False)),
    'wa_science.source': (('source_id', True), ('semantic_key', True), ('revision', True), ('title', True), ('authority', True), ('source_type', True), ('url', False), ('doi', False), ('publication_time_id', False), ('acquired_time_id', False), ('notes', False), ('snapshot_id', False)),
    'wa_science.source_artifact': (('artifact_id', True), ('source_id', True), ('semantic_key', True), ('revision', True), ('local_path_lexeme', False), ('retrieval_url', False), ('byte_sha256', False), ('byte_count', False), ('acquired_time_id', False), ('custody_kind', True)),
    'wa_science.spatial_product': (('product_id', True), ('body_id', True), ('support_id', True), ('semantic_key', True), ('product_type', True), ('title', True), ('source_id', True), ('horizontal_resolution_value', False), ('horizontal_resolution_unit_key', False), ('vertical_sensitivity_min', False), ('vertical_sensitivity_max', False), ('vertical_sensitivity_unit_key', False), ('geometry_ref_lexeme', False), ('coordinate_frame_lexeme', False), ('status_lexeme', True)),
    'wa_science.supersession': (('old_assertion_id', True), ('new_assertion_id', True), ('source_id', True), ('reason', True)),
    'wa_science.support': (('support_id', True), ('body_id', True), ('scope_kind', True), ('location_id', False), ('sample_id', False), ('geometry_id', False), ('support_resolution', True), ('vertical_id', False), ('valid_time_id', False), ('representativeness_lexeme', True), ('scope_warrant_ref', True)),
    'wa_world.constraint_binding': (('world_id', True), ('body_id', True), ('binding_key', True), ('assertion_id', True), ('admission_id', True), ('target_support_id', True), ('extrapolation_warrant_id', False), ('assertion_metadata_sha256', True), ('binding_role', True), ('use_contract_ref', True)),
    'wa_world.deposit': (('deposit_id', True), ('world_id', True), ('body_id', True), ('site_id', True), ('location_id', True), ('resource_class', True), ('geometry_class_lexeme', True), ('initial_in_situ_state', True), ('initial_in_situ_quantity', False), ('unit_key', False), ('concentration_state', True), ('concentration_value', False), ('concentration_unit_key', False), ('vertical_id', False), ('phase_ref', True), ('physical_form_ref', True), ('original_accessibility_lexeme', False), ('provenance_ref', True)),
    'wa_world.generation_model': (('model_id', True), ('semantic_key', True), ('version', True), ('name', True), ('status_lexeme', True), ('implementation_sha256', True), ('implementation_locator', True), ('model_family_ref', True), ('uncertainty_contract_ref', True), ('parameter_schema_ref', True)),
    'wa_world.generation_policy': (('policy_id', True), ('model_id', True), ('semantic_key', True), ('version', True), ('body_id', True), ('property_code', True), ('policy_type_lexeme', True), ('parameters', True), ('parameter_schema_ref', True), ('original_parameter_lexeme', False), ('policy_bytes', True), ('policy_sha256', True), ('authorization_ref', True), ('notes', False)),
    'wa_world.hidden_state': (('state_id', True), ('world_id', True), ('body_id', True), ('location_id', False), ('property_code', True), ('value_state', True), ('numeric_value', False), ('text_value', False), ('unit_key', False), ('model_family_ref', True), ('uncertainty_ref', True), ('derivation_ref', True), ('value_sha256', True), ('original_provenance_lexeme', False)),
    'wa_world.physical_property': (('property_code', True), ('value_domain', True), ('physical_semantics_ref', True), ('schema_ref', True)),
    'wa_world.realization': (('world_id', True), ('scenario_id', True), ('model_id', True), ('policy_id', True), ('body_id', True), ('semantic_key', True), ('world_seed_lexeme', True), ('seed_lineage_ref', True), ('scientific_cutoff_ordinal', True), ('random_algorithm_ref', True), ('key_schema_ref', True), ('constraints_digest', True), ('generator_output_sha256', True), ('status_lexeme', True), ('created_time_lexeme', False), ('initial_epoch_id', False), ('world_context', True)),
    'wa_world.scenario': (('scenario_id', True), ('semantic_key', True), ('version', True), ('definition_sha256', True), ('authorization_ref', True), ('definition_locator', True), ('world_context', True)),
    'wa_world.site': (('site_id', True), ('world_id', True), ('body_id', True), ('location_id', True), ('semantic_key', True), ('name', True), ('status_lexeme', True), ('refinement_model_ref', True), ('refinement_seed_lineage_ref', True), ('realization_sha256', True)),
}
SQL_PRIMARY_KEYS = {
    'wa_geo.body': ('body_id',),
    'wa_geo.body_identifier': ('body_id', 'authority', 'identifier_type', 'identifier_value'),
    'wa_geo.body_system': ('system_id',),
    'wa_geo.frame': ('frame_id',),
    'wa_geo.geometry': ('geometry_id',),
    'wa_geo.location': ('location_id',),
    'wa_geo.location_relation': ('from_location_id', 'to_location_id', 'relation_kind'),
    'wa_geo.system_member': ('system_id', 'body_id', 'role_lexeme'),
    'wa_geo.time_support': ('time_id',),
    'wa_geo.vertical_support': ('vertical_id',),
    'wa_info.action_authorization': ('run_id', 'authorization_id'),
    'wa_info.agent_fact': ('run_id', 'actor_id', 'snapshot_ref', 'fact_key'),
    'wa_info.agent_snapshot': ('run_id', 'snapshot_ref'),
    'wa_info.belief': ('run_id', 'actor_id', 'belief_key', 'event_id'),
    'wa_info.consumption_request': ('run_id', 'request_id'),
    'wa_info.context_value': ('run_id', 'value_ref'),
    'wa_info.decision': ('run_id', 'decision_id'),
    'wa_info.epistemic_loop': ('run_id', 'loop_key'),
    'wa_info.information_artifact': ('run_id', 'information_id'),
    'wa_info.possession': ('run_id', 'actor_id', 'information_id', 'possession_key'),
    'wa_info.principal_binding': ('login_name',),
    'wa_info.receipt': ('run_id', 'receipt_id'),
    'wa_meta.design_version': ('version_key',),
    'wa_meta.legacy_row': ('snapshot_id', 'table_name', 'source_key'),
    'wa_meta.source_snapshot': ('snapshot_id',),
    'wa_meta.unit': ('unit_key',),
    'wa_nav.coverage': ('product_id', 'body_id', 'coverage_key'),
    'wa_nav.product': ('product_id',),
    'wa_run.accessibility_assessment': ('run_id', 'deposit_id', 'assessment_key'),
    'wa_run.actor_reference': ('run_id', 'actor_id'),
    'wa_run.artifact': ('run_id', 'artifact_ref'),
    'wa_run.asset': ('run_id', 'asset_id'),
    'wa_run.asset_location': ('run_id', 'asset_id', 'placement_key'),
    'wa_run.causal_envelope': ('run_id', 'envelope_id'),
    'wa_run.execution': ('run_id',),
    'wa_run.mission': ('run_id', 'mission_id'),
    'wa_run.observation': ('run_id', 'observation_id'),
    'wa_run.organization_reference': ('run_id', 'organization_id'),
    'wa_run.population_origin': ('run_id', 'cohort_id'),
    'wa_run.population_state': ('run_id', 'cohort_id', 'event_id', 'position_key'),
    'wa_run.project': ('run_id', 'project_id'),
    'wa_run.project_location': ('run_id', 'project_id', 'binding_key'),
    'wa_run.project_party': ('run_id', 'project_id', 'organization_id', 'relationship_ref', 'effective_period'),
    'wa_run.recoverability_assessment': ('run_id', 'deposit_id', 'project_id', 'assessment_key'),
    'wa_run.reserve_interpretation': ('run_id', 'deposit_id', 'project_id', 'interpretation_key'),
    'wa_run.settlement': ('run_id', 'settlement_id'),
    'wa_run.settlement_asset': ('run_id', 'settlement_id', 'asset_id', 'relationship_ref', 'effective_period'),
    'wa_run.settlement_location': ('run_id', 'settlement_id', 'occupation_key'),
    'wa_run.settlement_state': ('run_id', 'settlement_id', 'event_id'),
    'wa_run.stock_state': ('run_id', 'deposit_id', 'event_id'),
    'wa_run.trace_artifact_edge': ('run_id', 'envelope_id', 'edge_role', 'edge_ordinal'),
    'wa_run.trace_parent': ('run_id', 'child_envelope_id', 'parent_envelope_id'),
    'wa_run.world_binding': ('run_id', 'world_id'),
    'wa_science.admission': ('admission_id',),
    'wa_science.assertion': ('assertion_id',),
    'wa_science.assertion_input': ('assertion_id', 'input_key'),
    'wa_science.coverage': ('coverage_id',),
    'wa_science.extrapolation': ('warrant_id',),
    'wa_science.knowledge_event': ('event_id',),
    'wa_science.material_evidence': ('evidence_id',),
    'wa_science.observation': ('observation_id',),
    'wa_science.reconciliation': ('reconciliation_id',),
    'wa_science.sample': ('sample_id',),
    'wa_science.source': ('source_id',),
    'wa_science.source_artifact': ('artifact_id',),
    'wa_science.spatial_product': ('product_id',),
    'wa_science.supersession': ('old_assertion_id', 'new_assertion_id'),
    'wa_science.support': ('support_id',),
    'wa_world.constraint_binding': ('world_id', 'binding_key'),
    'wa_world.deposit': ('deposit_id',),
    'wa_world.generation_model': ('model_id',),
    'wa_world.generation_policy': ('policy_id',),
    'wa_world.hidden_state': ('state_id',),
    'wa_world.physical_property': ('property_code',),
    'wa_world.realization': ('world_id',),
    'wa_world.scenario': ('scenario_id',),
    'wa_world.site': ('site_id',),
}


def _complete_columns(table,values):
    if table not in SQL_COLUMN_PROFILE:raise IntegrityFailure('UNDECLARED_SQL_TABLE')
    columns=SQL_COLUMN_PROFILE[table]
    if set(values)-{c for c,_ in columns}:raise IntegrityFailure('UNDECLARED_SQL_COLUMN')
    full={c:values.get(c) for c,_ in columns}
    if any(full[c] is None for c,required in columns if required):raise IntegrityFailure('MISSING_REQUIRED_SQL_COLUMN')
    return full


def _validate_original_projection(table,v):
    pairs={'wa_run.execution':(('original_run_identity','identity_sha256'),('boundary_manifest_bytes','boundary_manifest_sha256')),
        'wa_run.artifact':(('payload_bytes','payload_sha256'),),'wa_run.causal_envelope':(('original_envelope_bytes','original_envelope_sha256'),('original_hash_material','envelope_hash')),
        'wa_info.agent_snapshot':(('original_snapshot_bytes','original_snapshot_sha256'),),'wa_science.assertion':(('metadata_bytes','metadata_sha256'),),'wa_world.generation_policy':(('policy_bytes','policy_sha256'),)}
    for payload,d in pairs.get(table,()):verify_original_bytes(v[payload],v[d])
    if table=='wa_run.artifact' and v['artifact_ref']!=v['record_kind']+':'+v['payload_sha256']:raise IntegrityFailure('ORIGINAL_ARTIFACT_REF_MISMATCH')
    if table=='wa_info.agent_snapshot' and v['snapshot_ref']!='decision-snapshot:'+v['period_key']+':'+v['worker_fingerprint']:raise IntegrityFailure('ORIGINAL_SNAPSHOT_REF_MISMATCH')


def _match_or_insert_columns(conn,table,values,*,read_only=False):
    from psycopg import sql
    from psycopg.types.json import Jsonb
    v=_complete_columns(table,values);_validate_original_projection(table,v)
    keys=SQL_PRIMARY_KEYS[table];columns=tuple(v)
    where=sql.SQL(' AND ').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in keys)
    ident=sql.Identifier(*table.split('.'))
    old=conn.execute(sql.SQL('SELECT {} FROM {} WHERE {}').format(sql.SQL(',').join(map(sql.Identifier,columns)),ident,where),[v[k] for k in keys]).fetchone()
    if old is not None:
        if tuple(v.values())!=old:raise CollisionFailure('IMMUTABLE_SQL_ROW_COLLISION:'+table)
        return 'ALREADY_MATCHED'
    if read_only:raise IntegrityFailure('INCOMPLETE_SQL_ROW:'+table)
    q=sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(ident,sql.SQL(',').join(map(sql.Identifier,columns)),sql.SQL(',').join(sql.Placeholder() for _ in v))
    conn.execute(q,[Jsonb(z) if isinstance(z,dict) else z for z in v.values()]);return 'INSERTED'


def install_exact_world(conn,rows):
    """Fixed authored WORLD rows only. No science, generator or run execution."""
    allowed=('wa_world.generation_model','wa_world.generation_policy','wa_world.scenario','wa_world.realization','wa_world.constraint_binding','wa_world.physical_property','wa_world.hidden_state','wa_world.site','wa_world.deposit')
    material=tuple(rows)
    if not material or any(t not in allowed for t,v in material):raise IntegrityFailure('WORLD_BATCH_TABLES')
    if conn.info.transaction_status.value!=0:raise IntegrityFailure('WORLD_INSTALL_REQUIRES_IDLE_CONNECTION')
    with conn.transaction():
        serializable(conn);_require_session_group(conn,'wa_world_writer');conn.execute('SET LOCAL ROLE wa_world_writer')
        # Fixed rows supplied in FK-ready order; no random/database ordering.
        worlds=[v['world_id'] for t,v in material if t=='wa_world.realization']
        if not worlds:raise IntegrityFailure('WORLD_BATCH_WITHOUT_REALIZATION')
        replay=any(conn.execute('SELECT count(*) FROM wa_world.realization WHERE world_id=%s',(wid,)).fetchone()[0] for wid in worlds)
        statuses=[_match_or_insert_columns(conn,t,v,read_only=replay) for t,v in material]
        conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return 'ALREADY_MATCHED' if all(s=='ALREADY_MATCHED' for s in statuses) else 'INSERTED'


def read_admitted_constraints(conn,assertion_ids,cutoff,use_contract_ref,target_support_ids,*,consumer,context,perspective):
    """Explicit cutoff/use/scope closure. Missing evidence is BLOCKED, not default."""
    from psycopg.rows import dict_row
    if context!='REAL' or perspective not in ('WORLD_SIM','GOVERNANCE') or not consumer or type(cutoff) is not int or cutoff<0:raise IntegrityFailure('BLOCKED_DECLARATION')
    if not conn.execute("SELECT pg_has_role(session_user,'wa_reference_reader','MEMBER') OR pg_has_role(session_user,'wa_world_writer','MEMBER')").fetchone()[0]:raise RoleViolation('CONSTRAINT_READER_ROLE')
    if len(assertion_ids)!=len(target_support_ids) or not assertion_ids:raise IntegrityFailure('BLOCKED_DECLARATION')
    out=[]
    with conn.cursor(row_factory=dict_row) as cur:
        for aid,support in zip(assertion_ids,target_support_ids,strict=True):
            cur.execute('''SELECT a.*,s.scope_kind,s.support_resolution,s.location_id,s.sample_id AS support_sample_id,s.representativeness_lexeme,
                d.admission_id,d.standing,d.use_contract_ref,d.authorization_ref,d.decision_ordinal,
                so.snapshot_id,so.title,so.authority,so.url,so.doi,sa.custody_kind,sa.byte_sha256 AS source_byte_sha256
                FROM wa_science.assertion a JOIN wa_science.support s ON s.support_id=a.support_id
                JOIN wa_science.source so ON so.source_id=a.source_id LEFT JOIN wa_science.source_artifact sa ON sa.artifact_id=a.source_artifact_id
                LEFT JOIN LATERAL(SELECT * FROM wa_science.admission WHERE target_assertion_id=a.assertion_id AND decision_ordinal<=%s ORDER BY decision_ordinal DESC LIMIT 1)d ON true
                WHERE a.assertion_id=%s''',(cutoff,aid))
            a=cur.fetchone()
            if not a or a['standing']!='ADMITTED' or a['use_contract_ref']!=use_contract_ref:raise IntegrityFailure('BLOCKED_SCIENCE_ADMISSION')
            _validate_original_projection('wa_science.assertion',a)
            if a['support_resolution']!='IDENTIFIED':raise IntegrityFailure('BLOCKED_SCOPE')
            target=conn.execute('SELECT support_resolution FROM wa_science.support WHERE support_id=%s',(support,)).fetchone()
            if not target or target[0]!='IDENTIFIED':raise IntegrityFailure('BLOCKED_SCOPE')
            if a['support_id']!=support:
                w=conn.execute('''SELECT x.warrant_id FROM wa_science.extrapolation x JOIN LATERAL
                    (SELECT standing,use_contract_ref FROM wa_science.admission WHERE target_warrant_id=x.warrant_id AND decision_ordinal<=%s ORDER BY decision_ordinal DESC LIMIT 1)d ON true
                    WHERE x.assertion_id=%s AND x.to_support_id=%s AND x.knowledge_ordinal<=%s AND d.standing='ADMITTED' AND d.use_contract_ref=%s''',(cutoff,aid,support,cutoff,use_contract_ref)).fetchall()
                if len(w)!=1:raise IntegrityFailure('BLOCKED_SCOPE')
                a['extrapolation_warrant_id']=w[0][0]
            # Recursive typed parents must themselves be admitted at supported scope.
            parent=conn.execute('''WITH RECURSIVE ancestors(id) AS(SELECT %s::uuid UNION SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN ancestors a ON i.assertion_id=a.id WHERE i.input_assertion_id IS NOT NULL)
                SELECT i.assertion_id,i.input_assertion_id,i.input_material_id FROM ancestors p JOIN wa_science.assertion_input i ON i.assertion_id=p.id ORDER BY i.assertion_id,i.input_key COLLATE "C"''',(aid,)).fetchall()
            for child_id,parent_id,material_id in parent:
                if parent_id is not None:
                    ps=conn.execute('SELECT support_id FROM wa_science.assertion WHERE assertion_id=%s',(parent_id,)).fetchone()[0]
                    cs=conn.execute('SELECT support_id FROM wa_science.assertion WHERE assertion_id=%s',(child_id,)).fetchone()[0]
                    # Acyclic graph is SQL-enforced; recursive reads never widen support.
                    read_admitted_constraints(conn,[parent_id],cutoff,use_contract_ref,[cs],consumer=consumer,context=context,perspective=perspective)
                elif material_id is not None:
                    m=conn.execute('''SELECT m.support_id,s.support_resolution,d.standing,d.use_contract_ref,c.support_id FROM wa_science.material_evidence m JOIN wa_science.support s ON s.support_id=m.support_id JOIN wa_science.assertion c ON c.assertion_id=%s LEFT JOIN LATERAL(SELECT standing,use_contract_ref FROM wa_science.admission WHERE target_material_id=m.evidence_id AND decision_ordinal<=%s ORDER BY decision_ordinal DESC LIMIT 1)d ON true WHERE m.evidence_id=%s''',(child_id,cutoff,material_id)).fetchone()
                    if not m or m[1]!='IDENTIFIED' or m[2:4]!=('ADMITTED',use_contract_ref) or m[0]!=m[4]:raise IntegrityFailure('BLOCKED_SCOPE')
            a['typed_parent_refs']=tuple(parent);out.append(a)
    return tuple(out)


def load_bound_world(conn,run_id,binding_key,*,context,effective_time):
    """Trusted runtime physical projection; no Worker or scientific re-generation."""
    _require_session_group(conn,'wa_runtime_writer')
    if context!='REALIZED' or effective_time<0:raise IntegrityFailure('BLOCKED_CONTEXT')
    binding=conn.execute('SELECT world_id,body_id FROM wa_run.world_binding WHERE run_id=%s AND binding_key=%s',(run_id,binding_key)).fetchone()
    if binding is None:raise IntegrityFailure('BLOCKED_CONTEXT')
    world,body=binding
    from psycopg.rows import dict_row
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT * FROM wa_world.realization WHERE world_id=%s AND body_id=%s',(world,body));realization=cur.fetchone()
        cur.execute('SELECT * FROM wa_world.hidden_state WHERE world_id=%s ORDER BY state_id',(world,));states=tuple(cur.fetchall())
        cur.execute('SELECT * FROM wa_world.site WHERE world_id=%s ORDER BY site_id',(world,));sites=tuple(cur.fetchall())
        cur.execute('SELECT * FROM wa_world.deposit WHERE world_id=%s ORDER BY deposit_id',(world,));deposits=tuple(cur.fetchall())
        cur.execute('SELECT s.* FROM wa_run.stock_state s JOIN wa_run.causal_envelope e ON e.run_id=s.run_id AND e.envelope_id=s.event_id WHERE s.run_id=%s AND s.world_id=%s AND e.realized_time<=%s ORDER BY s.deposit_id,e.event_ordinal',(run_id,world,effective_time));stocks=tuple(cur.fetchall())
    return dict(realization=realization,hidden_states=states,sites=sites,deposits=deposits,stock_history=stocks)


def persist_epoch(conn,run_id,epoch_id,expected_previous_head,rows,terminal_artifact_refs):
    """Atomic fixed-column persistence only; consumer validates/executes the kernel.

    An existing caller transaction must already be SERIALIZABLE and bound before
    kernel execution. This function commits; no uncommitted result is returned.
    """
    material=tuple(rows)
    runtime={t for t in SQL_COLUMN_PROFILE if t.startswith('wa_run.')}
    admission={t for t in SQL_COLUMN_PROFILE if t.startswith('wa_info.')}
    if not material or any(t not in runtime|admission or v.get('run_id')!=run_id for t,v in material):raise IntegrityFailure('EPOCH_BATCH_CONTEXT')
    if len(terminal_artifact_refs)!=2 or len(set(terminal_artifact_refs))!=2:raise IntegrityFailure('EPOCH_TERMINAL_ORIGINALS')
    supplied_envelopes=[]
    for table,values in material:
        if table=='wa_run.causal_envelope':
            v=_complete_columns(table,values)
            if v['epoch_id']!=epoch_id:raise IntegrityFailure('EPOCH_BATCH_CONTEXT')
            supplied_envelopes.append((v['event_ordinal'],v['envelope_id']))
    if not supplied_envelopes or len({e for _,e in supplied_envelopes})!=len(supplied_envelopes) or len({o for o,_ in supplied_envelopes})!=len(supplied_envelopes):raise IntegrityFailure('EPOCH_WITHOUT_CAUSAL_ENVELOPES')
    supplied_envelopes.sort()
    if conn.info.transaction_status.value==0:conn.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
    try:
        if conn.execute('SHOW transaction_isolation').fetchone()[0]!='serializable':raise IntegrityFailure('EPOCH_REQUIRES_SERIALIZABLE')
        _require_session_group(conn,'wa_runtime_writer');_require_session_group(conn,'wa_admission_writer')
        conn.execute('SET LOCAL ROLE wa_runtime_writer')
        conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('wa_run:'+run_id,))
        old=conn.execute('SELECT envelope_id,envelope_hash,event_ordinal FROM wa_run.causal_envelope WHERE run_id=%s ORDER BY event_ordinal DESC LIMIT 1',(run_id,)).fetchone()
        replay=conn.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s AND epoch_id=%s',(run_id,epoch_id)).fetchone()[0]>0
        first_ordinal=supplied_envelopes[0][0]
        if replay:
            predecessor=conn.execute('SELECT envelope_id,envelope_hash FROM wa_run.causal_envelope WHERE run_id=%s AND event_ordinal<%s ORDER BY event_ordinal DESC LIMIT 1',(run_id,first_ordinal)).fetchone()
            if predecessor!=expected_previous_head:raise CollisionFailure('EPOCH_PREVIOUS_HEAD_MISMATCH')
        elif old is not None and (old[:2]!=expected_previous_head or first_ordinal<=old[2]):
            raise CollisionFailure('EPOCH_PREVIOUS_HEAD_MISMATCH')
        elif old is None and expected_previous_head is not None:
            raise CollisionFailure('EPOCH_PREVIOUS_HEAD_MISMATCH')
        for table,values in material:
            role='wa_runtime_writer' if table in runtime else 'wa_admission_writer'
            conn.execute('SET LOCAL ROLE '+role)  # exactly one of two fixed literals
            if table=='wa_info.principal_binding':
                if replay:continue
                v=_complete_columns(table,values)
                from psycopg import sql
                oldbinding=conn.execute('SELECT login_name FROM wa_info.principal_binding WHERE login_name=%s',(v['login_name'],)).fetchone()
                if oldbinding:
                    cols=[k for k in v if k!='login_name']
                    conn.execute(sql.SQL('UPDATE wa_info.principal_binding SET {} WHERE login_name=%s').format(sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in cols)),[v[k] for k in cols]+[v['login_name']])
                else:_match_or_insert_columns(conn,table,v)
            else:_match_or_insert_columns(conn,table,values,read_only=bool(replay))
        conn.execute('SET LOCAL ROLE wa_runtime_writer');conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
        actual_envelopes=conn.execute('SELECT event_ordinal,envelope_id FROM wa_run.causal_envelope WHERE run_id=%s AND epoch_id=%s ORDER BY event_ordinal,envelope_id COLLATE "C"',(run_id,epoch_id)).fetchall()
        if actual_envelopes!=supplied_envelopes:raise IntegrityFailure('EPOCH_REPLAY_ENVELOPE_SET_MISMATCH')
        envelope_ids=[e for _,e in supplied_envelopes]
        expected_edges=[]
        edge_columns=tuple(c for c,_ in SQL_COLUMN_PROFILE['wa_run.trace_artifact_edge'])
        for table,values in material:
            if table=='wa_run.trace_artifact_edge':
                v=_complete_columns(table,values);expected_edges.append(tuple(v[c] for c in edge_columns))
        actual_edges=conn.execute("""SELECT run_id,envelope_id,edge_role,edge_ordinal,artifact_ref FROM wa_run.trace_artifact_edge
            WHERE run_id=%s AND envelope_id=ANY(%s) ORDER BY envelope_id COLLATE "C",edge_role COLLATE "C",edge_ordinal,artifact_ref COLLATE "C" """,(run_id,envelope_ids)).fetchall()
        if sorted(actual_edges,key=lambda e:(e[1],e[2],e[3],e[4]))!=sorted(expected_edges,key=lambda e:(e[1],e[2],e[3],e[4])):raise IntegrityFailure('EPOCH_REPLAY_TRACE_EDGE_SET_MISMATCH')
        for ref in terminal_artifact_refs:
            if conn.execute('SELECT count(*) FROM wa_run.artifact WHERE run_id=%s AND artifact_ref=%s',(run_id,ref)).fetchone()[0]!=1:raise IntegrityFailure('EPOCH_TERMINAL_ORIGINAL_MISSING')
            if not conn.execute('''SELECT 1 FROM wa_run.trace_artifact_edge e JOIN wa_run.causal_envelope c ON c.run_id=e.run_id AND c.envelope_id=e.envelope_id WHERE e.run_id=%s AND c.epoch_id=%s AND e.artifact_ref=%s LIMIT 1''',(run_id,epoch_id,ref)).fetchone():raise IntegrityFailure('EPOCH_TERMINAL_TRACE_CLOSURE')
        conn.commit()
    except Exception:
        conn.rollback();raise
    return 'ALREADY_MATCHED' if replay else 'COMMITTED'

def read_replay_prefix(conn,run_id,*,input_snapshot_ref,code_contract,code_tree_sha256):
    """Ordered pinned originals for the trusted consumer's own decoder/replay."""
    from psycopg.rows import dict_row
    if not conn.execute("SELECT pg_has_role(session_user,'wa_runtime_writer','MEMBER') OR pg_has_role(session_user,'wa_auditor','MEMBER')").fetchone()[0]:raise RoleViolation('REPLAY_READER_ROLE')
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute('SELECT * FROM wa_run.execution WHERE run_id=%s',(run_id,));execution=cur.fetchone()
        if not execution or (execution['input_snapshot_ref'],execution['code_contract'],execution['code_tree_sha256'])!=(input_snapshot_ref,code_contract,code_tree_sha256):raise IntegrityFailure('REPLAY_IDENTITY_MISMATCH')
        cur.execute('SELECT * FROM wa_run.causal_envelope WHERE run_id=%s ORDER BY event_ordinal',(run_id,));envelopes=tuple(cur.fetchall())
        cur.execute('SELECT * FROM wa_run.artifact WHERE run_id=%s ORDER BY artifact_ref COLLATE "C"',(run_id,));artifacts=tuple(cur.fetchall())
        cur.execute('SELECT * FROM wa_run.trace_artifact_edge WHERE run_id=%s ORDER BY envelope_id COLLATE "C",edge_role COLLATE "C",edge_ordinal',(run_id,));edges=tuple(cur.fetchall())
    for v in envelopes:_validate_original_projection('wa_run.causal_envelope',v)
    for v in artifacts:_validate_original_projection('wa_run.artifact',v)
    return dict(execution=execution,envelopes=envelopes,artifacts=artifacts,trace_artifact_edges=edges)


def export_run(conn,run_id,*,input_snapshot_ref,code_contract,code_tree_sha256):
    """Deterministic private complete relational run package, audit role only."""
    from .etl import canonical
    from psycopg import sql
    _require_session_group(conn,'wa_auditor')
    prefix=read_replay_prefix(conn,run_id,input_snapshot_ref=input_snapshot_ref,code_contract=code_contract,code_tree_sha256=code_tree_sha256)
    tables={}
    for table,profile in SQL_COLUMN_PROFILE.items():
        if not table.startswith(('wa_run.','wa_info.')):continue
        columns=[c for c,_ in profile]
        q=sql.SQL('SELECT {} FROM {} WHERE run_id=%s ORDER BY {}').format(sql.SQL(',').join(map(sql.Identifier,columns)),sql.Identifier(*table.split('.')),sql.SQL(',').join(map(sql.Identifier,SQL_PRIMARY_KEYS[table])))
        tables[table]=[dict(zip(columns,v)) for v in conn.execute(q,(run_id,)).fetchall()]
    return canonical(dict(profile='WA_PRIVATE_RUN_EXPORT_V1',run_id=run_id,execution=prefix['execution'],tables=tables))
