#!/usr/bin/env python3
"""Gate C qualification: real GIS session -> Navigator -> campaign persistence."""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
sys.path.insert(0,str(REPO/'tools'))

import loom_navigator
from loom.campaign import CAMPAIGN_EXECUTION_VERSION, LegacyCampaignExecutionService
from loom.gis.flight_planning import GISFlightPlanningSession
from loom.navigation import NavigationContext
from loom.navigation.service import LegacyNavigationService
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight


def prepare_transaction_runtime(bundle):
    rows=history_records(bundle.history)
    commit,arrived=newest_completed_flight(rows)
    departure=copy.deepcopy(dict(commit['details']['replay']['departure_state_snapshot']))
    expected=copy.deepcopy(dict(arrived.get('state_after_snapshot') or arrived.get('details',{}).get('state_after_snapshot') or {}))
    td=Path(tempfile.mkdtemp(prefix='loom_phase6_gatec_'))
    root=td/'runtime'
    shutil.copytree(bundle.root,root)
    state_path=root/'LOOM_STATE_V1.json'; bak=root/'LOOM_STATE_V1.bak'
    for p in root.glob('LOOM_CAMPAIGN_HISTORY.jsonl.gz*'):
        if p.is_file(): p.unlink()
    if bak.exists(): bak.unlink()
    core=loom_navigator.load_core()
    core._atomic_save(state_path,bak,departure)
    ledger=core.HistoryLedger(root,departure)
    ledger.append('CAMPAIGN_MIGRATED',None,departure,{
        'phase6_gate_c_fixture':True,
        'source_departure_state_id':departure.get('state_id'),
    },state_after_snapshot=departure)
    return root,departure,expected,arrived


def qualify(bundle):
    root,departure,expected,arrived=prepare_transaction_runtime(bundle)
    core=loom_navigator.load_core()
    nav=LegacyNavigationService(core)
    campaign=LegacyCampaignExecutionService(core)
    b1=next(iter(sorted(root.glob('LOOM_Navigator_Visual_Design_B1_LOCKED_Package*.zip'))),None)
    context=NavigationContext(
        campaign_state=departure,
        cache_dir=root/'LOOM_Navigator_Cache_v1',
        b1_package=b1,
        runtime_root=root,
    )
    session=GISFlightPlanningSession(nav,context,offline=True,campaign_execution_service=campaign)
    if not session.state().execution_available:
        raise RuntimeError('Gate C runtime did not expose campaign execution')
    discovered=session.discover('MARS','BALANCED')
    selectable=[c for c in discovered.candidates if c.summary.get('selectable')]
    if not selectable: raise RuntimeError('no selectable frozen Ceres->Mars candidate')
    chosen=selectable[0]
    session.preview(chosen.route_id)
    session.commit(chosen.route_id)
    before_revision=int(departure['revision'])
    executed=session.execute()
    info=dict(executed.last_execution or {})
    if info.get('contract')!=CAMPAIGN_EXECUTION_VERSION:
        raise RuntimeError('wrong campaign execution contract')
    if executed.origin!='MARS':
        raise RuntimeError(f"GIS session did not rebind to arrival location: {executed.origin}")
    if executed.committed_route_id is not None or executed.candidates:
        raise RuntimeError('executed planning state was not cleared after arrival')
    final=json.loads((root/'LOOM_STATE_V1.json').read_text(encoding='utf-8'))
    core._validate_state(final)
    if final!=dict(session.context.campaign_state):
        raise RuntimeError('GIS session differs from persisted canonical state')
    if final['location_token']!='MARS' or int(final['revision'])!=before_revision+1:
        raise RuntimeError('campaign location/revision did not advance exactly once')
    if final['epoch_utc']!=info['arrival_epoch_utc']:
        raise RuntimeError('campaign epoch differs from authoritative execution arrival')
    if final['last_flight']['flight_id']!=info['flight_id']:
        raise RuntimeError('campaign last_flight differs from committed flight')
    recs=core._read_gzip_jsonl(root/'LOOM_CAMPAIGN_HISTORY.jsonl.gz')
    arrivals=[r for r in recs if r.get('record_type')=='FLIGHT_ARRIVED']
    if len(arrivals)!=1:
        raise RuntimeError(f'expected exactly one FLIGHT_ARRIVED record, got {len(arrivals)}')
    if arrivals[0]['record_sha256']!=info['history_record_sha256']:
        raise RuntimeError('history identity differs from campaign commit result')
    if arrived['details']['runtime_sha256']!=final['last_flight']['runtime_sha256']:
        raise RuntimeError('Gate C flight differs from frozen runtime physics oracle')
    # The new session has no committed plan; duplicate execution must be rejected.
    try:
        session.execute()
    except Exception:
        pass
    else:
        raise RuntimeError('duplicate execute was accepted after arrival')
    return root,chosen,final,info,arrivals[0],arrived,expected


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime_root');args=ap.parse_args()
    result=None;last=None
    for bundle in discover_runtime_bundles(Path(args.runtime_root).resolve()):
        try:
            result=qualify(bundle);break
        except Exception as exc:
            last=exc;print('REJECT BUNDLE:',bundle.root,repr(exc))
    if result is None: raise RuntimeError(f'Gate C found no qualifying frozen runtime bundle: {last}')
    root,chosen,final,info,record,arrived,_=result
    print('PHASE6_GATE_C=PASS')
    print('CAMPAIGN_CONTRACT=',info['contract'])
    print('FLOW=GIS_PLAN_COMMIT_EXECUTE_NAVIGATOR_CAMPAIGN_PERSIST_REFRESH')
    print('origin=',info['origin'])
    print('destination=',info['destination'])
    print('selected_route_id=',chosen.route_id)
    print('flight_id=',info['flight_id'])
    print('revision=',info['revision_before'],'->',info['revision_after'])
    print('epoch=',info['departure_epoch_utc'],'->',info['arrival_epoch_utc'])
    print('remass_t=',info['remass_before_t'],'->',info['remass_after_t'])
    print('history_record_number=',record['record_number'])
    print('history_record_sha256=',record['record_sha256'])
    print('runtime_sha256=',final['last_flight']['runtime_sha256'])
    print('frozen_runtime_sha256=',arrived['details']['runtime_sha256'])
    print('duplicate_execution=REJECTED')
    print('gate_c_runtime_root=',root)
    return 0

if __name__=='__main__': raise SystemExit(main())
