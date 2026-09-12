import importlib.util
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'engineering'/'experience_one'/'spikes'/'e1_1_ceres_motivation_probe.py'
s=importlib.util.spec_from_file_location('motivation_probe',P); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m)

def test_probe_does_not_promote_hook_surface_to_current_motivation():
 r=m.build_probe(); assert r['actionable_current_hook_count']==0; assert r['diagnosis']=='MOTIVATION_CONNECTIVE_TISSUE_ABSENT'

def test_probe_preserves_supported_surfaces():
 r=m.build_probe(); ids={h['hook_id'] for h in r['hooks']}; assert {'CERES_RESTRICTED_ANCHORAGE','CERES_SHIPYARD_ARC','CERES_BELT_EXCHANGE','CERES_DOCKING_PRECEDENT','COURIER_CONTRACT_MECHANIC','WAYFARER_CERES_NAV_STATE'}<=ids

def test_every_nonactionable_hook_states_missing_discriminator():
 r=m.build_probe(); assert all(h['missing'].strip() for h in r['hooks'] if not h['can_motivate_now'])

def test_probe_has_zero_content_and_state_authority():
 r=m.build_probe(); assert r['new_lore_authored'] is False; assert r['campaign_mutation'] is False; assert r['canon_mutation'] is False; assert r['model_called'] is False
