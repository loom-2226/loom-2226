"""LOOM technology timeline -> CIVPROP opportunity-frontier bridge V0.3.

Threshold years are consideration anchors only. They never grant actor capability,
installed capacity, transport access, or successful achievement.
"""
from __future__ import annotations
import re
from pathlib import Path

BRIDGE_VERSION = "0.3.0"
ROW = re.compile(r"^\| \x60(?P<id>[^\x60]+)\x60 / (?P<family>[A-Z]+) \| \*\*(?P<year>\d{4})\*\* \| (?P<cap>.*?) \| (?P<gate>.*?) \| (?P<basis>.*?) \|$")
SPEC = re.compile(r"^\| \x60(?P<id>SPEC-MOD-[^\x60]+)\x60 \| \*\*(?P<year>\d{4})\*\* \| (?P<cap>.*?) \| (?P<gate>.*?) \|$")

def build_timeline_technology_bridge(register_path: Path, snapshot_id: str):
    rows=[]; section=None
    for raw in register_path.read_text().splitlines():
        if raw.startswith("## 4. SELECTED MODERATE SCENARIO"): section="MODERATE"
        elif raw.startswith("## 5. FICTIONAL CANON COMPARATOR"): section="CANON"
        elif raw.startswith("### 5.1 SELECTED MODERATE"): section="SPECULATIVE"
        elif raw.startswith("## 6. "): section=None
        m=ROW.match(raw) if section=="MODERATE" else SPEC.match(raw) if section=="SPECULATIVE" else None
        if not m: continue
        d=m.groupdict(); mid=d["id"]
        rows.append({
          "tech_id":mid.replace("-","_"), "source_milestone_id":mid,
          "family":d.get("family") or "SPEC", "frontier_year":int(d["year"]),
          "frontier_semantics":"CONSIDERATION_ANCHOR_NOT_ACHIEVEMENT",
          "authority_class":"AUTHOR_SCENARIO_MODERATE" if section=="MODERATE" else "SPECULATIVE_FICTION",
          "capability_change":d["cap"], "threshold_gate":d["gate"],
          "basis_uncertainty":d.get("basis"),
          "actor_capability_effect":"NONE_WITHOUT_SEPARATE_ACTOR_STATE_EVENT",
          "installed_capacity_effect":"NONE_WITHOUT_SEPARATE_COMMISSIONED_ASSET",
          "provenance_refs":[snapshot_id,"LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md"],
        })
    return {"format":"CIVPROP_TIMELINE_TECHNOLOGY_BRIDGE_V0_3","bridge_version":BRIDGE_VERSION,
      "timeline_snapshot_id":snapshot_id,
      "semantics":{"date_does_not_unlock":True,"four_tech_states_preserved":True,
        "canon_comparator_excluded":True,"site_specific":True,"unknown_not_zero":True,
        "frontier_year_means_consideration_not_achievement":True},
      "technology_frontier":rows}
