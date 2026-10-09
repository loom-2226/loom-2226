"""Build 7 breadth qualification: every eligible generated body opens and replays.

One generated Solar WORLD batch is reused for all bodies.  For each eligible body the
normal Build 7 kernel is constructed, the opening REMOTE decision epoch is persisted,
then the campaign is rebuilt from its World Authority binding and the same epoch must
return ALREADY_MATCHED.  No downstream outcome is forced here.
"""
from __future__ import annotations

import argparse
import json
import psycopg

from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel import policy_runner as workers
from loom_world_authority import store

from simulation.offworld_mvp.build6e.generated_world import generate_solar_system
from simulation.offworld_mvp.build7.generated_campaign import (
    AUTHORIZATION, _agent_logins, _attach_persistence, _build_kernel, _load_solar_catalog,
    _target_from_bound, _target_from_generated, load_config, flow,
)


def _opening_remote(k,h):
    req=build_exploration_request('REMOTE:request',1,'EXP','RES','REMOTE')
    decision,_=flow.policy_epoch(
        k,h,'REMOTE','PUB','1',req,
        ('exploration.REMOTE_COST','opportunity.NAMED_LOCATION','opportunity.AUTHORED_SITE'),
        workers.run_public_explorer_policy,workers.public_explorer_policy_version())
    return decision


def qualify(*,reference_service='reference_reader',science_writer_service='science_writer',
            world_writer_service='world_writer',runtime_service='runtime',
            world_seed='BUILD7-BREADTH-20261007-A',science_cutoff=0):
    config=load_config();catalog,_=_load_solar_catalog();logins=_agent_logins()
    with psycopg.connect(service=reference_service) as reader, \
         psycopg.connect(service=science_writer_service) as science, \
         psycopg.connect(service=world_writer_service) as writer:
        store.install_generation_body_catalog(science,catalog)
        generated=generate_solar_system(reader,science,writer,seed=world_seed,
            authorization_ref=AUTHORIZATION,science_cutoff=science_cutoff,return_bindings=True,
            supplemental_catalog_sha256=catalog['body_rows_sha256'])
    bodies=tuple(sorted(generated['_bindings']))
    rows=[]
    for body in bodies:
        target=_target_from_generated(generated['_bindings'][body],config);target['world_seed']=world_seed
        k,h=_build_kernel(target,config,world_seed=world_seed)
        _attach_persistence(h,target,runtime_service,logins)
        d=_opening_remote(k,h)
        first=tuple(h.get('epoch_commits',()))
        if first != (('REMOTE','COMMITTED'),) and first != (('REMOTE','ALREADY_MATCHED'),):
            raise RuntimeError(f'{body}: opening persistence status {first!r}')
        run_id=k.boundary_manifest.run_id
        with psycopg.connect(service=reference_service) as reader:
            rebound=_target_from_bound(reader,runtime_service,run_id,config['runtime']['site_binding_key'],config)
        k2,h2=_build_kernel(rebound,config,world_seed=rebound['world_seed'])
        _attach_persistence(h2,rebound,runtime_service,logins)
        d2=_opening_remote(k2,h2)
        replay=tuple(h2.get('epoch_commits',()))
        if replay != (('REMOTE','ALREADY_MATCHED'),):
            raise RuntimeError(f'{body}: replay status {replay!r}')
        if d.id != d2.id or k2.boundary_manifest.run_id != run_id:
            raise RuntimeError(f'{body}: deterministic reopening mismatch')
        rows.append({'body':body,'run_id':run_id,'world_id':str(target['binding'].world_id),
                     'opening':first[0][1],'replay':replay[0][1]})
    if len(rows)!=len(bodies) or len(rows)!=90:
        raise RuntimeError(f'eligible body cardinality {len(rows)} != 90')
    return {'status':'PASS','body_count':len(rows),'world_seed':world_seed,'bodies':rows}


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference-service',default='reference_reader')
    ap.add_argument('--science-writer-service',default='science_writer')
    ap.add_argument('--world-writer-service',default='world_writer')
    ap.add_argument('--runtime-service',default='runtime')
    ap.add_argument('--world-seed',default='BUILD7-BREADTH-20261007-A')
    ap.add_argument('--science-cutoff',type=int,default=0)
    a=ap.parse_args(argv)
    print(json.dumps(qualify(reference_service=a.reference_service,science_writer_service=a.science_writer_service,
        world_writer_service=a.world_writer_service,runtime_service=a.runtime_service,
        world_seed=a.world_seed,science_cutoff=a.science_cutoff),sort_keys=True))

if __name__=='__main__': main()
