"""Incremental current-state indexes over append-only CIVPROP provenance ledgers."""
from __future__ import annotations

class CurrentStateIndexV03:
    def __init__(self):
        self._facility_cursor=0
        self._power_cursor=0
        self._traffic_cursor=0
        self._resource_cursor=0
        self.facilities_by_location={}
        self.active_facilities_by_location={}
        self.latest_power_by_location={}
        self.latest_traffic_by_location={}
        self.latest_resource_by_key={}

    def sync_facilities(self,facilities,*,year:int)->None:
        for x in facilities[self._facility_cursor:]:
            self.facilities_by_location.setdefault(x.location_id,[]).append(x)
        self._facility_cursor=len(facilities)
        self.active_facilities_by_location={
            loc:tuple(x for x in rows if x.status=="ACTIVE" and x.commissioned_year<=year)
            for loc,rows in self.facilities_by_location.items()
        }

    def active_facilities(self)->tuple:
        return tuple(x for loc in sorted(self.active_facilities_by_location)
                     for x in self.active_facilities_by_location[loc])

    def sync_physical_states(self,recorder)->None:
        for x in recorder.power_states[self._power_cursor:]:
            self.latest_power_by_location[x.location_id]=x
        self._power_cursor=len(recorder.power_states)
        for x in recorder.location_traffic_states[self._traffic_cursor:]:
            self.latest_traffic_by_location[x.location_id]=x
        self._traffic_cursor=len(recorder.location_traffic_states)
        for x in recorder.resource_states[self._resource_cursor:]:
            key=(getattr(x,"location_id",None),getattr(x,"resource_id",None))
            self.latest_resource_by_key[key]=x
        self._resource_cursor=len(recorder.resource_states)

__all__=["CurrentStateIndexV03"]
