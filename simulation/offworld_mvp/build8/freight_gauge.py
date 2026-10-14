"""Read-only Earth-side Offworld freight payment gauge (Build 8 only).

An Earth-to-Earth TRANSPORT_PAYMENT is not an Offworld capital transfer.
This derives a parallel display line from actual frozen-kernel transactions.
"""
from __future__ import annotations

from decimal import Decimal

from offworld_kernel.model import NodeKind, TxPurpose

LINE = "earth_side_transport_spending_for_offworld_projects"


def eligible_transport_payments(state):
    """Count a transaction once if its explicit order links an Offworld project.

    Return real immutable transaction rows, not treasury appropriations,
    quotes, duplicated PAYMENT events, or implied spending from cargo status.
    """
    offworld_projects = {
        project_id for project_id, project in state.projects.items()
        if state.nodes[project.node_id].kind == NodeKind.OFFWORLD
    }
    links = offworld_projects | {
        project_id + ":transport_order" for project_id in offworld_projects
    }
    return tuple(
        tx for tx in state.transactions
        if tx.purpose == TxPurpose.TRANSPORT_PAYMENT
        and state.nodes[tx.source_location].kind == NodeKind.EARTH
        and state.nodes[tx.destination_location].kind == NodeKind.EARTH
        and any(parent in links for parent in tx.parent_ids)
    )


def with_earth_side_freight_line(state, annual_rows):
    """One additional visible line on each annual gauge row, including zeros.

    Original annual results and their established fingerprints remain
    unchanged. This is a derived presentation of immutable ledger transfers.
    """
    per_year = {}
    for tx in eligible_transport_payments(state):
        per_year[tx.year] = per_year.get(tx.year, Decimal("0")) + tx.amount
    return [
        {**row, LINE: str(per_year.get(row["year"], Decimal("0")))}
        for row in annual_rows
    ]
