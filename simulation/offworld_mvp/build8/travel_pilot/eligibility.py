"""Catalog-wide, date-qualified endpoint state evidence. No route search.

Reads the frozen 110-identity catalog and already-qualified Solar manifests.
DIRECT is *state authority*, not a vehicle, freight, or local-leg permission.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.loom_spice_ephemeris_adapter import (
    BodyIdentifier, EphemerisCoverage, SolarBody, SolarEphemerisRegistry,
)
from src.loom_spatial_state_authority import CelestialStateError
from simulation.offworld_mvp.build7 import compile_solar_accessibility as solar

CATALOG = solar.ROOT / "dev/solar_baseline_01/raw/loom_solar_identity_snapshot.tsv"
DE440_PROMOTED = (
    "MERCURY_SYSTEM_BARYCENTER", "VENUS_SYSTEM_BARYCENTER",
    "EARTH_MOON_BARYCENTER", "MARS_SYSTEM_BARYCENTER",
    "JUPITER_SYSTEM_BARYCENTER", "SATURN_SYSTEM_BARYCENTER",
    "URANUS_SYSTEM_BARYCENTER", "NEPTUNE_SYSTEM_BARYCENTER",
    "PLUTO_SYSTEM_BARYCENTER", "SUN", "MERCURY", "VENUS", "MOON", "EARTH",
)
# The official planet-center product is the governing physical-center
# selection where an older Phase4B Saturn physical-center source overlaps.
SATURN_CENTER_SOURCE = "JPL_SAT441"


def catalog_rows():
    entries = []
    for line in CATALOG.read_text().splitlines():
        key, name, cls, parent, status, authority, id_type, identity, id_status = line.split("|")
        if status != "ACTIVE" or id_status != "ACTIVE":
            raise ValueError("UNQUALIFIED_CATALOG_IDENTITY:" + key)
        entries.append(dict(body_id=key, name=name, body_class=cls,
                            parent_body_id=parent or None, identifier_authority=authority,
                            identifier_type=id_type, identifier_value=identity))
    if len(entries) != 110 or len({x["body_id"] for x in entries}) != 110:
        raise ValueError("CATALOG_IDENTITY_COUNT_MISMATCH")
    return entries


def catalog_registry(asset_root):
    """Merge published body-specific coverage, not guessed positions.

    Identical coverage duplicates deduplicate. Saturn's official physical
    center governs its earlier Phase4B overlap. Existing pilot 4-body
    route provenance must remain byte-identical.
    """
    source_index, _ = solar._source_index(Path(asset_root))
    sources = {sid: src for sid, (src, _) in source_index.items()}
    entries = catalog_rows()
    bodies = [SolarBody(x["body_id"], x["name"], x["body_class"]) for x in entries]
    identifiers = [BodyIdentifier(x["body_id"], x["identifier_authority"],
                                  x["identifier_type"], x["identifier_value"])
                   for x in entries]
    coverage = {}
    known = {x["body_id"] for x in entries}
    for sid, (_, source_coverages) in sorted(source_index.items()):
        for record in source_coverages:
            # _source_index groups manifest coverage alongside shared asset
            # identities: never attribute another source's rows to this SID.
            if record.ephemeris_source_id != sid or record.body_id not in known:
                continue
            if sid == "DE440" and record.body_id in DE440_PROMOTED:
                continue
            if record.body_id == "SATURN" and sid != SATURN_CENTER_SOURCE:
                continue
            key = (record.ephemeris_source_id, record.body_id, record.valid_from,
                   record.valid_until, record.coverage_class)
            existing = coverage.get(key)
            if existing is not None and existing != record:
                raise ValueError("SOURCE_COVERAGE_CONFLICT:" + str(key))
            coverage[key] = record
    # Migration 012 *explicitly* promoted fourteen DE440 coverage rows.
    # Their absence from an older manifest must not be mistaken for missing
    # authority, nor generalized into barycenter substitutions.
    if "DE440" not in sources:
        raise ValueError("QUALIFIED_DE440_MISSING")
    for body in DE440_PROMOTED:
        row = EphemerisCoverage("DE440", body, solar.DE440_FROM, solar.DE440_UNTIL)
        key = (row.ephemeris_source_id, row.body_id, row.valid_from,
               row.valid_until, row.coverage_class)
        coverage.setdefault(key, row)
    return SolarEphemerisRegistry(bodies, identifiers, sources.values(), coverage.values())


def _epoch(value):
    if isinstance(value, datetime):
        day = value
    else:
        day = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if day.tzinfo is None:
        day = day.replace(tzinfo=timezone.utc)
    return day.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_endpoint(body_id, epoch_utc, *, registry, catalog=None):
    """Return status + independent ephemeris status for a single body/date.

    Moons may have DIRECT ephemerides but are UNKNOWN_LOCAL_LEG until
    user-authored access physics exists. Sun cannot be a project terminal.
    Spacecraft never obtain navigation-grade target authority from
    propagated trajectories.
    """
    rows = catalog if catalog is not None else catalog_rows()
    identity = next((r for r in rows if r["body_id"] == body_id), None)
    epoch = _epoch(epoch_utc)
    result = dict(body_id=body_id, epoch_utc=epoch,
                  status=None, ephemeris_status=None, eligible=False,
                  parent_body_id=identity["parent_body_id"] if identity else None,
                  source_id=None, source_sha256=None,
                  coverage_from=None, coverage_until=None,
                  alternate_barycenter=None, reason=None)
    if identity is None:
        result.update(status="UNKNOWN_CATALOG_ENTITY",
                      ephemeris_status="UNKNOWN_CATALOG_ENTITY",
                      reason="NO_MATCHING_CATALOG_IDENTITY")
        return result
    if identity["body_id"] == "SUN":
        result.update(status="UNSUPPORTED_SUN_ENDPOINT",
                      ephemeris_status="DIRECT",
                      reason="SOLAR_CENTRE_NOT_A_SUPPORTED_TRAVEL_TERMINAL")
        return result

    try:
        src, coverage = registry.source_for(body_id, epoch)
    except CelestialStateError as exc:
        # Missing direct coverage is not permission to substitute a
        # parent barycenter, infer a trajectory or use a propagated state.
        text = str(exc)
        if "conflict" in text.lower() or "ambiguous" in text.lower():
            result.update(status="UNKNOWN_EPHEMERIS_MISSING",
                          ephemeris_status="UNKNOWN_EPHEMERIS_MISSING",
                          reason="QUALIFIED_SOURCE_CONFLICT")
        else:
            result.update(status="UNKNOWN_EPHEMERIS_MISSING",
                          ephemeris_status="UNKNOWN_EPHEMERIS_MISSING",
                          reason="NO_QUALIFIED_DATE_COVERAGE")
    else:
        result.update(source_id=src.ephemeris_source_id,
                      source_sha256=src.sha256,
                      coverage_from=coverage.valid_from,
                      coverage_until=coverage.valid_until)
        if not src.navigation_grade or identity["body_class"] == "SPACECRAFT":
            result.update(status="UNKNOWN_EPHEMERIS_PROPAGATED",
                          ephemeris_status="UNKNOWN_EPHEMERIS_PROPAGATED",
                          reason="NOT_NAVIGATION_GRADE")
        elif identity["body_class"] == "NATURAL_SATELLITE":
            result.update(status="UNKNOWN_LOCAL_LEG", ephemeris_status="DIRECT",
                          reason="LOCAL_ACCESS_TIME_COST_FEASIBILITY_NOT_AUTHORED")
        else:
            result.update(status="DIRECT", ephemeris_status="DIRECT",
                          eligible=True, reason="QUALIFIED_DATE_COVERAGE")

    if identity["body_class"] == "SPACECRAFT":
        result.update(status="UNKNOWN_EPHEMERIS_PROPAGATED",
                      ephemeris_status="UNKNOWN_EPHEMERIS_PROPAGATED",
                      eligible=False, reason="SPACECRAFT_STATE_NOT_NAVIGATION_GRADE")
    if identity["body_class"] == "NATURAL_SATELLITE" and result["ephemeris_status"] == "DIRECT":
        result["status"] = "UNKNOWN_LOCAL_LEG"
        result["eligible"] = False
    # Suggest a *distinct* known identity, not an actual replacement state.
    bary = body_id + "_SYSTEM_BARYCENTER"
    if body_id == "EARTH":
        bary = "EARTH_MOON_BARYCENTER"
    if (result["ephemeris_status"] != "DIRECT"
            and bary in registry.bodies and bary != body_id):
        try:
            alt, _ = registry.source_for(bary, epoch)
            if alt.navigation_grade:
                result["alternate_barycenter"] = bary
        except CelestialStateError:
            pass
    return result
