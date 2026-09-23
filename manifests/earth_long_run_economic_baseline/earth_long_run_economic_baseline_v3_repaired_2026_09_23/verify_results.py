"""Validate the completed experimental trajectory; no baseline files are written."""
import json
import math
from collections import defaultdict
from pathlib import Path

P=Path(__file__).resolve().parent/'full_2226'/'results'

def rows(name):
    with (P/name).open() as f:
        for line in f: yield json.loads(line)

def close(a,b):
    return math.isclose(a,b,rel_tol=3e-12,abs_tol=1e-8)

country={}
for r in rows('countries_2060_2226.ndjson'):
    key=(r['iso3'],r['year'])
    assert key not in country
    country[key]=r
assert len(country)==80*167

sector_sums=defaultdict(lambda:defaultdict(list))
sector_cap={}
historical_A={}
sector_count=0
for r in rows('country_sectors_2060_2226.ndjson'):
    key=(r['iso3'],r['sector'])
    cy=(r['iso3'],r['year'])
    for field in ('value_added','capital','investment','employment','gross_output'):
        sector_sums[cy][field].append(r[field])
    sector_cap[(r['iso3'],r['sector'],r['year'])]=r['capital']
    if key in historical_A:
        assert r['cobb_douglas_A_2026']==historical_A[key]
    else:
        historical_A[key]=r['cobb_douglas_A_2026']
    if r['year']>2060:
        assert close(r['capital_share_alpha']+r['labor_exponent_effective'],1.0)
        modeled=(r['country_tfp_multiplier']*r['technology_productivity_multiplier']
                 *r['A']*r['capital']**r['capital_share_alpha']
                 *r['effective_labor_input']**r['labor_exponent_effective'])
        assert close(modeled,r['value_added']), (key,r['year'],modeled,r['value_added'])
    if key==('TWN','ENERGY'):
        assert r['value_added']>0 and r['gross_output']>0 and r['capital']>0 and r['A']>0
    sector_count+=1
assert sector_count==80*10*167
for key,fields in sector_sums.items():
    for field,vals in fields.items():
        assert close(math.fsum(vals),country[key][field]),(key,field)

asset_cap=defaultdict(list)
prior={}
asset_count=0
for r in rows('country_sector_assets_2060_2226.ndjson'):
    key=(r['iso3'],r['sector'],r['asset_class'])
    if key in prior:
        old=prior[key]
        assert r['year']==old['year']+1
        predicted=(1-r['asset_depreciation_rate'])*old['capital']+old['investment']
        assert close(predicted,r['capital']),(key,r['year'],predicted,r['capital'])
    prior[key]=r
    asset_cap[(r['iso3'],r['sector'],r['year'])].append(r['capital'])
    asset_count+=1
assert asset_count==80*10*4*167
for key,vals in asset_cap.items():
    assert close(math.fsum(vals),sector_cap[key]),key
print('PASS: 80 countries x 167 years; 800 sectors x 167 years; 3,200 assets x 167 years')
print('PASS: all country-sector, sector-asset and asset stock-flow identities')
print('PASS: production equation, effective exponents, immutable historical A')
print('PASS: TWN ENERGY positive VA, GO, capital and A in every year')
