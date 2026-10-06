"""World Authority PostgreSQL security qualification probes.

These tests require an installed disposable PostgreSQL 18 qualification cluster.
They intentionally use real LOGIN principals rather than trusting catalog helpers.
"""
import os
import hashlib
import json
import unittest
import uuid
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from loom_world_authority.store import RoleViolation, CollisionFailure, stable_uuid, length_prefixed, _complete_columns, read_catalog_location, read_admitted_constraints, install_exact_world, install_authored_site_metadata, install_fixture_time_support, record_fixture_admission, persist_epoch, read_replay_prefix, export_run, IntegrityFailure, sha256_bytes, require_sha256, verify_original_bytes, load_current_agent_snapshot

try:
    import psycopg
except ImportError:
    psycopg = None

EXECUTED=set()
AGENT_B="wa_q_agent_b"
WORLD="wa_q_world"
GOVERNOR="wa_q_governor"
AUDITOR="wa_q_auditor"
ADMISSION="wa_q_admission"
EXECUTOR="wa_q_executor"
REFERENCE="wa_q_reference_security"
HOST=os.getenv("LOOM_WA_PGHOST","127.0.0.1")
PORT=int(os.getenv("LOOM_WA_PGPORT","55419"))
DB=os.getenv("LOOM_WA_PGDATABASE","loom_world_authority")
ADMIN=os.getenv("LOOM_WA_PGADMIN","loom_wa_admin")
ADMIN_PASSWORD=os.getenv("LOOM_WA_PGADMIN_PASSWORD")
AGENT="wa_q_agent"
WRITER="wa_q_science_writer"
RUNTIME="wa_q_runtime_writer"
TEST_PASSWORD=os.getenv("LOOM_WA_TEST_PASSWORD","wa-qualification-only")

def conn(user,password,**kw):
    return psycopg.connect(host=HOST,port=PORT,dbname=DB,user=user,password=password,**kw)

def public_report_token(run,actor,period):
    # Fixture report labels are actor-visible evidence. They deliberately do
    # not serialize private run identifiers into values, snapshots or hashes.
    index=(('QUAL-RUN-A','AGENT-A','P0'),('QUAL-RUN-A','AGENT-A','P1'),
           ('QUAL-RUN-A','AGENT-B','P0'),('QUAL-RUN-A','AGENT-B','P1'),
           ('QUAL-RUN-B','AGENT-A','P0'),('QUAL-RUN-B','AGENT-A','P1'),
           ('QUAL-RUN-B','AGENT-B','P0'),('QUAL-RUN-B','AGENT-B','P1')).index((run,actor,period))+1
    return 'PUBLIC_OBSERVATION_REPORT_%02d'%index

@unittest.skipIf(psycopg is None,"psycopg 3 not installed")
@unittest.skipUnless(ADMIN_PASSWORD,"LOOM_WA_PGADMIN_PASSWORD not set")
class WorldAuthoritySecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with conn(ADMIN,ADMIN_PASSWORD,autocommit=True) as c:
            c.execute(f"DROP ROLE IF EXISTS {AGENT}")
            c.execute(f"DROP ROLE IF EXISTS {WRITER}")
            c.execute(f"DROP ROLE IF EXISTS {RUNTIME}")
            c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(AGENT),sql.Literal(TEST_PASSWORD)))
            c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(WRITER),sql.Literal(TEST_PASSWORD)))
            c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(RUNTIME),sql.Literal(TEST_PASSWORD)))
            c.execute(f"GRANT wa_agent_reader TO {AGENT}")
            c.execute(f"GRANT wa_science_writer TO {WRITER}")
            c.execute(f"GRANT wa_runtime_writer TO {RUNTIME}")
            for login,group in ((AGENT_B,'wa_agent_reader'),(WORLD,'wa_world_writer'),(GOVERNOR,'wa_science_governor'),(AUDITOR,'wa_auditor'),(ADMISSION,'wa_admission_writer'),(REFERENCE,'wa_reference_reader'),(EXECUTOR,'wa_runtime_writer')):
                c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(login),sql.Literal(TEST_PASSWORD)))
                c.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(group),sql.Identifier(login)))
            c.execute(sql.SQL('GRANT wa_admission_writer TO {}').format(sql.Identifier(EXECUTOR)))
            # Minimal valid authority chain for populated S02/S04 boundary tests.
            c.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            scenario="00000000-0000-0000-0000-00000000a201"
            zero="0"*64
            c.execute("""INSERT INTO wa_world.scenario
                (scenario_id,semantic_key,version,definition_sha256,authorization_ref,definition_locator,world_context)
                VALUES (%s,'QUAL_SECURITY','V1',%s,'QUAL','qualification://security','SCENARIO')""",(scenario,zero))
            for run in ("QUAL-RUN-A","QUAL-RUN-B"):
                ident=(run+"-identity").encode(); boundary=(run+"-boundary").encode()
                c.execute("""INSERT INTO wa_run.execution
                    (run_id,scenario_id,original_run_identity,identity_sha256,code_contract,code_tree_sha256,
                     input_snapshot_ref,boundary_manifest_bytes,boundary_manifest_sha256,policy_seed_lexeme,
                     world_seed_manifest_ref,world_seed_lexeme,comparison_group_ref,comparison_key_schema_ref,
                     random_algorithm_ref,decimal_precision,decimal_rounding_ref,clock_mapping_ref,qualification_protocol_ref)
                    VALUES (%s,%s,%s,encode(wa_crypto.digest(%s,'sha256'),'hex'),'QUAL',%s,'QUAL',%s,
                    encode(wa_crypto.digest(%s,'sha256'),'hex'),'policy','world-manifest','world','cmp','cmp-schema',
                    'QUAL-RNG',28,'ROUND_HALF_EVEN','QUAL-CLOCK','S02-S04')""",
                    (run,scenario,ident,ident,zero,boundary,boundary))
                for actor in ("AGENT-A","AGENT-B"):
                    payload=(run+actor+"-actor").encode()
                    h=c.execute("SELECT encode(wa_crypto.digest(%s,'sha256'),'hex')",(payload,)).fetchone()[0]
                    aref="ACTOR:"+h
                    c.execute("""INSERT INTO wa_run.artifact(run_id,artifact_ref,record_kind,serializer_ref,payload_bytes,payload_sha256)
                        VALUES (%s,%s,'ACTOR','QUAL',%s,%s)""",(run,aref,payload,h))
                    c.execute("INSERT INTO wa_run.actor_reference VALUES (%s,%s,'AGENT',%s)",(run,actor,aref))
                    for period,t in (("P0",0),("P1",1)):
                        token=public_report_token(run,actor,period)
                        snap=json.dumps(dict(actor_id=actor,period_key=period,facts={'REPORT':token}),sort_keys=True,separators=(',',':')).encode()
                        sh=c.execute("SELECT encode(wa_crypto.digest(%s,'sha256'),'hex')",(snap,)).fetchone()[0]
                        sref="DECISION_STATE:"+sh
                        c.execute("""INSERT INTO wa_run.artifact(run_id,artifact_ref,record_kind,serializer_ref,payload_bytes,payload_sha256)
                            VALUES (%s,%s,'DECISION_STATE','QUAL',%s,%s)""",(run,sref,snap,sh))
                        wf=hashlib.sha256(snap).hexdigest()
                        snapref="decision-snapshot:"+period+":"+wf
                        c.execute("""INSERT INTO wa_info.agent_snapshot
                            (run_id,snapshot_ref,actor_id,period_key,effective_time,effective_time_lexeme,
                             original_snapshot_bytes,original_snapshot_sha256,original_artifact_ref,worker_fingerprint,
                             producer_contract_ref,sanitizer_attestation_sha256)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'QUAL',%s)""",
                            (run,snapref,actor,period,t,str(t),snap,sh,sref,wf,zero))
            c.execute("""INSERT INTO wa_info.principal_binding
                (login_name,run_id,actor_id,authorized_snapshot_ref,effective_time,authorization_ref)
                VALUES (%s,'QUAL-RUN-A','AGENT-A',%s,0,'QUAL')""",
                (AGENT,"decision-snapshot:P0:"+hashlib.sha256(json.dumps(dict(actor_id='AGENT-A',period_key='P0',facts={'REPORT':public_report_token('QUAL-RUN-A','AGENT-A','P0')}),sort_keys=True,separators=(',',':')).encode()).hexdigest()))
            c.execute("INSERT INTO wa_info.principal_binding VALUES (%s,'QUAL-RUN-B','AGENT-B',%s,0,'QUAL')",(AGENT_B,"decision-snapshot:P0:"+hashlib.sha256(json.dumps(dict(actor_id='AGENT-B',period_key='P0',facts={'REPORT':public_report_token('QUAL-RUN-B','AGENT-B','P0')}),sort_keys=True,separators=(',',':')).encode()).hexdigest()))
            cls._populate_facts(c)
            c.execute("COMMIT")
        cls._populate_science()

    @classmethod
    def tearDownClass(cls):
        with conn(ADMIN,ADMIN_PASSWORD,autocommit=True) as c:
            c.execute(f"DROP ROLE IF EXISTS {AGENT}")
            c.execute(f"DROP ROLE IF EXISTS {WRITER}")
            c.execute(f"DROP ROLE IF EXISTS {RUNTIME}")
            for login in (AGENT_B,WORLD,GOVERNOR,AUDITOR,ADMISSION,REFERENCE,EXECUTOR):c.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(login)))

    def setUp(self):
        name=self._testMethodName
        if name.startswith('test_S'):EXECUTED.add(name[5:8])

    @staticmethod
    def _insert(c,table,values):
        q=sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(*table.split('.')),sql.SQL(',').join(map(sql.Identifier,values)),sql.SQL(',').join(sql.Placeholder() for _ in values))
        c.execute(q,[Jsonb(v) if isinstance(v,dict) else v for v in values.values()])

    @staticmethod
    def _artifact(c,run,kind,payload):
        h=hashlib.sha256(payload).hexdigest();ref=kind+':'+h
        WorldAuthoritySecurity._insert(c,'wa_run.artifact',dict(run_id=run,artifact_ref=ref,record_kind=kind,serializer_ref='QUAL',payload_bytes=payload,payload_sha256=h))
        return ref

    @classmethod
    def _populate_facts(cls,c):
        for run in ('QUAL-RUN-A','QUAL-RUN-B'):
            for actor in ('AGENT-A','AGENT-B'):
                for period,t in (('P0',0),('P1',1)):
                    key=run+':'+actor+':'+period;token=public_report_token(run,actor,period);aref=cls._artifact(c,run,'CONTEXT_VALUE',key.encode())
                    v=dict(run_id=run,value_ref=key,assertion_ref='QUAL-REPORT',subject_ref='VISIBLE_TARGET',concept='REPORT',scope_ref='QUAL_SITE',world_context='REALIZED',context_id=run,perspective='AGENT',perspective_actor_id=actor,value_state='KNOWN',value_lexeme=token,unit_lexeme='TEXT',reason_code='QUAL_ADMITTED_REPORT',proposition_kind='REPORT',proposition_role='REPORT',epistemic_mode='OBSERVED',admission_state='ADMITTED',uncertainty_state='DECLARED',uncertainty_ref='QUAL',time_basis='SIM_TIME',valid_from=t,valid_to=t,available_from=t,source_time=t,source_refs=['QUAL-OBSERVATION'],source_hashes=[hashlib.sha256(token.encode()).hexdigest()],warrant_refs=[],support_conflict_refs=[],dependency_refs=[],transformation_ref='QUAL',transformation_version='V1',authorization_ref='QUAL',reference_role='REPORT',record_version='V1',original_artifact_ref=aref,fingerprint=hashlib.sha256((token+'-fingerprint').encode()).hexdigest())
                    cls._insert(c,'wa_info.context_value',v)
                    q=dict(run_id=run,request_id=key,consumer_id=actor,use_ref='POLICY',subject_ref='VISIBLE_TARGET',concept='REPORT',scope_ref='QUAL_SITE',time_basis='SIM_TIME',effective_time=t,knowledge_cutoff=t,world_context='REALIZED',context_id=run,perspective='AGENT',perspective_actor_id=actor,assertion_set='ADMITTED',required_unit='TEXT',required_role='REPORT',original_artifact_ref=cls._artifact(c,run,'CONSUMPTION_REQUEST',(key+'-request').encode()))
                    cls._insert(c,'wa_info.consumption_request',q)
                    receipt=dict(run_id=run,receipt_id=key,request_id=key,value_ref=key,resolved_value_hash=v['fingerprint'],state='KNOWN',reason_code='QUAL',consumer_contract_ref='QUAL',consumer_contract_version='V1',receipt_version='V1',original_artifact_ref=cls._artifact(c,run,'ADMISSION_RECEIPT',(key+'-receipt').encode()))
                    cls._insert(c,'wa_info.receipt',receipt)
                    ref='decision-snapshot:'+period+':'+hashlib.sha256(json.dumps(dict(actor_id=actor,period_key=period,facts={'REPORT':token}),sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    cls._insert(c,'wa_info.agent_fact',dict(run_id=run,actor_id=actor,snapshot_ref=ref,fact_key='REPORT',receipt_id=key,effective_time=t,value_state='KNOWN',value_lexeme=token,worker_source_ref='admitted:REPORT',producer_contract_ref='QUAL',sanitizer_attestation_sha256='0'*64))

    @classmethod
    def _populate_science(cls):
        # All copied claims and decisions are explicitly synthetic, confined to
        # this disposable security DB. No accepted migrated database is admitted.
        with conn(ADMIN,ADMIN_PASSWORD,autocommit=True,row_factory=dict_row) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            base=c.execute("SELECT a.* FROM wa_science.assertion a JOIN wa_science.support s ON s.support_id=a.support_id JOIN wa_geo.body b ON b.body_id=a.body_id WHERE s.support_resolution='IDENTIFIED' AND s.scope_kind='BODY' AND b.semantic_key='MOON' ORDER BY a.semantic_key LIMIT 1").fetchone()
            unresolved=c.execute("SELECT support_id FROM wa_science.support WHERE body_id=%s AND support_resolution='UNRESOLVED' ORDER BY support_id LIMIT 1",(base['body_id'],)).fetchone()['support_id']
            other=c.execute("SELECT support_id FROM wa_science.support WHERE body_id=%s AND support_resolution='IDENTIFIED' AND support_id<>%s ORDER BY support_id LIMIT 1",(base['body_id'],base['support_id'])).fetchone()['support_id']
            cls.science={};cls.body=base['body_id'];cls.support=base['support_id'];cls.other_support=other
            for i,key in enumerate(('GOOD','CANDIDATE','PARENT','CHILD','UNRESOLVED'),1):
                r=base.copy();r.update(assertion_id=uuid.UUID(int=0xb100+i),semantic_key='QUAL_S11_'+key,revision='QUAL_V1',initial_standing='CANDIDATE',metadata_bytes=('QUAL_S11_'+key).encode(),metadata_sha256=hashlib.sha256(('QUAL_S11_'+key).encode()).hexdigest(),notes='SYNTHETIC_SECURITY_FIXTURE_NOT_SCIENTIFIC_ADMISSION_OF_SOURCE')
                if key=='UNRESOLVED':r.update(support_id=unresolved,observation_id=None,sample_id=None,product_id=None)
                cls._insert(c,'wa_science.assertion',r);cls.science[key]=r
            c.execute("INSERT INTO wa_science.assertion_input (body_id,assertion_id,input_key,input_assertion_id,role_lexeme) VALUES (%s,%s,'PARENT',%s,'QUAL')",(cls.body,cls.science['CHILD']['assertion_id'],cls.science['PARENT']['assertion_id']))
            c.execute('COMMIT')
        # Genuine governor login creates only synthetic use-scoped decisions.
        cls.admissions={}
        with conn(GOVERNOR,TEST_PASSWORD,autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            for i,(key,standing) in enumerate((('GOOD','ADMITTED'),('CANDIDATE','CANDIDATE'),('CHILD','ADMITTED'),('UNRESOLVED','ADMITTED')),1):
                aid=uuid.UUID(int=0xb200+i);cls.admissions[key]=aid
                cls._insert(c,'wa_science.admission',dict(admission_id=aid,target_assertion_id=cls.science[key]['assertion_id'],decision_ordinal=i,standing=standing,use_contract_ref='QUAL_USE',authorization_ref='QUAL_SECURITY_ONLY',decision_sha256='0'*64))
            cls._insert(c,'wa_science.admission',dict(admission_id=uuid.UUID(int=0xb299),target_assertion_id=cls.science['GOOD']['assertion_id'],decision_ordinal=100,standing='HOLD',use_contract_ref='QUAL_USE',authorization_ref='QUAL_SECURITY_ONLY',decision_sha256='0'*64))
            c.execute('COMMIT')
        with conn(WORLD,TEST_PASSWORD,autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            cls.model=uuid.UUID(int=0xb301);cls.policy=uuid.UUID(int=0xb302);cls.worlds={}
            cls._insert(c,'wa_world.generation_model',dict(model_id=cls.model,semantic_key='QUAL_MODEL',version='V1',name='SQL_GUARD_FIXTURE',status_lexeme='SYNTHETIC',implementation_sha256='0'*64,implementation_locator='qualification://S11',model_family_ref='QUAL',uncertainty_contract_ref='QUAL',parameter_schema_ref='QUAL'))
            cls._insert(c,'wa_world.generation_policy',dict(policy_id=cls.policy,model_id=cls.model,semantic_key='QUAL_POLICY',version='V1',body_id=cls.body,property_code=base['property_code'],policy_type_lexeme='QUAL',parameters={},parameter_schema_ref='QUAL',policy_bytes=b'{}',policy_sha256=hashlib.sha256(b'{}').hexdigest(),authorization_ref='QUAL'))
            for cutoff in (99,100):
                wid=uuid.UUID(int=0xb400+cutoff);cls.worlds[cutoff]=wid
                cls._insert(c,'wa_world.realization',dict(world_id=wid,scenario_id=uuid.UUID(int=0xa201),model_id=cls.model,policy_id=cls.policy,body_id=cls.body,semantic_key='QUAL_WORLD_'+str(cutoff),world_seed_lexeme='QUAL_NOT_SIMULATED',seed_lineage_ref='QUAL',scientific_cutoff_ordinal=cutoff,random_algorithm_ref='QUAL',key_schema_ref='QUAL',constraints_digest='0'*64,generator_output_sha256='0'*64,status_lexeme='SQL_GUARD_FIXTURE',world_context='SCENARIO'))
            c.execute('COMMIT')

    def test_S01_agent_private_schemas_denied(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            for sql in (
                "SELECT 1 FROM wa_world.realization LIMIT 1",
                "SELECT 1 FROM wa_run.execution LIMIT 1",
                "SELECT 1 FROM wa_info.agent_snapshot LIMIT 1",
                "SELECT 1 FROM wa_science.assertion LIMIT 1",
                "SELECT 1 FROM wa_meta.design_version LIMIT 1",
                "SELECT original_columns FROM wa_meta.legacy_row LIMIT 1",
            ):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    c.execute(sql).fetchone()

    def test_S03_agent_cannot_set_privileged_role(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                c.execute("SET ROLE wa_world_writer")
            c.execute("SET loom.actor_id='AGENT-B'");c.execute("SET loom.run_id='QUAL-RUN-B'")
            self.assertEqual(c.execute("SELECT actor_id FROM wa_agent_api.current_snapshot").fetchall(),[("AGENT-A",)])
            for group in ('wa_owner','wa_admission_writer','wa_science_governor','wa_auditor','wa_agent_view_owner'):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute(sql.SQL('SET ROLE {}').format(sql.Identifier(group)))

    def test_S05_agent_crypto_surface_denied(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                c.execute("SELECT wa_crypto.digest('x'::bytea,'sha256')").fetchone()
            for q in ('SELECT original_envelope_bytes FROM wa_run.causal_envelope','SELECT payload_bytes FROM wa_run.artifact','SELECT world_seed_lexeme FROM wa_world.realization','SELECT fingerprint FROM wa_info.context_value'):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute(q)

    def test_S06_agent_dml_denied(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                c.execute("DELETE FROM wa_info.agent_snapshot WHERE false")
            for q in ('INSERT INTO wa_info.receipt DEFAULT VALUES',"UPDATE wa_info.principal_binding SET actor_id='AGENT-B'",'INSERT INTO wa_run.artifact DEFAULT VALUES'):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute(q)
            import loom_world_authority.store as store
            self.assertFalse(hasattr(store,'fetch_one_fixed'))

    def test_S08_agent_has_only_reader_membership(self):
        with conn(ADMIN,ADMIN_PASSWORD,autocommit=True) as c:
            rows=c.execute("""SELECT parent.rolname FROM pg_auth_members m
                JOIN pg_roles child ON child.oid=m.member
                JOIN pg_roles parent ON parent.oid=m.roleid
                WHERE child.rolname=%s ORDER BY 1""",(AGENT,)).fetchall()
        self.assertEqual(rows,[("wa_agent_reader",)])
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            for group in ('wa_owner','wa_science_writer','wa_world_writer','wa_runtime_writer','wa_admission_writer','wa_science_governor','wa_auditor','wa_agent_view_owner'):
                self.assertFalse(c.execute("SELECT pg_has_role(current_user,%s,'MEMBER')",(group,)).fetchone()[0])
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute(sql.SQL('SET ROLE {}').format(sql.Identifier(group)))
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute('SELECT * FROM wa_world.scenario')


    def test_S02_agent_api_is_exactly_binding_scoped(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            rows=c.execute("""SELECT actor_id,period_key,effective_time
                FROM wa_agent_api.current_snapshot""").fetchall()
            self.assertEqual(rows,[("AGENT-A","P0",0)])
            current=load_current_agent_snapshot(c);self.assertEqual(current['actor_id'],'AGENT-A')
            self.assertNotIn('run_id',current)
            self.assertNotIn('QUAL-RUN',str(current))
            # Other actor, other run, and future P1 all exist but remain invisible.
            self.assertEqual(c.execute("SELECT fact_key,value_lexeme FROM wa_agent_api.snapshot_facts").fetchall(),[("REPORT","PUBLIC_OBSERVATION_REPORT_01")])

        with conn(AGENT_B,TEST_PASSWORD,autocommit=True) as c:
            self.assertEqual(c.execute("SELECT actor_id,period_key,effective_time FROM wa_agent_api.current_snapshot").fetchall(),[("AGENT-B","P0",0)])
            self.assertEqual(c.execute("SELECT value_lexeme FROM wa_agent_api.snapshot_facts").fetchall(),[("PUBLIC_OBSERVATION_REPORT_07",)])

    def test_S04_current_binding_advancement(self):
        # Advancing the binding makes only the new exact snapshot visible;
        # the old P0 history is no longer exposed.
        with conn(ADMISSION,TEST_PASSWORD,autocommit=True) as c:
            c.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            c.execute("""UPDATE wa_info.principal_binding
                SET authorized_snapshot_ref=%s,effective_time=1,authorization_ref='QUAL-ADVANCE'
                WHERE login_name=%s""",("decision-snapshot:P1:"+hashlib.sha256(json.dumps(dict(actor_id='AGENT-A',period_key='P1',facts={'REPORT':public_report_token('QUAL-RUN-A','AGENT-A','P1')}),sort_keys=True,separators=(',',':')).encode()).hexdigest(),AGENT))
            c.execute("COMMIT")
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            rows=c.execute("""SELECT actor_id,period_key,effective_time
                FROM wa_agent_api.current_snapshot""").fetchall()
            self.assertEqual(rows,[("AGENT-A","P1",1)])
            self.assertEqual(c.execute("SELECT value_lexeme FROM wa_agent_api.snapshot_facts").fetchall(),[("PUBLIC_OBSERVATION_REPORT_02",)])
            self.assertEqual(c.execute("SELECT count(*) FROM wa_agent_api.current_snapshot WHERE period_key='P0'").fetchone()[0],0)

    def test_S07_agent_cannot_query_science_catalog(self):
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            for sql in (
                "SELECT 1 FROM wa_science.assertion LIMIT 1",
                "SELECT 1 FROM wa_science.admission LIMIT 1",
                "SELECT 1 FROM wa_science.extrapolation LIMIT 1",
            ):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    c.execute(sql).fetchone()

    def test_S09_admin_exception_is_explicitly_privileged(self):
        with conn(ADMIN,ADMIN_PASSWORD,autocommit=True) as c:
            row=c.execute("SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user").fetchone()
            self.assertTrue(row[0])
            self.assertTrue(c.execute("SELECT has_schema_privilege(current_user,'wa_world','USAGE')").fetchone()[0])
            c.execute('SET ROLE wa_owner');self.assertGreater(c.execute('SELECT count(*) FROM wa_run.execution').fetchone()[0],0)
        with conn(AUDITOR,TEST_PASSWORD,autocommit=True) as c:
            self.assertGreater(c.execute('SELECT count(*) FROM wa_run.execution').fetchone()[0],0)
            self.assertGreater(c.execute('SELECT count(*) FROM wa_science.assertion').fetchone()[0],880)
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute('INSERT INTO wa_run.execution DEFAULT VALUES')

    def test_S10_writer_rejects_read_committed_write(self):
        with conn(RUNTIME,TEST_PASSWORD) as c:
            iso=c.execute("SHOW transaction_isolation").fetchone()[0]
            self.assertEqual(iso,"read committed")
            # Use a table this service is actually authorized to INSERT into.
            # The isolation trigger must reject the write before row constraints matter.
            with self.assertRaises(psycopg.Error) as cm:
                c.execute("INSERT INTO wa_run.execution DEFAULT VALUES")
            self.assertIn("SERIALIZABLE",str(cm.exception).upper())
        with conn(ADMISSION,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaisesRegex(psycopg.Error,'SERIALIZABLE'):c.execute("UPDATE wa_info.principal_binding SET authorization_ref='FORGED' WHERE login_name=%s",(AGENT,))
            with self.assertRaisesRegex(psycopg.Error,'SERIALIZABLE'):c.execute('DELETE FROM wa_info.principal_binding WHERE login_name=%s',(AGENT,))
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            c.execute("UPDATE wa_info.principal_binding SET authorization_ref='QUAL_SERIALIZABLE' WHERE login_name=%s",(AGENT,));c.execute('COMMIT')


    def test_S11_behavioral_science_guards(self):
        def binding(key,*,cutoff=99,target=None,sha=None):
            r=self.science[key]
            return dict(world_id=self.worlds[cutoff],body_id=self.body,binding_key='QUAL_'+key,assertion_id=r['assertion_id'],admission_id=self.admissions[key],target_support_id=target or r['support_id'],assertion_metadata_sha256=sha or r['metadata_sha256'],binding_role='QUAL',use_contract_ref='QUAL_USE')
        cases=[('candidate',binding('CANDIDATE'),'unadmitted'),('unresolved',binding('UNRESOLVED'),'unresolved'),('stale',binding('GOOD',cutoff=100),'cutoff'),('parent',binding('CHILD'),'parent'),('cross-scope',binding('GOOD',target=self.other_support),'scope'),('hash',binding('GOOD',sha='0'*64),'stale')]
        with conn(WORLD,TEST_PASSWORD,autocommit=True) as c:
            for name,values,reason in cases:
                c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
                try:
                    with self.assertRaises(psycopg.Error) as cm:self._insert(c,'wa_world.constraint_binding',values)
                    self.assertIn(reason,str(cm.exception).lower(),name)
                finally:c.execute('ROLLBACK')
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            self._insert(c,'wa_world.constraint_binding',binding('GOOD'));c.execute('COMMIT')
            self.assertEqual(c.execute('SELECT count(*) FROM wa_world.constraint_binding').fetchone()[0],1)
        with conn(GOVERNOR,TEST_PASSWORD,autocommit=True) as c:
            remote=c.execute("SELECT artifact_id FROM wa_science.source_artifact WHERE custody_kind='REMOTE_REFERENCE_ONLY' ORDER BY artifact_id LIMIT 1").fetchone()[0]
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            try:
                r=self.science['GOOD']
                with self.assertRaisesRegex(psycopg.Error,'unqualified extrapolation warrant'):
                    self._insert(c,'wa_science.extrapolation',dict(warrant_id=uuid.UUID(int=0xb555),assertion_id=r['assertion_id'],from_body_id=self.body,to_body_id=self.body,from_support_id=r['support_id'],to_support_id=self.other_support,property_code=r['property_code'],model_family_ref='QUAL',method_ref='QUAL',uncertainty_ref='QUAL',knowledge_ordinal=1,initial_standing='CANDIDATE',admission_id=self.admissions['GOOD'],authorization_ref='QUAL',scientific_warrant_artifact_id=remote))
            finally:c.execute('ROLLBACK')

    def test_S12_behavioral_original_hash_guards(self):
        # Typed primitive byte guard and SQL are independent boundaries.
        with self.assertRaises(IntegrityFailure):require_sha256('FORGED')
        with self.assertRaisesRegex(IntegrityFailure,'ORIGINAL_BYTES_MISMATCH'):verify_original_bytes(b'FORGED',sha256_bytes(b'snapshot'))
        self.assertNotEqual(sha256_bytes(b'snapshot'),sha256_bytes(b'worker hash material'))
        with conn(RUNTIME,TEST_PASSWORD,autocommit=True,row_factory=dict_row) as c:
            snap=c.execute("SELECT * FROM wa_info.agent_snapshot WHERE run_id='QUAL-RUN-A' AND actor_id='AGENT-A' AND period_key='P0'").fetchone()
            bad=snap.copy();bad.update(snapshot_ref='decision-snapshot:BAD:'+snap['worker_fingerprint'],period_key='BAD',original_snapshot_sha256='0'*64)
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            try:
                # runtime writer has no snapshot INSERT; admission writer is the
                # authorized boundary, tested below rather than treating ACL as hash PASS.
                pass
            finally:c.execute('ROLLBACK')
        with conn(ADMISSION,TEST_PASSWORD,autocommit=True,row_factory=dict_row) as c:
            for mutation in (dict(original_snapshot_sha256='0'*64),dict(original_snapshot_bytes=b'FORGED',original_snapshot_sha256=hashlib.sha256(b'FORGED').hexdigest())):
                bad=snap|dict(snapshot_ref='decision-snapshot:BAD:'+snap['worker_fingerprint'],period_key='BAD')|mutation
                c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
                try:
                    with self.assertRaises(psycopg.Error):self._insert(c,'wa_info.agent_snapshot',bad)
                finally:c.execute('ROLLBACK')
            r=c.execute("SELECT * FROM wa_info.receipt WHERE run_id='QUAL-RUN-A' ORDER BY receipt_id LIMIT 1").fetchone()
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            try:
                with self.assertRaises(psycopg.errors.ForeignKeyViolation):self._insert(c,'wa_info.receipt',r|dict(receipt_id='FORGED_RECEIPT',resolved_value_hash='f'*64))
            finally:c.execute('ROLLBACK')
            f=c.execute("SELECT * FROM wa_info.agent_fact WHERE run_id='QUAL-RUN-A' AND actor_id='AGENT-A' AND effective_time=0").fetchone()
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            try:
                # Change the source value in the normalized safe index, while
                # retaining a real admitted receipt: laundering must fail.
                with self.assertRaisesRegex(psycopg.Error,'invalid Agent snapshot fact'):self._insert(c,'wa_info.agent_fact',f|dict(value_lexeme='HIDDEN_WORLD_FORGED'))
            finally:c.execute('ROLLBACK')
        e=dict(run_id='QUAL-RUN-A',envelope_id='QUAL_E0',event_ordinal=0,record_version='QUAL',scheduled_event_id='QUAL',epoch_id='QUAL',actor_ref='AGENT-A',process_ref='QUAL',action_ref='QUAL',world_context='REALIZED',context_id='QUAL-RUN-A',perspective='GOVERNANCE',time_basis='SIM_TIME',effective_time=0,realized_time=0,effective_time_lexeme='0',realized_time_lexeme='0',reason_code='QUAL',original_envelope_bytes=b'complete envelope bytes',original_envelope_sha256=hashlib.sha256(b'complete envelope bytes').hexdigest(),original_hash_material=b'original digest tuple',envelope_hash=hashlib.sha256(b'original digest tuple').hexdigest(),previous_trace_hash='',pre_domain_hash='0'*64,post_domain_hash='1'*64)
        with conn(RUNTIME,TEST_PASSWORD,autocommit=True) as c:
            for col in ('original_envelope_sha256','envelope_hash'):
                c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
                try:
                    with self.assertRaises(psycopg.errors.CheckViolation):self._insert(c,'wa_run.causal_envelope',e|{col:'f'*64})
                finally:c.execute('ROLLBACK')
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE');self._insert(c,'wa_run.causal_envelope',e);c.execute('COMMIT')
            self.assertNotEqual(e['original_envelope_sha256'],e['envelope_hash'])
            self.assertEqual(c.execute("SELECT count(*) FROM wa_run.causal_envelope WHERE envelope_id='QUAL_E0'").fetchone()[0],1)

    def test_store_read_and_world_routes(self):
        with conn(REFERENCE,TEST_PASSWORD) as c:
            location=read_catalog_location(c,'MOON','CABEU')
            self.assertEqual(str(location[0]),'9426049d-f5f8-5146-9eca-be36f8c4bc32')
            good=self.science['GOOD']
            values=read_admitted_constraints(c,[good['assertion_id']],99,'QUAL_USE',[good['support_id']],consumer='QUAL_GENERATOR',context='REAL',perspective='WORLD_SIM')
            self.assertEqual(values[0]['standing'],'ADMITTED')
            with self.assertRaisesRegex(IntegrityFailure,'BLOCKED_SCIENCE_ADMISSION'):read_admitted_constraints(c,[self.science['CANDIDATE']['assertion_id']],99,'QUAL_USE',[self.science['CANDIDATE']['support_id']],consumer='QUAL_GENERATOR',context='REAL',perspective='WORLD_SIM')
            with self.assertRaisesRegex(IntegrityFailure,'BLOCKED_SCOPE'):read_admitted_constraints(c,[good['assertion_id']],99,'QUAL_USE',[self.other_support],consumer='QUAL_GENERATOR',context='REAL',perspective='WORLD_SIM')
        with conn(WORLD,TEST_PASSWORD,autocommit=True,row_factory=dict_row) as c:
            r=c.execute('SELECT * FROM wa_world.realization WHERE world_id=%s',(self.worlds[99],)).fetchone()
        r.update(world_id=uuid.UUID(int=0xb777),semantic_key='QUAL_STORE_WORLD')
        with conn(WORLD,TEST_PASSWORD) as c:self.assertEqual(install_exact_world(c,[('wa_world.realization',r)]),'INSERTED')
        with conn(WORLD,TEST_PASSWORD) as c:self.assertEqual(install_exact_world(c,[('wa_world.realization',r)]),'ALREADY_MATCHED')
        with conn(WORLD,TEST_PASSWORD) as c:
            with self.assertRaises(CollisionFailure):install_exact_world(c,[('wa_world.realization',r|{'world_seed_lexeme':'FORGED'})])
        with conn(AGENT,TEST_PASSWORD) as c:
            with self.assertRaises(RoleViolation):read_catalog_location(c,'MOON','CABEU')

    def test_store_fixture_admission_separate_roles(self):
        from loom_world_authority.etl import canonical,SOURCE_SHA
        a=self.science['CANDIDATE']
        tm=dict(kind='LEXICAL',time_lexeme='2',start_lexeme=None,end_lexeme=None,calendar_ref=None,timescale_ref='SIM_TIME',instant_utc=None,interval_utc=None,parsing_warrant_ref=None)
        manifest=dict(profile='WA_FIXTURE_ADMISSION_MANIFEST_V1',assertion_id=str(a['assertion_id']),assertion_metadata_sha256=a['metadata_sha256'],support_id=str(a['support_id']),source_snapshot_sha256=SOURCE_SHA,initial_standing='CANDIDATE',use_contract_ref='QUAL_SEPARATE_FIXTURE',authorization_ref='QUAL_SECURITY_ONLY',decision_ordinal=10,standing='ADMITTED',effective_availability_lexeme='2',time_support=tm)
        mh=sha256_bytes(canonical(manifest));tid=stable_uuid('TIME_SUPPORT','LOOM_WORLD_AUTHORITY_V1','BUILD6E_FIXTURE_ADMISSION:10',mh)
        with conn(GOVERNOR,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'FIXTURE_TIME_METADATA_MISMATCH'):record_fixture_admission(c,manifest)
        with conn(WRITER,TEST_PASSWORD,autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE');self._insert(c,'wa_geo.time_support',dict(time_id=tid,**tm));c.execute('COMMIT')
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute('SET ROLE wa_science_governor')
        with conn(GOVERNOR,TEST_PASSWORD) as c:self.assertEqual(record_fixture_admission(c,manifest),'INSERTED')
        with conn(GOVERNOR,TEST_PASSWORD) as c:self.assertEqual(record_fixture_admission(c,manifest),'ALREADY_MATCHED')
        with conn(GOVERNOR,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute('INSERT INTO wa_geo.time_support DEFAULT VALUES')
        with conn(AGENT,TEST_PASSWORD) as c:
            with self.assertRaises(RoleViolation):record_fixture_admission(c,manifest)

    def test_store_atomic_epoch_and_private_replay(self):
        run='QUAL-RUN-B';epoch='QUAL_STORE_EPOCH';rows=[];refs=[]
        for kind,payload in (('QUAL_TERMINAL_EPOCH',b'complete epoch original'),('QUAL_TERMINAL_RESULT',b'complete result original')):
            h=sha256_bytes(payload);ref=kind+':'+h;refs.append(ref)
            rows.append(('wa_run.artifact',dict(run_id=run,artifact_ref=ref,record_kind=kind,serializer_ref='QUAL',payload_bytes=payload,payload_sha256=h)))
        e=dict(run_id=run,envelope_id='QUAL_STORE_E0',event_ordinal=0,record_version='QUAL',scheduled_event_id='QUAL',epoch_id=epoch,actor_ref='AGENT-B',process_ref='QUAL',action_ref='QUAL',world_context='REALIZED',context_id=run,perspective='GOVERNANCE',time_basis='SIM_TIME',effective_time=0,realized_time=0,effective_time_lexeme='0',realized_time_lexeme='0',reason_code='QUAL',original_envelope_bytes=b'complete neutral epoch envelope',original_envelope_sha256=sha256_bytes(b'complete neutral epoch envelope'),original_hash_material=b'neutral epoch digest tuple',envelope_hash=sha256_bytes(b'neutral epoch digest tuple'),previous_trace_hash='',pre_domain_hash='0'*64,post_domain_hash='1'*64)
        rows.append(('wa_run.causal_envelope',e))
        for i,ref in enumerate(refs):rows.append(('wa_run.trace_artifact_edge',dict(run_id=run,envelope_id=e['envelope_id'],edge_role='QUAL_TERMINAL',edge_ordinal=i,artifact_ref=ref)))
        bad=rows[:-1]
        with conn(EXECUTOR,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'EPOCH_TERMINAL_TRACE_CLOSURE'):persist_epoch(c,run,epoch,None,bad,refs)
        with conn(AUDITOR,TEST_PASSWORD,autocommit=True) as c:self.assertEqual(c.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s',(run,)).fetchone()[0],0)
        with conn(EXECUTOR,TEST_PASSWORD) as c:self.assertEqual(persist_epoch(c,run,epoch,None,rows,refs),'COMMITTED')
        with conn(EXECUTOR,TEST_PASSWORD) as c:self.assertEqual(persist_epoch(c,run,epoch,None,rows,refs),'ALREADY_MATCHED')
        with conn(AUDITOR,TEST_PASSWORD) as c:
            prefix=read_replay_prefix(c,run,input_snapshot_ref='QUAL',code_contract='QUAL',code_tree_sha256='0'*64)
            self.assertEqual(len(prefix['envelopes']),1)
            a=export_run(c,run,input_snapshot_ref='QUAL',code_contract='QUAL',code_tree_sha256='0'*64)
            b=export_run(c,run,input_snapshot_ref='QUAL',code_contract='QUAL',code_tree_sha256='0'*64)
            self.assertEqual(a,b)
        # A same-epoch extra envelope is hostile partial/replay corruption.
        # Keep it in the replay transaction so failure must roll it back.
        rogue_bytes=b'rogue extra envelope'
        rogue_material=b'rogue extra envelope hash material'
        rogue=e|dict(envelope_id='QUAL_STORE_E1',event_ordinal=1,realized_time=1,realized_time_lexeme='1',pre_domain_hash=e['post_domain_hash'],post_domain_hash='2'*64,original_envelope_bytes=rogue_bytes,original_envelope_sha256=sha256_bytes(rogue_bytes),original_hash_material=rogue_material,envelope_hash=sha256_bytes(rogue_material),previous_trace_hash=e['envelope_hash'])
        with conn(EXECUTOR,TEST_PASSWORD) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            self._insert(c,'wa_run.causal_envelope',rogue)
            with self.assertRaisesRegex(IntegrityFailure,'EPOCH_REPLAY_ENVELOPE_SET_MISMATCH'):
                persist_epoch(c,run,epoch,None,rows,refs)
        with conn(AUDITOR,TEST_PASSWORD) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM wa_run.causal_envelope WHERE run_id=%s AND epoch_id=%s',(run,epoch)).fetchone()[0],1)
        with conn(AGENT,TEST_PASSWORD) as c:
            with self.assertRaises(RoleViolation):export_run(c,run,input_snapshot_ref='QUAL',code_contract='QUAL',code_tree_sha256='0'*64)

    def test_writer_digest_succeeds(self):
        with conn(WRITER,TEST_PASSWORD,autocommit=True) as c:
            got=c.execute("SELECT encode(wa_crypto.digest('x'::bytea,'sha256'),'hex')").fetchone()[0]
        self.assertEqual(got,"2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881")

    @staticmethod
    def _authored_manifest(suffix='01'):
        return dict(profile='WA_AUTHORED_SITE_METADATA_V1',authorization_ref='WA-OWNER-2026-10-06-01:BUILD6E_QUALIFICATION_FIXTURE',
                    identity_authority='LOOM_BUILD6E_NAMED_WORLD_V1',body_key='MOON',parent_location_key='CABEU',
                    site_key='B6E_MOON_CABEU_SITE_'+suffix,site_name='Moon — Cabeus authored site '+suffix,
                    feature_key='B6E_MOON_CABEU_LOCAL_FEATURE'+suffix,feature_name='Authored local feature '+suffix,
                    unit_key='MODEL_RESOURCE_UNIT_BY_FAMILY')

    def test_onboarding_exact_authored_site_and_science_separation(self):
        manifest=self._authored_manifest()
        with conn(AUDITOR,TEST_PASSWORD) as c:
            before=c.execute('SELECT count(*) FROM wa_science.admission').fetchone()[0]
            candidate=c.execute("SELECT initial_standing FROM wa_science.assertion WHERE semantic_key='R_MOON_CAB_WATER'").fetchone()
            parent=c.execute("SELECT location_kind,original_region_type FROM wa_geo.location WHERE semantic_key='CABEU' AND body_id=%s",(self.body,)).fetchone()
        self.assertEqual(parent,('SITE','LOCAL_SITE'))
        self.assertEqual(candidate,('CANDIDATE',))
        with conn(WRITER,TEST_PASSWORD) as c:status,site_id,feature_id=install_authored_site_metadata(c,manifest)
        self.assertEqual(status,'INSERTED')
        with conn(WRITER,TEST_PASSWORD) as c:self.assertEqual(install_authored_site_metadata(c,manifest),('ALREADY_MATCHED',site_id,feature_id))
        with conn(REFERENCE,TEST_PASSWORD) as c:
            site=read_catalog_location(c,'MOON',manifest['site_key'])
            self.assertEqual((site[5],site[8],site[9],site[10]),(site_id,'SITE','AUTHORED_SPATIAL_ANCHOR',None))
            feature=read_catalog_location(c,'MOON',manifest['feature_key'])
            self.assertEqual((feature[5],feature[8],feature[9],feature[10]),(feature_id,'LOCAL_FEATURE','AUTHORED_SPATIAL_ANCHOR',None))
        with conn(AUDITOR,TEST_PASSWORD) as c:
            relations=c.execute('SELECT relation_kind,warrant_ref FROM wa_geo.location_relation WHERE to_location_id IN (%s,%s) ORDER BY to_location_id',(site_id,feature_id)).fetchall()
            self.assertEqual(len(relations),2)
            self.assertTrue(all(k=='CONTAINS' and manifest['authorization_ref'] in w for k,w in relations))
            self.assertEqual(c.execute('SELECT count(*) FROM wa_science.admission').fetchone()[0],before)
            self.assertEqual(c.execute("SELECT initial_standing FROM wa_science.assertion WHERE semantic_key='R_MOON_CAB_WATER'").fetchone(),candidate)
            self.assertEqual(c.execute("SELECT interpretation_state FROM wa_meta.unit WHERE unit_key='MODEL_RESOURCE_UNIT_BY_FAMILY'").fetchone(),('UNCHARACTERIZED',))

    def test_onboarding_collisions_atomicity_and_scope(self):
        manifest=self._authored_manifest('02')
        with conn(WRITER,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'AUTHORED_SITE_PARENT_NOT_EMPIRICAL'):
                install_authored_site_metadata(c,manifest|{'body_key':'MARS'})
        with conn(WRITER,TEST_PASSWORD,autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            self._insert(c,'wa_geo.location',dict(location_id=uuid.UUID(int=0xb6e001),body_id=self.body,system_id=None,
                semantic_key='QUAL_FORGED_EMPIRICAL_PARENT',name='forged parent',location_kind='SITE',
                original_region_type='LOCAL_SITE',origin_kind='EMPIRICALLY_IDENTIFIED',geometry_id=None,
                source_ref='FORGED_NOT_MIGRATED',notes=None))
            c.execute('COMMIT')
        with conn(WRITER,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'AUTHORED_SITE_PARENT_NOT_EMPIRICAL'):
                install_authored_site_metadata(c,manifest|{'parent_location_key':'QUAL_FORGED_EMPIRICAL_PARENT'})
        with conn(AUDITOR,TEST_PASSWORD) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM wa_geo.location WHERE semantic_key=%s',(manifest['site_key'],)).fetchone()[0],0)
        with conn(WRITER,TEST_PASSWORD) as c:status,site_id,feature_id=install_authored_site_metadata(c,manifest)
        self.assertEqual(status,'INSERTED')
        with conn(WRITER,TEST_PASSWORD) as c:
            with self.assertRaises(CollisionFailure):install_authored_site_metadata(c,manifest|{'site_name':'forged name'})
        with conn(AUDITOR,TEST_PASSWORD) as c:
            self.assertEqual(c.execute('SELECT name FROM wa_geo.location WHERE location_id=%s',(site_id,)).fetchone(),(manifest['site_name'],))
            self.assertEqual(c.execute('SELECT count(*) FROM wa_geo.location_relation WHERE to_location_id=%s',(feature_id,)).fetchone()[0],1)
        with conn(WRITER,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'AUTHORED_SITE_MANIFEST_FIELDS'):
                install_authored_site_metadata(c,manifest|{'sql':'DROP TABLE wa_geo.body'})

    def test_onboarding_fixture_time_is_not_admission(self):
        from loom_world_authority.etl import SOURCE_SHA
        a=self.science['CANDIDATE']
        tm=dict(kind='LEXICAL',time_lexeme='2',start_lexeme=None,end_lexeme=None,calendar_ref=None,timescale_ref='SIM_TIME',instant_utc=None,interval_utc=None,parsing_warrant_ref=None)
        manifest=dict(profile='WA_FIXTURE_ADMISSION_MANIFEST_V1',assertion_id=str(a['assertion_id']),assertion_metadata_sha256=a['metadata_sha256'],support_id=str(a['support_id']),source_snapshot_sha256=SOURCE_SHA,initial_standing='CANDIDATE',use_contract_ref='QUAL_SUCCESSOR_TIME',authorization_ref='WA-OWNER-2026-10-06-01:BUILD6E_QUALIFICATION_FIXTURE',decision_ordinal=2002,standing='ADMITTED',effective_availability_lexeme='2',time_support=tm)
        with conn(AUDITOR,TEST_PASSWORD) as c:before=c.execute('SELECT count(*) FROM wa_science.admission').fetchone()[0]
        with conn(WRITER,TEST_PASSWORD) as c:self.assertEqual(install_fixture_time_support(c,manifest),'INSERTED')
        with conn(WRITER,TEST_PASSWORD) as c:self.assertEqual(install_fixture_time_support(c,manifest),'ALREADY_MATCHED')
        with conn(AUDITOR,TEST_PASSWORD) as c:self.assertEqual(c.execute('SELECT count(*) FROM wa_science.admission').fetchone()[0],before)
        with conn(GOVERNOR,TEST_PASSWORD) as c:self.assertEqual(record_fixture_admission(c,manifest),'INSERTED')
        with conn(GOVERNOR,TEST_PASSWORD) as c:self.assertEqual(record_fixture_admission(c,manifest),'ALREADY_MATCHED')
        with conn(WRITER,TEST_PASSWORD) as c:
            with self.assertRaisesRegex(IntegrityFailure,'FIXTURE_TIME_METADATA'):
                install_fixture_time_support(c,manifest|{'time_support':tm|{'instant_utc':'2026-10-06'}})

    def test_onboarding_principal_boundaries(self):
        manifest=self._authored_manifest('03')
        for login in (AGENT,WORLD,RUNTIME,GOVERNOR,ADMISSION,EXECUTOR,REFERENCE):
            with conn(login,TEST_PASSWORD) as c:
                with self.assertRaises(RoleViolation):install_authored_site_metadata(c,manifest)
        from loom_world_authority.etl import SOURCE_SHA
        a=self.science['CANDIDATE']
        tm=dict(kind='LEXICAL',time_lexeme='2',start_lexeme=None,end_lexeme=None,calendar_ref=None,timescale_ref='SIM_TIME',instant_utc=None,interval_utc=None,parsing_warrant_ref=None)
        m=dict(profile='WA_FIXTURE_ADMISSION_MANIFEST_V1',assertion_id=str(a['assertion_id']),assertion_metadata_sha256=a['metadata_sha256'],support_id=str(a['support_id']),source_snapshot_sha256=SOURCE_SHA,initial_standing='CANDIDATE',use_contract_ref='QUAL_DENIED',authorization_ref='QUAL',decision_ordinal=2003,standing='ADMITTED',effective_availability_lexeme='2',time_support=tm)
        for login in (AGENT,WORLD,RUNTIME,GOVERNOR,ADMISSION,EXECUTOR,REFERENCE):
            with conn(login,TEST_PASSWORD) as c:
                with self.assertRaises(RoleViolation):install_fixture_time_support(c,m)
        with conn(AGENT,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute('SELECT 1 FROM wa_geo.location LIMIT 1')
        with conn(WORLD,TEST_PASSWORD,autocommit=True) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute("INSERT INTO wa_meta.unit(unit_key,source_lexeme,interpretation_state) VALUES ('FORGED','FORGED','UNCHARACTERIZED')")

if __name__=="__main__":
    unittest.main()
