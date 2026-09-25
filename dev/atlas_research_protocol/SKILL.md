---
name: solar-atlas-research
description: Route qualified Solar-System factual research campaigns through ARP v1.0; preserve source provenance, epistemic classes, resolution, coverage, resumability, and independent liens. Do not use for new science unless a governed campaign is explicitly requested.
metadata:
  short-description: Route Solar Atlas research through ARP v1.0
---

# Solar Atlas Research Router

Use this skill for a governed empirical Solar-System factual campaign.

1. Read [protocol.md](protocol.md) for the operating loop and firewall.
2. Select a body profile from [profiles/body_profiles.json](profiles/body_profiles.json).
3. Apply [policies/source_authority.json](policies/source_authority.json) to the claim domain.
4. Use the JSON contracts under `contracts/` for campaign, source, artifact,
   assertion, frontier, and lien records.
5. Run the deterministic validator before claiming qualification.
6. Submit an independent qualification result; do not have the researcher
   silently resolve its own blocking liens.

ARP does not authorize external acquisition, new body campaigns, preferred
facts, Phase-4 state, engineering/resource/economic/habitation conclusions,
or CIVPROP. It does not replace Solar Facts v0.3-R1.
