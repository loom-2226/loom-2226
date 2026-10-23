"""PR427 TEST_ONLY recovered-vintage SPK registry; does not change canonical authority."""
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from src.loom_spice_ephemeris_adapter import KernelAsset, SolarEphemerisRegistry, SpiceEphemerisAdapter
from simulation.offworld_mvp.build8.travel_pilot.eligibility import catalog_registry

WINDOW_START='2026-01-01T00:00:00Z'
WINDOW_END='2031-12-31T23:59:59Z'
HERE=Path(__file__).resolve().parent
RECOVERY=HERE/'PHASE4E_RECOVERY_34_TEST_ONLY_MANIFEST.json'

def recovered_registry(asset_root, recovery_manifest=RECOVERY):
    base=catalog_registry(Path(asset_root))
    data=json.loads(Path(recovery_manifest).read_text())
    assert len(data['files'])==34
    sources=dict(base.sources)
    for row in data['files']:
        sid='HORIZONS_4E_'+row['body']
        original=sources[sid]
        assert original.sha256.lower()==row['old_pin_sha256'].lower(),sid
        assert len([a for a in original.kernel_assets if Path(a.path).name==original.asset_filename])==1,sid
        new_asset=KernelAsset(row['stored_at'],row['sha256'],int(row['size_bytes']))
        new_assets=tuple(new_asset if Path(a.path).name==original.asset_filename else a for a in original.kernel_assets)
        sources[sid]=replace(original,asset_filename=row['filename'],sha256=row['sha256'],byte_count=int(row['size_bytes']),kernel_assets=new_assets,product_version=original.product_version+'|RECOVERED_VINTAGE_TEST_ONLY',status='QUALIFIED',navigation_grade=True,state_capability='DIRECT_SPICE_TEST_ONLY_RECOVERED')
    recovered_ids={'HORIZONS_4E_'+row['body'] for row in data['files']}
    coverage=tuple(replace(c,valid_from=WINDOW_START,valid_until=WINDOW_END) if c.ephemeris_source_id in recovered_ids else c for c in base.coverage)
    return SolarEphemerisRegistry(base.bodies.values(),base.identifiers,sources.values(),coverage)

def recovered_adapter(asset_root):
    return SpiceEphemerisAdapter(recovered_registry(asset_root))

def recovery_sha256():
    return sha256(RECOVERY.read_bytes()).hexdigest()

def test_only_run_identity():
    return {'classification':'RECOVERED_TEST_ONLY','window_start':WINDOW_START,'window_end':WINDOW_END,'recovery_manifest_sha256':recovery_sha256()}

def endpoint_with_window_reason(body, departure, arrival, registry, catalog=None):
    from simulation.offworld_mvp.build8.travel_pilot.eligibility import resolve_endpoint
    from datetime import datetime, timezone
    date=lambda x: datetime.fromisoformat(str(x).replace('Z','+00:00')).replace(tzinfo=timezone.utc) if datetime.fromisoformat(str(x).replace('Z','+00:00')).tzinfo is None else datetime.fromisoformat(str(x).replace('Z','+00:00')).astimezone(timezone.utc)
    end=date(arrival)
    result=resolve_endpoint(body,departure,registry=registry,catalog=catalog)
    if 'HORIZONS_4E_'+body in registry.sources and registry.sources['HORIZONS_4E_'+body].state_capability=='DIRECT_SPICE_TEST_ONLY_RECOVERED' and end>date(WINDOW_END):
        return {**result,'status':'UNPRICED','eligible':False,'reason':'RECOVERED_TEST_ONLY_ARRIVAL_AFTER_2031_12_31','arrival_utc':str(arrival)}
    if result['status']=='DIRECT':
        arrival_result=resolve_endpoint(body,arrival,registry=registry,catalog=catalog)
        if arrival_result['status']!='DIRECT':return {**result,'status':'UNPRICED','eligible':False,'reason':'ARRIVAL_ENDPOINT_'+str(arrival_result['reason'])}
    return result
