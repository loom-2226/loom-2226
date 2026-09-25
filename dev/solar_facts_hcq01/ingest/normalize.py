from __future__ import annotations

from dataclasses import replace

from .models import FactCandidate, StagingRecord


def normalize(record: StagingRecord) -> StagingRecord:
    """Normalize known units without changing the source-reported fields."""
    facts: list[FactCandidate] = []
    for fact in record.facts:
        value, unit = fact.normalized_value, fact.normalized_unit
        if fact.property_code == "GM" and fact.reported_unit == "km^3/s^2":
            value, unit = float(fact.reported_value_text), "km^3/s^2"
        elif fact.property_code == "MASS" and fact.reported_unit == "10^18 kg":
            value, unit = float(fact.reported_value_text) * 10**18, "kg"
            plus = fact.uncertainty_plus * 10**18 if fact.uncertainty_plus is not None else None
            minus = fact.uncertainty_minus * 10**18 if fact.uncertainty_minus is not None else None
            facts.append(replace(fact, normalized_value=value, normalized_unit=unit,
                                 uncertainty_plus=plus, uncertainty_minus=minus))
            continue
        elif fact.property_code == "BULK_DENSITY" and fact.reported_unit == "g/cm^3":
            value, unit = float(fact.reported_value_text) * 1000, "kg/m^3"
            plus = fact.uncertainty_plus * 1000 if fact.uncertainty_plus is not None else None
            minus = fact.uncertainty_minus * 1000 if fact.uncertainty_minus is not None else None
            facts.append(replace(fact, normalized_value=value, normalized_unit=unit,
                                 uncertainty_plus=plus, uncertainty_minus=minus))
            continue
        elif fact.property_code == "ROTATION_PERIOD" and fact.reported_unit == "d":
            value, unit = float(fact.reported_value_text) * 86400.0, "s"
        elif fact.normalized_value is None and fact.value_min is not None and fact.value_max is not None:
            # Preserve a reported range without manufacturing a midpoint scalar.
            value, unit = None, fact.normalized_unit or fact.reported_unit
        elif fact.normalized_value is None and fact.reported_value_text not in (None, "UNKNOWN"):
            value, unit = float(fact.reported_value_text), fact.reported_unit
        facts.append(replace(fact, normalized_value=value, normalized_unit=unit))
    return replace(record, facts=tuple(facts))
