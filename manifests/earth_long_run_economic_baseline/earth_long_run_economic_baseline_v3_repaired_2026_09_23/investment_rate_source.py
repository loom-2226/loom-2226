"""Frozen-vintage WDI national GFCF/GDP rates for forward investment initialization.

This changes the rate used after the preserved 2060 boundary. It does not rewrite
the 2026 seed, the 2031–2060 history, or the frozen 2060 economic state.
"""
import hashlib
import json
import math
import statistics
from pathlib import Path

SOURCE=Path('/home/ubuntu/LOOM_Earth2026/raw/WB_WDI_NE.GDI.FTOT.ZS_1990_2026.json')
SOURCE_SHA256='bdcba23035a47cefebc486ba17e12a1d8fbc977759668100b69c86b6bf86c5bc'
INDICATOR='NE.GDI.FTOT.ZS'
CURRENT_YEARS=(2025,2024)
FALLBACK_YEAR=2024
POLICY_ID='WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1'

def select_rates(observations,isos):
    """Use latest current national rate; impute missing from the same WDI series.

    `observations` maps ISO3 to {year: WDI percentage}. The fallback is the
    unweighted median of 2024 values among modeled economies with a 2024/25
    current national observation. It is an authored pooled imputation, never a
    claimed observation for the recipient country.
    """
    isos=tuple(sorted(isos))
    if len(isos)!=80 or len(set(isos))!=80:
        raise ValueError('expected exactly 80 unique modeled economies')
    for iso,series in observations.items():
        for year,value in series.items():
            if year in CURRENT_YEARS and not (
                isinstance(year,int) and math.isfinite(value) and 0.0<value<100.0
            ):
                raise ValueError(('invalid WDI national rate',iso,year,value))
    direct={iso:next(((year,observations[iso][year]) for year in CURRENT_YEARS
                      if year in observations.get(iso,{})),None) for iso in isos}
    donors=tuple(iso for iso in isos if direct[iso] is not None
                 and FALLBACK_YEAR in observations.get(iso,{}))
    if not donors:raise ValueError('no current WDI national-account fallback donors')
    fallback_pct=statistics.median(observations[iso][FALLBACK_YEAR] for iso in donors)
    result={}
    for iso in isos:
        chosen=direct[iso]
        if chosen is None:
            pct=fallback_pct
            years=(FALLBACK_YEAR,)
            method=f'unweighted_median_of_{len(donors)}_modeled_country_WDI_{FALLBACK_YEAR}_GFCF_GDP_percentages_divided_by_100'
            fallback=True
        else:
            year,pct=chosen
            years=(year,)
            method=f'latest_available_{CURRENT_YEARS[0]}_then_{CURRENT_YEARS[1]}_WDI_GFCF_GDP_percentage_divided_by_100'
            fallback=False
        result[iso]={
            'iso3':iso,'investment_rate':pct/100.0,
            'source':'World Bank WDI '+INDICATOR,
            'source_years':years,'calculation_method':method,
            'fallback_used':fallback,
            'fallback_donor_count':len(donors) if fallback else 0,
            'fallback_donor_iso3':donors if fallback else (),
            'source_sha256':SOURCE_SHA256,
        }
    return result,{'direct_count':sum(not row['fallback_used'] for row in result.values()),
                   'fallback_count':sum(row['fallback_used'] for row in result.values()),
                   'fallback_rate':fallback_pct/100.0,
                   'fallback_donors':donors,'current_years':CURRENT_YEARS,
                   'fallback_year':FALLBACK_YEAR}

def load_rates(isos):
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise ValueError('WDI GFCF/GDP source hash mismatch')
    metadata,rows=json.loads(SOURCE.read_text(encoding='utf-8'))
    if metadata['lastupdated']!='2026-07-13':
        raise ValueError('unexpected WDI source vintage')
    modeled=set(isos);observations={}
    for row in rows:
        iso=row['countryiso3code'];value=row['value']
        if iso not in modeled or value is None:continue
        if row['indicator']['id']!=INDICATOR:raise ValueError('WDI indicator mismatch')
        year=int(row['date'])
        series=observations.setdefault(iso,{})
        if year in series:raise ValueError(('duplicate WDI country-year',iso,year))
        series[year]=float(value)
    return select_rates(observations,modeled)
