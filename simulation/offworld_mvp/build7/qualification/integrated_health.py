"""Disposable PostgreSQL 18 Build 7 integration proof for GitHub Actions."""
import json
import os
from pathlib import Path
import tempfile
import psycopg
from psycopg import sql
from loom_world_authority.etl import plan_sqlite_import
from loom_world_authority.store import import_exact_snapshot
from simulation.offworld_mvp.build7.generated_campaign import start_world_run, run_world_annual

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = Path(__file__).resolve().parent / 'reference_snapshot' / 'LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3'
DB = 'loom_b7_health_disposable'
ROLES = {'science_writer':'wa_science_writer','world_writer':'wa_world_writer','runtime':'wa_runtime_writer','reference_reader':'wa_reference_reader','agent_pub':'wa_agent_reader','agent_spn':'wa_agent_reader','agent_fin':'wa_agent_reader'}

def main():
    admin = dict(host='127.0.0.1', port=int(os.getenv('LOOM_HEALTH_PGPORT','5432')), user='postgres', password=os.environ['LOOM_HEALTH_PGPASSWORD'])
    with psycopg.connect(**admin, dbname='postgres', autocommit=True) as c:
        version = int(c.execute('show server_version_num').fetchone()[0])
        if version // 10000 != 18: raise RuntimeError('PostgreSQL 18 required')
        c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DB)))
    with psycopg.connect(**admin,dbname=DB) as c:
        c.execute((ROOT/'data/world_authority/migrations/001_world_authority_v1.sql').read_text())
        c.execute((ROOT/'data/world_authority/migrations/002_body_remote_observation.sql').read_text())
        c.commit()
        print('SCHEMA INSTALLED',flush=True)
        plan = plan_sqlite_import(FIXTURE)
        print('SOURCE',import_exact_snapshot(c,plan),flush=True)
    with psycopg.connect(**admin,dbname='postgres',autocommit=True) as c:
        for service,role in ROLES.items():
            username = 'health_'+service
            c.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(username),sql.Literal(os.environ['LOOM_HEALTH_PGPASSWORD'])))
            c.execute(sql.SQL('GRANT {} TO {}').format(sql.Identifier(role),sql.Identifier(username)))
            if service=='runtime': c.execute(sql.SQL('GRANT wa_admission_writer TO {}').format(sql.Identifier(username)))
    with tempfile.TemporaryDirectory() as tmp:
        service_file=Path(tmp)/'pg_service.conf'
        service_file.write_text(''.join(f'[{name}]\nhost=127.0.0.1\nport={admin["port"]}\ndbname={DB}\nuser=health_{name}\npassword={admin["password"]}\n' for name in ROLES))
        service_file.chmod(0o600)
        os.environ['PGSERVICEFILE']=str(service_file)
        opened=start_world_run(reference_service='reference_reader',science_writer_service='science_writer',world_writer_service='world_writer',runtime_service='runtime',world_seed='BUILD7-HEALTH-CI-20261010')
        assert opened['generated_body_count']==90,opened
        run_id=opened['run_id']
        first=run_world_annual(reference_service='reference_reader',runtime_service='runtime',run_id=run_id,through_year=2029)
        second=run_world_annual(reference_service='reference_reader',runtime_service='runtime',run_id=run_id,through_year=2029)
        fields=('annual','exploration_annual','project_annual','project_ids','project_cash','study_expenses','regional_observations','study_reviews','public_balance','sponsor_funds','capital_coupling')
        for key in fields: assert first[key]==second[key],('REPLAY_DRIFT',key)
        assert first['projects']==1 and first['study_expenses']==1 and first['regional_observations']==4 and first['study_reviews']==1,first
        assert first['annual'][0][1]=='AUTHORIZE' and first['annual'][1][1].startswith('STUDY_') and first['annual'][2][1] in ('ADVANCE','DEFER','ABANDON')
        assert len(second['epoch_commits'])>=70
        assert all(status=='ALREADY_MATCHED' for _,status in second['epoch_commits']),second['epoch_commits']
        with psycopg.connect(**admin,dbname=DB) as c:
            counts=c.execute('select (select count(*) from wa_run.project),(select count(*) from wa_run.causal_envelope),(select count(*) from wa_world.realization)').fetchone()
        assert counts[0]==1 and counts[1]>70 and counts[2]==90,counts
        print('INTEGRATED PASS',json.dumps(dict(run_id=run_id,years='2026-2029',epochs=len(second['epoch_commits']),project_count=counts[0],causal_envelopes=counts[1],realizations=counts[2],annual=first['annual'])),flush=True)

if __name__=='__main__':main()
