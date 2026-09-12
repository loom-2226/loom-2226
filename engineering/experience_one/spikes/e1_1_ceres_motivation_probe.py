#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 MOTIVATION diagnostic: inventory existing grounded hooks before authoring lore.

This probe is deliberately read-only and documentary. It does not invent an incident,
mission, contract, NPC, or objective. It reports only hook classes already evidenced by
supplied artifacts/source excerpts and labels missing connective tissue explicitly.
"""
import argparse, json
from pathlib import Path

DEFAULT_OUT=Path('/storage/emulated/0/Download/E1_1_CERES_MOTIVATION_PROBE.json')

def build_probe():
    hooks=[
      {"hook_id":"CERES_RESTRICTED_ANCHORAGE","status":"SUPPORTED_WORLD_HOOK","evidence":"Canon Context projects CER-P05 Ceres Metric & Loom Anchorage as STRATEGIC_PORT / RESTRICTED.","can_motivate_now":False,"missing":"No existing evidence yet ties Wayfarer, crew, cargo, contract, obligation, incident, or objective to CER-P05."},
      {"hook_id":"CERES_SHIPYARD_ARC","status":"SUPPORTED_WORLD_HOOK","evidence":"Canon Context projects CER-P04 Ceres Shipyard Arc as ORBITAL_SHIPYARD.","can_motivate_now":False,"missing":"No existing evidence yet establishes a Wayfarer repair, inspection, fabrication, certification, or resupply need at this facility."},
      {"hook_id":"CERES_BELT_EXCHANGE","status":"SUPPORTED_WORLD_HOOK","evidence":"Canon Context projects CER-P03 Ceres Belt Exchange as ORBITAL_HABITAT_PORT / Belt network exchange.","can_motivate_now":False,"missing":"No existing evidence yet establishes a current Wayfarer commercial, social, information, or contractual dependency there."},
      {"hook_id":"CERES_DOCKING_PRECEDENT","status":"SUPPORTED_SHIP_OPERATIONS_PRECEDENT","evidence":"Ship Operations compendium records routine Ceres docking under a valid automated contract.","can_motivate_now":False,"missing":"Historical/operational precedent is not evidence of a current Experience One docking contract or obligation."},
      {"hook_id":"COURIER_CONTRACT_MECHANIC","status":"SUPPORTED_MECHANIC","evidence":"Ship Operations compendium defines structured courier contracts from job type, information age, route/operational risk, legal/insurance status, payoff, and complication.","can_motivate_now":False,"missing":"A mechanic capable of generating motivation is not an existing current contract. Generating one would be new state/content and requires the proper governed layer."},
      {"hook_id":"WAYFARER_CERES_NAV_STATE","status":"SUPPORTED_QUALIFICATION_START_STATE","evidence":"Navigator baseline initializes Wayfarer at CERES with READY_HOLD and full remass in its qualification state.","can_motivate_now":False,"missing":"Qualification start state establishes place/readiness, not an in-world reason to choose a particular local action."},
    ]
    return {"schema":"LOOM_E1_1_CERES_MOTIVATION_PROBE_V1","diagnosis":"MOTIVATION_CONNECTIVE_TISSUE_ABSENT","hooks":hooks,"supported_hook_count":len(hooks),"actionable_current_hook_count":sum(1 for h in hooks if h['can_motivate_now']),"new_lore_authored":False,"campaign_mutation":False,"canon_mutation":False,"model_called":False,"conclusion":"Existing canon and mechanics provide multiple credible hook surfaces, but current evidence does not establish a Wayfarer-specific reason to care about any of them right now. Do not manufacture urgency in presentation. The next discriminator belongs at the governed mechanics/state boundary: determine whether existing campaign/ship/contract/relationship state contains a current dependency; if not, classify the absence before authoring new content."}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=DEFAULT_OUT); a=ap.parse_args(); result=build_probe(); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print('schema:',result['schema']); print('diagnosis:',result['diagnosis']); print('supported_hook_count:',result['supported_hook_count']); print('actionable_current_hook_count:',result['actionable_current_hook_count']); print('new_lore_authored:',result['new_lore_authored']); print('out:',a.out); return 0
if __name__=='__main__': raise SystemExit(main())
