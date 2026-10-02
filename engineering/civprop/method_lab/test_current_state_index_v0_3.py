import unittest
from types import SimpleNamespace
from engineering.civprop.method_lab.current_state_index_v0_3 import CurrentStateIndexV03

class CurrentStateIndexTests(unittest.TestCase):
    def test_incremental_facility_index_and_year_filter(self):
        i=CurrentStateIndexV03()
        rows=[SimpleNamespace(location_id="A",facility_id="F1",status="ACTIVE",commissioned_year=2027),
              SimpleNamespace(location_id="B",facility_id="F2",status="ACTIVE",commissioned_year=2030)]
        i.sync_facilities(rows,year=2028)
        self.assertEqual([x.facility_id for x in i.active_facilities()],["F1"])
        rows.append(SimpleNamespace(location_id="A",facility_id="F3",status="ACTIVE",commissioned_year=2029))
        i.sync_facilities(rows,year=2030)
        self.assertEqual([x.facility_id for x in i.active_facilities()],["F1","F3","F2"])

    def test_latest_state_indexes(self):
        i=CurrentStateIndexV03()
        r=SimpleNamespace(power_states=[SimpleNamespace(location_id="A",year=1)],
            location_traffic_states=[SimpleNamespace(location_id="A",year=1)],
            resource_states=[SimpleNamespace(location_id="A",resource_id="W",year=1)])
        i.sync_physical_states(r)
        r.power_states.append(SimpleNamespace(location_id="A",year=2))
        i.sync_physical_states(r)
        self.assertEqual(i.latest_power_by_location["A"].year,2)
        self.assertEqual(i.latest_resource_by_key[("A","W")].year,1)

if __name__=="__main__": unittest.main()
