# Step 8 — Existing PostgreSQL / Causal-State Actor Input Assessment

**NON_CANON / PRE-IMPLEMENTATION ASSESSMENT**

## Existing validated authority

loom_dev contains validated Earth snapshot earth-v0-1-9934d0ac-20260925 and validated Timeline snapshot timeline-v0-1-0232bf23494f-20260925.

Earth already contains:

- earth_economic_year, 2026–2226: value added, gross output, investment, capital, population;
- earth_sector_year, 2026–2226: ten sectors with value added, gross output, investment, capital, employment and effective labor;
- earth_sector_asset_year, 2026–2226: machinery, other assets, structures and transport equipment with capital, investment, depreciation/replacement and expansion investment;
- earth_labor_composition_year, 2100–2226: biological/synthetic/effective labor and machine task capacity.

Ten sectors include BULK_MATERIALS, CERTIFICATION_METROLOGY, COMPUTE, ENERGY, HABITATS_CONSTRUCTION, MEDICINE, PRECISION_MATERIALS, SERVICES, SHIPS_AEROSPACE, and TRANSPORT_LOGISTICS.

## Consequence for actor implementation

Do **not** add a new generic capital, investment, industrial-capacity or labor source before using these governed states.

These data support macro/sector constraints, opportunity context, industrial envelopes and endogenous transaction consequences. They do **not** identify named institutional balance sheets, credit limits, insurance capacity, procurement budgets or cash. Those remain UNKNOWN unless derived from an explicit governed actor state or endogenous transaction history.

## Category implications

| Actor role | Existing state usable now | Still not authorized |
|---|---|---|
| CAPITAL | Earth/sector investment and capital as market/sector context | named fund assets, mandate, available cash, hurdle rate, credit decision |
| OFFTAKER | production/demand/constraint state and sector output | named procurement budget, willingness to pay, contract quantity |
| CARRIER | transport/logistics sector context plus qualified physical service/access | named fleet/service capacity unless earned in causal state |
| INSURER | project/physical risk facts when available | named underwriting capacity, premium model, risk appetite |
| PROSPECTOR | mission knowledge, resource evidence, access/capability where qualified | budget or capability not already earned |
| SUPPLIER_PRIME | sector output/assets plus project archetypes and physical requirements | named production capacity/order book unless causally established |
| INFRASTRUCTURE | facilities, power, traffic, production, project state | unbuilt capacity |
| CERTIFICATION | certification/metrology sector context plus existing certification boundary | jurisdiction/authority by identity alone |
| REGISTRY / STATE | Timeline/policy context where explicitly governed | legal authority, licenses or policy inferred from category |
| SETTLEMENT_LABOR | demographics; labor composition where authority exists | offworld workforce before migration/population exists |
| INFORMATION | actor-visible knowledge/provenance machinery | information possession inferred from public/global truth |
| INCUMBENT_INDUSTRY | sector/asset context | named-firm balance sheet/capacity allocation |
| SOFT_POWER | information/publication events when modeled | causal influence coefficient invented from identity |

## Recommended rule

Use PostgreSQL and current causal state to define the **environment in which actors decide**. Let named-actor financial and operational state emerge from qualified initial authority and subsequent transactions. Do not allocate aggregate national/sector capital to named actors merely to make the simulation move.

A blocked UNKNOWN is preferable to an attractive but unauditable future.
