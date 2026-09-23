#!/usr/bin/env python3
"""
LOOM SOLAR-CIVPROP — Horizon Adapter v0.6.1-d1-c1-h1

Extends the authored tail horizon to 2226. Historical documentation below describes
the inherited qualified 2060–2190 model. Use --stop-after for prefix/boundary tests.

Purpose
-------
Run a single long-horizon Earth-only blind propagation from the frozen,
qualified 2060 asset-aware boundary to 2190.

This script is specifically designed to eliminate manual five-year review
cycles. It computes every year internally, applies hard annual qualification
gates, prints only sparse checkpoints, and stops early only if a gate fails.

Boundary
--------
earth2060_boundary_FROZEN_v1.0/
    countries_2060.ndjson
    country_sectors_2060.ndjson
    country_sector_assets_2060.ndjson

Empirical / projected inputs
----------------------------
- UN WPP medium projection through 2100.
- Penn World Table 11.0 historical TFP anchor.
- OECD 2024 ten-sector bilateral IO topology as the REVEALED ACCESSIBILITY /
  TRADE-RESISTANCE PRIOR.

Post-2100 demography
--------------------
No 2226 demographic endpoint is used.

For each country:
- median 2091-2100 annual log population growth is observed from WPP;
- median 2091-2100 annual change in 15-64 share is observed from WPP;
- both rates decay exponentially toward zero after 2100.

This produces an asymptotic continuation of the WPP trajectory rather than a
hidden population target.

Trade / accessibility
---------------------
The OECD 2024 supplier-to-destination topology is no longer frozen.

For each supplier node (country, sector), its destination portfolio evolves:
- the 2024 normalized bilateral pattern is the revealed-accessibility prior;
- destination demand growth pulls weight toward faster-growing destinations;
- a small annual rewiring speed preserves network inertia;
- weights always renormalize to 1 exactly.

This is intentionally a "revealed trade resistance" model. It does NOT claim
to reconstruct physical distance, tariffs, institutions, or future treaties.
The same interface can later accept explicit generalized transport cost /
ephemeris accessibility for off-Earth propagation.

Important remaining provisional assumptions
-------------------------------------------
- 2060 labor-market frame ratio is held constant by country.
- 2060 labor-force participation rate is held constant by country.
- 2060 employment rate is held constant by country.
- 2060 aggregate investment / VA rate is held constant by country.
- no migration module;
- no explicit resource / energy constraint;
- no technology-threshold module;
- no off-Earth population or industry;
- no country/institution/corporation future canon is used.

This is therefore a BLIND EARTH CAUSAL-TECHNOLOGY QUALIFICATION RUN, not the
final Solar civilization simulator.

Outputs
-------
earth2060_2190_empirical_frontier_v0.5/
    countries_2060_2190.ndjson
    country_sectors_2060_2190.ndjson
    country_sector_assets_2060_2190.ndjson
    countries_2190.ndjson
    country_sectors_2190.ndjson
    country_sector_assets_2190.ndjson
    checkpoints.json

Earth2060_2190_empirical_frontier_report_v0.5.json

If all annual hard gates pass, status is:
    QUALIFIED_CAUSAL_TECH_BLIND_EARTH_2060_2190_PROVISIONAL
"""

from pathlib import Path
from collections import defaultdict
import csv, gzip, json, math, zipfile, time, hashlib
import xml.etree.ElementTree as ET
import argparse
import horizon_checkpoint as _checkpoint_io
from alpha_transform import transform as _transform_alpha
from investment_rate_source import load_rates as _load_national_investment_rates
from investment_rate_source import SOURCE as WDI_GFCF_SOURCE
from investment_rate_source import SOURCE_SHA256 as WDI_GFCF_SOURCE_SHA256
from investment_rate_source import POLICY_ID as NATIONAL_INVESTMENT_POLICY_ID
from long_run_repair import (effective_alpha, rebase_A, investment_budget,
                             repair_active_boundary)

ROOT = Path("/home/ubuntu/LOOM_Earth2026")
FREEZE = Path(__file__).resolve().parent / "frozen_2060"

COUNTRIES_2060_SRC = FREEZE / "countries_2060.ndjson"
SECTORS_2060_SRC = FREEZE / "country_sectors_2060.ndjson"
ASSETS_2060_SRC = FREEZE / "country_sector_assets_2060.ndjson"
FREEZE_MANIFEST = FREEZE / "Earth2060_boundary_FROZEN_manifest_v1.0.json"
POLICY_ID = "UNTREATED_FROZEN_2060_EXPLICIT_v1"
POLICY_FINGERPRINT = "db0dbfa36a3f98b0ca5917a72f842f26542240a6fe9746cda04965360bb8ae83"
ALPHA_CEILING = None
ALPHA_CEILING_ID = "NONE"
ALPHA_TRANSFORM_SHA256 = hashlib.sha256((Path(__file__).resolve().parent / "alpha_transform.py").read_bytes()).hexdigest()
INVESTMENT_SOURCE_HELPER_SHA256 = hashlib.sha256((Path(__file__).resolve().parent / "investment_rate_source.py").read_bytes()).hexdigest()

OECD = Path("/home/ubuntu/loom_earth_2026_2035/oecd_ten_sector_2024")
OECD_INTER = OECD / "current_bilateral_sector_intermediate_2024.ndjson"
OECD_FINAL = OECD / "current_bilateral_sector_final_demand_2024.ndjson"

RAW = ROOT / "raw"
WPP_TOTAL = RAW / "WPP2024_Demographic_Indicators_Medium.csv.gz"
WPP_AGE = RAW / "WPP2024_PopulationByAge5GroupSex_Percentage_Medium.csv.gz"
PWT_MAIN = Path("/home/ubuntu/loom_earth_2026_2035/source_archives/pwt110.xlsx")

OUTDIR = Path(__file__).resolve().parent / "unconfigured_results"
COUNTRIES_ALL = OUTDIR / f"countries_2060_2226.ndjson"
SECTORS_ALL = OUTDIR / f"country_sectors_2060_2226.ndjson"
ASSETS_ALL = OUTDIR / f"country_sector_assets_2060_2226.ndjson"
COUNTRIES_END = OUTDIR / "countries_2226.ndjson"
SECTORS_END = OUTDIR / "country_sectors_2226.ndjson"
ASSETS_END = OUTDIR / "country_sector_assets_2226.ndjson"
CHECKPOINTS = OUTDIR / "checkpoints.json"
REPORT = OUTDIR / "trajectory_report.json"

START_YEAR = 2060
END_YEAR = 2226
YEARS = tuple(range(START_YEAR, END_YEAR + 1))
FORECAST_YEARS = tuple(range(START_YEAR + 1, END_YEAR + 1))
WPP_END_YEAR = 2100
CHECKPOINT_YEARS = (2060, 2080, 2100, 2130, 2160, 2190, 2226)

TFP_HISTORY_START = 2000
TFP_HISTORY_END = 2023
TFP_TRANSITION_HALF_LIFE_YEARS = 10.0

# EVIDENCE-BOUNDED TECHNOLOGY POLICY (v0.3)
#
# IMPORTANT: published empirical results are used as VALIDATION BOUNDS, not as
# century-scale causal coefficients. The cited studies do not identify a lawful
# mapping from 2060 compute/robot stocks to 2190 macro productivity, and there is
# no empirical calibration for human-equivalent synthetic workers. Therefore the
# default blind run does not invent such a mapping.
#
# Historical anchors used for validation/documentation:
# - Graetz & Michaels (2018): robot adoption contributed ~0.36 percentage points
#   per year to labor-productivity growth in 17 countries, 1993-2007.
# - Brynjolfsson, Li & Raymond (2023/2025): generative-AI assistance raised
#   customer-support productivity ~14% on average, ~34% for novice/low-skill
#   workers, with minimal effects for experienced/high-skill workers. This is a
#   task-level treatment effect, NOT a macro TFP elasticity.
# - Comin, Hobijn & Rovito (2006): average cross-country convergence in technology
#   adoption ~4%/yr, while intensive-margin diffusion is not generally logistic.
# - Acemoglu & Restrepo (2018/2019): automation should be represented through
#   task displacement/new-task reinstatement, not generic factor augmentation.
# - Energy production-function evidence reports positive but highly heterogeneous
#   elasticities (~0.12 EU15 to ~0.37 BRIC in one 1995-2007 panel), which is too
#   broad to justify invented LOOM sector elasticities.
ROBOT_LABOR_PRODUCTIVITY_VALIDATION_PP = 0.36
GENAI_TASK_PRODUCTIVITY_VALIDATION_AVG = 0.14
GENAI_TASK_PRODUCTIVITY_VALIDATION_NOVICE = 0.34
TECH_ADOPTION_CONVERGENCE_VALIDATION_RATE = 0.04
ENERGY_ELASTICITY_VALIDATION_RANGE = (0.12, 0.37)

# Synthetics: no empirical 2026 calibration exists. Until a canon technology
# threshold + bill-of-materials/energy/compute production pathway is supplied,
# synthetic labor is held at zero rather than assigned an arbitrary cap, target,
# or diffusion speed.
SYNTHETIC_EMPIRICAL_MODE = False

# Legacy TFP bridge remains an inherited forecast assumption pending direct PWT persistence calibration.
TFP_TRANSITION_HALF_LIFE_YEARS = 10.0
# v0.4: do not force productivity growth to zero.  TFP is the macro residual through
# which disembodied technological/organizational progress is observed.  Future
# growth is anchored to each country's PWT history, with frontier/catch-up
# dynamics.  Compute/automation/energy indexes remain diagnostics until a
# separately identified causal mapping can be calibrated; this avoids double
# counting technology as both TFP and an extra multiplier.
TFP_FRONTIER_QUANTILE = 0.80
# v0.5 estimates frontier growth and convergence directly from PWT history.
# No permanent country-specific TFP growth anchors are propagated beyond 2060.
TFP_CATCHUP_SPEED_MIN = 0.0
TFP_CATCHUP_SPEED_MAX = 0.08

# v0.6.1 tagged productivity-boundary fills. Published PWT values always win.
CK_FILL = {"ARE":0.042465807136647986,"BGD":0.03657705248657813,"BRN":0.0024508590042336366,"COD":0.004160686530803769,"KHM":0.0035867531634272655,"MMR":0.011381396981094593,"PAK":0.028982054637810672,"VNM":0.040643641114690154}
HC_FILL = {"BLR":3.429450348,"STP":2.049918426}
ILOSTAT_LABSH_2019 = {"ARE":0.35811,"BGD":0.47151,"BLR":0.51693,"BRN":0.31733,"COD":0.38194,"KHM":0.46277,"MMR":0.51341,"PAK":0.52053,"STP":0.44471,"VNM":0.46764}
BOUNDARY_VERSION = "LOOM_Earth2026_Productivity_Boundary_Closure_v1.0"


# Post-2100 demographic rate half-lives.
POP_GROWTH_TAIL_HALF_LIFE = 40.0
WAP_SHARE_TAIL_HALF_LIFE = 30.0

# Structural allocation parameters inherited unchanged from qualified v0.5.
LABOR_ADJUST_SPEED = 0.10
INVESTMENT_ADJUST_SPEED = 0.12
DEMAND_ELASTICITY_LABOR = 0.60
PRODUCTIVITY_ELASTICITY_LABOR = 0.15
DEMAND_ELASTICITY_EXPANSION = 0.60
PRODUCTIVITY_ELASTICITY_EXPANSION = 0.15
INVESTMENT_INERTIA_EXPONENT = 0.70

# Endogenous trade / revealed-accessibility parameters.
TRADE_REWIRE_SPEED = 0.04
TRADE_DESTINATION_ELASTICITY = 0.75

SECTORS = (
    "ENERGY","BULK_MATERIALS","PRECISION_MATERIALS","COMPUTE",
    "HABITATS_CONSTRUCTION","SHIPS_AEROSPACE","MEDICINE",
    "TRANSPORT_LOGISTICS","CERTIFICATION_METROLOGY","SERVICES"
)
ASSETS = (
    "structures","machinery","transport_equipment","other_assets"
)
FD_CAPITAL = {"GFCF","INVNT"}

EPS = 1e-30
NS = {"a":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

# Hard annual gates: meant to catch explosions, not tune outcomes.
MAX_ANNUAL_LABOR_SHARE_MOVE_PP = 1.5
MAX_ANNUAL_INVESTMENT_SHARE_MOVE_PP = 2.0
MAX_ANNUAL_TRADE_TV_MOVE = 0.10
MIN_COUNTRY_VA_GROWTH = -0.15
MAX_COUNTRY_VA_GROWTH = 0.15
MIN_GLOBAL_VA_GROWTH = -0.08
MAX_GLOBAL_VA_GROWTH = 0.10
MAX_SECTOR_VA_SHARE = 0.90
MIN_WAP_SHARE = 0.20
MAX_WAP_SHARE = 0.80
MIN_CAPITAL_OUTPUT_RATIO = 0.25
MAX_CAPITAL_OUTPUT_RATIO = 25.0
MAX_ANNUAL_SYNTHETIC_RATIO_MOVE = 0.25
MAX_ANNUAL_TECH_MULTIPLIER_LOG_MOVE = 0.12


def sf(x):
    try:
        v=float(str(x).strip())
        return v if math.isfinite(v) else None
    except Exception:
        return None

def si(x):
    try:
        return int(float(str(x).strip()))
    except Exception:
        return None

def norm(x):
    return str(x or "").strip()

def progress(msg, started):
    print(
        f"[PROGRESS] {msg} | elapsed={time.monotonic()-started:.1f}s",
        flush=True
    )

def choose(fields,candidates):
    low={f.lower():f for f in fields}
    for c in candidates:
        if c in fields:
            return c
        if c.lower() in low:
            return low[c.lower()]
    return None

def open_csv(path):
    if str(path).endswith(".gz"):
        return gzip.open(path,"rt",encoding="utf-8-sig",newline="")
    return path.open("r",encoding="utf-8-sig",newline="")

def load_ndjson(path):
    out=[]
    with path.open("r",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def median(vals):
    vals=sorted(vals)
    if not vals:
        raise ValueError("median of empty sequence")
    n=len(vals)
    m=n//2
    return vals[m] if n%2 else 0.5*(vals[m-1]+vals[m])

def normalize(d,keys):
    vals={k:max(0.0,float(d.get(k,0.0))) for k in keys}
    z=sum(vals.values())
    if z<=0:
        return {k:1.0/len(keys) for k in keys}
    return {k:vals[k]/z for k in keys}

def blend_shares(old,target,speed,keys):
    if not 0<=speed<=1:
        raise ValueError("bad blend speed")
    raw={k:(1-speed)*old[k]+speed*target[k] for k in keys}
    return normalize(raw,keys)

def calibrated_ratio(current,baseline):
    current=float(current)
    baseline=float(baseline)
    if not math.isfinite(current) or not math.isfinite(baseline):
        raise ValueError("non-finite calibrated ratio")
    if current<0 or baseline<0:
        raise ValueError("negative calibrated ratio")
    if baseline<=EPS:
        return 1.0
    return max(EPS,current/baseline)

# ---------------------------------------------------------------------------
# XLSX reader for PWT
# ---------------------------------------------------------------------------

def xlsx_shared_strings(z):
    try:
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out=[]
    for si_el in root.findall("a:si",NS):
        parts=[]
        for t in si_el.iter("{%s}t"%NS["a"]):
            parts.append(t.text or "")
        out.append("".join(parts))
    return out

def xlsx_sheet_path(z,sheet_name):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={
        r.attrib["Id"]:r.attrib["Target"]
        for r in rels
    }
    for sh in wb.find("a:sheets",NS):
        if sh.attrib.get("name")==sheet_name:
            rid=sh.attrib.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            target=relmap[rid]
            if target.startswith("/"):
                return target.lstrip("/")
            if not target.startswith("xl/"):
                target="xl/"+target
            return target
    raise ValueError(f"sheet not found {sheet_name}")

def col_index(ref):
    letters="".join(ch for ch in ref if ch.isalpha())
    n=0
    for ch in letters:
        n=n*26+(ord(ch.upper())-64)
    return n-1

def read_xlsx_rows(path,sheet_name):
    with zipfile.ZipFile(path,"r") as z:
        shared=xlsx_shared_strings(z)
        sheet=xlsx_sheet_path(z,sheet_name)
        root=ET.fromstring(z.read(sheet))
        data=root.find("a:sheetData",NS)
        for row in data.findall("a:row",NS):
            vals={}
            mx=-1
            for c in row.findall("a:c",NS):
                idx=col_index(c.attrib["r"])
                mx=max(mx,idx)
                typ=c.attrib.get("t")
                v=c.find("a:v",NS)
                if typ=="inlineStr":
                    t=c.find("a:is/a:t",NS)
                    value=t.text if t is not None else ""
                elif v is None:
                    value=""
                elif typ=="s":
                    value=shared[int(v.text)]
                else:
                    value=v.text
                vals[idx]=value
            yield [vals.get(i,"") for i in range(mx+1)]

# ---------------------------------------------------------------------------
# WPP demography
# ---------------------------------------------------------------------------

def load_wpp_total_years(target_isos,years):
    years=set(years)
    out={y:{} for y in years}
    started=time.monotonic()
    progress("WPP total population: opening compressed CSV",started)

    with open_csv(WPP_TOTAL) as f:
        rd=csv.DictReader(f)
        fields=rd.fieldnames or []
        iso_col=choose(fields,("ISO3_code","ISO3 Alpha-code","ISO3"))
        year_col=choose(fields,("Time","Year"))
        pop_col=choose(fields,(
            "TPopulation1Jan","TPopulation",
            "Total Population, as of 1 January (thousands)"
        ))
        if not iso_col or not year_col or not pop_col:
            raise ValueError("WPP total columns unresolved")

        scanned=matched=0
        for r in rd:
            scanned+=1
            if scanned%50000==0:
                progress(f"WPP total: scanned {scanned:,}, matched {matched:,}",started)
            y=si(r.get(year_col))
            if y not in years:
                continue
            iso=norm(r.get(iso_col))
            if iso not in target_isos:
                continue
            v=sf(r.get(pop_col))
            if v is not None:
                out[y][iso]=v*1000.0
                matched+=1

    progress(
        f"WPP total complete: scanned {scanned:,}, matched {matched:,}",started
    )
    return out

def load_wpp_working_age_years(target_isos,years):
    years=set(years)
    accum={y:{} for y in years}
    started=time.monotonic()
    progress("WPP age structure: opening compressed CSV",started)

    with open_csv(WPP_AGE) as f:
        rd=csv.DictReader(f)
        fields=rd.fieldnames or []
        iso_col=choose(fields,("ISO3_code","ISO3 Alpha-code","ISO3"))
        year_col=choose(fields,("Time","Year"))
        age_start_col=choose(fields,("AgeGrpStart","AgeStart","Age group start"))
        age_col=choose(fields,("AgeGrp","Age group","Age"))
        pct_col=choose(fields,("PopTotal","Population total","Population"))
        if not iso_col or not year_col or not pct_col:
            raise ValueError("WPP age columns unresolved")

        scanned=matched=0
        for r in rd:
            scanned+=1
            if scanned%100000==0:
                progress(f"WPP age: scanned {scanned:,}, matched {matched:,}",started)

            y=si(r.get(year_col))
            if y not in years:
                continue
            iso=norm(r.get(iso_col))
            if iso not in target_isos:
                continue

            age=si(r.get(age_start_col)) if age_start_col else None
            if age is None and age_col:
                digits="".join(
                    ch if ch.isdigit() else " "
                    for ch in norm(r.get(age_col))
                ).split()
                age=int(digits[0]) if digits else None

            if age is None or not 15<=age<=60:
                continue

            v=sf(r.get(pct_col))
            if v is not None:
                accum[y][iso]=accum[y].get(iso,0.0)+v
                matched+=1

    out={}
    for y in years:
        bad={iso:v for iso,v in accum[y].items() if not 0<v<100}
        if bad:
            raise ValueError(f"WPP age bad percentages {y}: {list(bad.items())[:5]}")
        out[y]={iso:v/100.0 for iso,v in accum[y].items()}

    progress(
        f"WPP age complete: scanned {scanned:,}, matched {matched:,}",started
    )
    return out

def extend_demography_tail(isos,wpp_pop,wpp_wap):
    """
    Extrapolate WPP after 2100 without an endpoint target.

    Country-specific terminal rates are estimated from 2091-2100 and their
    magnitudes decay toward zero.
    """
    pop_tail_anchor={}
    wap_tail_anchor={}

    for iso in sorted(isos):
        gs=[]
        ds=[]
        for y in range(2092,2101):
            a=wpp_pop[y-1][iso]
            b=wpp_pop[y][iso]
            if a>0 and b>0:
                gs.append(math.log(b/a))
            ds.append(wpp_wap[y][iso]-wpp_wap[y-1][iso])

        pop_tail_anchor[iso]=median(gs)
        wap_tail_anchor[iso]=median(ds)

    pop={y:dict(v) for y,v in wpp_pop.items()}
    wap={y:dict(v) for y,v in wpp_wap.items()}

    for y in range(2101,END_YEAR+1):
        n=y-2100
        decay_pop=math.exp(-math.log(2.0)*n/POP_GROWTH_TAIL_HALF_LIFE)
        decay_wap=math.exp(-math.log(2.0)*n/WAP_SHARE_TAIL_HALF_LIFE)

        pop[y]={}
        wap[y]={}
        for iso in sorted(isos):
            g=pop_tail_anchor[iso]*decay_pop
            d=wap_tail_anchor[iso]*decay_wap

            pop[y][iso]=pop[y-1][iso]*math.exp(g)
            wap[y][iso]=min(
                MAX_WAP_SHARE,
                max(MIN_WAP_SHARE,wap[y-1][iso]+d)
            )

    return pop,wap,pop_tail_anchor,wap_tail_anchor

# ---------------------------------------------------------------------------
# PWT TFP anchors
# ---------------------------------------------------------------------------

def load_pwt_tfp_anchors(target_isos):
    """v0.6.1: ctfp for comparable levels; rtfpna for within-country growth only."""
    started=time.monotonic()
    progress("PWT CTFP-gap calibration: opening workbook",started)
    rows=read_xlsx_rows(PWT_MAIN,"Data")
    header=next(rows); idx={h:i for i,h in enumerate(header)}
    needed=("countrycode","year","ctfp","rtfpna","cgdpo","cda","pop","ck","emp","avh","hc","labsh")
    missing=[k for k in needed if k not in idx]
    if missing: raise ValueError(f"PWT v0.6.1 calibration missing fields: {missing}")
    raw=defaultdict(dict); scanned=0; maxidx=max(idx[k] for k in needed)
    for row in rows:
        scanned+=1
        if scanned%5000==0: progress(f"PWT CTFP-gap calibration: scanned {scanned:,}",started)
        if len(row)<=maxidx: row=row+[""]*(maxidx+1-len(row))
        iso=norm(row[idx["countrycode"]]).upper(); y=si(row[idx["year"]])
        if not iso or y is None: continue
        rec={}
        for k in needed:
            if k not in ("countrycode","year"): rec[k]=sf(row[idx[k]])
        raw[iso][y]=rec

    # Original PWT 2019 complete cases define the fixed published reference frame.
    ref=[]
    for iso in sorted(raw):
        ss=raw[iso]
        r=ss.get(2019)
        if not r: continue
        vals=[r.get(k) for k in ("cgdpo","cda","pop","ck","emp","avh","hc","labsh")]
        if any(v is None for v in vals) or any(v<=0 for v in vals[:-1]) or not 0<r["labsh"]<1: continue
        ref.append({"iso3":iso,"yo":math.log(r["cgdpo"]/r["pop"]),"dap":math.log(r["cda"]/r["pop"]),
                    "l":math.log((r["avh"]*r["emp"]*r["hc"])/r["pop"]),"k":math.log(r["ck"]/r["pop"]),"labsh":r["labsh"]})
    if len(ref)<80: raise ValueError(f"Too few original PWT 2019 complete cases: {len(ref)}")
    mean_yo=sum(r["yo"] for r in ref)/len(ref); mean_dap=sum(r["dap"] for r in ref)/len(ref)
    mean_l=sum(r["l"] for r in ref)/len(ref); mean_k=sum(r["k"] for r in ref)/len(ref)
    mean_labsh=sum(r["labsh"] for r in ref)/len(ref)

    def raw_ctfp(r):
        yo=math.log(r["cgdpo"]/r["pop"]); _dap=math.log(r["cda"]/r["pop"])
        l=math.log((r["avh"]*r["emp"]*r["hc"])/r["pop"]); k=math.log(r["ck"]/r["pop"])
        avlsh=.5*(r["labsh"]+mean_labsh)
        return math.exp((yo-mean_yo)-avlsh*(l-mean_l)-(1-avlsh)*(k-mean_k))

    usa=raw.get("USA",{}).get(2019)
    if not usa: raise ValueError("USA 2019 missing")
    usa_raw=raw_ctfp(usa)

    # v0.6.1 boundary-component preflight.
    # Some PWT rows with missing ctfp also lack avh. Fill avh transparently:
    # 1) nearest same-country positive PWT avh observation;
    # 2) median of the 10 2019 PWT countries nearest in log cgdpo/pop;
    # 3) global 2019 positive-avh median.
    avh_2019=[]
    for jiso in sorted(raw):
        jss=raw[jiso]
        jr=jss.get(2019)
        if not jr: continue
        javh=jr.get("avh"); jcgdpo=jr.get("cgdpo"); jpop=jr.get("pop")
        if javh is not None and javh>0:
            avh_2019.append((jiso,javh,jcgdpo,jpop))
    if not avh_2019:
        raise ValueError("No positive PWT 2019 avh observations available")
    avh_global=median([x[1] for x in avh_2019])

    def boundary_avh_fill(iso,rr):
        v=rr.get("avh")
        if v is not None and v>0: return v,None
        hist=[]
        for y in sorted(raw.get(iso,{})):
            rh=raw[iso][y]
            hv=rh.get("avh")
            if hv is not None and hv>0:
                hist.append((abs(y-2019),-y,y,hv))
        if hist:
            hist.sort()
            _,_,yr,hv=hist[0]
            return hv,{"method":"PWT11_NEAREST_YEAR_AVH","source_year":yr,"value":hv}
        cgdpo=rr.get("cgdpo"); pop=rr.get("pop")
        if cgdpo is not None and pop is not None and cgdpo>0 and pop>0:
            target_log=math.log(cgdpo/pop)
            peers=[]
            for piso,pavh,pcgdpo,ppop in avh_2019:
                if pcgdpo is None or ppop is None or pcgdpo<=0 or ppop<=0: continue
                peers.append((abs(math.log(pcgdpo/ppop)-target_log),piso,pavh))
            peers.sort()
            chosen=peers[:10]
            if chosen:
                hv=median([x[2] for x in chosen])
                return hv,{"method":"PWT11_2019_INCOME_NEAREST_PEER_MEDIAN_AVH",
                           "peer_count":len(chosen),"peers":[x[1] for x in chosen],"value":hv}
        return avh_global,{"method":"PWT11_2019_GLOBAL_MEDIAN_AVH","value":avh_global}

    boundary_component_fills={}
    ctfp2019={}; provenance={}; direct=derived=0
    for iso in sorted(target_isos):
        r=raw.get(iso,{}).get(2019)
        if not r: raise ValueError(f"{iso}: PWT 2019 row missing")
        c=r.get("ctfp")
        if c is not None and c>0:
            ctfp2019[iso]=c; provenance[iso]="PWT11_OBSERVED_CTFP_2019"; direct+=1; continue
        rr=dict(r)
        if iso in CK_FILL and (rr.get("ck") is None or rr.get("ck")<=0): rr["ck"]=CK_FILL[iso]
        if iso in HC_FILL and (rr.get("hc") is None or rr.get("hc")<=0): rr["hc"]=HC_FILL[iso]
        if rr.get("labsh") is None or not 0<rr["labsh"]<1:
            if iso in ILOSTAT_LABSH_2019: rr["labsh"]=ILOSTAT_LABSH_2019[iso]
        avh_fill,avh_meta=boundary_avh_fill(iso,rr)
        if rr.get("avh") is None or rr.get("avh")<=0:
            rr["avh"]=avh_fill
            boundary_component_fills.setdefault(iso,{})["avh"]=avh_meta
        req=("cgdpo","cda","pop","ck","emp","avh","hc","labsh")
        bad=[k for k in req if rr.get(k) is None or rr[k]<=0]
        if bad: raise ValueError(f"{iso}: unresolved ctfp components {bad}")
        ctfp2019[iso]=raw_ctfp(rr)/usa_raw; provenance[iso]="PWT11_METHOD_DERIVED_CTFP_2019_TAGGED"; derived+=1
    if set(ctfp2019)!=set(target_isos): raise ValueError("ctfp roster coverage failure")

    ranked=sorted(ctfp2019,key=lambda i:ctfp2019[i],reverse=True); top10=tuple(ranked[:10]); top20=tuple(ranked[:20])
    vv=sorted(ctfp2019.values()); pos=.90*(len(vv)-1); lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    q90=vv[lo] if lo==hi else vv[lo]*(hi-pos)+vv[hi]*(pos-lo)
    groups={"TOP10":top10,"TOP20":top20,"Q90":tuple(sorted(i for i,v in ctfp2019.items() if v>=q90))}

    estimates=[]; detail=[]
    for gname,members in groups.items():
        for start,end in ((1990,2023),(2000,2023),(2010,2023)):
            annual=[]
            for y in range(start+1,end+1):
                gs=[]
                for iso in sorted(members):
                    a=raw.get(iso,{}).get(y-1,{}).get("rtfpna"); b=raw.get(iso,{}).get(y,{}).get("rtfpna")
                    if a is not None and b is not None and a>0 and b>0: gs.append(math.log(b/a))
                if len(gs)>=max(3,len(members)//3): annual.append(median(gs))
            if len(annual)>=8:
                est=median(annual); estimates.append(est)
                detail.append({"group":gname,"window":[start,end],"n_years":len(annual),"log_growth":est,"simple_growth":math.exp(est)-1})
    if len(estimates)<3: raise ValueError("Insufficient fixed-frontier growth estimates")
    frontier_growth_log=median(estimates)

    anchored={}
    for iso in sorted(target_isos):
        rt19=raw.get(iso,{}).get(2019,{}).get("rtfpna")
        if rt19 is None or rt19<=0: continue
        anchored[iso]={}
        for y in range(2000,2024):
            rt=raw.get(iso,{}).get(y,{}).get("rtfpna")
            if rt is not None and rt>0: anchored[iso][y]=ctfp2019[iso]*(rt/rt19)
    frontier_hist={}
    for y in range(2000,2024):
        xs=[anchored[i][y] for i in sorted(top20) if i in anchored and y in anchored[i]]
        if len(xs)>=8: frontier_hist[y]=median(xs)
    xy=xx=0.0; nobs=0
    observation_ids=[]
    for iso in sorted(anchored):
        ss=anchored[iso]
        for y in range(2001,2024):
            if y not in ss or y-1 not in ss or y not in frontier_hist or y-1 not in frontier_hist: continue
            gap=max(0.0,math.log(frontier_hist[y-1]/ss[y-1]))
            if gap<=0: continue
            excess=math.log(ss[y]/ss[y-1])-math.log(frontier_hist[y]/frontier_hist[y-1])
            xy+=gap*excess; xx+=gap*gap; nobs+=1
            observation_ids.append([iso,y-1,y])
    raw_beta=xy/xx if xx>0 else 0.0
    catchup_speed=min(TFP_CATCHUP_SPEED_MAX,max(TFP_CATCHUP_SPEED_MIN,raw_beta))
    frontier_2019=median([ctfp2019[i] for i in sorted(top20)])
    gap2019={i:max(0.0,math.log(frontier_2019/ctfp2019[i])) for i in sorted(target_isos)}
    gap2060={i:gap2019[i]*math.exp(-catchup_speed*41) for i in sorted(target_isos)}

    # Preserve old return interface; country rates are diagnostic only.
    out={}; fallback_isos=[]; pool=[]
    for iso in sorted(target_isos):
        gs=[]
        for y in range(2001,2024):
            a=raw.get(iso,{}).get(y-1,{}).get("rtfpna"); b=raw.get(iso,{}).get(y,{}).get("rtfpna")
            if a is not None and b is not None and a>0 and b>0: gs.append(math.log(b/a))
        if len(gs)>=8: pool.append(median(gs))
    fallback=median(pool) if pool else frontier_growth_log
    for iso in sorted(target_isos):
        gs=[]
        for y in range(2001,2024):
            a=raw.get(iso,{}).get(y-1,{}).get("rtfpna"); b=raw.get(iso,{}).get(y,{}).get("rtfpna")
            if a is not None and b is not None and a>0 and b>0: gs.append(math.log(b/a))
        good=len(gs)>=8
        if not good: fallback_isos.append(iso)
        g=median(gs) if good else fallback
        out[iso]={"annual_log_growth_anchor":g,"annual_simple_growth_anchor":math.exp(g)-1,
                  "method":"PWT11_RTFPNA_DIAGNOSTIC_ONLY","fallback":not good,"observed_transitions":len(gs)}

    calibration={
      "method":"PWT11_CTFP_LEVEL_GAP_PLUS_RTFPNA_WITHIN_COUNTRY_GROWTH_v0.6.1",
      "boundary_version":BOUNDARY_VERSION,"ctfp_anchor_year":2019,"ctfp_direct_count":direct,"ctfp_derived_count":derived,
      "ctfp_provenance":provenance,"ctfp_2019":ctfp2019,"boundary_component_fills":boundary_component_fills,"fixed_frontier_groups":{k:list(v) for k,v in groups.items()},
      "frontier_growth_log":frontier_growth_log,"frontier_growth_simple":math.exp(frontier_growth_log)-1,
      "innovation_estimates":detail,"catchup_speed":catchup_speed,"raw_catchup_speed":raw_beta,"convergence_observations":nobs,
      "frontier_2019":frontier_2019,"gap_2019_log":gap2019,"gap_2060_log":gap2060,
      "reference_sample":"ORIGINAL_PWT11_2019_COMPLETE_CASES_FIXED","original_reference_n":len(ref),
      "cross_country_rtfpna_levels_used":False,"runtime_internal_tfp_multiplier_used_as_cross_country_level":False,
    }
    calibration["ordering_audit"]={
        "policy":"ISO3_ASCENDING_THEN_TRANSITION_END_YEAR_ASCENDING",
        "observation_id_fields":["iso3","start_year","end_year"],
        "ordered_observation_ids":observation_ids,
        "observation_sequence_sha256":hashlib.sha256(json.dumps(observation_ids,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest(),
        "reference_country_order":[r["iso3"] for r in ref],
        "anchored_country_order":list(anchored),
        "sequence_encoding":"compact ASCII JSON array; no trailing newline",
    }
    if boundary_component_fills:
        print("BOUNDARY COMPONENT FILLS:",json.dumps(boundary_component_fills,sort_keys=True),flush=True)
    else:
        print("BOUNDARY COMPONENT FILLS: none",flush=True)
    progress(f"PWT CTFP-gap complete: direct={direct} derived={derived}; frontier_g={calibration['frontier_growth_simple']:.4%}; catchup={catchup_speed:.5f}; n={nobs:,}",started)
    return out,fallback_isos,fallback,calibration

def transition_tfp_growth(start_simple,frontier_growth_log,catchup_speed,years_after_2060,gap_log=None):
    """Inherited 2060 growth transitions to frontier innovation + CTFP-gap catch-up."""
    if start_simple<=-1: raise ValueError("invalid starting TFP growth")
    start_log=math.log1p(start_simple)
    decay=math.exp(-math.log(2.0)*years_after_2060/TFP_TRANSITION_HALF_LIFE_YEARS)
    base_log=frontier_growth_log+(start_log-frontier_growth_log)*decay
    return math.exp(base_log+catchup_speed*max(0.0,float(gap_log or 0.0)))-1.0


def causal_technology_state(
    compute_index,
    automation_index,
    energy_index,
    previous_synthetic_ratio,
    sector,
):
    """
    Evidence-bounded v0.3 technology interface.

    We continue to calculate compute, automation and energy capability indexes so
    the run exposes the physical state needed for later task/technology modules.
    We DO NOT turn those indexes into productivity or synthetic labor using
    invented elasticities. Published empirical estimates above are diagnostics /
    calibration targets only.
    """
    for x in (compute_index, automation_index, energy_index):
        if not math.isfinite(float(x)) or float(x) < 0:
            raise ValueError("invalid enabling-capacity index")
    return 0.0, 1.0, 0.0

# ---------------------------------------------------------------------------
# OECD revealed-accessibility topology
# ---------------------------------------------------------------------------

def load_io_topology(target_isos):
    """
    Supplier-oriented sparse topology normalized to one per supplier node.

    Key types:
      ("INTER", destination_country, destination_sector)
      ("FINAL", destination_country, final_demand_category)
      ("ROW_INTER",)
      ("ROW_FINAL", final_demand_category)
    """
    started=time.monotonic()
    progress("OECD topology: reading intermediate flows",started)

    components=defaultdict(lambda:defaultdict(float))
    inter_rows=0
    final_rows=0

    with OECD_INTER.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            inter_rows+=1
            if inter_rows%100000==0:
                progress(f"OECD intermediate: {inter_rows:,} rows",started)

            r=json.loads(line)
            oc=r["origin_country"]
            os=r["origin_sector"]
            dc=r["destination_country"]
            ds=r["destination_sector"]
            v=float(r["value"])

            if oc not in target_isos or os not in SECTORS or v<=0:
                continue

            node=(oc,os)
            if dc in target_isos and ds in SECTORS:
                components[node][("INTER",dc,ds)]+=v
            else:
                components[node][("ROW_INTER",)]+=v

    progress("OECD topology: reading final demand",started)

    with OECD_FINAL.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            final_rows+=1
            if final_rows%100000==0:
                progress(f"OECD final demand: {final_rows:,} rows",started)

            r=json.loads(line)
            oc=r["origin_country"]
            os=r["origin_sector"]
            dc=r["destination_country"]
            fd=r["final_demand_category"]
            v=float(r["value"])

            if oc not in target_isos or os not in SECTORS or v<=0:
                continue

            node=(oc,os)
            if dc in target_isos:
                components[node][("FINAL",dc,fd)]+=v
            else:
                components[node][("ROW_FINAL",fd)]+=v

    weights={}
    zero_nodes=[]
    component_count=0

    for iso in sorted(target_isos):
        for s in SECTORS:
            node=(iso,s)
            c=components.get(node,{})
            total=sum(c.values())
            if total<=0:
                weights[node]={("SELF_BASE",):1.0}
                zero_nodes.append(node)
            else:
                weights[node]={k:v/total for k,v in c.items() if v>0}
            component_count+=len(weights[node])

    progress(
        f"OECD topology complete: intermediate_rows={inter_rows:,} "
        f"final_rows={final_rows:,} supplier_components={component_count:,} "
        f"zero_nodes={len(zero_nodes)}",
        started
    )
    return weights,{
        "intermediate_rows":inter_rows,
        "final_rows":final_rows,
        "supplier_components":component_count,
        "zero_supplier_nodes":[{"iso3":i,"sector":s} for i,s in zero_nodes],
    }

def component_driver(
    key,
    prev_go_ratio,
    prev_country_va_ratio,
    prev_country_inv_ratio,
    global_va_ratio,
):
    typ=key[0]
    if typ=="INTER":
        _,dc,ds=key
        return prev_go_ratio[(dc,ds)]
    if typ=="FINAL":
        _,dc,fd=key
        return (
            prev_country_inv_ratio[dc]
            if fd in FD_CAPITAL
            else prev_country_va_ratio[dc]
        )
    if typ in {"ROW_INTER","ROW_FINAL"}:
        return global_va_ratio
    if typ=="SELF_BASE":
        return 1.0
    raise ValueError(f"unknown topology key {key}")

def rewire_supplier_weights(
    baseline,
    current,
    prev_go_ratio,
    prev_country_va_ratio,
    prev_country_inv_ratio,
    global_va_ratio,
):
    """
    Slow destination rewiring around the 2024 revealed-accessibility prior.

    target[k] proportional to:
        baseline[k] * destination_driver[k]^elasticity

    current moves only TRADE_REWIRE_SPEED toward target.
    """
    keys=tuple(current.keys())
    raw={}
    for k in keys:
        driver=max(
            EPS,
            component_driver(
                k,prev_go_ratio,prev_country_va_ratio,
                prev_country_inv_ratio,global_va_ratio
            )
        )
        raw[k]=max(EPS,baseline[k])*(driver**TRADE_DESTINATION_ELASTICITY)

    target=normalize(raw,keys)
    new=blend_shares(current,target,TRADE_REWIRE_SPEED,keys)

    max_component=max(abs(new[k]-current[k]) for k in keys)
    total_variation=0.5*sum(abs(new[k]-current[k]) for k in keys)

    demand_factor=sum(
        new[k]*max(
            EPS,
            component_driver(
                k,prev_go_ratio,prev_country_va_ratio,
                prev_country_inv_ratio,global_va_ratio
            )
        )
        for k in keys
    )

    return new,max_component,total_variation,max(EPS,demand_factor)

# ---------------------------------------------------------------------------
# Production and structural allocation
# ---------------------------------------------------------------------------

def production(A,k,l,alpha,tfp):
    if A==0:
        return 0.0
    if min(k,l,tfp)<=0:
        return 0.0
    y=tfp*A*(k**alpha)*(l**(1-alpha))
    if not math.isfinite(y) or y<0:
        raise ValueError("invalid production")
    return y

def desired_labor_shares(prev_shares,demand_pressure,labor_productivity):
    prod_vals=[max(EPS,labor_productivity[s]) for s in SECTORS]
    prod_ref=median(prod_vals)
    raw={}
    for s in SECTORS:
        dp=max(EPS,demand_pressure[s])
        rp=max(EPS,labor_productivity[s]/prod_ref)
        raw[s]=(
            max(EPS,prev_shares[s])
            * (dp**DEMAND_ELASTICITY_LABOR)
            * (rp**PRODUCTIVITY_ELASTICITY_LABOR)
        )
    return normalize(raw,SECTORS)

def desired_expansion_investment_shares(
    prev_investment_shares,
    demand_pressure,
    capital_productivity,
):
    prod_vals=[max(EPS,capital_productivity[s]) for s in SECTORS]
    prod_ref=median(prod_vals)
    raw={}
    for s in SECTORS:
        prior=max(EPS,prev_investment_shares[s])
        dp=max(EPS,demand_pressure[s])
        rp=max(EPS,capital_productivity[s]/prod_ref)
        raw[s]=(
            (prior**INVESTMENT_INERTIA_EXPONENT)
            * (dp**DEMAND_ELASTICITY_EXPANSION)
            * (rp**PRODUCTIVITY_ELASTICITY_EXPANSION)
        )
    return normalize(raw,SECTORS)

def allocate_asset_replacement_and_expansion(
    country_investment,
    asset_capital,
    asset_depreciation,
    prev_investment_shares,
    demand_pressure,
    capital_productivity,
):
    replacement_need={}
    replacement_funded={}
    expansion_asset={}
    investment_asset={}

    total_replacement=0.0
    for s in SECTORS:
        for a in ASSETS:
            k=max(0.0,float(asset_capital[(s,a)]))
            d=float(asset_depreciation[(s,a)])
            if not (0<=d<1):
                raise ValueError(f"bad depreciation {s}/{a}")
            need=d*k
            replacement_need[(s,a)]=need
            total_replacement+=need

    coverage=(
        min(1.0,country_investment/total_replacement)
        if total_replacement>0 else 1.0
    )

    for key,need in replacement_need.items():
        funded=need*coverage
        replacement_funded[key]=funded
        expansion_asset[key]=0.0
        investment_asset[key]=funded

    remaining=(0.0 if country_investment<=total_replacement
               else max(0.0,country_investment-sum(replacement_funded.values())))

    expansion_sector={s:0.0 for s in SECTORS}

    if remaining>0:
        desired=desired_expansion_investment_shares(
            prev_investment_shares,
            demand_pressure,
            capital_productivity,
        )
        expansion_share=blend_shares(
            prev_investment_shares,
            desired,
            INVESTMENT_ADJUST_SPEED,
            SECTORS,
        )
        for s in SECTORS:
            sector_exp=remaining*expansion_share[s]
            expansion_sector[s]=sector_exp
            comp=normalize(
                {a:asset_capital[(s,a)] for a in ASSETS},
                ASSETS
            )
            for a in ASSETS:
                v=sector_exp*comp[a]
                expansion_asset[(s,a)]=v
                investment_asset[(s,a)]+=v

    investment_sector={
        s:sum(investment_asset[(s,a)] for a in ASSETS)
        for s in SECTORS
    }
    shares=normalize(investment_sector,SECTORS)

    resid=abs(sum(investment_asset.values())-country_investment)/max(
        1.0,abs(country_investment)
    )
    if resid>1e-12:
        raise ValueError(f"investment allocation residual {resid}")

    return (
        investment_sector,
        investment_asset,
        shares,
        replacement_need,
        replacement_funded,
        expansion_sector,
        expansion_asset,
        coverage,
    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def verify_policy(base=None):
    """Reject silent fallback, changed frozen inputs, or an archived output as input."""
    manifest=json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    policy=manifest["economic_policy"]
    if policy["id"]!=POLICY_ID or policy["ordered_vector_sha256"]!=POLICY_FINGERPRINT:
        raise ValueError("Economic policy identity mismatch")
    for name,record in manifest["files"].items():
        if (FREEZE/name).resolve()!=Path(record["path"]).resolve():
            raise ValueError("Economic source path mismatch")
        if _checkpoint_io.sha(FREEZE/name)!=record["sha256"]:
            raise ValueError("Economic source hash mismatch")
    vector=policy["ordered_vector"]
    digest=hashlib.sha256(json.dumps(vector,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    if digest!=POLICY_FINGERPRINT or len(vector)!=80:
        raise ValueError("Economic policy vector mismatch")
    if base is not None:
        actual=[[iso,base[iso]["alpha"],base[iso]["investment_rate"]] for iso in sorted(base)]
        if actual!=vector:
            raise ValueError("Economic policy not loaded into active state")
    return policy

def effective_policy_vector(policy, ceiling, national_rates):
    return [[iso, min(alpha, ceiling) if ceiling is not None else alpha,
             national_rates[iso]["investment_rate"]]
            for iso, alpha, _original_rate in policy["ordered_vector"]]

def verify_effective_policy(base, policy, national_rates):
    expected=effective_policy_vector(policy, ALPHA_CEILING, national_rates)
    actual=[[iso,base[iso]["alpha"],base[iso]["investment_rate"]] for iso in sorted(base)]
    if actual!=expected:
        raise ValueError("National GFCF and alpha experiment policy not loaded into active state")
    return hashlib.sha256(json.dumps(expected,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def main():
    run_started=time.monotonic()
    print(f"VISIBLE OUTPUT ROOT: {ROOT}",flush=True)

    _policy=verify_policy()
    _national_rates,_national_summary=_load_national_investment_rates(
        [row[0] for row in _policy["ordered_vector"]]
    )
    _compat,_constants=_checkpoint_io.compatibility(globals(),__file__)
    if _options.resume:
        _restored,_manifest=_checkpoint_io.load(_options.resume,_compat,_constants)
        _compat=_checkpoint_io.inherit_provenance(_compat,_manifest)
        isos=_restored['isos']
        base=_restored['base']
        state=_restored['state']
        asset_state=_restored['asset_state']
        asset_dep=_restored['asset_dep']
        labor_shares=_restored['labor_shares']
        investment_shares=_restored['investment_shares']
        current_tfp=_restored['current_tfp']
        current_gap=_restored['current_gap']
        synthetic_ratio=_restored['synthetic_ratio']
        previous_tech_multiplier=_restored['previous_tech_multiplier']
        base_compute_enabling_per_worker=_restored['base_compute_enabling_per_worker']
        base_automation_per_worker=_restored['base_automation_per_worker']
        base_energy_go_per_worker=_restored['base_energy_go_per_worker']
        base_go60=_restored['base_go60']
        base_va60=_restored['base_va60']
        base_inv60=_restored['base_inv60']
        prev_country_va=_restored['prev_country_va']
        prev_country_inv=_restored['prev_country_inv']
        prev_global_va=_restored['prev_global_va']
        baseline_trade=_restored['baseline_trade']
        current_trade=_restored['current_trade']
        topology_meta=_restored['topology_meta']
        demo_pop=_restored['demo_pop']
        demo_wap=_restored['demo_wap']
        pop_tail_anchor=_restored['pop_tail_anchor']
        wap_tail_anchor=_restored['wap_tail_anchor']
        tfp_calibration=_restored['tfp_calibration']
        country_rows=_restored['country_rows']
        sector_rows=_restored['sector_rows']
        asset_rows=_restored['asset_rows']
        max_capital_identity=_restored['max_capital_identity']
        max_employment_recon=_restored['max_employment_recon']
        max_labor_share_move=_restored['max_labor_share_move']
        max_investment_share_move=_restored['max_investment_share_move']
        max_trade_tv_move=_restored['max_trade_tv_move']
        max_trade_component_move=_restored['max_trade_component_move']
        max_synthetic_ratio_move=_restored['max_synthetic_ratio_move']
        max_tech_multiplier_log_move=_restored['max_tech_multiplier_log_move']
        max_synthetic_ratio_level=_restored['max_synthetic_ratio_level']
        min_replacement_coverage=_restored['min_replacement_coverage']
        min_country_growth=_restored['min_country_growth']
        max_country_growth=_restored['max_country_growth']
        annual_gate_failures=_restored['annual_gate_failures']
        checkpoints=_restored['checkpoints']
        _current_year=_manifest['current_year']
        _input_hashes=_manifest['input_hashes']
        del _restored
        progress(f"Restored complete boundary {_current_year}; no input replay",run_started)
    else:
        required=(
            COUNTRIES_2060_SRC,SECTORS_2060_SRC,ASSETS_2060_SRC,
            FREEZE_MANIFEST,OECD_INTER,OECD_FINAL,WPP_TOTAL,WPP_AGE,PWT_MAIN,
            WDI_GFCF_SOURCE
        )
        for p in required:
            if not p.is_file():
                raise FileNotFoundError(p)

        OUTDIR.mkdir(parents=True,exist_ok=True)

        progress("Loading frozen 2060 boundary",run_started)

        crows=load_ndjson(COUNTRIES_2060_SRC)
        srows=load_ndjson(SECTORS_2060_SRC)
        arows=load_ndjson(ASSETS_2060_SRC)

        countries={r["iso3"]:r for r in crows}
        sectors=defaultdict(dict)
        for r in srows:
            sectors[r["iso3"]][r["sector"]]=r
        assets=defaultdict(lambda:defaultdict(dict))
        for r in arows:
            assets[r["iso3"]][r["sector"]][r["asset_class"]]=r

        isos=set(countries)
        if len(isos)!=80:
            raise ValueError(f"expected 80 countries, found {len(isos)}")

        for iso in isos:
            if set(sectors[iso])!=set(SECTORS):
                raise ValueError(f"{iso} incomplete sectors")
            for s in SECTORS:
                if set(assets[iso][s])!=set(ASSETS):
                    raise ValueError(f"{iso}/{s} incomplete assets")

        progress("Loading PWT TFP anchors",run_started)
        tfp_anchor,tfp_fallbacks,tfp_fallback,tfp_calibration=load_pwt_tfp_anchors(isos)

        progress("Loading WPP 2061-2100",run_started)
        wpp_years=tuple(range(2061,WPP_END_YEAR+1))
        wpp_pop=load_wpp_total_years(isos,wpp_years)
        wpp_wap=load_wpp_working_age_years(isos,wpp_years)

        for y in wpp_years:
            if set(wpp_pop[y])!=isos:
                raise ValueError(
                    f"WPP population {y} missing {sorted(isos-set(wpp_pop[y]))[:10]}"
                )
            if set(wpp_wap[y])!=isos:
                raise ValueError(
                    f"WPP WAP {y} missing {sorted(isos-set(wpp_wap[y]))[:10]}"
                )

        # Insert frozen 2060 into demographic series.
        wpp_pop[2060]={
            iso:float(countries[iso]["population"]) for iso in isos
        }
        wpp_wap[2060]={
            iso:(
                float(countries[iso]["demographic_working_age_population"])
                / float(countries[iso]["population"])
            )
            for iso in isos
        }

        progress(f"Extending authored demography 2101-{END_YEAR}",run_started)
        demo_pop,demo_wap,pop_tail_anchor,wap_tail_anchor=extend_demography_tail(
            isos,wpp_pop,wpp_wap
        )

        progress("Loading rewiring OECD trade/IO topology",run_started)
        baseline_trade,topology_meta=load_io_topology(isos)
        current_trade={
            node:dict(weights) for node,weights in baseline_trade.items()
        }

        # 2060 base and dynamic states.
        base={}
        state={}
        asset_state={}
        asset_dep={}
        labor_shares={}
        investment_shares={}
        current_tfp={}
        current_gap={}
        synthetic_ratio={}
        previous_tech_multiplier={}

        base_compute_enabling_per_worker={}
        base_automation_per_worker={}
        base_energy_go_per_worker={}

        base_go60={}
        base_va60={}
        base_inv60={}

        country_rows=[]
        sector_rows=[]
        asset_rows=[]

        for iso in sorted(isos):
            c=countries[iso]

            pop=float(c["population"])
            demo_wap_pop=float(c["demographic_working_age_population"])
            labor_wap=float(c["labor_market_working_age_population"])
            labor_force=float(c["labor_force"])
            employment=float(c["employment"])
            va=float(c["value_added"])
            inv=float(c["investment"])

            frame_ratio=labor_wap/max(EPS,demo_wap_pop)
            participation=labor_force/max(EPS,labor_wap)
            employment_rate=employment/max(EPS,labor_force)
            investment_rate=inv/max(EPS,va)

            base[iso]={
                "alpha":float(c["capital_share_alpha"]),
                "labor_share":float(c["labor_share"]),
                "frame_ratio":frame_ratio,
                "participation_rate":participation,
                "employment_rate":employment_rate,
                "investment_rate":investment_rate,
                "tfp_start_growth":float(c["country_tfp_growth"]),
            }
            current_tfp[iso]=float(c["country_tfp_multiplier"])
            current_gap[iso]=tfp_calibration["gap_2060_log"][iso]
            base_va60[iso]=va
            base_inv60[iso]=inv

            labor_shares[iso]=normalize(
                {
                    s:float(sectors[iso][s]["employment"])
                    for s in SECTORS
                },
                SECTORS
            )
            investment_shares[iso]=normalize(
                {
                    s:float(sectors[iso][s]["investment"])
                    for s in SECTORS
                },
                SECTORS
            )

            # 2060 enabling-capacity baselines. All later technology indexes are
            # relative to these already-realized conditions, so existing 2060 AI /
            # automation is not counted again as a new technology shock.
            compute_enabling=(
                float(assets[iso]["COMPUTE"]["machinery"]["capital"])
                + float(assets[iso]["COMPUTE"]["other_assets"]["capital"])
            )
            base_compute_enabling_per_worker[iso]=(
                compute_enabling/max(EPS,employment)
            )
            base_energy_go_per_worker[iso]=(
                float(sectors[iso]["ENERGY"]["gross_output"])
                /max(EPS,employment)
            )

            for s in SECTORS:
                auto_cap=(
                    float(assets[iso][s]["machinery"]["capital"])
                    + float(assets[iso][s]["transport_equipment"]["capital"])
                )
                base_automation_per_worker[(iso,s)]=(
                    auto_cap/max(EPS,float(sectors[iso][s]["employment"]))
                )
                synthetic_ratio[(iso,s)]=0.0
                previous_tech_multiplier[(iso,s)]=1.0

            country_rows.append({
                **c,
                "demography_source":"FROZEN_2060_BOUNDARY",
                "trade_topology_regime":"OECD_2024_REVEALED_PRIOR_BOUNDARY",
                "blind_runtime_version":"v0.2_CAUSAL_TECH",
            })

            for s in SECTORS:
                r=sectors[iso][s]
                node=(iso,s)
                base_go60[node]=float(r["gross_output"])
                state[node]={
                    "capital":float(r["capital"]),
                    "investment":float(r["investment"]),
                    "employment":float(r["employment"]),
                    "value_added":float(r["value_added"]),
                    "gross_output":float(r["gross_output"]),
                    "A":float(r.get("A",r.get("cobb_douglas_A_2026"))),
                    "A_historical_2026":float(r["cobb_douglas_A_2026"]),
                    "go_va_ratio":(
                        float(r["gross_output"])/float(r["value_added"])
                        if float(r["value_added"])>0 else 1.0
                    ),
                }
                sector_rows.append({
                    **r,
                    "demography_source":"FROZEN_2060_BOUNDARY",
                    "trade_topology_regime":"OECD_2024_REVEALED_PRIOR_BOUNDARY",
                    "blind_runtime_version":"v0.2_CAUSAL_TECH",
                })

                for a in ASSETS:
                    ar=assets[iso][s][a]
                    asset_state[(iso,s,a)]={
                        "capital":float(ar["capital"]),
                        "investment":float(ar["investment"]),
                    }
                    asset_dep[(iso,s,a)]=float(ar["asset_depreciation_rate"])
                    asset_rows.append({
                        **ar,
                        "blind_runtime_version":"v0.2_CAUSAL_TECH",
                    })

        prev_country_va=dict(base_va60)
        prev_country_inv=dict(base_inv60)
        prev_global_va=sum(prev_country_va.values())

        max_capital_identity=0.0
        max_employment_recon=0.0
        max_labor_share_move=0.0
        max_investment_share_move=0.0
        max_trade_tv_move=0.0
        max_trade_component_move=0.0
        max_synthetic_ratio_move=0.0
        max_tech_multiplier_log_move=0.0
        max_synthetic_ratio_level=(0.0,None,None,None)
        min_replacement_coverage=(1.0,None,None)
        min_country_growth=(1e99,None,None)
        max_country_growth=(-1e99,None,None)

        annual_gate_failures=[]
        checkpoints={}

        _current_year=START_YEAR
        _input_hashes={str(p):_checkpoint_io.sha(p) for p in required}

    if not _options.resume:
        verify_policy(base)
        _boundary_repairs=repair_active_boundary(
            Path('/home/ubuntu/loom_earth_2026_2035'), countries, base, state,
            asset_state, sector_rows, asset_rows, labor_shares, investment_shares,
            base_go60, base_compute_enabling_per_worker,
            base_automation_per_worker, base_energy_go_per_worker,
            current_tfp, SECTORS, ASSETS)
        (OUTDIR/'active_boundary_repairs.json').write_text(
            json.dumps(_boundary_repairs, indent=2, sort_keys=True)+'\n')
        for iso in sorted(base):
            base[iso]["investment_rate"]=_national_rates[iso]["investment_rate"]
        boundary_records=[]
        for iso in sorted(base):
            original=base[iso]["alpha"]
            for sector in SECTORS:
                node=(iso,sector)
                item=state[node]
                effective,rebased,capped,factor=_transform_alpha(
                    item["A"],original,item["capital"],item["employment"],ALPHA_CEILING
                )
                item["A"]=rebased
                boundary_records.append({
                    "iso3":iso,"sector":sector,"alpha_original":original,
                    "alpha_effective":effective,"alpha_was_capped":capped,
                    "continuity_rebase_factor":factor,
                })
            base[iso]["alpha"]=effective
            base[iso]["alpha_2060"]=effective
    else:
        boundary_records=None
    _effective_policy_fingerprint=verify_effective_policy(base,_policy,_national_rates)
    if boundary_records is not None:
        (OUTDIR/"alpha_boundary_transform.json").write_text(
            json.dumps(boundary_records,indent=2,sort_keys=True)+"\n",encoding="utf-8"
        )
        (OUTDIR/"investment_rate_provenance.json").write_text(
            json.dumps({"policy_id":NATIONAL_INVESTMENT_POLICY_ID,
                        "source":str(WDI_GFCF_SOURCE),
                        "source_sha256":WDI_GFCF_SOURCE_SHA256,
                        "summary":_national_summary,
                        "countries":_national_rates},indent=2,sort_keys=True)+"\n",
            encoding="utf-8"
        )
    _execution_start_year=_current_year

    def build_checkpoint(y):
        cr=[r for r in country_rows if int(r["year"])==y]
        sr=[r for r in sector_rows if int(r["year"])==y]
        total_va=sum(float(r["value_added"]) for r in cr)
        total_cap=sum(float(r["capital"]) for r in cr)
        total_inv=sum(float(r["investment"]) for r in cr)

        by_sector={}
        for s in SECTORS:
            rows=[r for r in sr if r["sector"]==s]
            sva=sum(float(r["value_added"]) for r in rows)
            sk=sum(float(r["capital"]) for r in rows)
            by_sector[s]={
                "global_va_share":sva/max(EPS,total_va),
                "global_capital_share":sk/max(EPS,total_cap),
            }

        total_bio_emp=sum(float(r["employment"]) for r in cr)
        total_synth=sum(
            float(r.get("synthetic_labor_equivalent",0.0))
            for r in sr
        )
        tech_weight=sum(
            float(r.get("technology_productivity_multiplier",1.0))
            * float(r["value_added"])
            for r in sr
        )/max(EPS,total_va)

        return {
            "year":y,
            "population":sum(float(r["population"]) for r in cr),
            "employment":sum(float(r["employment"]) for r in cr),
            "value_added":total_va,
            "capital":total_cap,
            "investment":total_inv,
            "capital_output_ratio":total_cap/max(EPS,total_va),
            "investment_output_ratio":total_inv/max(EPS,total_va),
            "weighted_legacy_tfp_level":(
                sum(
                    float(r["country_tfp_multiplier"])*float(r["value_added"])
                    for r in cr
                )/max(EPS,total_va)
            ),
            "weighted_technology_productivity_multiplier":tech_weight,
            "synthetic_labor_equivalent":total_synth,
            "synthetic_to_biological_employment_ratio":
                total_synth/max(EPS,total_bio_emp),
            "sector_structure":by_sector,
        }

    if not _options.resume:
        checkpoints["2060"]=build_checkpoint(2060)

    progress(f"Beginning annual propagation {_current_year+1}-{_output_year}",run_started)

    for y in FORECAST_YEARS:
        if y<=_current_year:
            continue
        year_started=time.monotonic()

        # Ratios relative to frozen 2060 demand calibration.
        prev_go_ratio={
            node:calibrated_ratio(state[node]["gross_output"],base_go60[node])
            for node in state
        }
        prev_country_va_ratio={
            iso:calibrated_ratio(prev_country_va[iso],base_va60[iso])
            for iso in isos
        }
        prev_country_inv_ratio={
            iso:calibrated_ratio(prev_country_inv[iso],base_inv60[iso])
            for iso in isos
        }
        global_va_ratio=max(EPS,prev_global_va/sum(base_va60.values()))

        # Endogenous destination rewiring + supplier demand factors.
        demand_factor={}
        year_trade_tv=0.0
        year_trade_component=0.0

        for node in state:
            new_w,comp_move,tv_move,df=rewire_supplier_weights(
                baseline_trade[node],
                current_trade[node],
                prev_go_ratio,
                prev_country_va_ratio,
                prev_country_inv_ratio,
                global_va_ratio,
            )
            current_trade[node]=new_w
            demand_factor[node]=df
            year_trade_tv=max(year_trade_tv,tv_move)
            year_trade_component=max(year_trade_component,comp_move)

            wsum=sum(new_w.values())
            if abs(wsum-1.0)>1e-12:
                raise ValueError(f"trade weight normalization failure {node} {wsum}")

        max_trade_tv_move=max(max_trade_tv_move,year_trade_tv)
        max_trade_component_move=max(
            max_trade_component_move,year_trade_component
        )

        new_state={}
        new_country_va={}
        new_country_inv={}
        year_country_rows=[]
        year_sector_rows=[]
        year_asset_rows=[]

        year_max_labor_move=0.0
        year_max_inv_move=0.0
        year_min_growth=1e99
        year_max_growth=-1e99
        year_max_sector_share=0.0
        year_max_synthetic_move=0.0
        year_max_tech_log_move=0.0

        for iso in sorted(isos):
            pop=demo_pop[y][iso]
            demo_wap_share=demo_wap[y][iso]
            demo_wap_pop=pop*demo_wap_share

            labor_wap=demo_wap_pop*base[iso]["frame_ratio"]
            labor_force=labor_wap*base[iso]["participation_rate"]
            total_emp=labor_force*base[iso]["employment_rate"]

            # v0.6.1: cross-country gap is a separate CTFP-derived state.
            gap_before=current_gap[iso]
            g_tfp=transition_tfp_growth(
                base[iso]["tfp_start_growth"],
                tfp_calibration["frontier_growth_log"],
                tfp_calibration["catchup_speed"],
                y-2060,
                gap_before,
            )
            current_tfp[iso]*=(1+g_tfp)
            current_gap[iso]=max(0.0,gap_before*math.exp(-tfp_calibration["catchup_speed"]))

            # Asset-level capital evolution.
            asset_capital={}
            capital={}
            for s in SECTORS:
                sk=0.0
                for a in ASSETS:
                    pa=asset_state[(iso,s,a)]
                    d=asset_dep[(iso,s,a)]
                    k=(1-d)*pa["capital"]+pa["investment"]
                    identity=(1-d)*pa["capital"]+pa["investment"]
                    rr=abs(k-identity)/max(1.0,abs(identity))
                    max_capital_identity=max(max_capital_identity,rr)
                    asset_capital[(s,a)]=k
                    sk+=k
                capital[s]=sk

            next_alpha=effective_alpha(base[iso]["alpha_2060"],y)

            pressure={}
            for s in SECTORS:
                node=(iso,s)
                desired_go=base_go60[node]*demand_factor[node]
                supply_ref=max(EPS,state[node]["gross_output"])
                pressure[s]=max(EPS,desired_go/supply_ref)

            labor_prod={
                s:state[(iso,s)]["value_added"]
                /max(EPS,state[(iso,s)]["employment"])
                for s in SECTORS
            }
            capital_prod={
                s:state[(iso,s)]["value_added"]
                /max(EPS,state[(iso,s)]["capital"])
                for s in SECTORS
            }

            desired_l=desired_labor_shares(
                labor_shares[iso],pressure,labor_prod
            )
            new_lshare=blend_shares(
                labor_shares[iso],desired_l,LABOR_ADJUST_SPEED,SECTORS
            )

            for s in SECTORS:
                mv=abs(new_lshare[s]-labor_shares[iso][s])
                max_labor_share_move=max(max_labor_share_move,mv)
                year_max_labor_move=max(year_max_labor_move,mv)

            employment={s:total_emp*new_lshare[s] for s in SECTORS}
            emp_resid=abs(sum(employment.values())-total_emp)/max(1.0,total_emp)
            max_employment_recon=max(max_employment_recon,emp_resid)

            # Causal technology state from PRIOR realized energy output and
            # CURRENT physical enabling capital. Synthetic capacity is explicit
            # labor-equivalent input; AI/energy effects are efficiency multipliers.
            country_bio_emp=max(EPS,sum(employment.values()))

            compute_enabling_current=(
                asset_capital[("COMPUTE","machinery")]
                + asset_capital[("COMPUTE","other_assets")]
            )
            compute_index=(
                compute_enabling_current/country_bio_emp
            )/max(EPS,base_compute_enabling_per_worker[iso])

            energy_index=(
                state[(iso,"ENERGY")]["gross_output"]/country_bio_emp
            )/max(EPS,base_energy_go_per_worker[iso])

            va={}
            go={}
            synthetic_equivalent={}
            tech_multiplier={}
            automation_index={}

            for s in SECTORS:
                prev=state[(iso,s)]
                bio_emp=max(EPS,employment[s])
                automation_cap=(
                    asset_capital[(s,"machinery")]
                    + asset_capital[(s,"transport_equipment")]
                )
                automation_index[s]=(
                    automation_cap/bio_emp
                )/max(EPS,base_automation_per_worker[(iso,s)])

                old_syn=synthetic_ratio[(iso,s)]
                new_syn,tech_mult,syn_target=causal_technology_state(
                    compute_index,
                    automation_index[s],
                    energy_index,
                    old_syn,
                    s,
                )
                synthetic_ratio[(iso,s)]=new_syn
                tech_multiplier[s]=tech_mult
                synthetic_equivalent[s]=employment[s]*new_syn

                syn_move=abs(new_syn-old_syn)
                max_synthetic_ratio_move=max(
                    max_synthetic_ratio_move,syn_move
                )
                year_max_synthetic_move=max(
                    year_max_synthetic_move,syn_move
                )
                if new_syn>max_synthetic_ratio_level[0]:
                    max_synthetic_ratio_level=(new_syn,iso,s,y)

                old_tm=previous_tech_multiplier[(iso,s)]
                log_move=abs(math.log(tech_mult/max(EPS,old_tm)))
                max_tech_multiplier_log_move=max(
                    max_tech_multiplier_log_move,log_move
                )
                year_max_tech_log_move=max(
                    year_max_tech_log_move,log_move
                )
                previous_tech_multiplier[(iso,s)]=tech_mult

                effective_labor=employment[s]+synthetic_equivalent[s]
                effective_productivity=current_tfp[iso]*tech_mult

                prev["A"],_alpha_rebase_factor=rebase_A(
                    prev["A"],base[iso]["alpha"],next_alpha,
                    capital[s],effective_labor)

                va[s]=production(
                    prev["A"],
                    capital[s],
                    effective_labor,
                    next_alpha,
                    effective_productivity,
                )
                go[s]=va[s]*prev["go_va_ratio"]

            country_va=sum(va.values())
            country_go=sum(go.values())
            depreciation_need=sum(
                asset_dep[(iso,s,a)]*asset_capital[(s,a)]
                for s in SECTORS for a in ASSETS)
            country_inv=investment_budget(
                y,base[iso]["investment_rate"],country_va,
                prev_country_va[iso],sum(capital.values()),depreciation_need)
            base[iso]["alpha"]=next_alpha

            current_cap_prod={
                s:va[s]/max(EPS,capital[s])
                for s in SECTORS
            }

            (
                investment,
                investment_asset,
                new_ishare,
                repl_need,
                repl_funded,
                expansion_sector,
                expansion_asset,
                replacement_coverage,
            )=allocate_asset_replacement_and_expansion(
                country_inv,
                asset_capital,
                {
                    (s,a):asset_dep[(iso,s,a)]
                    for s in SECTORS for a in ASSETS
                },
                investment_shares[iso],
                pressure,
                current_cap_prod,
            )

            if replacement_coverage<min_replacement_coverage[0]:
                min_replacement_coverage=(
                    replacement_coverage,iso,y
                )

            for s in SECTORS:
                mv=abs(new_ishare[s]-investment_shares[iso][s])
                max_investment_share_move=max(max_investment_share_move,mv)
                year_max_inv_move=max(year_max_inv_move,mv)

            prev_va=prev_country_va[iso]
            growth=(
                country_va/prev_va-1.0
                if prev_va>0 else 0.0
            )
            year_min_growth=min(year_min_growth,growth)
            year_max_growth=max(year_max_growth,growth)

            if growth<min_country_growth[0]:
                min_country_growth=(growth,iso,y)
            if growth>max_country_growth[0]:
                max_country_growth=(growth,iso,y)

            for s in SECTORS:
                node=(iso,s)
                prev=state[node]
                dep_eff=sum(
                    asset_dep[(iso,s,a)]*asset_capital[(s,a)]
                    for a in ASSETS
                )/max(EPS,capital[s])

                r={
                    "iso3":iso,
                    "sector":s,
                    "year":y,
                    "capital":capital[s],
                    "employment":employment[s],
                    "value_added":va[s],
                    "gross_output":go[s],
                    "investment":investment[s],
                    "A":prev["A"],
                    "cobb_douglas_A_2026":prev["A_historical_2026"],
                    "capital_share_alpha":base[iso]["alpha"],
                    "labor_exponent_effective":1.0-base[iso]["alpha"],
                    "labor_share":base[iso]["labor_share"],
                    "depreciation_rate":dep_eff,
                    "depreciation_source":
                        "CURRENT_ASSET_WEIGHTED_EFFECTIVE_RATE",
                    "country_tfp_multiplier":current_tfp[iso],
                    "country_tfp_growth":g_tfp,
                    "legacy_tfp_regime":
                        "PWT_BRIDGE_DECAYING_TO_ZERO_GROWTH",
                    "compute_enabling_index":compute_index,
                    "automation_enabling_index":automation_index[s],
                    "energy_abundance_index":energy_index,
                    "technology_productivity_multiplier":tech_multiplier[s],
                    "synthetic_labor_equivalent_ratio":
                        synthetic_ratio[(iso,s)],
                    "synthetic_labor_equivalent":
                        synthetic_equivalent[s],
                    "effective_labor_input":
                        employment[s]+synthetic_equivalent[s],
                    "labor_share_of_country":new_lshare[s],
                    "investment_share_of_country":new_ishare[s],
                    "replacement_investment_need":
                        sum(repl_need[(s,a)] for a in ASSETS),
                    "replacement_investment_funded":
                        sum(repl_funded[(s,a)] for a in ASSETS),
                    "expansion_investment":expansion_sector[s],
                    "replacement_coverage_ratio":replacement_coverage,
                    "io_demand_factor":demand_factor[node],
                    "io_demand_pressure":pressure[s],
                    "trade_topology_regime":
                        "ENDOGENOUS_REVEALED_ACCESSIBILITY_REWIRING",
                    "structural_regime":
                        "BLIND_EARTH_EVIDENCE_BOUNDED_ASSET_LABOR_TRADE_REALLOCATION",
                    "demography_source":
                        "WPP_MEDIUM" if y<=2100 else "DECAYING_WPP_TAIL",
                }
                sector_rows.append(r)
                year_sector_rows.append(r)

                new_state[node]={
                    "capital":capital[s],
                    "investment":investment[s],
                    "employment":employment[s],
                    "value_added":va[s],
                    "gross_output":go[s],
                    "A":prev["A"],
                    "A_historical_2026":prev["A_historical_2026"],
                    "go_va_ratio":prev["go_va_ratio"],
                }

                for a in ASSETS:
                    ar={
                        "iso3":iso,
                        "sector":s,
                        "asset_class":a,
                        "year":y,
                        "capital":asset_capital[(s,a)],
                        "investment":investment_asset[(s,a)],
                        "replacement_need":repl_need[(s,a)],
                        "replacement_funded":repl_funded[(s,a)],
                        "expansion_investment":expansion_asset[(s,a)],
                        "replacement_coverage_ratio":replacement_coverage,
                        "asset_depreciation_rate":asset_dep[(iso,s,a)],
                        "share_of_sector_capital":
                            asset_capital[(s,a)]/max(EPS,capital[s]),
                        "structural_regime":
                            "BLIND_EARTH_ASSET_PROPAGATION",
                    }
                    asset_rows.append(ar)
                    year_asset_rows.append(ar)

                    asset_state[(iso,s,a)]={
                        "capital":asset_capital[(s,a)],
                        "investment":investment_asset[(s,a)],
                    }

            sector_va_total=sum(va.values())
            for s in SECTORS:
                year_max_sector_share=max(
                    year_max_sector_share,
                    va[s]/max(EPS,sector_va_total)
                )

            cr={
                "iso3":iso,
                "year":y,
                "population":pop,
                "demographic_working_age_population":demo_wap_pop,
                "demographic_working_age_share":demo_wap_share,
                "labor_market_working_age_population":labor_wap,
                "labor_force":labor_force,
                "employment":sum(employment.values()),
                "synthetic_labor_equivalent":sum(
                    synthetic_equivalent.values()
                ),
                "effective_labor_input":(
                    sum(employment.values())
                    + sum(synthetic_equivalent.values())
                ),
                "synthetic_to_biological_employment_ratio":(
                    sum(synthetic_equivalent.values())
                    /max(EPS,sum(employment.values()))
                ),
                "value_added":country_va,
                "gross_output":country_go,
                "capital":sum(capital.values()),
                "investment":country_inv,
                "capital_share_alpha":base[iso]["alpha"],
                "labor_exponent_effective":1.0-base[iso]["alpha"],
                "labor_share":base[iso]["labor_share"],
                "country_tfp_multiplier":current_tfp[iso],
                "country_tfp_growth":g_tfp,
                "legacy_tfp_regime":
                    "PWT_BRIDGE_DECAYING_TO_ZERO_GROWTH",
                "real_value_added_growth":growth,
                "investment_output_ratio":
                    country_inv/max(EPS,country_va),
                "replacement_coverage_ratio":replacement_coverage,
                "demography_source":
                    "WPP_MEDIUM" if y<=2100 else "DECAYING_WPP_TAIL",
                "trade_topology_regime":
                    "ENDOGENOUS_REVEALED_ACCESSIBILITY_REWIRING",
                "structural_regime":
                    "BLIND_EARTH_EVIDENCE_BOUNDED_ASSET_LABOR_TRADE_REALLOCATION",
            }
            country_rows.append(cr)
            year_country_rows.append(cr)

            new_country_va[iso]=country_va
            new_country_inv[iso]=country_inv
            labor_shares[iso]=new_lshare
            investment_shares[iso]=new_ishare

        # Synchronous annual commit.
        state=new_state
        prev_country_va=new_country_va
        prev_country_inv=new_country_inv
        prev_global_va=sum(new_country_va.values())

        # Annual hard gates.
        year_global_va=sum(r["value_added"] for r in year_country_rows)
        prev_year_global_va=(
            checkpoints[str(y-1)]["value_added"]
            if str(y-1) in checkpoints
            else sum(
                float(r["value_added"])
                for r in country_rows
                if int(r["year"])==y-1
            )
        )
        global_growth=year_global_va/max(EPS,prev_year_global_va)-1.0

        year_global_cap=sum(r["capital"] for r in year_country_rows)
        ky=year_global_cap/max(EPS,year_global_va)

        failures=[]
        if 100*year_max_labor_move>MAX_ANNUAL_LABOR_SHARE_MOVE_PP:
            failures.append(
                f"labor share move {100*year_max_labor_move:.3f}pp"
            )
        if 100*year_max_inv_move>MAX_ANNUAL_INVESTMENT_SHARE_MOVE_PP:
            failures.append(
                f"investment share move {100*year_max_inv_move:.3f}pp"
            )
        if year_trade_tv>MAX_ANNUAL_TRADE_TV_MOVE:
            failures.append(
                f"trade TV move {year_trade_tv:.4f}"
            )
        if year_min_growth<MIN_COUNTRY_VA_GROWTH:
            failures.append(
                f"country VA growth min {year_min_growth:.4f}"
            )
        if year_max_growth>MAX_COUNTRY_VA_GROWTH:
            failures.append(
                f"country VA growth max {year_max_growth:.4f}"
            )
        if global_growth<MIN_GLOBAL_VA_GROWTH:
            failures.append(
                f"global VA growth min {global_growth:.4f}"
            )
        if global_growth>MAX_GLOBAL_VA_GROWTH:
            failures.append(
                f"global VA growth max {global_growth:.4f}"
            )
        if year_max_sector_share>MAX_SECTOR_VA_SHARE:
            failures.append(
                f"sector VA share max {year_max_sector_share:.4f}"
            )
        if not MIN_CAPITAL_OUTPUT_RATIO<=ky<=MAX_CAPITAL_OUTPUT_RATIO:
            failures.append(
                f"global K/Y {ky:.4f}"
            )
        if year_max_synthetic_move>MAX_ANNUAL_SYNTHETIC_RATIO_MOVE:
            failures.append(
                f"synthetic ratio move {year_max_synthetic_move:.4f}"
            )
        if year_max_tech_log_move>MAX_ANNUAL_TECH_MULTIPLIER_LOG_MOVE:
            failures.append(
                f"technology multiplier log move {year_max_tech_log_move:.4f}"
            )

        if failures:
            annual_gate_failures.append({
                "year":y,
                "failures":failures,
                "max_labor_share_move_pp":100*year_max_labor_move,
                "max_investment_share_move_pp":100*year_max_inv_move,
                "max_trade_total_variation_move":year_trade_tv,
                "global_value_added_growth":global_growth,
                "global_capital_output_ratio":ky,
                "max_synthetic_ratio_move":year_max_synthetic_move,
                "max_technology_multiplier_log_move":
                    year_max_tech_log_move,
            })
            print(
                f"[HARD GATE FAIL] YEAR {y}: " + "; ".join(failures),
                flush=True
            )
            break

        if y in CHECKPOINT_YEARS:
            checkpoints[str(y)]=build_checkpoint(y)
            cp=checkpoints[str(y)]
            print(
                f"[CHECKPOINT] {y}: "
                f"pop={cp['population']:,.0f} "
                f"VA={cp['value_added']:.3e} "
                f"K/Y={cp['capital_output_ratio']:.3f} "
                f"legacyTFP={cp['weighted_legacy_tfp_level']:.3f} "
                f"tech={cp['weighted_technology_productivity_multiplier']:.3f} "
                f"synth/bio={cp['synthetic_to_biological_employment_ratio']:.3f}",
                flush=True
            )
        elif y%10==0:
            progress(
                f"YEAR {y} complete: "
                f"global_VA={year_global_va:.3e} "
                f"global_growth={global_growth:.4%}",
                year_started
            )

        _current_year=y
        if y==END_YEAR or y==_options.stop_after or y in _options.save_at:
            _checkpoint_io.save(
                _checkpoint_dir/f"earth_{y}.checkpoint.zip",y,locals(),
                _compat,_constants,_input_hashes
            )
        if y==_options.stop_after:
            progress(f"Stopped after qualified boundary {y}",run_started)
            break

    final_year=max(int(r["year"]) for r in country_rows)
    passed=(not annual_gate_failures and final_year==_output_year)

    # Final diagnostics.
    progress("Building long-run diagnostics",run_started)

    max_asset_sector_resid=0.0
    by_asset_k=defaultdict(float)
    for r in asset_rows:
        by_asset_k[(r["iso3"],r["sector"],int(r["year"]))]+=float(r["capital"])
    for r in sector_rows:
        key=(r["iso3"],r["sector"],int(r["year"]))
        rr=abs(by_asset_k[key]-float(r["capital"]))/max(1.0,abs(float(r["capital"])))
        max_asset_sector_resid=max(max_asset_sector_resid,rr)

    # Write all generated rows even on failure so debugging is possible.
    with COUNTRIES_ALL.open("w",encoding="utf-8") as f:
        for r in sorted(country_rows,key=lambda x:(x["iso3"],int(x["year"]))):
            f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

    with SECTORS_ALL.open("w",encoding="utf-8") as f:
        for r in sorted(
            sector_rows,
            key=lambda x:(x["iso3"],x["sector"],int(x["year"]))
        ):
            f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

    with ASSETS_ALL.open("w",encoding="utf-8") as f:
        for r in sorted(
            asset_rows,
            key=lambda x:(x["iso3"],x["sector"],x["asset_class"],int(x["year"]))
        ):
            f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

    if passed:
        with COUNTRIES_END.open("w",encoding="utf-8") as f:
            for r in sorted(
                (x for x in country_rows if int(x["year"])==_output_year),
                key=lambda x:x["iso3"]
            ):
                f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

        with SECTORS_END.open("w",encoding="utf-8") as f:
            for r in sorted(
                (x for x in sector_rows if int(x["year"])==_output_year),
                key=lambda x:(x["iso3"],x["sector"])
            ):
                f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

        with ASSETS_END.open("w",encoding="utf-8") as f:
            for r in sorted(
                (x for x in asset_rows if int(x["year"])==_output_year),
                key=lambda x:(x["iso3"],x["sector"],x["asset_class"])
            ):
                f.write(json.dumps(r,separators=(",",":"),sort_keys=True)+"\n")

    CHECKPOINTS.write_text(
        json.dumps(checkpoints,indent=2,sort_keys=True)+"\n",
        encoding="utf-8"
    )

    report={
        "schema":f"LOOM_SOLAR_CIVPROP_EARTH2060_{_output_year}_CAUSAL_TECH_BLIND_v2",
        "economic_policy":{"id":POLICY_ID,"ordered_vector_sha256":POLICY_FINGERPRINT,
                           "basis":_policy["interpretation"]},
        "alpha_experiment":{"id":"UNIVERSAL_ALPHA_CEILING_ROUND1_"+ALPHA_CEILING_ID,
                            "alpha_ceiling":ALPHA_CEILING,
                            "effective_policy_vector_sha256":_effective_policy_fingerprint,
                            "transform_source_sha256":ALPHA_TRANSFORM_SHA256},
        "investment_rate_source":{"id":NATIONAL_INVESTMENT_POLICY_ID,
                                  "wdi_source_sha256":WDI_GFCF_SOURCE_SHA256,
                                  "helper_sha256":INVESTMENT_SOURCE_HELPER_SHA256,
                                  "summary":_national_summary},
        "horizon_adapter":{
            "model_version":_checkpoint_io.MODEL,
            "demographic_scenario":_checkpoint_io.SCENARIO,
            "starting_boundary":_execution_start_year,
            "requested_end_year":_output_year,
            "model_horizon":END_YEAR,
            "full_horizon_reached":passed and final_year==END_YEAR,
        },
        "status":
            f"QUALIFIED_CAUSAL_TECH_BLIND_EARTH_2060_{_output_year}_PROVISIONAL"
            if passed else "HARD_GATE_STOP",
        "qualification":{
            "passed":passed,
            "final_year_reached":final_year,
            "annual_gate_failures":annual_gate_failures,
            "max_capital_identity_relative_residual":
                max_capital_identity,
            "max_employment_reconciliation_relative_residual":
                max_employment_recon,
            "max_asset_to_sector_capital_relative_residual":
                max_asset_sector_resid,
            "max_annual_labor_share_move_pp":
                100*max_labor_share_move,
            "max_annual_investment_share_move_pp":
                100*max_investment_share_move,
            "max_annual_trade_total_variation_move":
                max_trade_tv_move,
            "max_annual_trade_component_weight_move":
                max_trade_component_move,
            "max_annual_synthetic_ratio_move":
                max_synthetic_ratio_move,
            "max_annual_technology_multiplier_log_move":
                max_tech_multiplier_log_move,
            "maximum_synthetic_labor_equivalent_ratio":
                {
                    "ratio":max_synthetic_ratio_level[0],
                    "iso3":max_synthetic_ratio_level[1],
                    "sector":max_synthetic_ratio_level[2],
                    "year":max_synthetic_ratio_level[3],
                },
            "minimum_replacement_coverage":
                {
                    "ratio":min_replacement_coverage[0],
                    "iso3":min_replacement_coverage[1],
                    "year":min_replacement_coverage[2],
                },
            "minimum_country_year_va_growth":
                {
                    "growth":min_country_growth[0],
                    "iso3":min_country_growth[1],
                    "year":min_country_growth[2],
                },
            "maximum_country_year_va_growth":
                {
                    "growth":max_country_growth[0],
                    "iso3":max_country_growth[1],
                    "year":max_country_growth[2],
                },
        },
        "demography":{
            "wpp_used_through_year":2100,
            "post_2100_method":
                "COUNTRY_2091_2100_MEDIAN_RATE_DECAY_TO_ZERO",
            "population_growth_tail_half_life_years":
                POP_GROWTH_TAIL_HALF_LIFE,
            "working_age_share_tail_half_life_years":
                WAP_SHARE_TAIL_HALF_LIFE,
            "population_tail_anchor_log_growth":pop_tail_anchor,
            "working_age_share_tail_anchor_delta":wap_tail_anchor,
        },
        "trade":{
            "prior":"OECD_2024_REVEALED_ACCESSIBILITY",
            "endogenous_rewiring":True,
            "rewire_speed":TRADE_REWIRE_SPEED,
            "destination_elasticity":TRADE_DESTINATION_ELASTICITY,
            "physical_distance_model_used":False,
            "tariff_institution_model_used":False,
            "topology_metadata":topology_meta,
        },
        "causal_technology":{
            "mode":"EVIDENCE_BOUNDED_NEUTRAL_PENDING_TASK_MODEL",
            "technology_indexes_relative_to_frozen_2060":True,
            "productivity_multiplier_applied":False,
            "synthetic_labor_applied":False,
            "robot_labor_productivity_validation_pp":ROBOT_LABOR_PRODUCTIVITY_VALIDATION_PP,
            "genai_task_productivity_validation_avg":GENAI_TASK_PRODUCTIVITY_VALIDATION_AVG,
            "genai_task_productivity_validation_novice":GENAI_TASK_PRODUCTIVITY_VALIDATION_NOVICE,
            "technology_adoption_convergence_validation_rate":TECH_ADOPTION_CONVERGENCE_VALIDATION_RATE,
            "energy_elasticity_validation_range":ENERGY_ELASTICITY_VALIDATION_RANGE,
            "2226_technology_endpoint_used":False,
            "tfp_empirical_frontier_calibration":tfp_calibration,
            "note":"v0.6.1: ctfp supplies comparable gaps; rtfpna supplies within-country growth only; internal TFP multipliers are never cross-country compared.",
        },
        "provisional_assumptions":{
            "labor_market_frame_ratio_frozen_at_2060":True,
            "participation_rate_frozen_at_2060":True,
            "employment_rate_frozen_at_2060":True,
            "country_investment_va_rate_frozen_at_2060":True,
            "migration_modeled":False,
            "resource_constraints_modeled":False,
            "discrete_technology_thresholds_modeled":False,
            "continuous_ai_robotics_synthetics_layer_modeled":True,
            "off_earth_economy_modeled":False,
        },
        "governance":{
            "2226_endpoint_used":False,
            "future_country_canon_used":False,
            "future_institution_canon_used":False,
            "future_corporation_canon_used":False,
            "blind_run":True,
            "annual_state_computed":True,
            "sparse_human_checkpoints":list(CHECKPOINT_YEARS),
        },
        "checkpoints":checkpoints,
        "output_files":{
            "countries_all":{
                "path":str(COUNTRIES_ALL),
                "sha256":sha256_file(COUNTRIES_ALL),
            },
            "sectors_all":{
                "path":str(SECTORS_ALL),
                "sha256":sha256_file(SECTORS_ALL),
            },
            "assets_all":{
                "path":str(ASSETS_ALL),
                "sha256":sha256_file(ASSETS_ALL),
            },
            "checkpoints":{
                "path":str(CHECKPOINTS),
                "sha256":sha256_file(CHECKPOINTS),
            },
        },
    }

    if passed:
        report["output_files"][f"countries_{_output_year}"]={
            "path":str(COUNTRIES_END),
            "sha256":sha256_file(COUNTRIES_END),
        }
        report["output_files"][f"sectors_{_output_year}"]={
            "path":str(SECTORS_END),
            "sha256":sha256_file(SECTORS_END),
        }
        report["output_files"][f"assets_{_output_year}"]={
            "path":str(ASSETS_END),
            "sha256":sha256_file(ASSETS_END),
        }

    REPORT.write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",
        encoding="utf-8"
    )

    print("\n=== BLIND RUN SUMMARY ===",flush=True)
    print(f"FINAL YEAR REACHED: {final_year}",flush=True)
    print(
        f"MAX LABOR SHARE MOVE: {100*max_labor_share_move:.4f} pp",
        flush=True
    )
    print(
        f"MAX INVESTMENT SHARE MOVE: "
        f"{100*max_investment_share_move:.4f} pp",
        flush=True
    )
    print(
        f"MAX TRADE TOTAL-VARIATION MOVE: "
        f"{max_trade_tv_move:.6f}",
        flush=True
    )
    print(
        f"MAX SYNTHETIC RATIO MOVE: "
        f"{max_synthetic_ratio_move:.6f}",
        flush=True
    )
    print(
        f"MAX TECHNOLOGY MULTIPLIER LOG MOVE: "
        f"{max_tech_multiplier_log_move:.6f}",
        flush=True
    )
    print(
        "MAX SYNTHETIC LABOR-EQUIVALENT RATIO:",
        {
            "ratio":max_synthetic_ratio_level[0],
            "iso3":max_synthetic_ratio_level[1],
            "sector":max_synthetic_ratio_level[2],
            "year":max_synthetic_ratio_level[3],
        },
        flush=True
    )
    print(
        f"MAX ASSET->SECTOR CAPITAL RESIDUAL: "
        f"{max_asset_sector_resid:.3e}",
        flush=True
    )
    print(
        "MIN REPLACEMENT COVERAGE:",
        {
            "ratio":min_replacement_coverage[0],
            "iso3":min_replacement_coverage[1],
            "year":min_replacement_coverage[2],
        },
        flush=True
    )
    print(
        "MIN COUNTRY-YEAR VA GROWTH:",
        {
            "growth":min_country_growth[0],
            "iso3":min_country_growth[1],
            "year":min_country_growth[2],
        },
        flush=True
    )
    print(
        "MAX COUNTRY-YEAR VA GROWTH:",
        {
            "growth":max_country_growth[0],
            "iso3":max_country_growth[1],
            "year":max_country_growth[2],
        },
        flush=True
    )

    print("\n=== CHECKPOINTS ===",flush=True)
    for y in CHECKPOINT_YEARS:
        if str(y) in checkpoints:
            cp=checkpoints[str(y)]
            print({
                "year":y,
                "population":cp["population"],
                "employment":cp["employment"],
                "value_added":cp["value_added"],
                "capital":cp["capital"],
                "capital_output_ratio":cp["capital_output_ratio"],
                "investment_output_ratio":cp["investment_output_ratio"],
                "weighted_legacy_tfp_level":
                    cp["weighted_legacy_tfp_level"],
                "weighted_technology_productivity_multiplier":
                    cp["weighted_technology_productivity_multiplier"],
                "synthetic_to_biological_employment_ratio":
                    cp["synthetic_to_biological_employment_ratio"],
            },flush=True)

    print(f"\nQUALIFICATION GATE: {'PASS' if passed else 'FAIL'}",flush=True)
    print(f"STATUS: {report['status']}",flush=True)
    print(f"OUTPUT DIR: {OUTDIR}",flush=True)
    print(f"REPORT: {REPORT}",flush=True)
    progress("RUN COMPLETE",run_started)


def _configure_checkpoint_run():
    parser=argparse.ArgumentParser(description='h1 authored horizon to 2226; --stop-after limits execution for qualification')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--resume',type=Path)
    parser.add_argument('--stop-after',type=int)
    parser.add_argument('--save-at',type=int,action='append',default=[])
    parser.add_argument('--alpha-ceiling',type=float,choices=(0.60,),required=True)
    options=parser.parse_args()
    global ALPHA_CEILING,ALPHA_CEILING_ID
    ALPHA_CEILING=options.alpha_ceiling
    ALPHA_CEILING_ID='NONE' if ALPHA_CEILING is None else f'{ALPHA_CEILING:.2f}'
    for year in options.save_at+([options.stop_after] if options.stop_after is not None else []):
        if not START_YEAR<year<END_YEAR:parser.error(f'Intermediate boundary must be between {START_YEAR+1} and {END_YEAR-1}')
    output_year=options.stop_after or END_YEAR
    options.output_dir.mkdir(parents=True,exist_ok=False)
    global OUTDIR,COUNTRIES_ALL,SECTORS_ALL,ASSETS_ALL,COUNTRIES_END,SECTORS_END,ASSETS_END,CHECKPOINTS,REPORT
    OUTDIR=options.output_dir/'results'
    OUTDIR.mkdir()
    COUNTRIES_ALL=OUTDIR/f'countries_2060_{output_year}.ndjson'
    SECTORS_ALL=OUTDIR/f'country_sectors_2060_{output_year}.ndjson'
    ASSETS_ALL=OUTDIR/f'country_sector_assets_2060_{output_year}.ndjson'
    COUNTRIES_END=OUTDIR/f'countries_{output_year}.ndjson'
    SECTORS_END=OUTDIR/f'country_sectors_{output_year}.ndjson'
    ASSETS_END=OUTDIR/f'country_sector_assets_{output_year}.ndjson'
    CHECKPOINTS=OUTDIR/'checkpoints.json'
    REPORT=options.output_dir/'trajectory_report.json'
    checkpoint_dir=options.output_dir/'complete_checkpoints'
    checkpoint_dir.mkdir()
    return options,checkpoint_dir,output_year


if __name__=="__main__":
    _options,_checkpoint_dir,_output_year=_configure_checkpoint_run()
    main()
