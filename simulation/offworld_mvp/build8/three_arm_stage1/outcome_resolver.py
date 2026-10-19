"""TEST ONLY seeded outcome resolver; no claim of real mission reliability."""
from decimal import Decimal
from hashlib import sha256

def resolve(seed, chance, case_id):
    probability = Decimal(str(chance))
    if not 0 <= probability <= 1:
        raise ValueError('INVALID_CHANCE')
    payload = f'{seed}|{case_id}'.encode('utf-8')
    digest = sha256(payload).hexdigest()
    draw = Decimal(int(digest[:16], 16)) / Decimal(2**64)
    return {'outcome': 'DELIVERED' if draw < probability else 'FAILED',
            'draw': str(draw), 'success_chance': str(probability),
            'draw_sha256': digest, 'method': 'SHA256_SEED_CASE_FIRST64_TEST_ONLY'}
