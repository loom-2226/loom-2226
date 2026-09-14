#!/usr/bin/env python3
from pathlib import Path


def main() -> int:
    # Deliberate Termux/shared-storage portability defect for assisted-repair smoke test.
    # /tmp is intentionally not writable in this environment; the repair agent should
    # replace this with a writable Termux temp/cache path without touching authority.
    target = Path('/tmp/loom-assisted-controlled-test.txt')
    target.write_text('controlled repair fixture\n', encoding='utf-8')
    print(f'CONTROLLED_REPAIR_FIXTURE_OK={target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
