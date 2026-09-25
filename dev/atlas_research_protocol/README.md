# Atlas Research Protocol v1.0 / implementation v1.0.2

Small deterministic machinery for future empirical Solar-System factual
campaigns. Implementation v1.0.1 formalizes the ARP-QUAL-01 repair; v1.0.2
adds the narrow, body-agnostic coverage-basis hardening earned by post-hoc
miss forensics. This package does not perform a research campaign and does
not replace Solar Facts v0.3-R1.

## Files

- `SKILL.md` — thin agent-facing router.
- `protocol.md` — progressive-disclosure operating method.
- `models.py` — typed source, artifact, assertion, frontier and lien contracts.
- `validate.py` — deterministic campaign, provenance, cutoff, coverage,
  frontier, duplication, scope, contamination and lien checks.
- `cli.py` — validation entry point.
- `profiles/` — body-class profiles.
- `policies/` — domain-sensitive source authority policy.
- `contracts/` — machine-readable contract summary.
- `fixtures/` — resumable reference campaign and Ceres gold evaluation data.
- `ARP_PREEXISTING_WORKTREE_INVENTORY.json` — preservation record created before ARP implementation.
- `tests/test_arp.py` — hostile synthetic tests.
- `releases/` — earned implementation release records.
- `qualifications/arp_qual_01_ceres/ARP_QUAL01_CERES_MISS_FORENSICS.*` — frozen
  miss analysis and disposition.

Run the local qualification report:

```bash
PYTHONPATH=. python -m dev.atlas_research_protocol.qualify
```

No external research operation is performed by that command.
