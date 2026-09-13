#!/usr/bin/env python3
from __future__ import annotations

"""One-command Pixel runner for Experience One Ceres→Neptune qualification.

Creates a fresh disposable Ceres campaign from Navigator's own constructor, copies
only required read inputs from the live runtime root, then executes the existing
Navigator campaign path through the disposable qualification harness. The user's
live campaign is never selected as the mutation target.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ANDROID_ROOT = Path('/storage/emulated/0/Download')
DEFAULT_RUNTIME = ANDROID_ROOT / 'LOOM_TEST'
DEFAULT_QUAL_ROOT = ANDROID_ROOT / 'LOOM_E1_NEPTUNE_QUAL'
DEFAULT_RESULT = ANDROID_ROOT / 'E1_NEPTUNE_QUALIFICATION_RESULT.json'
SCRIPT = Path(__file__).resolve()
DEFAULT_REPO = SCRIPT.parents[3]


def run_checked(argv: list[str]) -> None:
    print('\n$', ' '.join(argv))
    subprocess.run(argv, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    ap.add_argument('--runtime-root', type=Path, default=DEFAULT_RUNTIME)
    ap.add_argument('--qualification-root', type=Path, default=DEFAULT_QUAL_ROOT)
    ap.add_argument('--result', type=Path, default=DEFAULT_RESULT)
    ap.add_argument('--plan', type=int, default=1)
    ap.add_argument('--priority', default='BALANCED')
    ap.add_argument('--keep-existing-qualification-root', action='store_true')
    args = ap.parse_args()

    repo = args.repo.resolve()
    runtime = args.runtime_root.resolve()
    qual = args.qualification_root.resolve()
    result = args.result.resolve()

    if not (repo / 'src' / 'loom_navigator_core.py').exists():
        raise RuntimeError(f'Navigator source missing under repo: {repo}')
    if not runtime.exists():
        raise RuntimeError(f'Pixel runtime root missing: {runtime}')

    if qual.exists() and not args.keep_existing_qualification_root:
        if qual == runtime:
            raise RuntimeError('qualification root resolves to live runtime root — HARD FAIL')
        shutil.rmtree(qual)
    qual.mkdir(parents=True, exist_ok=True)

    seed = repo / 'engineering' / 'experience_one' / 'e1_neptune_seed_ceres.py'
    harness = repo / 'engineering' / 'experience_one' / 'qualification' / 'e1_neptune_disposable_campaign.py'

    run_checked([
        sys.executable, str(seed),
        '--repo', str(repo),
        '--runtime-root', str(runtime),
        '--out-root', str(qual),
    ])

    run_checked([
        sys.executable, str(harness),
        '--repo', str(repo),
        '--root', str(qual),
        '--destination', 'NEPTUNE_SYSTEM',
        '--priority', args.priority.upper(),
        '--plan', str(args.plan),
        '--out', str(result),
    ])

    print('\nE1 NEPTUNE QUALIFICATION COMPLETE')
    print('Result:', result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
