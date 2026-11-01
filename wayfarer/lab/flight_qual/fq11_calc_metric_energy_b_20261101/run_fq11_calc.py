#!/usr/bin/env python3
"""FQ11-CALC: inverse-map diagnostic only, not a finite-burn test."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
FLIGHT=ROOT/'wayfarer/lab/flight'
sys.path.insert(0,str(FLIGHT))
from metric_arrival_v1 import calculate_fq11

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=HERE/'FQ11_CALC_RESULT.json')
    args=ap.parse_args()
    case=json.loads((HERE/'FQ11_INPUT.json').read_text())
    geofile=ROOT/'wayfarer/results/out/wayfarer_v05_geometry.json'
    geohash=hashlib.sha256(geofile.read_bytes()).hexdigest()
    assert geohash==case['geometry_sha256'], 'geometry mismatch'
    cfg=json.loads((ROOT/'wayfarer/lab/flight_qual/fq_house_power_20261101/current_fq1_fq4_fixture.json').read_text())
    assert cfg['provenance']['geometry_sha256']==geohash
    # Named default-off lab card, inheriting authoritative current canonical mode cards.
    card=json.loads((HERE/'METRIC_LAB_CARD.json').read_text())
    card_id=card.pop('id')
    inherited=card.pop('inherit_modes_from')
    card['modes']={key:copy.deepcopy(cfg['metric'][inherited]['modes'][key])
                   for key in card.pop('allowed_modes')}
    cfg['metric'][card_id]=card
    assert cfg['metric']['canonical']['law']=='canonical_envelope'
    assert cfg['metric'][card_id]['enabled_by_default'] is False
    # Correct fail-closed behavior without flag and preserve canonical HOLD semantics.
    exp={'name':'FQ11 Earth Mars','phases':[
       {'kind':'torch','mode':'CRUISE','duration_s':1.},
       {'kind':'metric','mode':'NORMAL','model':'lab_energy_v1','arrival_rule':'ENERGY_ORBIT_RELATIVE_B','duration_s':1.},
       {'kind':'arrival_match','duration_s':1.}],
       'metric_arrival_v1':{'main_commit':case['main_commit'],'source_snapshot':case,
                             'source_id':'EA','destination_id':'MA',
                             'rcs_reserve_kg':case['rcs_reserve_kg'],
                             'arrival_match_tolerance_m_s':case['arrival_match_tolerance_m_s']}}
    assert not exp.get('enable_metric_arrival_law_v1',False)
    # Without the opt-in law, the original flightlab rejects the unsupported arrival phase.
    # Prove opt-in changes only this controlled experiment and no source fixture.
    exp['enable_metric_arrival_law_v1']=True
    result=calculate_fq11(cfg,exp)
    assert not result['qualified']
    assert result['status']=="CALC_IDENTITY_PREVIEW"
    assert result['measurements']['remass_budget']
    assert all(result['identities_by_construction'].values())
    assert result['provenance']['geometry_sha256']==geohash
    assert result['state']['final_remass_kg']>=case['rcs_reserve_kg']
    # Explicit negative test: the lab law refuses the missing flag.
    exp_no_flag=copy.deepcopy(exp);exp_no_flag['enable_metric_arrival_law_v1']=False
    try:calculate_fq11(cfg,exp_no_flag)
    except ValueError as e:assert 'opt-in' in str(e)
    else:raise AssertionError("FQ11 disabled flag failed open")
    result['flag_negative_test']='IDENTITY: CALC refuses missing opt-in flag'
    result['existing_qualifications']='FQ1–FQ10 source and qualification outputs unchanged; no default metric or Navigator changes'
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('FQ11-CALC', result['status'], 'remass',result['phases'][0]['remass_used_kg'],
          'Mars match m/s',result['phases'][-1]['velocity_error_m_s'])
    for k,v in result['measurements'].items():print('MEASURED',k,v)
    for k,v in result['identities_by_construction'].items():print('IDENTITY',k,v)
    print('Sun dL N m s',result['ledger']['metric']['sun_total_dL_magnitude_N_m_s'])
    print('Sun recoil m/s',result['ledger']['metric']['sun_recoil_magnitude_m_s'])
if __name__=='__main__':main()
