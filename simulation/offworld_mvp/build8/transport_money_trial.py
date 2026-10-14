"""Opt-in real-campaign prerequisite, generic seed-freight money demonstration.

Runs existing Route 1 Ceres source only to read its 90-body review receipts
and verify legacy pins. A separate frozen Kernel records actual transfers
for the dated seed-equipment projects. Original run remains unchanged.
"""
from __future__ import annotations

from hashlib import sha256
import json

from .ceres_downstream import run_ceres_downstream
from .transport_money_rows import AUTHORED_TRANSPORT_ROWS
from .transport_to_money import (ready_from_review, quote_and_choose,
                                  settle_money_chain, stable_bytes)
from .travel_pilot.on_demand import OnDemandTravel
from .travel_pilot.pilot import price_table


def run_transport_money_trial(*, rows=AUTHORED_TRANSPORT_ROWS, studies=None,
                              geometry_factory=OnDemandTravel, rates=None,
                              legacy_check=True, year_end=2226):
    if studies is None:
        source=run_ceres_downstream()
        studies=source["campaign"]["studies"]
        if legacy_check:
            assert len(source["kernel"].state.transactions)==8798
            assert len(source["campaign"]["receipts"])==249
            legacy_fingerprint=source["kernel"].fingerprint()
        else:
            legacy_fingerprint=None
    else:
        legacy_fingerprint=None
    rates = price_table()[0] if rates is None else rates
    results=[]
    for row in rows:
        ready=ready_from_review(row, studies)
        if ready is None:
            raise ValueError("PREREQUISITE_REVIEW_NOT_SATISFIED:"+row["requirement_id"])
        selected=quote_and_choose(row,ready,geometry=geometry_factory(),rates=rates)
        result=settle_money_chain(row,ready,selected,year_end=year_end)
        results.append(result)
    content=dict(classification="BUILD8_TEST_ONLY_GENERIC_DATED_TRANSPORT",
                 source="OBSERVED_ROUTE1_YEARLY_REVIEWS_YEAR_END_NOT_HISTORIC_DATE",
                 policy="CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED",
                 legacy_fingerprint=legacy_fingerprint,
                 requirements=list(rows),results=results)
    # No wall-clock timing in reproducible run output.
    content["fingerprint"]=sha256(stable_bytes(content)).hexdigest()
    return content
