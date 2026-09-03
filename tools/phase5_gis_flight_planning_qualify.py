#!/usr/bin/env python3
"""Qualify Phase 5 GIS flight planning against the frozen Pixel runtime."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
sys.path.insert(0,str(REPO/'tools'))

import loom_navigator
from loom.gis.flight_planning import GISFlightPlanningSession, GIS_FLIGHT_PLANNING_VERSION
from loom.navigation import NavigationContext
from loom.navigation.service import LegacyNavigationService
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight


def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def qualify(bundle):
    rows=history_records(bundle.history)
    commit,arrived=newest_completed_flight(rows)
    replay=commit['details']['replay']
    state=copy.deepcopy(dict(replay['departure_state_snapshot']))
    if state.get('location_token')!='CERES':
        raise RuntimeError('frozen qualification departure is not CERES')
    before=copy.deepcopy(state);before_sha=sha(before)
    service=LegacyNavigationService(loom_navigator.load_core())
    context=NavigationContext(campaign_state=state,cache_dir=bundle.cache,b1_package=bundle.b1,runtime_root=bundle.root)
    session=GISFlightPlanningSession(service,context,offline=True)
    initial=session.state()
    if initial.contract!=GIS_FLIGHT_PLANNING_VERSION:
        raise RuntimeError('wrong planning contract')
    discovered=session.discover('MARS','BALANCED')
    if not discovered.candidates:
        raise RuntimeError('Navigator returned no real Ceres->Mars candidates')
    selectable=[c for c in discovered.candidates if c.summary.get('selectable')]
    if not selectable:
        raise RuntimeError('Navigator returned no selectable real candidates')
    candidate=selectable[0]
    preview=session.preview(candidate.route_id)
    if preview.preview_route_id!=candidate.route_id or not preview.preview_overlay:
        raise RuntimeError('GIS preview did not produce Phase-4 overlay')
    overlay=preview.preview_overlay
    if overlay.get('contract')!='LOOM_GIS_NAVIGATION_OVERLAY_V1':
        raise RuntimeError('preview did not use Phase-4 GIS overlay contract')
    active=overlay.get('active_route') or {}
    if active.get('origin')!='CERES' or active.get('destination')!='MARS':
        raise RuntimeError('preview overlay endpoints differ from planning request')
    if not active.get('source_sha256'):
        raise RuntimeError('preview overlay lost route-layer source identity')
    committed=session.commit(candidate.route_id)
    if committed.committed_route_id!=candidate.route_id:
        raise RuntimeError('Phase-5 plan selection did not lock')
    if session.committed_plan() is None:
        raise RuntimeError('committed plan object unavailable to Phase 6 handoff')
    if sha(dict(session.context.campaign_state))!=before_sha or dict(session.context.campaign_state)!=before:
        raise RuntimeError('Phase-5 planning mutated campaign state')
    cancelled=session.cancel()
    if cancelled.preview_route_id is not None or cancelled.committed_route_id is not None or cancelled.preview_overlay is not None:
        raise RuntimeError('cancel did not clear planning selection')
    if sha(dict(session.context.campaign_state))!=before_sha:
        raise RuntimeError('cancel mutated campaign state')
    return {
        'bundle':bundle,
        'candidate_count':len(discovered.candidates),
        'candidate_route_id':candidate.route_id,
        'summary':dict(candidate.summary),
        'route_layer_sha':active['source_sha256'],
        'campaign_sha':before_sha,
        'planning_session':session.session_id,
        'frozen_runtime_sha':arrived['details']['runtime_sha256'],
    }


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime_root');args=ap.parse_args()
    root=Path(args.runtime_root).resolve();result=None;last=None
    for bundle in discover_runtime_bundles(root):
        try:
            result=qualify(bundle);break
        except Exception as exc:
            last=exc;print('REJECT BUNDLE:',bundle.root,repr(exc))
    if result is None: raise RuntimeError(f'Phase 5 found no qualifying frozen runtime bundle: {last}')
    print('PHASE5_GIS_FLIGHT_PLANNING=PASS')
    print('EPHEMERIS_MODE=FROZEN_OFFLINE_ONLY')
    print('PLANNING_CONTRACT=',GIS_FLIGHT_PLANNING_VERSION)
    print('origin=CERES')
    print('destination=MARS')
    print('candidate_count=',result['candidate_count'])
    print('selected_route_id=',result['candidate_route_id'])
    print('candidate_summary=',json.dumps(result['summary'],sort_keys=True))
    print('route_layer_sha256=',result['route_layer_sha'])
    print('campaign_state_sha256=',result['campaign_sha'])
    print('campaign_mutation=NONE')
    print('commit_semantics=PLANNING_SELECTION_ONLY_PHASE6_EXECUTION_REQUIRED')
    print('frozen_runtime_sha256=',result['frozen_runtime_sha'])
    print('runtime_bundle_root=',result['bundle'].root)
    return 0

if __name__=='__main__': raise SystemExit(main())
