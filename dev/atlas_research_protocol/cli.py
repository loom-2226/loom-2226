"""Command-line entry point for deterministic ARP qualification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validate import efficiency_metrics, load_json, qualify
from .state import remaining_work


def main() -> int:
    parser = argparse.ArgumentParser(description="ARP v1.0 deterministic campaign validator")
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--authority-policy", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--metrics", action="store_true")
    parser.add_argument("--profile", type=Path, help="Body profile JSON object or full profiles file")
    args = parser.parse_args()
    campaign = load_json(args.campaign)
    policy = load_json(args.authority_policy) if args.authority_policy else None
    result = qualify(campaign, policy, args.root)
    output = {"qualification": result}
    if args.metrics:
        output["metrics"] = efficiency_metrics(campaign)
    if args.profile:
        profile_doc = load_json(args.profile)
        profile = profile_doc.get("profiles", {}).get(campaign["body_profile"], profile_doc)
        output["remaining_work"] = remaining_work(campaign, profile)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
