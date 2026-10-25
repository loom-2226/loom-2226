"""Solar interface time conversion. Physical authority uses numeric SPICE ET.

TDB calendar text is parsed by CSPICE TPARSE without a leap-second kernel.
Explicit UTC input is accepted only at this boundary, using the pinned LSK;
the resulting ET is thereafter independent of the display representation.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import math
from pathlib import Path
import re
from threading import RLock

from src.loom_spatial_state_authority import CelestialStateError

SPICE_LOCK = RLock()


def finite_et(value):
    if isinstance(value, bool):
        raise CelestialStateError('epoch_et must be a finite number')
    try:
        et = float(value)
    except (TypeError, ValueError) as exc:
        raise CelestialStateError('epoch_et must be a finite number') from exc
    if not math.isfinite(et):
        raise CelestialStateError('epoch_et must be a finite number')
    return et


class SolarTimeCodec:
    def __init__(self, lsk_asset=None):
        self.lsk_asset = lsk_asset
        self.lsk_sha256 = getattr(lsk_asset, 'sha256', None)

    @contextmanager
    def _lsk_pool(self):
        if self.lsk_asset is None:
            raise CelestialStateError('explicit UTC input requires a pinned Solar LSK')
        import spiceypy as spice
        path = Path(self.lsk_asset.path).expanduser().resolve()
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != self.lsk_sha256:
            raise CelestialStateError('pinned Solar LSK is missing or has changed')
        previous = [spice.kdata(i, 'ALL') for i in range(spice.ktotal('ALL'))]
        try:
            spice.kclear()
            spice.furnsh(str(path))
            yield spice
        finally:
            spice.kclear()
            for prior, _, parent, _ in previous:
                if not parent:
                    spice.furnsh(prior)

    def parse(self, value):
        """Return ET seconds past J2000 from ET, explicit TDB or explicit UTC."""
        if isinstance(value, (float, int)):
            return finite_et(value)
        raw = str(value).strip()
        if not raw:
            raise CelestialStateError('Solar epoch is required')
        try:
            return finite_et(raw)
        except CelestialStateError:
            pass
        import spiceypy as spice
        if raw.upper().endswith(' TDB'):
            with SPICE_LOCK:
                et, error = spice.tparse(raw[:-4].strip())
            if error:
                raise CelestialStateError(f'invalid TDB calendar epoch: {value!r}: {error}')
            return finite_et(et)
        if raw.endswith('Z') or re.search(r'[+-]\d\d:\d\d$', raw):
            try:
                dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    raise ValueError('UTC offset required')
            except ValueError as exc:
                raise CelestialStateError(f'invalid explicit UTC epoch: {value!r}') from exc
            utc = dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            with SPICE_LOCK, self._lsk_pool() as loaded:
                return finite_et(loaded.str2et(utc))
        raise CelestialStateError('epoch must be numeric ET, a TDB calendar ending in TDB, or explicit UTC ending in Z')

    @staticmethod
    def representation(value):
        if isinstance(value, (int, float)):
            return 'SPICE_ET'
        raw = str(value).strip()
        try:
            finite_et(raw)
            return 'SPICE_ET'
        except CelestialStateError:
            pass
        return 'TDB_CALENDAR' if raw.upper().endswith(' TDB') else 'UTC_LSK_PROJECTION'

    @staticmethod
    def label(et):
        import spiceypy as spice
        with SPICE_LOCK:
            return spice.etcal(finite_et(et)) + ' TDB'


def codec_from_registry(registry):
    lsks = {}
    for source in registry.sources.values():
        if source.status != 'QUALIFIED':
            continue
        matches = [a for a in source.kernel_assets if str(a.path).lower().endswith('.tls')]
        if len(matches) != 1:
            raise CelestialStateError(f'qualified source requires exactly one pinned LSK: {source.ephemeris_source_id}')
        asset = matches[0]
        lsks[asset.sha256] = asset
    if len(lsks) != 1:
        raise CelestialStateError('qualified Solar sources disagree on LSK identity')
    return SolarTimeCodec(next(iter(lsks.values())))
