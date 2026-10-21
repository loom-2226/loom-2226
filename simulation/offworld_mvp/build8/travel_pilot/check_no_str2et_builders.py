"""CI guard for text-based UTC-to-ET conversion in table/bulk builders."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BUILDER_NAMES = {'batch.py', 'body_lattice_builder.py'}

def main():
    base = ROOT / 'simulation/offworld_mvp'
    candidates = [p for p in base.rglob('*.py') if p.name in BUILDER_NAMES or ('table' in p.name.lower() and 'build' in p.name.lower()) or ('lattice' in p.name.lower() and 'builder' in p.name.lower())]
    failures = [str(p.relative_to(ROOT)) for p in candidates if ('spice.' + 'str2et') in p.read_text() or ('spiceypy.' + 'str2et') in p.read_text()]
    if failures:
        raise SystemExit('Text UTC-to-ET prohibited in table builders: '+', '.join(failures))
    print(f'PASS: {len(candidates)} table/bulk builders contain no text UTC-to-ET conversion')

if __name__ == '__main__':
    main()
