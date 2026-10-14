"""Authored TEST_ONLY requirements. All project identities stay in DATA, not mechanics.

The 20-tonne CARGO_DELIVERY Build 7 cost anchor describes spacecraft tonnes,
NOT an independently qualified cargo payload or performance envelope. 10/10
endpoint caps are a user-authored simplification to revisit with technology.
Each review trigger comes from the observed Route 1 campaign, not an invented
January 1 ready date. Annual review completion is dated at UTC year end.
"""

AUTHORED_TRANSPORT_ROWS = (
    dict(
        requirement_id="SEED_FACTORY_CERES",
        project_id="SEED_FACTORY:CERES",
        sponsor="ISRO",
        origin="EARTH", destination="CERES",
        prerequisite=dict(body="CERES", stage="A2", review="ADVANCE",
                          result="SUPPORTS_ADVANCE"),
        ready_rule="ANNUAL_REVIEW_YEAR_END_UTC",
        wait_limit_days=730, flight_range_days=(45.0, 3000.0),
        vehicle=dict(service_type="CARGO_DELIVERY", spacecraft_tonnes=20,
                     max_departure_vinf_km_s=10.0, max_arrival_vinf_km_s=10.0,
                     standing="TEST_ONLY_AUTHORED_ENDPOINT_CAP_NOT_QUALIFIED_FREIGHT"),
        price_rule="BUILD7_2026_HELD_CARGO_DELIVERY_RATE",
        payment_rule="PAY_AT_DEPARTURE",
        delivery_rule="SCRIPTED_ON_ORBITAL_ARRIVAL",
        funding_mode="TEST_ONLY_TREASURY_FISCAL_APPROPRIATION",
        payer_account="treasury:IND",
        treasury_owner_type="public_agency",
        treasury_owner_id="STATE:IND",
        # Explicit TEST_ONLY unused 75% of IND mobilization after Route1's
        # 25% commitment. Derived from existing Earth inputs (not new money
        # assigned as an opening balance); values are upper bounds in MC.
        fiscal_source="UNALLOCATED_75_PERCENT_OF_ROUTE1_IND_MOBILIZATION_TEST_ONLY",
        fiscal_available_by_year=(
            (2038, "1.790823221450457975"),
            (2039, "1.887055144526041275"),
        ),
        original_project_funds="0.080",
        construction_cost="0.060", productive_capacity="5",
        financing_node="EARTH:IND",
        test_only=True,
    ),
    dict(
        requirement_id="SEED_FACTORY_MARS_ILLUSTRATIVE",
        project_id="SEED_FACTORY:MARS",
        sponsor="MARS_DEMO_SPONSOR",
        origin="EARTH", destination="MARS",
        prerequisite=dict(body="MARS", stage="A1", review="ADVANCE",
                          result="SUPPORTS_ADVANCE"),
        ready_rule="ANNUAL_REVIEW_YEAR_END_UTC",
        wait_limit_days=730, flight_range_days=(45.0, 3000.0),
        vehicle=dict(service_type="CARGO_DELIVERY", spacecraft_tonnes=20,
                     max_departure_vinf_km_s=10.0, max_arrival_vinf_km_s=10.0,
                     standing="TEST_ONLY_AUTHORED_ENDPOINT_CAP_NOT_QUALIFIED_FREIGHT"),
        price_rule="BUILD7_2026_HELD_CARGO_DELIVERY_RATE",
        payment_rule="PAY_AT_DEPARTURE",
        delivery_rule="SCRIPTED_ON_ORBITAL_ARRIVAL",
        funding_mode="TEST_ONLY_NO_TREASURY_FISCAL_ALLOCATION",
        payer_account="treasury:TEST",
        treasury_owner_type="public_agency",
        treasury_owner_id="STATE:TEST",
        fiscal_source="NONE",
        fiscal_available_by_year=(),
        original_project_funds="0.080",
        construction_cost="0.060", productive_capacity="5",
        financing_node="EARTH:TEST",
        test_only=True,
    ),
)
