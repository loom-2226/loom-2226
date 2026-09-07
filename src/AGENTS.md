# Runtime source agent rules

Applies to `src/**`.

## Authority

Runtime implements governing canon/engineering/data contracts. Executable behavior does not become canon merely because it runs.

Before substantive mutation:

- load current workstate and relevant engineering/canon authority;
- declare runtime change class and downstream compatibility impact;
- identify schema/data/launcher/release dependencies;
- preserve current Pixel/Windows behavior unless the approved work item explicitly changes it.

## Architecture discipline

- avoid hard-coded runtime payload field names and timeline/mode codes across consumers;
- prefer canonical typed/validated schemas with adapters/accessors;
- avoid whack-a-mole consumer patches when a shared contract should be changed;
- distinguish authoritative source data from derived display/cache state.

## Tests

- any new Python release requires unit regression before release;
- substantive functional change requires unit + relevant functional tests;
- full end-to-end regression is reserved for production finalization unless a risk-specific work item requires earlier E2E.

## Canon/engineering conflict

If implementation exposes an inconsistency, raise an engineering/canon finding. Do not silently change governing assumptions from runtime code.

## Adoption pause

While current workstate says Governance Adoption is active, functional runtime changes are forbidden.