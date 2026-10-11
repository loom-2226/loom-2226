"""Build 8 PI01: independent, authored executor quote/refusal experiment.

This is a deterministic non-canon simulation. It evaluates one BUILD request
for the existing Northrop Grumman roster entry and one LAND request for
Firefly Aerospace, a sourced research candidate. Costs, markup rates, whole-
year durations, and available capacity below are authored scenario inputs;
they are not vendor quotes, prices, schedules, or capacity claims.

Firefly candidate provenance: the local completed-mission reference
``engineering/civprop/civprop0/blue_ghost_1_reference.json`` records Firefly's
completed Blue Ghost Mission 1 delivery. That supports considering Firefly as
a research candidate only. It does not establish a general service offer,
capacity, schedule, price, or bundled launch service. PI01 explicitly authors
the LAND request as a launch-plus-lunar-landing bundle for this trial.

No award, payment, contract, or physical delivery is represented here.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional, Tuple

from .sponsor_executor_network_trial import EXECUTORS as EXISTING_EXECUTORS
from .master_cast import name as cast_name


@dataclass(frozen=True)
class WorkRequest:
    request_id: str
    category: str
    quantity: int


@dataclass(frozen=True)
class ExecutorInput:
    name: str
    category: str
    authored_cost: Decimal
    markup_rate: Decimal
    duration_years: int
    available_capacity: int
    basis: str


@dataclass(frozen=True)
class Evaluation:
    request_id: str
    category: str
    executor: str
    status: str
    reason: Optional[str]
    authored_cost: Decimal
    markup_rate: Decimal
    quoted_price: Optional[Decimal]
    duration_years: int
    requested_capacity: int
    available_capacity: int
    basis: str


REQUESTS = (
    WorkRequest("PI01-BUILD-001", "BUILD", 1),
    WorkRequest("PI01-LAND-001", "LAND", 1),
)

# Northrop Grumman is reused from the existing Build 8 EXECUTORS roster. The
# Firefly entry is a sourced research candidate; its service and every number
# here remain authored assumptions. Decimal values are model currency units.
EXECUTORS = (
    ExecutorInput(
        name=cast_name("Northrop Grumman", "executor", "BUILD"),
        category="BUILD",
        authored_cost=Decimal("2.00"),
        markup_rate=Decimal("0.25"),
        duration_years=2,
        available_capacity=1,
        basis="Existing Build 8 EXECUTORS roster; authored BUILD scenario inputs",
    ),
    ExecutorInput(
        name=cast_name("Firefly Aerospace", "executor", "LAND"),
        category="LAND",
        authored_cost=Decimal("3.00"),
        markup_rate=Decimal("0.20"),
        duration_years=2,
        available_capacity=1,
        basis=(
            "Research candidate: completed Blue Ghost Mission 1 reference; "
            "launch-plus-LAND bundle, cost, markup, duration, and capacity "
            "are explicit PI01 assumptions"
        ),
    ),
)


def evaluate_quotes(
    requests: Iterable[WorkRequest] = REQUESTS,
    executors: Iterable[ExecutorInput] = EXECUTORS,
) -> Tuple[Evaluation, ...]:
    """Return sorted independent offers/refusals without mutating any state.

    Each request category must appear exactly once and have one matching
    executor input. Capacity is checked per request and is not consumed across
    categories. A quote is authored_cost * (1 + markup_rate).
    """
    request_rows = tuple(requests)
    executor_rows = tuple(executors)
    categories = {"BUILD", "LAND"}

    if len(request_rows) != 2 or {row.category for row in request_rows} != categories:
        raise ValueError("PI01 requires exactly one BUILD and one LAND request")
    if len({row.request_id for row in request_rows}) != len(request_rows):
        raise ValueError("request IDs must be unique")
    if any(not row.request_id or row.quantity <= 0 for row in request_rows):
        raise ValueError("requests require an ID and positive integer quantity")
    if len(executor_rows) != 2 or {row.category for row in executor_rows} != categories:
        raise ValueError("PI01 requires one executor input for each request category")
    if any(
        row.authored_cost < 0
        or row.markup_rate < 0
        or row.duration_years <= 0
        or row.available_capacity < 0
        for row in executor_rows
    ):
        raise ValueError("executor costs/markup/capacity must be nonnegative and duration positive")

    executor_by_category = {row.category: row for row in executor_rows}
    results = []
    for request in sorted(request_rows, key=lambda row: (row.category, row.request_id)):
        executor = executor_by_category[request.category]
        if (
            executor.name == "Northrop Grumman"
            and request.category not in EXISTING_EXECUTORS[executor.name][1]
        ):
            raise ValueError("Northrop Grumman request category is absent from the existing roster")
        offered = executor.available_capacity >= request.quantity
        results.append(
            Evaluation(
                request_id=request.request_id,
                category=request.category,
                executor=executor.name,
                status="OFFER" if offered else "REFUSAL",
                reason=None if offered else "INSUFFICIENT_AUTHORED_CAPACITY",
                authored_cost=executor.authored_cost,
                markup_rate=executor.markup_rate,
                quoted_price=(
                    executor.authored_cost * (Decimal(1) + executor.markup_rate)
                    if offered
                    else None
                ),
                duration_years=executor.duration_years,
                requested_capacity=request.quantity,
                available_capacity=executor.available_capacity,
                basis=executor.basis,
            )
        )
    return tuple(results)


if __name__ == "__main__":
    for row in evaluate_quotes():
        print(
            f"{row.request_id} {row.category} {row.status} executor={row.executor} "
            f"price={row.quoted_price} duration_years={row.duration_years} "
            f"capacity={row.requested_capacity}/{row.available_capacity} "
            f"reason={row.reason}"
        )
