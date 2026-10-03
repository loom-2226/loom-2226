"""Typed 2026 actor-jurisdiction links for adaptive actor matching.

Links are initialization metadata, never ownership/capability/budget authority.
"""
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re

@dataclass(frozen=True)
class JurisdictionLinkV03:
 actor_id:str; iso3:str; relation:str; evidence_status:str; confidence:str; source_ref:str

# Conservative text aliases. Match only explicit seed prose/name evidence.
ALIASES={
"USA":("United States","U.S.","US Department","US Space","US Federal","US SEC","US Geological","US Export","US launch","US Antarctic","US trade","American"),
"GBR":("United Kingdom","UK ","British","London","Lloyd's"),
"ARE":("United Arab Emirates","UAE","Abu Dhabi","Dubai"),"CHN":("China","Chinese","Shanghai"),
"JPN":("Japan","Japanese"),"IND":("India","Indian"),"AUS":("Australia","Australian","Australasia","Australasian"),
"CAN":("Canada","Canadian"),"RUS":("Russia","Russian"),"FRA":("France","French"),"DEU":("Germany","German"),
"NOR":("Norway","Norwegian","Svalbard"),"SWE":("Sweden","Swedish"),"FIN":("Finland","Finnish"),
"ESP":("Spain","Spanish"),"KOR":("South Korea","Republic of Korea","Korean"),"TWN":("Taiwan","Taiwanese"),
"ZAF":("South Africa","South African"),"BRA":("Brazil","Brazilian"),"SAU":("Saudi Arabia","Saudi"),
"SGP":("Singapore",),"CHE":("Switzerland","Swiss"),"LUX":("Luxembourg",),"TUR":("Türkiye","Turkey","Turkish"),
"QAT":("Qatar","Qatari"),"BEL":("Belgium","Belgian"),"NLD":("Netherlands","Dutch"),"CHL":("Chile","Chilean"),
}
# High-confidence institutional homes not stated literally enough in seed prose.
CURATED_HOME={
"CAP_ADIA":"ARE","CAP_MUBADALA":"ARE","CAP_GIC":"SGP","CAP_NBIM":"NOR","CAP_CPP":"CAN","CAP_BPI":"FRA",
"CAP_EXIM_US":"USA","CAP_JPM":"USA","CAP_DOD_OSC":"USA","CAP_IQT":"USA","CAP_AEI":"USA","CAP_ADVENT":"USA",
"CAP_QIA":"QAT","CAP_PIF":"SAU","CAR_SPACEX":"USA","CAR_BLUE_ORIGIN":"USA","CAR_ROCKET_LAB":"USA",
"CAR_ULA":"USA","CAR_INTUITIVE":"USA","CAR_FIREFLY":"USA","CAR_ASTROBOTIC":"USA","CAR_ORBIT_FAB":"USA",
"CAR_IMPULSE":"USA","CAR_ARIANE":"FRA","CAR_ISAR":"DEU","OFF_CATL":"CHN","OFF_AIRBUS":"FRA",
"OFF_UMICORE":"BEL","OFF_JM":"GBR","INS_AXA_XL":"FRA","INS_ALLIANZ":"DEU","INS_MUNICH_RE":"DEU",
"INS_MARSH":"USA","INS_AON":"GBR","INF_PLANET":"USA","INF_BLACKSKY":"USA","INF_LEOLABS":"USA",
"INF_SLINGSHOT":"USA","INF_KPLER":"BEL","INF_SPGLOBAL":"USA","INF_ARGUS":"GBR","INF_KOBOLD":"USA",
"INF_CME":"USA","INF_FASTMARKETS":"GBR","INF_VANTOR":"USA","INF_SPIRE":"USA","INF_WOODMAC":"GBR",
"PRO_INTERLUNE":"USA","PRO_ASTROFORGE":"USA","PRO_KARMAN":"USA","PRO_TRANSASTRA":"USA","PRO_HONEYBEE":"USA",
"INC_RIO":"GBR","INC_BHP":"AUS","INC_GLENCORE":"CHE","INC_FREEPORT":"USA","INC_LINDE":"GBR",
"INC_AIR_LIQUIDE":"FRA","INC_AIR_PRODUCTS":"USA","INC_QATARENERGY":"QAT","INC_CATERPILLAR":"USA",
"INC_VERMEER":"USA","INC_BECHTEL":"USA","INC_SLB":"USA","INC_TRAFIGURA":"SGP",
"SUP_LOCKHEED":"USA","SUP_BOEING":"USA","SUP_NORTHROP":"USA","SUP_L3HARRIS":"USA","SUP_REDWIRE":"USA",
"SUP_VOYAGER":"USA","SUP_SIERRA":"USA","SUP_YORK":"USA","SUP_BWXT":"USA","SUP_WESTINGHOUSE":"USA",
"SUP_CESIUMASTRO":"USA","SUP_LANTERIS":"USA","SUP_XENERGY":"USA","SUP_AIRBUS_DS":"FRA","SUP_THALES_ALENIA":"FRA","SUP_ARIANEGROUP":"FRA",
"SUP_SAFRAN_DSI":"FRA","INFRA_KSAT":"NOR","INFRA_INTUITIVE_NSN":"USA","INFRA_NASA_DSN":"USA","INFRA_ORBITAL_REEF":"USA","INFRA_STARLAB":"USA","INFRA_STARLINK":"USA","INFRA_VAST":"USA","INFRA_SES":"LUX","INFRA_EUTELSAT":"FRA",
"INFRA_AXIOM":"USA","INFRA_CAPE":"USA","SOFT_MINES":"USA","SOFT_CSIS":"USA","SOFT_AEROSPACE_CORP":"USA",
"SOFT_LPI":"USA","SOFT_SPACENEWS":"USA","SOFT_PAYLOAD":"USA","SOFT_CSF":"USA","SOFT_PLANETARY_SOCIETY":"USA",
"CERT_JORC":"AUS","CERT_SEC_SK1300":"USA","CERT_SME":"USA","CERT_AUSIMM":"AUS","CERT_SRK":"GBR",
"CERT_SGS":"CHE","CERT_BUREAU_VERITAS":"FRA","CERT_INTERTEK":"GBR","CERT_ALS":"AUS","CERT_AFRY_AMC":"SWE","INC_CHART":"USA","INC_EXXON_SHUTE_CREEK":"USA","OFF_DOE_ISOTOPE":"USA","OFF_MAYBELL":"USA","PRO_LUNAR_OUTPOST":"USA","SOFT_SWF":"USA",
}
GLOBAL_IDS={"CAP_QIA","INC_QATARENERGY","CERT_PERC","INFRA_ESTRACK","INFRA_MOONLIGHT","SET_INDUSTRIALL","SOFT_IISL","STA_EU_ESA"}
MULTINATIONAL_PREFIXES=("REG_","SOFT_ISO","SOFT_CCSDS","SOFT_ISECG","CERT_UNFC","CERT_ICMM","CERT_IRMA","CERT_EITI","CERT_OECD","CERT_RMI")

def build(seed,economic_iso3):
 valid=set(economic_iso3); out=[]
 for a in seed["actors"]:
  aid=a["id"]; text=" ".join(str(a.get(k,"")) for k in ("name","basis_2026","verify"))
  hits=set()
  for iso,terms in ALIASES.items():
   if iso in valid and any(term.lower() in text.lower() for term in terms): hits.add(iso)
  if aid in CURATED_HOME and CURATED_HOME[aid] in valid:
   out.append(JurisdictionLinkV03(aid,CURATED_HOME[aid],"HOME","BEST_ESTIMATE_CURATED","MEDIUM",f"model:CURATED_HOME:{aid}"))
   hits.discard(CURATED_HOME[aid])
  for iso in sorted(hits):
   out.append(JurisdictionLinkV03(aid,iso,"OPERATING_OR_INSTITUTIONAL_LINK","SEED_TEXT_EXPLICIT","HIGH",f"candidate_seed:{aid}"))
  if not any(x.actor_id==aid for x in out) and (aid in GLOBAL_IDS or aid.startswith(MULTINATIONAL_PREFIXES)):
   out.append(JurisdictionLinkV03(aid,"GLOBAL","MULTINATIONAL","ONTOLOGY_DERIVED","MEDIUM",f"candidate_seed:{aid}"))
 return tuple(sorted(out,key=lambda x:(x.actor_id,x.iso3,x.relation)))

def digest(rows):return sha256(json.dumps([asdict(x) for x in rows],sort_keys=True,separators=(",",":")).encode()).hexdigest()
