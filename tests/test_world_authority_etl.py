"""Exact E01--E28 procedure. Real PostgreSQL fixtures supplied only by qualifier."""
import csv,hashlib,json,sqlite3,struct,subprocess,tempfile,unittest,uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import psycopg
from psycopg import sql
from loom_world_authority.etl import (canonical,canonical_legacy_row,decode_scalar,digest,number,plan_sqlite_import,inspect_source_schema,SOURCE_SHA,SOURCE_COMMIT,SOURCE_PATH,DOMAIN)
from loom_world_authority.store import (stable_uuid,length_prefixed,import_exact_snapshot,verify_source_projection,export_source,IntegrityFailure,CollisionFailure,TABLE_KEYS)
CTX=None
EXECUTED=set()

class WorldAuthorityETL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if CTX is None:raise unittest.SkipTest('Use tools/qualify_world_authority.py; no default database')
        cls.p=CTX['plan'];cls.a,cls.b=CTX['clusters'];cls.out=CTX['output']
    def mark(self,k):EXECUTED.add(k)
    def clone(self,k):return self.a.clone_empty(k)
    def require_failure(self,f):
        with self.assertRaises(Exception):f()
    def scalar_count(self,cluster,db,table):
        with cluster.connect(db,autocommit=True) as c:return c.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(*table.split('.')))).fetchone()[0]
    def copy_source(self,tmp):
        p=Path(tmp)/'source.sqlite3';p.write_bytes(self.p.source_file.read_bytes());return p

    def test_E01_exact_source(self):
        self.mark('E01')
        for kw in ({'source_commit':'0'*40},{'source_path':'other.sqlite3'},{'expected_sha':'0'*64}):
            with self.assertRaisesRegex(IntegrityFailure,'SOURCE_DRIFT'):plan_sqlite_import(self.p.source_file,**kw)
        with tempfile.TemporaryDirectory() as d:
            p=self.copy_source(d);p.write_bytes(p.read_bytes()[:-1])
            with self.assertRaisesRegex(IntegrityFailure,'SOURCE_DRIFT'):plan_sqlite_import(p)
        with sqlite3.connect(self.p.source_file.as_uri()+'?mode=ro&immutable=1',uri=True) as c:
            with self.assertRaises(sqlite3.OperationalError):c.execute('CREATE TABLE qualification_write_forbidden (x)')
        self.assertEqual(hashlib.sha256(self.p.source_file.read_bytes()).hexdigest(),SOURCE_SHA)

    def test_E02_source_schema(self):
        self.mark('E02')
        for mutation in ('CREATE TABLE extra (x)','ALTER TABLE body ADD COLUMN extra TEXT','DROP TABLE lab_meta'):
            with tempfile.TemporaryDirectory() as d:
                p=self.copy_source(d)
                with sqlite3.connect(p) as c:c.execute(mutation)
                with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
                    with self.assertRaisesRegex(IntegrityFailure,'SOURCE_SCHEMA_DRIFT'):inspect_source_schema(c,self.p.source_schema)
        with tempfile.TemporaryDirectory() as d:
            p=self.copy_source(d)
            with sqlite3.connect(p) as c:
                # Insert a real complete skeleton row, not a mocked catalog.
                cols=c.execute('PRAGMA table_info(generation_model)').fetchall()
                values=[1 if col[2].upper().startswith('INTEGER') else 'QUAL' for col in cols]
                c.execute('INSERT INTO generation_model VALUES ('+','.join('?' for _ in values)+')',values)
            with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
                with self.assertRaisesRegex(IntegrityFailure,'NONEMPTY_WORLD_SKELETON'):inspect_source_schema(c,self.p.source_schema)

    def test_E03_integrity(self):
        self.mark('E03')
        with tempfile.TemporaryDirectory() as d:
            p=self.copy_source(d)
            with sqlite3.connect(p) as c:c.execute("UPDATE scientific_assertion SET body_id='NO_SUCH_BODY' WHERE assertion_id=1")
            with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
                with self.assertRaisesRegex(IntegrityFailure,'SOURCE_INTEGRITY'):inspect_source_schema(c,self.p.source_schema)
            p.write_bytes(b'not a sqlite database')
            with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
                with self.assertRaises(sqlite3.DatabaseError):inspect_source_schema(c,self.p.source_schema)

    def test_E04_fresh_install(self):
        self.mark('E04')
        # First cluster is installed here after genuine failure/collision probes.
        # E05/E06 execute inside this test before the only successful install.
        self._install_collision_and_failure()
        for c in (self.a,self.b):
            c.install(CTX['ddl']);c.ready=True
            inv=c.inventory();s=inv['settings']
            self.assertTrue(s['server_version'].startswith('18.6 '));self.assertEqual([s[k] for k in ('server_encoding','lc_collate','lc_ctype','timezone','standard_conforming_strings')],['UTF8','C','C','UTC','on']);self.assertEqual(inv['extensions'],[('pgcrypto','1.4')]);self.assertTrue(inv['psql_version'].startswith('psql (PostgreSQL) 18.6'));self.assertTrue(inv['postgres_binary_version'].startswith('postgres (PostgreSQL) 18.6'))
            self.assertEqual(len(inv['tables']),77)
            for schema,table,owner,rls,forced in inv['tables']:
                self.assertEqual(owner,'wa_owner')
                if schema in ('wa_world','wa_run','wa_info'):self.assertTrue(rls and forced,(schema,table))
                self.assertEqual(self.scalar_count(c,None,schema+'.'+table),0)
            with c.connect(autocommit=True) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM pg_attrdef WHERE adrelid IN (SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname LIKE 'wa_%') AND (pg_get_expr(adbin,adrelid) ~* 'uuid|random|nextval')").fetchone()[0],0)
                db.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
                db.execute("INSERT INTO wa_meta.design_version VALUES ('LOOM_WORLD_AUTHORITY_V1',%s,%s,'788f31c200ce59e844e44ef01ca62f37eb129bd8','2fca1d9efd6b50455a68db3618c0ef408d758d4b',current_user,clock_timestamp())",(CTX['manifest']['ddl_sha256'],hashlib.sha256((DOMAIN.parents[1]/'docs/database_semantics/world_authority/SEMANTIC_CONTRACT.md').read_bytes()).hexdigest()))
                db.execute('COMMIT')
        with self.a.connect(role='wa_etl_login') as c:self.assertEqual(import_exact_snapshot(c,self.p),'IMPORTED')
        with self.b.connect(role='wa_etl_login') as c:self.assertEqual(import_exact_snapshot(c,self.p),'IMPORTED')

    def _install_collision_and_failure(self):
        self.mark('E05');self.mark('E06')
        for collision in ('role','schema','extension'):
            with self.a.connect(autocommit=True) as c:
                c.execute({'role':'CREATE ROLE wa_owner','schema':'CREATE SCHEMA wa_meta','extension':'CREATE EXTENSION pgcrypto'}[collision])
            r=self.a.psql(CTX['ddl']);self.assertNotEqual(r.returncode,0)
            with self.a.connect(autocommit=True) as c:
                c.execute({'role':'DROP ROLE wa_owner','schema':'DROP SCHEMA wa_meta','extension':'DROP EXTENSION pgcrypto'}[collision])
                self.assertEqual(c.execute("SELECT count(*) FROM pg_roles WHERE rolname LIKE 'wa_%'").fetchone()[0],0)
                self.assertEqual(c.execute("SELECT count(*) FROM pg_namespace WHERE nspname LIKE 'wa_%'").fetchone()[0],0)
        original=CTX['ddl'];point=original.index(b'CREATE TABLE wa_science.source (')
        r=self.a.psql(original[:point]+b'SELECT 1/0;\n'+original[point:]);self.assertNotEqual(r.returncode,0)
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM pg_roles WHERE rolname LIKE 'wa_%'").fetchone()[0],0)
            self.assertEqual(c.execute("SELECT count(*) FROM pg_extension WHERE extname='pgcrypto'").fetchone()[0],0)
    def test_E05_collision_recorded(self):self.assertIn('E05',EXECUTED)
    def test_E06_rollback_recorded(self):self.assertIn('E06',EXECUTED)

    def test_E07_identity_vectors(self):
        self.mark('E07')
        vectors={'MOON':'9426049d-f5f8-5146-9eca-be36f8c4bc32','MARS':'8d40f6b7-d4f2-543c-8bf6-257de8d41c9e','CERES':'4292aec6-6341-524f-b9f0-d715b070472c','BENNU':'8b4641bf-e70e-567e-b6de-e1c0754bc271'}
        for key,value in vectors.items():self.assertEqual(str(stable_uuid('BODY','LOOM_BODY_V1',key,'IDENTITY_V1')),value)
        self.assertEqual(str(stable_uuid('LOCATION','LOOM_LOCATION_V1',length_prefixed('MOON','CABEU').decode(),'IDENTITY_V1')),'cac223e4-0f64-502f-8744-c2173446ee5c')
        self.assertEqual(length_prefixed('é'),b'2:\xc3\xa9')
        obj,_,_=canonical_legacy_row(['integer'],[123]);self.assertEqual(obj['integer'],{'ordinal':0,'storage_class':'INTEGER','integer_lexeme':'123'})
        self.assertNotEqual(stable_uuid('A','B','é','D'),stable_uuid('A','B','e\u0301','D'))

    def test_E08_complete_raw_reconstruction(self):
        self.mark('E08')
        with self.a.connect(autocommit=True) as c:
            raw=c.execute('SELECT table_name,source_key,original_columns,row_digest FROM wa_meta.legacy_row WHERE snapshot_id=%s ORDER BY table_name,source_key',(self.p.snapshot_id,)).fetchall()
        # Independent oracle: reopen the pinned SQLite bytes directly. It does
        # not consume ImportPlan.source_rows or the production raw-row encoder.
        def canonical_oracle(value):
            def encode(v):
                if isinstance(v,(bytes,bytearray,memoryview)):return {'bytea_hex':bytes(v).hex()}
                raise TypeError(type(v).__name__)
            return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False,default=encode).encode('utf8')
        def tagged(value,ordinal):
            cell={'ordinal':ordinal}
            if value is None:cell['storage_class']='NULL'
            elif isinstance(value,int):cell.update(storage_class='INTEGER',integer_lexeme=str(value))
            elif isinstance(value,float):cell.update(storage_class='REAL',ieee754_be64=struct.pack('>d',value).hex(),display_lexeme=repr(value))
            elif isinstance(value,str):cell.update(storage_class='TEXT',utf8_hex=value.encode('utf8').hex(),text=value)
            elif isinstance(value,bytes):cell.update(storage_class='BLOB',bytes_hex=value.hex())
            else:self.fail('unhandled SQLite storage type: '+type(value).__name__)
            return cell
        path=self.p.source_file
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),SOURCE_SHA)
        source_uri=path.as_uri()+'?mode=ro&immutable=1'
        expected_counts=json.loads((DOMAIN/'SOURCE_COUNTS_V1.json').read_text())
        pinned_schema=json.loads((DOMAIN/'SOURCE_SCHEMA_V1.json').read_text())
        oracle_rows={};oracle_counts={};cells=0
        with sqlite3.connect(source_uri,uri=True) as source_db:
            self.assertEqual(source_db.execute('PRAGMA integrity_check').fetchone(),('ok',))
            self.assertEqual(list(source_db.execute('PRAGMA foreign_key_check')),[])
            names=[r[0] for r in source_db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            actual_schema={name:[list(v) for v in source_db.execute('PRAGMA table_info("'+name+'")')] for name in names}
            self.assertEqual(actual_schema,pinned_schema)
            self.assertEqual(sum(len(cols) for cols in actual_schema.values()),256)
            for table,metadata in actual_schema.items():
                columns=[c[1] for c in metadata]
                pk=[c[1] for c in sorted(metadata,key=lambda c:c[5]) if c[5]]
                if table=='assertion_input':pk=columns
                query='SELECT '+','.join('"'+c+'"' for c in columns)+' FROM "'+table+'" ORDER BY '+','.join('"'+c+'"' for c in pk)
                table_count=0
                for values in source_db.execute(query):
                    obj={col:tagged(value,i) for i,(col,value) in enumerate(zip(columns,values,strict=True))}
                    key='ROWKEY_V1:'+canonical_oracle([obj[col] for col in pk]).decode('utf8')
                    row_digest=hashlib.sha256(canonical_oracle(obj)).hexdigest()
                    oracle_rows[(table,key)]=(obj,row_digest)
                    table_count+=1;cells+=len(columns)
                oracle_counts[table]=table_count
        self.assertEqual(oracle_counts,expected_counts)
        self.assertEqual(sum(oracle_counts.values()),2726)
        self.assertEqual(len(raw),2726)
        actual={(table,key):(obj,row_digest) for table,key,obj,row_digest in raw}
        self.assertEqual(set(actual),set(oracle_rows),'source-key set differs from raw preservation layer')
        for identity,expected in oracle_rows.items():self.assertEqual(actual[identity],expected,identity)
        self.assertEqual(cells,sum(n*len(actual_schema[t]) for t,n in oracle_counts.items()))
        matrix=list(csv.DictReader((DOMAIN/'SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').open()))
        columns={(t,c[1]) for t,cs in actual_schema.items() for c in cs}
        mapped={(r['sqlite_table'],r['sqlite_concept_or_column']) for r in matrix if r['sqlite_concept_or_column']!='TABLE' and r['sqlite_table'] in actual_schema}
        self.assertEqual(columns,mapped);self.assertEqual(len(mapped),256)
        (self.out/'SOURCE_COMPLETENESS.json').write_bytes(canonical(dict(source_rows=2726,columns=256,reconstructed_cells=cells,dispositions_sha256=hashlib.sha256((DOMAIN/'SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').read_bytes()).hexdigest()))+b'\n')

    def test_E09_numeric_fidelity(self):
        self.mark('E09')
        values=[5.6,1e-300,-0.0,123,None]
        obj,_,_=canonical_legacy_row([str(i) for i in range(len(values))],values)
        for i,v in enumerate(values):
            z=decode_scalar(obj[str(i)])
            if isinstance(v,float):self.assertEqual(struct.pack('>d',v),struct.pack('>d',z));self.assertEqual(number(v),Decimal(repr(v)))
            else:self.assertEqual(z,v)
        with self.a.connect(autocommit=True) as c:
            self.assertTrue(c.execute("SELECT bool_and(value_numeric IS NULL OR value_numeric::text NOT IN ('NaN','Infinity','-Infinity')) FROM wa_science.assertion").fetchone()[0])

    def test_E10_unknown_payload(self):
        self.mark('E10')
        assertions=[r for r in self.p.rows if r.table=='wa_science.assertion']
        source={r['assertion_key']:r for r in self.p.source_rows['scientific_assertion']}
        explanatory=[];unknown_with_report=0
        for row in assertions:
            v=row.values;r=source[v['semantic_key']]
            self.assertEqual(v['epistemic_class_lexeme'],r['epistemic_class']);self.assertEqual(v['value_kind'],r['value_kind'])
            self.assertEqual(v['value_numeric'],number(r['value_numeric']))
            if r['value_kind']=='UNKNOWN' and r['value_text'] is not None:
                self.assertIsNone(v['value_text']);explanatory.append(r['assertion_key'])
                self.assertIn(b'FORENSIC_ONLY_EXPLANATORY_TEXT_WHEN_VALUE_KIND_UNKNOWN',v['metadata_bytes'])
            else:self.assertEqual(v['value_text'],r['value_text'])
            if r['epistemic_class']=='UNKNOWN' and any(r[k] is not None for k in ('value_numeric','value_text','value_min','value_max')):unknown_with_report+=1
        self.assertEqual(len(explanatory),4);self.assertGreater(unknown_with_report,0)
        self.test_E08_complete_raw_reconstruction()

    def test_E11_units(self):
        self.mark('E11')
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM wa_meta.unit').fetchone()[0],25)
            for lexeme,dim,conv in c.execute('SELECT source_lexeme,dimension_ref,conversion_profile_ref FROM wa_meta.unit'):
                self.assertIsNone(dim);self.assertIsNone(conv);self.assertIsInstance(lexeme,str)
            self.assertEqual(c.execute("SELECT count(*) FROM wa_science.assertion WHERE (unit_key IS NULL)<>(unit_state='NOT_SUPPLIED')").fetchone()[0],0)
        # Every supplied source rate token remains lexical; none gets a stock dimension.
        self.assertTrue(all(r.values['interpretation_state']=='UNCHARACTERIZED' for r in self.p.rows if r.table=='wa_meta.unit'))

    def test_E12_times(self):
        self.mark('E12')
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(dict(c.execute('SELECT kind,count(*) FROM wa_geo.time_support GROUP BY kind').fetchall()),{'UNKNOWN':22,'LEXICAL':617})
            self.assertEqual(c.execute('SELECT count(*) FROM wa_geo.time_support WHERE instant_utc IS NOT NULL OR interval_utc IS NOT NULL OR parsing_warrant_ref IS NOT NULL').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM wa_science.assertion WHERE knowledge_time_id IS NOT NULL').fetchone()[0],0)

    def test_E13_vertical(self):
        self.mark('E13')
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM wa_geo.vertical_support').fetchone()[0],17)
            self.assertEqual(c.execute("SELECT count(*) FROM wa_geo.vertical_support WHERE coordinate_kind NOT IN ('ALTITUDE','DEPTH_BELOW_SURFACE','PRESSURE_LEVEL','UNKNOWN','NONE')").fetchone()[0],0)
            for table in ('wa_science.observation','wa_science.spatial_product'):
                rows=[r for r in self.p.rows if r.table==table]
                self.assertTrue(any('vertical_sensitivity_min' in r.values for r in rows))
        self.test_E19_full_projection()

    def test_E14_scope(self):
        self.mark('E14')
        expected={}
        for r in self.p.rows:
            if r.table=='wa_science.support':
                k=(r.values['scope_kind'],r.values['support_resolution']);expected[k]=expected.get(k,0)+1
        with self.a.connect(autocommit=True) as c:
            self.assertEqual({(k,v):n for k,v,n in c.execute('SELECT scope_kind,support_resolution,count(*) FROM wa_science.support GROUP BY 1,2')},expected)
            self.assertGreater(c.execute("SELECT count(*) FROM wa_science.support WHERE support_resolution='UNRESOLVED'").fetchone()[0],0)
            self.assertEqual(c.execute("SELECT count(*) FROM wa_science.support WHERE scope_kind='SAMPLE' AND sample_id IS NULL AND support_resolution<>'UNRESOLVED'").fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM wa_science.sample').fetchone()[0],4)
        (self.out/'SOURCE_SCOPE_COUNTS.json').write_bytes(canonical([{'scope':k[0],'resolution':k[1],'count':n} for k,n in sorted(expected.items())])+b'\n')

    def test_E15_ontology(self):
        self.mark('E15')
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(dict(c.execute('SELECT ontology,count(*) FROM wa_science.assertion GROUP BY 1')) ,{'REAL_EVIDENCE':432,'MODEL_INFERENCE':398,'DERIVED':50})
            self.assertEqual(c.execute("SELECT count(*) FROM wa_science.assertion WHERE world_context<>'REAL'").fetchone()[0],0)

    def test_E16_custody(self):
        self.mark('E16')
        with self.a.connect(autocommit=True) as c:
            self.assertEqual(dict(c.execute('SELECT custody_kind,count(*) FROM wa_science.source_artifact GROUP BY 1')),{'LOOM_FROZEN':43,'REMOTE_REFERENCE_ONLY':161})
            self.assertEqual(c.execute("SELECT count(*) FROM wa_science.source_artifact WHERE custody_kind='REMOTE_REFERENCE_ONLY' AND (byte_sha256 IS NOT NULL OR byte_count IS NOT NULL)").fetchone()[0],0)

    def test_E17_zero_admissions(self):
        self.mark('E17')
        for cluster in (self.a,self.b):
            with cluster.connect(autocommit=True) as c:
                self.assertEqual(c.execute("SELECT count(*) FROM wa_science.assertion WHERE initial_standing='CANDIDATE'").fetchone()[0],880)
                self.assertEqual(c.execute("SELECT count(*) FROM wa_science.material_evidence WHERE initial_standing='CANDIDATE'").fetchone()[0],35)
                tables=[n+'.'+t for n,t in c.execute("SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND (n.nspname IN ('wa_world','wa_run','wa_info') OR (n.nspname='wa_science' AND c.relname IN ('admission','extrapolation')))")]
                for t in tables:self.assertEqual(c.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(*t.split('.')))).fetchone()[0],0,t)

    def test_E18_competing_claims(self):
        self.mark('E18')
        with self.a.connect(autocommit=True) as c:
            pair=c.execute('SELECT assertion_a,assertion_b,classification_lexeme,reason,status_lexeme FROM wa_science.reconciliation').fetchone()
            self.assertIsNotNone(pair);self.assertNotEqual(pair[0],pair[1]);self.assertEqual(c.execute('SELECT count(*) FROM wa_science.assertion WHERE assertion_id IN (%s,%s)',pair[:2]).fetchone()[0],2)
        self.test_E19_full_projection()

    def test_E19_full_projection(self):
        self.mark('E19')
        with self.a.connect(autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE READ ONLY');result=verify_source_projection(c,self.p)
            self.assertEqual(result['planned_target_rows'],7126)
            expected={t:sum(r.table==t for r in self.p.rows) for t in TABLE_KEYS}
            for t,n in expected.items():self.assertEqual(c.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(*t.split('.')))).fetchone()[0],n,t)
            self.assertEqual(c.execute("SELECT count(*) FROM pg_constraint co JOIN pg_namespace n ON n.oid=co.connamespace WHERE n.nspname LIKE 'wa_%' AND NOT co.convalidated").fetchone()[0],0)
            for mb,h in c.execute('SELECT metadata_bytes,metadata_sha256 FROM wa_science.assertion'):self.assertEqual(hashlib.sha256(bytes(mb)).hexdigest(),h)
            c.execute('ROLLBACK')

    def test_E20_every_family_rollback(self):
        self.mark('E20')
        db=self.clone('rollback')
        for table in TABLE_KEYS:
            if not any(r.table==table for r in self.p.rows):continue
            with self.a.connect(db,role='wa_etl_login') as c:
                with self.assertRaisesRegex(IntegrityFailure,'QUALIFICATION_INJECTED_FAILURE'):import_exact_snapshot(c,self.p,failure_after_table=table)
            with self.a.connect(db,autocommit=True) as c:
                for t in TABLE_KEYS:self.assertEqual(c.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier(*t.split('.')))).fetchone()[0],0,t)
            print('E20 rolled back after',table,flush=True)

    def test_E21_repeat_zero_writes(self):
        self.mark('E21')
        with self.a.connect() as c:before=export_source(c,self.p,self.out/'export_a_before')
        # Remove every allowed INSERT route: exact repeat must still succeed.
        with self.a.connect(autocommit=True) as c:
            grants=c.execute("SELECT table_schema||'.'||table_name FROM information_schema.role_table_grants WHERE grantee='wa_science_writer' AND privilege_type='INSERT'").fetchall()
            for t, in grants:c.execute(sql.SQL('REVOKE INSERT ON {} FROM wa_science_writer').format(sql.Identifier(*t.split('.'))))
        try:
            with self.a.connect(role='wa_etl_login') as c:self.assertEqual(import_exact_snapshot(c,self.p),'ALREADY_MATCHED')
        finally:
            with self.a.connect(autocommit=True) as c:
                for t, in grants:c.execute(sql.SQL('GRANT INSERT ON {} TO wa_science_writer').format(sql.Identifier(*t.split('.'))))
        with self.a.connect() as c:after=export_source(c,self.p,self.out/'export_a_repeat')
        self.assertEqual(before,after)

    def test_E22_collision(self):
        self.mark('E22')
        row=next(r for r in self.p.rows if r.table=='wa_geo.body');bad=replace(row,values=row.values|{'canonical_name':'FORGED'})
        p=replace(self.p,rows=tuple(bad if r is row else r for r in self.p.rows))
        with self.a.connect(role='wa_etl_login') as c:
            with self.assertRaisesRegex(CollisionFailure,'IMPORT_COLLISION'):import_exact_snapshot(c,p)
        db=self.clone('partial')
        with self.a.connect(db,autocommit=True) as c:
            c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
            from loom_world_authority.store import _insert_row
            _insert_row(c,self.p.rows[0]);c.execute('COMMIT')
        with self.a.connect(db,role='wa_etl_login') as c:
            with self.assertRaises(CollisionFailure):import_exact_snapshot(c,self.p)
        self.assertEqual(self.scalar_count(self.a,db,'wa_meta.legacy_row'),0)

    def test_E23_concurrent(self):
        self.mark('E23');db=self.clone('concurrent')
        def run():
            with self.a.connect(db,role='wa_etl_login') as c:return import_exact_snapshot(c,self.p)
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:run(),range(2)))
        self.assertEqual(sorted(results),['ALREADY_MATCHED','IMPORTED']);self.assertEqual(self.scalar_count(self.a,db,'wa_meta.legacy_row'),2726)

    def test_E24_lost_acknowledgement(self):
        self.mark('E24');db=self.clone('lost_ack')
        with self.a.connect(db,role='wa_etl_login') as c:
            with self.assertRaises(ConnectionError):import_exact_snapshot(c,self.p,commit_ack_failure=True)
        with self.a.connect(db,role='wa_etl_login') as c:self.assertEqual(import_exact_snapshot(c,self.p),'ALREADY_MATCHED')
        self.assertEqual(self.scalar_count(self.a,db,'wa_meta.legacy_row'),2726)

    def test_E25_two_clusters(self):
        self.mark('E25')
        with self.a.connect() as c:a=export_source(c,self.p,self.out/'export_a_final')
        with self.b.connect() as c:b=export_source(c,self.p,self.out/'export_b_final')
        self.assertEqual(a,b)
        for record in a['files']:self.assertEqual((self.out/'export_a_final'/record['path']).read_bytes(),(self.out/'export_b_final'/record['path']).read_bytes())

    def test_E26_immutable(self):
        self.mark('E26')
        with self.a.connect(autocommit=True) as c:
            tables=c.execute("SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname LIKE 'wa_%' AND (n.nspname,c.relname)<>('wa_info','principal_binding') ORDER BY 1,2").fetchall()
            for schema,table in tables:
                col=c.execute('SELECT attname FROM pg_attribute WHERE attrelid=%s::regclass AND attnum>0 AND NOT attisdropped ORDER BY attnum LIMIT 1',(schema+'.'+table,)).fetchone()[0]
                # UPDATE/DELETE authorizations are absent on append-only service routes;
                # populated families additionally prove row-trigger rejection as DBA.
                for verb in ('UPDATE','DELETE','TRUNCATE'):
                    q={'UPDATE':sql.SQL('UPDATE {} SET {}={}'),'DELETE':sql.SQL('DELETE FROM {}'),'TRUNCATE':sql.SQL('TRUNCATE {}')}[verb]
                    q=q.format(sql.Identifier(schema,table),sql.Identifier(col),sql.Identifier(col)) if verb=='UPDATE' else q.format(sql.Identifier(schema,table))
                    c.execute('BEGIN ISOLATION LEVEL SERIALIZABLE')
                    try:
                        if verb!='TRUNCATE':c.execute('SET LOCAL ROLE wa_science_writer')
                        with self.assertRaises(psycopg.Error):c.execute(q)
                    finally:c.execute('ROLLBACK')

    def test_E27_role_boundaries(self):
        self.mark('E27')
        self.a.login('wa_q_reference','wa_reference_reader')
        for role,statements in [('wa_q_reference',['INSERT INTO wa_geo.body DEFAULT VALUES','INSERT INTO wa_science.admission DEFAULT VALUES','SELECT * FROM wa_world.realization']),('wa_etl_login',['SET ROLE wa_science_governor','SET ROLE wa_owner','INSERT INTO wa_science.admission DEFAULT VALUES','INSERT INTO wa_world.scenario DEFAULT VALUES'])]:
            with self.a.connect(role=role,autocommit=True) as c:
                for q in statements:
                    with self.assertRaises(psycopg.errors.InsufficientPrivilege):c.execute(q)

    def test_E28_source_and_independent_domain(self):
        self.mark('E28');self.assertEqual(hashlib.sha256(self.p.source_file.read_bytes()).hexdigest(),SOURCE_SHA)
        source_root=self.p.source_file.parents[4]
        original=subprocess.check_output(['git','-C',str(source_root),'show',SOURCE_COMMIT+':'+SOURCE_PATH])
        self.assertEqual(hashlib.sha256(original).hexdigest(),SOURCE_SHA)
        script="import sys;import loom_world_authority.store,loom_world_authority.etl;assert not any('offworld' in k or 'build6e' in k for k in sys.modules)"
        subprocess.run([str(DOMAIN.parents[1]/'.venv/bin/python'),'-c',script],check=True,env=__import__('os').environ|{'PYTHONPATH':str(DOMAIN.parents[1]/'src')})
        self.assertEqual(CTX['manifest']['domain'],'LOOM_WORLD_AUTHORITY');self.assertEqual(CTX['manifest']['database_name'],'loom_world_authority')
        before=self.p.source_file.parent/'SOURCE_MANIFEST.json'
        self.assertEqual(next(r.values['original_manifest'] for r in self.p.rows if r.table=='wa_meta.source_snapshot'),before.read_bytes())
        self.test_E17_zero_admissions()

if __name__=='__main__':unittest.main()
