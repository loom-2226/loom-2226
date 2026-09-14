#!/usr/bin/env python3
from pathlib import Path

# Controlled disposable failure for LOOM assisted qualification.
# Intentional bug: writes to Android/Termux-incompatible /tmp path.
# Safe repair should redirect to a writable Termux temp/cache path.

def main() -> int:
    target = Path('/tmp/loom-assisted-controlled-test.txt')
    target.write_text('controlled repair fixture\n', encoding='utf-8')
    print(f'CONTROLLED_REPAIR_FIXTURE_PASS path={target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
