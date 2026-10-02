"""GAP-014 migration / passenger-flow reconciliation boundary.

NON_CANON integration machinery. Migration is a change of residence and must be
backed by realized passenger movement on the same OD/year. Passenger movement is
not automatically migration.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MigrationDemandV1:
    year:int
    origin_location_id:str
    destination_location_id:str
    requested_persons:float|None
    provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class AuthorizedMigrationV1:
    year:int
    origin_location_id:str
    destination_location_id:str
    requested_persons:float|None
    realized_passenger_movements:float|None
    authorized_migrants:float|None
    status:str
    provenance_refs:tuple[str,...]

def authorize_migration(*, demand, route_traffic_state, origin_population):
    if not demand.provenance_refs:
        raise ValueError("MISSING_MIGRATION_DEMAND_PROVENANCE")
    if demand.requested_persons is not None and demand.requested_persons < 0:
        raise ValueError("NEGATIVE_MIGRATION_DEMAND")
    if origin_population < 0:
        raise ValueError("NEGATIVE_ORIGIN_POPULATION")
    if route_traffic_state.year != demand.year:
        raise ValueError("MIGRATION_TRAFFIC_YEAR_MISMATCH")
    if route_traffic_state.origin_location_id != demand.origin_location_id or route_traffic_state.destination_location_id != demand.destination_location_id:
        raise ValueError("MIGRATION_TRAFFIC_OD_MISMATCH")
    realized=route_traffic_state.realized_passenger_movements
    if demand.requested_persons is None or realized is None:
        return AuthorizedMigrationV1(demand.year,demand.origin_location_id,demand.destination_location_id,
            demand.requested_persons,realized,None,"UNKNOWN",demand.provenance_refs)
    if realized < 0:
        raise ValueError("NEGATIVE_REALIZED_PASSENGER_MOVEMENT")
    amount=min(float(demand.requested_persons),float(realized),float(origin_population))
    return AuthorizedMigrationV1(demand.year,demand.origin_location_id,demand.destination_location_id,
        demand.requested_persons,realized,amount,"AUTHORIZED",demand.provenance_refs)

def apply_conserved_migration(*, populations, authorization):
    if authorization.status!="AUTHORIZED" or authorization.authorized_migrants is None:
        raise ValueError("MIGRATION_NOT_AUTHORIZED")
    out=dict(populations)
    o=authorization.origin_location_id; d=authorization.destination_location_id
    if o not in out or d not in out: raise ValueError("MIGRATION_LOCATION_MISSING")
    amount=authorization.authorized_migrants
    if amount>out[o]: raise ValueError("MIGRATION_EXCEEDS_ORIGIN_POPULATION")
    before=sum(out.values())
    out[o]-=amount; out[d]+=amount
    if abs(sum(out.values())-before)>1e-9: raise ValueError("MIGRATION_CONSERVATION_FAILURE")
    return out
