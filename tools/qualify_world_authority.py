#!/usr/bin/env python3
"""Designated real PostgreSQL 18, lossless World Authority qualification.

Explicit --provision-docker is mandatory. Creates only fresh, uniquely named
qualification containers. No production/default DSN, source writes, promotion.
"""
from __future__ import annotations
import argparse, hashlib, json, os, secrets, subprocess, sys, time, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'tests')]
import psycopg
from psycopg import sql
from loom_world_authority.etl import plan_sqlite_import, canonical, SOURCE_SHA
from loom_world_authority.store import import_exact_snapshot, export_source

CONTEXT=None

class Cluster:
    def __init__(self,name,port,image,output):
        self.name=name;self.output=output;self.image=image
        self.kw=dict(host='127.0.0.1',port=port,dbname='loom_world_authority',user='loom_wa_admin',password=secrets.token_hex(24))
        subprocess.run(['sudo','-n','docker','run','-d','--name',name,'-p',f'127.0.0.1:{port}:5432','-e','POSTGRES_USER='+self.kw['user'],'-e','POSTGRES_PASSWORD='+self.kw['password'],'-e','POSTGRES_DB='+self.kw['dbname'],'-e','POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=C',image,'postgres','-c','timezone=UTC','-c','standard_conforming_strings=on'],check=True,stdout=subprocess.DEVNULL)
        for _ in range(150):
            try:
                with self.connect() as c:
                    if c.execute('SHOW server_version').fetchone()[0].startswith('18.6 '):break
            except psycopg.OperationalError:time.sleep(.2)
        else:raise RuntimeError('pinned PostgreSQL 18.6 not ready')
    def connect(self,dbname=None,role=None,**extra):
        kw=self.kw.copy()
        if dbname:kw['dbname']=dbname
        if role:kw.update(user=role,password='wa-qualification-only')
        return psycopg.connect(**kw,**extra)
    def psql(self,data,dbname=None):
        # In-container psql is the exact server major, never the host PG16 client.
        return subprocess.run(['sudo','-n','docker','exec','-i',self.name,'psql','-X','-v','ON_ERROR_STOP=1','-U',self.kw['user'],'-d',dbname or self.kw['dbname']],input=data,capture_output=True)
    def clone_empty(self,key):
        name='wa_qual_'+key
        with self.connect(autocommit=True) as c:c.execute(sql.SQL('CREATE DATABASE {} TEMPLATE wa_qual_empty').format(sql.Identifier(name)))
        return name
    def login(self,name,role):
        with self.connect(autocommit=True) as c:
            c.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD 'wa-qualification-only'").format(sql.Identifier(name)))
            c.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(role),sql.Identifier(name)))
    def install(self,ddl):
        result=self.psql(ddl)
        if result.returncode:raise RuntimeError(result.stderr.decode())
        with self.connect(autocommit=True) as c:
            c.execute('CREATE DATABASE wa_qual_empty TEMPLATE loom_world_authority')
        self.login('wa_etl_login','wa_science_writer')
    def inventory(self):
        with self.connect(autocommit=True) as c:
            settings={k:c.execute('SHOW '+k).fetchone()[0] for k in ['server_version','server_encoding','timezone','standard_conforming_strings']}
            settings.update(zip(('lc_collate','lc_ctype'),c.execute('SELECT datcollate,datctype FROM pg_database WHERE datname=current_database()').fetchone()))
            tables=c.execute("SELECT n.nspname,c.relname,r.rolname,c.relrowsecurity,c.relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner WHERE n.nspname LIKE 'wa_%' AND c.relkind='r' ORDER BY 1,2").fetchall()
            roles=c.execute("SELECT rolname,rolsuper,rolcanlogin,rolbypassrls FROM pg_roles WHERE rolname LIKE 'wa_%' ORDER BY 1").fetchall()
            grants=c.execute("SELECT table_schema,table_name,grantee,privilege_type FROM information_schema.role_table_grants WHERE table_schema LIKE 'wa_%' ORDER BY 1,2,3,4").fetchall()
            extensions=c.execute("SELECT extname,extversion FROM pg_extension WHERE extname='pgcrypto' ORDER BY extname").fetchall()
            psql=subprocess.check_output(['sudo','-n','docker','exec',self.name,'psql','--version'],text=True).strip()
            postgres=subprocess.check_output(['sudo','-n','docker','exec',self.name,'postgres','--version'],text=True).strip()
            return dict(settings=settings,tables=tables,roles=roles,grants=grants,extensions=extensions,psql_version=psql,postgres_binary_version=postgres)

def dependency_lock():
    result={}
    for raw in (ROOT/'data/world_authority/dependencies.lock').read_text().splitlines():
        line=raw.strip()
        if not line or line.startswith('#'):continue
        key,value=line.split('=',1);result[key.strip()]=value.strip()
    return result

def verify_locked_environment(source,image):
    lock=dependency_lock()
    manifest=json.loads((ROOT/'data/world_authority/WORLD_AUTHORITY_DOMAIN_V1.json').read_text())
    ddl=(ROOT/'data/world_authority/migrations/001_world_authority_v1.sql').read_bytes()
    checks={
        'source_sha256':SOURCE_SHA,
        'source_commit':manifest['source_git_commit'],
        'source_path':manifest['source_path'],
        'source_bytes':str(source.stat().st_size),
        'ddl_sha256':hashlib.sha256(ddl).hexdigest(),
        'source_schema_sha256':hashlib.sha256((ROOT/'data/world_authority/SOURCE_SCHEMA_V1.json').read_bytes()).hexdigest(),
        'source_counts_sha256':hashlib.sha256((ROOT/'data/world_authority/SOURCE_COUNTS_V1.json').read_bytes()).hexdigest(),
        'column_dispositions_sha256':hashlib.sha256((ROOT/'data/world_authority/SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').read_bytes()).hexdigest(),
        'python_version':sys.version.split()[0],
        'psycopg_version':psycopg.__version__,
        'libpq_version':str(psycopg.pq.version()),
        'psycopg_pq_implementation':psycopg.pq.__impl__,
        'postgres_server_version':'18.6',
        'postgres_client_version':'18.6',
        'pgcrypto_version':'1.4',
        'postgres_image_repo_digest':'postgres@sha256:5a5a84b19854a9ffaa54082c166ff4ec27473a361e496e5ea167f298f2da9722',
        'postgres_image_id':'sha256:5a5a84b19854a9ffaa54082c166ff4ec27473a361e496e5ea167f298f2da9722',
    }
    for key,value in checks.items():
        if lock.get(key)!=str(value):raise RuntimeError('DEPENDENCY_LOCK_MISMATCH:'+key)
    if manifest['ddl_sha256']!=checks['ddl_sha256'] or manifest['source_sqlite_sha256']!=SOURCE_SHA:raise RuntimeError('DOMAIN_MANIFEST_MISMATCH')
    if source.stat().st_size!=1056768:raise RuntimeError('SOURCE_SIZE_MISMATCH')
    if image.get('Id')!=checks['postgres_image_id'] or checks['postgres_image_repo_digest'] not in image.get('RepoDigests',[]):raise RuntimeError('POSTGRES_IMAGE_DIGEST_MISMATCH')
    return checks

def implementation_hashes():
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ('src/loom_world_authority','data/world_authority','docs/database_semantics/world_authority') for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    for rel in ['tools/qualify_world_authority.py','tests/test_world_authority_etl.py','tests/test_world_authority_security.py','tests/test_world_authority_store.py']:
        files[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    return files


def main():
    global CONTEXT
    ap=argparse.ArgumentParser();ap.add_argument('--provision-docker',action='store_true',required=True)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--image',default='postgres@sha256:5a5a84b19854a9ffaa54082c166ff4ec27473a361e496e5ea167f298f2da9722');ap.add_argument('--ports',type=int,nargs=2,default=[55440,55441])
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    files_before=implementation_hashes()
    plan=plan_sqlite_import(args.source);ddl=(ROOT/'data/world_authority/migrations/001_world_authority_v1.sql').read_bytes()
    manifest=json.loads((ROOT/'data/world_authority/WORLD_AUTHORITY_DOMAIN_V1.json').read_text())
    image=json.loads(subprocess.check_output(['sudo','-n','docker','image','inspect',args.image]))[0]
    locked=verify_locked_environment(args.source,image)
    if hashlib.sha256(ddl).hexdigest()!=manifest['ddl_sha256']:raise RuntimeError('DESIGN_HASH_MISMATCH')
    image_id=image['Id'];clusters=[Cluster('loom-wa-qual-'+secrets.token_hex(5),p,image_id,args.output) for p in args.ports]
    CONTEXT=dict(plan=plan,ddl=ddl,clusters=clusters,output=args.output,image=image_id,manifest=manifest,locked=locked)
    import test_world_authority_etl
    test_world_authority_etl.CTX=CONTEXT
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_world_authority_etl)
    results=unittest.TextTestRunner(verbosity=2).run(suite)
    observed=test_world_authority_etl.EXECUTED.copy()
    security_result=None
    # Always report partial/failure honestly; never run security on an uninstalled DB.
    if all(getattr(c,'ready',False) for c in clusters):
        db=clusters[0].clone_empty('security')
        with clusters[0].connect(db,role='wa_etl_login') as c:import_exact_snapshot(c,plan)
        os.environ.update(LOOM_WA_PGHOST=clusters[0].kw['host'],LOOM_WA_PGPORT=str(clusters[0].kw['port']),LOOM_WA_PGDATABASE=db,LOOM_WA_PGADMIN=clusters[0].kw['user'],LOOM_WA_PGADMIN_PASSWORD=clusters[0].kw['password'])
        import test_world_authority_security
        security_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_world_authority_security))
        observed |= test_world_authority_security.EXECUTED
    required={f'E{i:02}' for i in range(1,29)}|{f'S{i:02}' for i in range(1,13)}
    passed=results.wasSuccessful() and not results.skipped and security_result is not None and security_result.wasSuccessful() and not security_result.skipped and observed==required
    files=implementation_hashes()
    passed=passed and files==files_before
    import test_world_authority_store
    identity_result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_world_authority_store))
    passed=passed and identity_result.wasSuccessful() and not identity_result.skipped
    source_after=hashlib.sha256(args.source.read_bytes()).hexdigest()
    passed=passed and source_after==SOURCE_SHA
    report=dict(status='PASS' if passed else 'FAIL',standing='MIGRATION_QUALIFIED_SCIENCE_CANDIDATE_PRESERVED' if passed else 'NOT_QUALIFIED',required_ids=sorted(required),observed_ids=sorted(observed),source_sha256=source_after,source_bytes=args.source.stat().st_size,source_git_commit=manifest['source_git_commit'],source_path=manifest['source_path'],forensic_rows=2726,source_columns=256,plan_sha256=plan.plan_hash,implementation_files=files_before,implementation_unchanged_during_run=(files==files_before),store_regressions_passed=identity_result.wasSuccessful(),locked_environment=locked,image_id=image_id,image_repo_digests=image.get('RepoDigests',[]),python=sys.version,psycopg=psycopg.__version__,libpq=psycopg.pq.version(),clusters=[dict(container=c.name,port=c.kw['port'],inventory=c.inventory()) for c in clusters],errors=[(str(t),s) for t,s in results.errors+results.failures]+([] if security_result is None else [(str(t),s) for t,s in security_result.errors+security_result.failures]),skipped=results.skipped+([] if security_result is None else security_result.skipped))
    (args.output/'SOURCE_TO_TARGET_CROSSWALK.json').write_bytes(canonical(plan.crosswalk)+b'\n')
    (args.output/'SOURCE_SCHEMA.json').write_bytes(canonical(plan.source_schema)+b'\n')
    (args.output/'COLUMN_DISPOSITIONS.csv').write_bytes((ROOT/'data/world_authority/SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').read_bytes())
    (args.output/'WORLD_AUTHORITY_QUALIFICATION.json').write_bytes(canonical(report)+b'\n')
    # Credentials remain local protected operator configuration, never evidence export.
    secret=Path('/tmp')/('wa-qual-services-'+secrets.token_hex(6)+'.json');secret.write_text(json.dumps([c.kw|{'name':c.name} for c in clusters]));secret.chmod(0o600)
    print('Qualification',report['status'],'Report:',args.output/'WORLD_AUTHORITY_QUALIFICATION.json')
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
