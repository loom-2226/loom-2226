from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parent


def digest_tree(path: Path) -> list[dict]:
    rows = []
    for item in sorted(path.rglob('*')):
        if item.is_file() and not item.is_symlink():
            data = item.read_bytes()
            rows.append({'path': str(item.relative_to(path)), 'sha256': hashlib.sha256(data).hexdigest(), 'byte_count': len(data)})
    return rows


def emit(name: str, directory: str) -> None:
    base = ROOT / directory
    campaign = json.loads((base / 'campaign.json').read_text())
    manifest = {
        'campaign_id': campaign['campaign_id'],
        'arp_version': campaign['arp_version'],
        'arp_implementation_revision': campaign.get('arp_implementation_revision', '1.0.0'),
        'campaign_sha256': hashlib.sha256((base / 'campaign.json').read_bytes()).hexdigest(),
        'files': digest_tree(base),
        'scientific_counts': {
            'sources': len(campaign['sources']),
            'artifacts': len(campaign['artifacts']),
            'assertions': len(campaign['assertions']),
            'independent_evidence_lineages': len({a['independent_evidence_lineage_id'] for a in campaign['assertions']}),
        },
        'cutoff': campaign['knowledge_cutoff'],
        'blindness': campaign['blindness'],
    }
    (ROOT / name).write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    emit('attempt_01_manifest.json', 'frozen_attempt_01')
    emit('attempt_02_manifest.json', 'attempt_02')
