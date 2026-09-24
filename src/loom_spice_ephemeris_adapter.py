"""Governed local SPICE adapter for the Solar Phase-1 state authority.

SPICE is deliberately private to this module. Consumers receive the existing
HybridCelestialStateService and therefore cannot bypass LOOM identity,
coverage, frame, unit, or provenance checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Iterable, Mapping

from src.loom_spatial_state_authority import (
    CANONICAL_FRAME,
    CelestialStateError,
    HybridCelestialStateService,
    SpatialState,
)


SPICE_FRAME = "ECLIPJ2000"
SPICE_ABERRATION = "NONE"
STATE_UNITS = "km,km/s"


def _epoch(value: str) -> datetime:
    text = str(value).strip()
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise CelestialStateError(f"invalid epoch_utc: {value!r}") from exc
    if parsed.tzinfo is None:
        raise CelestialStateError("epoch_utc must include timezone")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class KernelAsset:
    path: Path | str
    sha256: str
    byte_count: int | None = None


@dataclass(frozen=True)
class SolarBody:
    body_id: str
    canonical_name: str
    body_class: str


@dataclass(frozen=True)
class BodyIdentifier:
    body_id: str
    authority: str
    identifier_type: str
    identifier_value: str
    status: str = "ACTIVE"


@dataclass(frozen=True)
class EphemerisSource:
    ephemeris_source_id: str
    provider: str
    product_name: str
    product_version: str
    asset_filename: str
    sha256: str
    byte_count: int
    source_url: str
    acquired_at: str
    status: str
    kernel_assets: tuple[KernelAsset, ...]


@dataclass(frozen=True)
class EphemerisCoverage:
    ephemeris_source_id: str
    body_id: str | None
    valid_from: str
    valid_until: str
    reference_frame: str = SPICE_FRAME
    units: str = STATE_UNITS
    coverage_class: str = "BODY"
    status: str = "QUALIFIED"


class SolarEphemerisRegistry:
    """In-memory form of the governed identity/source metadata contract."""

    def __init__(
        self,
        bodies: Iterable[SolarBody],
        identifiers: Iterable[BodyIdentifier],
        sources: Iterable[EphemerisSource],
        coverage: Iterable[EphemerisCoverage],
    ) -> None:
        self.bodies = {b.body_id: b for b in bodies}
        if len(self.bodies) == 0 or any(not k.strip() for k in self.bodies):
            raise CelestialStateError("at least one valid LOOM Solar body is required")
        self.identifiers = tuple(identifiers)
        self.sources = {s.ephemeris_source_id: s for s in sources}
        self.coverage = tuple(coverage)
        self._by_body: dict[str, tuple[BodyIdentifier, ...]] = {}
        for identifier in self.identifiers:
            if identifier.body_id not in self.bodies:
                raise CelestialStateError(f"identifier references unknown LOOM body: {identifier.body_id}")
            self._by_body.setdefault(identifier.body_id, tuple())
            self._by_body[identifier.body_id] += (identifier,)
        for record in self.coverage:
            if record.ephemeris_source_id not in self.sources:
                raise CelestialStateError(f"coverage references unknown source: {record.ephemeris_source_id}")
            if record.body_id is not None and record.body_id not in self.bodies:
                raise CelestialStateError(f"coverage references unknown LOOM body: {record.body_id}")
            if _epoch(record.valid_from) >= _epoch(record.valid_until):
                raise CelestialStateError("ephemeris coverage must have valid_from < valid_until")

    def body_identifier(self, body_id: str) -> BodyIdentifier:
        matches = tuple(
            v for v in self._by_body.get(body_id, ())
            if v.status == "ACTIVE" and v.authority == "NAIF" and v.identifier_type == "NAIF_ID"
        )
        if len(matches) != 1:
            raise CelestialStateError(f"LOOM body must have exactly one active governed identifier: {body_id}")
        return matches[0]

    def source_for(self, body_id: str, epoch_utc: str) -> tuple[EphemerisSource, EphemerisCoverage]:
        if body_id not in self.bodies:
            raise CelestialStateError(f"unknown LOOM body: {body_id}")
        requested = _epoch(epoch_utc)
        candidates: list[tuple[EphemerisSource, EphemerisCoverage]] = []
        for record in self.coverage:
            if record.status != "QUALIFIED" or record.reference_frame != SPICE_FRAME or record.units != STATE_UNITS:
                continue
            source = self.sources[record.ephemeris_source_id]
            if source.status != "QUALIFIED":
                continue
            if record.body_id not in (None, body_id):
                continue
            if _epoch(record.valid_from) <= requested <= _epoch(record.valid_until):
                candidates.append((source, record))
        if not candidates:
            raise CelestialStateError(f"no qualified source coverage for LOOM body {body_id} at {_iso(requested)}")
        # Body-specific coverage outranks product coverage. Equal specificity
        # is an authority conflict; metadata input order is never a tiebreaker.
        specificity = max(record.body_id is not None for _, record in candidates)
        candidates = [(source, record) for source, record in candidates
                      if (record.body_id is not None) == specificity]
        if len(candidates) != 1:
            source_ids = sorted(source.ephemeris_source_id for source, _ in candidates)
            raise CelestialStateError(
                "ambiguous qualified ephemeris authority for "
                f"LOOM body {body_id} at {_iso(requested)}: {source_ids}"
            )
        source, record = candidates[0]
        return source, record


class SpiceEphemerisAdapter:
    """Private SPICE evaluator exposed only through HybridCelestialStateService."""

    def __init__(self, registry: SolarEphemerisRegistry):
        self.registry = registry
        self._loaded: set[str] = set()
        self._service = HybridCelestialStateService(self._direct_lookup, {})

    def service(self) -> HybridCelestialStateService:
        return self._service

    def resolve(self, body_id: str, epoch_utc: str) -> SpatialState:
        """Convenience delegation; the returned state still comes from the shared authority."""
        return self._service.resolve(body_id, epoch_utc)

    def _spice(self):
        try:
            import spiceypy  # type: ignore
        except ImportError as exc:
            raise CelestialStateError("spiceypy is required for the local SPICE adapter") from exc
        return spiceypy

    @staticmethod
    def _verify_asset(asset: KernelAsset) -> Path:
        path = Path(asset.path).expanduser().resolve()
        if not path.is_file():
            raise CelestialStateError(f"pinned kernel asset is missing: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != asset.sha256.lower():
            raise CelestialStateError(f"kernel hash mismatch: {path}")
        if asset.byte_count is not None and path.stat().st_size != asset.byte_count:
            raise CelestialStateError(f"kernel byte-count mismatch: {path}")
        return path

    def _load_source(self, source: EphemerisSource) -> None:
        if source.ephemeris_source_id in self._loaded:
            return
        spice = self._spice()
        for asset in source.kernel_assets:
            spice.furnsh(str(self._verify_asset(asset)))
        self._loaded.add(source.ephemeris_source_id)

    def _direct_lookup(self, body_id: str, epoch_utc: str) -> SpatialState | None:
        identifier = self.registry.body_identifier(body_id)
        if identifier.authority != "NAIF" or identifier.identifier_type != "NAIF_ID":
            raise CelestialStateError(f"unsupported governed identifier semantics for {body_id}")
        try:
            target = int(identifier.identifier_value)
        except ValueError as exc:
            raise CelestialStateError(f"NAIF identifier is not an integer for {body_id}") from exc
        source, coverage = self.registry.source_for(body_id, epoch_utc)
        self._load_source(source)
        spice = self._spice()
        requested = _iso(_epoch(epoch_utc))
        try:
            et = float(spice.str2et(requested))
            # spkgeo is the geometric (aberration-free) state API: target,
            # ET, frame, observer. Keep the explicit NONE contract in the
            # metadata even though this API has no aberration argument.
            state, _ = spice.spkgeo(target, et, SPICE_FRAME, 10)
        except Exception as exc:
            raise CelestialStateError(
                f"SPICE state unavailable for LOOM body {body_id} from {source.ephemeris_source_id}"
            ) from exc
        return SpatialState(
            entity_id=body_id,
            epoch_utc=requested,
            reference_frame=CANONICAL_FRAME,
            position_km=tuple(float(v) for v in state[:3]),
            velocity_km_s=tuple(float(v) for v in state[3:]),
            provenance={
                "state_source": "LOCAL_SPICE",
                "provider": source.provider,
                "product_name": source.product_name,
                "product_version": source.product_version,
                "ephemeris_source_id": source.ephemeris_source_id,
                "asset_filename": source.asset_filename,
                "asset_sha256": source.sha256,
                "kernel_assets": [
                    {"path": str(Path(a.path)), "sha256": a.sha256, "byte_count": a.byte_count}
                    for a in source.kernel_assets
                ],
                "source_url": source.source_url,
                "coverage": {
                    "valid_from": coverage.valid_from,
                    "valid_until": coverage.valid_until,
                    "coverage_class": coverage.coverage_class,
                },
                "naif_identifier": identifier.identifier_value,
                "observer_naif_identifier": "10",
                "spice_frame": SPICE_FRAME,
                "aberration_correction": SPICE_ABERRATION,
                "time_scale_internal": "SPICE ET/TDB",
                "request_time_scale": "UTC",
                "units": STATE_UNITS,
            },
            navigation_grade=True,
            payload={"state_class": "CELESTIAL", "ephemeris_quality": "QUALIFIED"},
        )


__all__ = [
    "BodyIdentifier", "EphemerisCoverage", "EphemerisSource", "KernelAsset",
    "SolarBody", "SolarEphemerisRegistry", "SpiceEphemerisAdapter",
]
