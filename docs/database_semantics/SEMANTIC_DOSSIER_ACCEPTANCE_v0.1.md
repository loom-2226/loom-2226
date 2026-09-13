# Semantic Dossier Acceptance v0.1

## Coverage result

- CIVSTATE tables in verified runtime inventory: **53 / 53 represented**.
- Core-world tables in verified runtime inventory: **42 / 42 represented**.
- Total: **95 / 95 represented**.
- Initiating work order stated 43 core tables; preserved runtime inventory lists 42. This discrepancy remains open for later-schema verification and is not repaired by invention.

## Semantic result

**TABLE COVERAGE: PASS**  
**COMPLETE SEMANTIC UNDERSTANDING: NOT YET CLAIMED**

The acceptance rule deliberately permits `NOT_UNDERSTOOD`. Therefore an unresolved table is not a coverage failure if it is present and explicitly blocked from inferred use. It remains a semantic-recovery work item.

## No-change verification

This branch changes documentation only. It does not modify SQLite bytes, schemas, values, runtime behavior, canon, engineering parameters, or release payloads.

## Promotion rule

Do not describe this as a complete dictionary in the sense of 'every field understood' until the unresolved core/CIVSTATE field contracts have been recovered from builders/migrations/methodology/authoritative consumers. It is complete as a **coverage and anti-invention contract** for the verified table inventory.
