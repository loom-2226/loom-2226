"""GAP-014 Earth demographic authority adapter.

NON_CANON integration machinery. This adapter consumes already-promoted Earth
authority. It does not propagate, recalibrate, or reinterpret Earth demography.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class EarthDemographicAuthorityPointV1:
    snapshot_id: str
    year: int
    biological_population: float
    births: float | None
    deaths: float | None
    workforce: float | None
    provenance_refs: tuple[str, ...]
    authority_class: str = "EARTH_PROMOTED_DEMOGRAPHIC_AUTHORITY"

def aggregate_earth_authority(*, demographic_rows, labor_rows, snapshot_id, year,
                              provenance_refs):
    if not provenance_refs:
        raise ValueError("MISSING_EARTH_AUTHORITY_PROVENANCE")
    d=[r for r in demographic_rows if r["snapshot_id"]==snapshot_id and int(r["year"])==year]
    if not d:
        raise ValueError("EARTH_DEMOGRAPHIC_AUTHORITY_MISSING")
    pop=sum(float(r["biological_population"]) for r in d)
    births=None if any(r.get("births") is None for r in d) else sum(float(r["births"]) for r in d)
    deaths=None if any(r.get("deaths") is None for r in d) else sum(float(r["deaths"]) for r in d)
    labor=[r for r in labor_rows if r["snapshot_id"]==snapshot_id and int(r["year"])==year]
    workforce=None
    if labor:
        field="total_effective_labor" if "total_effective_labor" in labor[0] else "legacy_employment"
        if all(r.get(field) is not None for r in labor):
            workforce=sum(float(r[field]) for r in labor)
    return EarthDemographicAuthorityPointV1(snapshot_id,year,pop,births,deaths,workforce,
                                             tuple(provenance_refs))

def apply_earth_authority_to_state(*, point, location_id):
    if location_id!="EARTH_SURFACE":
        raise ValueError("EARTH_AUTHORITY_CANNOT_SEED_OFFWORLD")
    return {
        "location_id": location_id,
        "year": point.year,
        "biological_population": point.biological_population,
        "workforce": point.workforce,
        "source_snapshot_id": point.snapshot_id,
        "authority_class": point.authority_class,
        "provenance_refs": point.provenance_refs,
    }

def may_recompute_earth_demography():
    return False
