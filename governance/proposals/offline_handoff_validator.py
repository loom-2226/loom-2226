"""DRAFT integrity preflight only; not authenticated provenance or governance approval.

Use only with a separately approved protocol. No network, publishing or mutation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

REQUIRED = (
    'LOOM_START_HERE.md',
    'governance/current/LOOM_CURRENT_WORKSTATE.yml',
    'governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md',
    'governance/current/LOOM_AUTHORITY_MODEL.yml',
    'governance/current/LOOM_CHANGE_CONTROL_v1.0.md',
    'governance/current/LOOM_RESEARCH_AUTHORITY_BOUNDARY_v1.0.md',
    'AGENTS.md',
)


def validate(snapshot: Path, head: str, parent_ancestor: bool) -> list[str]:
    errors = []
    try:
        manifest = json.loads((snapshot / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return ['STOP: manifest missing or malformed']
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        return ['STOP: unsupported schema']
    for key in ('main_commit', 'head_commit', 'base_commit'):
        value = manifest.get(key)
        if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{40}', value):
            errors.append('STOP: invalid ' + key)
    if manifest.get('head_commit') != head:
        errors.append('STOP: local head mismatch')
    if not parent_ancestor:
        errors.append('STOP: parent ancestry unverified')
    if manifest.get('approval_status') != 'approved_governance_on_main':
        errors.append('STOP: governing approval absent')
    if manifest.get('capture_status') != 'authenticated_verified':
        errors.append('STOP: source provenance unverified')
    if not manifest.get('scope_review_complete'):
        errors.append('STOP: scoped AGENTS/scope review incomplete')
    files = manifest.get('files')
    if not isinstance(files, list):
        return errors + ['STOP: missing inventory']
    seen = set()
    for entry in files:
        if not isinstance(entry, dict):
            errors.append('STOP: malformed entry')
            continue
        name, digest = entry.get('path'), entry.get('sha256')
        if (not isinstance(name, str) or not name or name.startswith('/')
                or '..' in Path(name).parts or '\\' in name or name in seen):
            errors.append('STOP: unsafe or duplicate path')
            continue
        seen.add(name)
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            errors.append('STOP: bad digest: ' + name)
            continue
        target = snapshot / 'content' / name
        if target.is_symlink() or not target.is_file():
            errors.append('STOP: missing or symlink: ' + name)
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            errors.append('STOP: content mismatch: ' + name)
    for required in REQUIRED:
        if required not in seen:
            errors.append('STOP: missing required source: ' + required)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--local-head', required=True)
    parser.add_argument('--parent-is-ancestor', action='store_true')
    args = parser.parse_args()
    problems = validate(args.snapshot, args.local_head, args.parent_is_ancestor)
    for problem in problems:
        print(problem)
    if problems:
        return 2
    print('OFFLINE INTEGRITY ONLY: PASS. Not live GitHub verification, publication, or deployment approval.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
