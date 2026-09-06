#!/usr/bin/env python3
"""Read-only LOOM campaign clock diagnostic."""
from __future__ import annotations

from dataclasses import asdict
import argparse
import json

from loom.campaign.clock import LegacyCampaignClockService
from loom.runtime import resolve_runtime_roots


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Show authoritative LOOM campaign time/revision")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--campaign-root", help="override campaign root for diagnostics/testing")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    roots = resolve_runtime_roots(campaign_root=args.campaign_root or None)
    clock = LegacyCampaignClockService(roots.campaign_root).now()
    value = asdict(clock)
    if args.json:
        print(json.dumps(value, indent=2, sort_keys=True))
    else:
        print("LOOM CAMPAIGN CLOCK")
        print(f"CAMPAIGN  {clock.campaign_id}")
        print(f"REVISION  {clock.revision}")
        print(f"EPOCH UTC {clock.epoch_utc}")
        print(f"LAST      {clock.last_transition_id or '-'}")
        print("AUTHORITY CAMPAIGN JSON/HISTORY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
