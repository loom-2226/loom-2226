"""Read-only comparison of the repaired run with the designated v2 trajectory."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NEW = ROOT / 'full_2226' / 'results'
OLD = ROOT.parent / 'investment_rate_source_round1_2026_09_23' / 'TRAJECTORY' / 'results'
YEARS = (2060,2090,2120,2165,2180,2205,2226)


def rows(path):
    with path.open() as f:
        for line in f:
            yield json.loads(line)


def country_series(path):
    out=defaultdict(dict)
    for r in rows(path):
        if r['year'] in YEARS:
            assert r['iso3'] not in out[r['year']]
            out[r['year']][r['iso3']]=r
    assert set(out)==set(YEARS)
    assert all(len(v)==80 for v in out.values())
    return out


def total(series,year,field):
    return math.fsum(r[field] for r in series[year].values())


def main():
    run=country_series(NEW/'countries_2060_2226.ndjson')
    v2=country_series(OLD/'countries_2060_2226.ndjson')
    with (ROOT.parent/'investment_rate_source_round1_2026_09_23'/'COUNTRY_COMPARISON.csv').open() as f:
        names={r['iso3']:r['country_name'] for r in csv.DictReader(f)}
    end=run[2226]
    va=total(run,2226,'value_added')
    order=sorted(end,key=lambda i:end[i]['value_added'],reverse=True)
    print('TOTALS')
    for field in ('value_added','capital','investment'):
        print(field,repr(total(run,2226,field)),'v2',repr(total(v2,2226,field)),
              'ratio',total(run,2226,field)/total(v2,2226,field))
    print('TOP20')
    for n,iso in enumerate(order[:20],1):
        r=end[iso]
        print(n,iso,names[iso],f"{r['value_added']/1e12:.6f}",f"{100*r['value_added']/va:.4f}%")
    print('SHARES')
    totals={year:total(run,year,'value_added') for year in YEARS}
    for iso in order[:20]:
        print(iso,*(f"{100*run[y][iso]['value_added']/totals[y]:.4f}" for y in YEARS))
    print('FOUR TRAJECTORIES')
    for iso in ('NGA','CHN','IND','USA'):
        print(iso)
        for y in YEARS:
            r=run[y][iso]; old=v2[y][iso]
            print(y,'VA_T',round(r['value_added']/1e12,6),'share_pct',round(100*r['value_added']/totals[y],4),
                  'K_T',round(r['capital']/1e12,6),'I_T',round(r['investment']/1e12,6),
                  'alpha',round(r['capital_share_alpha'],6),'v2_VA_T',round(old['value_added']/1e12,6))
    frozen=ROOT/'frozen_2060'/'countries_2060.ndjson'
    cohort=[r['iso3'] for r in rows(frozen) if r['capital_share_alpha']>0.60]
    print('HIGH_ALPHA',len(cohort),','.join(sorted(cohort)))
    for y in YEARS:
        cv=math.fsum(run[y][iso]['value_added'] for iso in cohort)
        ck=math.fsum(run[y][iso]['capital'] for iso in cohort)
        ci=math.fsum(run[y][iso]['investment'] for iso in cohort)
        ov=math.fsum(v2[y][iso]['value_added'] for iso in cohort)
        print(y,'VA_T',cv/1e12,'VA_share_pct',100*cv/totals[y],
              'K_T',ck/1e12,'I_T',ci/1e12,'v2_VA_T',ov/1e12,
              'alpha_minmax',(min(run[y][i]['capital_share_alpha'] for i in cohort),
                              max(run[y][i]['capital_share_alpha'] for i in cohort)))
    print('TAIWAN ENERGY')
    for r in rows(NEW/'country_sectors_2060_2226.ndjson'):
        if r['iso3']=='TWN' and r['sector']=='ENERGY' and r['year'] in YEARS:
            print(r['year'],'VA',r['value_added'],'GO',r['gross_output'],
                  'K',r['capital'],'A',r['A'],'employment',r['employment'],
                  'energy_index',r.get('energy_abundance_index'))
    print('GLOBAL')
    for y in YEARS:
        print(y,'VA_T',totals[y]/1e12,'K_T',total(run,y,'capital')/1e12,
              'I_T',total(run,y,'investment')/1e12,
              'KY',total(run,y,'capital')/totals[y])


if __name__=='__main__': main()
