"""Classify the 233-node 2026 institutional roster by execution ontology."""
from dataclasses import dataclass
from collections import Counter,defaultdict

AUTONOMOUS="AUTONOMOUS_ACTOR"; COMPOSITE="COMPOSITE_ACTOR"; MARKET="MARKET_MECHANISM"
REGIME="REGIME_RULE"; INFRA="INFRASTRUCTURE_OBJECT"; ANALOG="ANALOG_CONTEXT"
PROPOSAL="PROPOSAL"; HISTORICAL="HISTORICAL"

# Explicit ontology corrections where category alone cannot tell us whether a node decides.
OVERRIDE={}
for x in ("PRO_PLANETARY_RESOURCES","PRO_DEEP_SPACE_INDUSTRIES"): OVERRIDE[x]=HISTORICAL
for x in ("CERT_LORS101","REG_EU_SPACE_ACT","SUP_ROCKETDYNE"): OVERRIDE[x]=PROPOSAL
for x in ("CAP_PUBLIC_EQUITY","CAP_STAR_MARKET","INF_LME","INF_CME"): OVERRIDE[x]=MARKET
for x in ("REG_ARTEMIS","REG_EXPORT_CONTROL","SET_ANTARCTIC","SET_ISS","SET_MLC_ITF","SET_KAFALA",
          "CERT_UNFC","CERT_SEC_SK1300","CERT_OECD_DD"): OVERRIDE[x]=REGIME
for x in ("INFRA_LUNANET","INFRA_CAPE","INFRA_KOUROU","INFRA_AUS_GROUND"): OVERRIDE[x]=INFRA
for x in ("CAP_SPACE_VC","CAP_BANKS","CAP_CHN_GUIDANCE","OFF_FUSION","OFF_SEMI_FABS","OFF_MRI",
          "OFF_QUANTUM_OEMS","OFF_NEUTRON_DETECTION","INF_STATE_INTEL","REG_CLASS_SOCIETIES","REG_PSC"):
    OVERRIDE[x]=COMPOSITE
for x in ("REG_ISA_ANALOG","REG_IMO","SET_SVALBARD","SET_MCMURDO","SET_STARBASE","SET_PILBARA",
          "SET_NORTH_SEA","PRO_TERRESTRIAL_HELIUM","INS_IG_PI"): OVERRIDE[x]=ANALOG
# Service/institution nodes that are autonomous operators even though they expose infrastructure.
for x in ("INFRA_NASA_DSN","INFRA_ESTRACK","INFRA_KSAT","INFRA_SSC","INFRA_INTUITIVE_NSN",
          "INFRA_STARLINK","INFRA_SES","INFRA_EUTELSAT","INFRA_AXIOM","INFRA_VAST","INFRA_STARLAB",
          "INFRA_ORBITAL_REEF","INFRA_MOONLIGHT"): OVERRIDE[x]=AUTONOMOUS

ROLE_BY_CATEGORY={
"CAPITAL":("CAPITAL",),"OFFTAKER":("DEMAND",),"INSURER":("RISK",),
"CARRIER":("TRANSPORT",),"REGISTRY":("REGULATION",),"STATE":("STATE","REGULATION"),
"SETTLEMENT_LABOR":("LABOR",),"INFORMATION":("INFORMATION",),"PROSPECTOR":("PROJECT_DEVELOPMENT",),
"INCUMBENT_INDUSTRY":("MANUFACTURING","DEMAND"),"SUPPLIER_PRIME":("MANUFACTURING",),
"INFRASTRUCTURE":("INFRASTRUCTURE",),"SOFT_POWER":("INFORMATION",),
"CERTIFICATION":("CERTIFICATION",)}

@dataclass(frozen=True)
class RosterNodeAuditV03:
 actor_id:str; name:str; category:str; ontology:str; autonomous_eligible:bool
 causal_roles:tuple[str,...]; reason:str

def classify(seed):
 out=[]
 for a in sorted(seed["actors"],key=lambda z:z["id"]):
  aid=a["id"]; ont=OVERRIDE.get(aid)
  if ont is None:
   if a.get("analog"): ont=ANALOG
   elif str(a.get("status_2026","")).upper().startswith("PROPOSAL"): ont=PROPOSAL
   else: ont=AUTONOMOUS
  eligible=ont==AUTONOMOUS
  reason="EXPLICIT_ONTOLOGY_AUDIT" if aid in OVERRIDE else "DEFAULT_NAMED_2026_INSTITUTION"
  out.append(RosterNodeAuditV03(aid,a["name"],a["category"],ont,eligible,ROLE_BY_CATEGORY[a["category"]],reason))
 return tuple(out)

def coverage(rows):
 d=defaultdict(list)
 for x in rows:
  if x.autonomous_eligible:
   for r in x.causal_roles:d[r].append(x.actor_id)
 return {k:tuple(v) for k,v in sorted(d.items())}

__all__=["classify","coverage","RosterNodeAuditV03","AUTONOMOUS","COMPOSITE","MARKET","REGIME","INFRA","ANALOG","PROPOSAL","HISTORICAL"]
