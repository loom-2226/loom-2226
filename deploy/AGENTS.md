# Deployment subtree agent rules

Applies to `deploy/**`.

## Stability priority

Deployment changes can break working Pixel/Windows installations even when source code is otherwise correct. Treat launch/update paths as compatibility contracts.

Before mutation:

- load current compatibility/release metadata;
- identify Pixel and Windows impact separately;
- preserve local campaign/user state where policy requires it;
- identify rollback/recovery point;
- verify release asset hashes/source refs;
- check whether a vendor/external service is being introduced.

## Prohibitions

- do not move/rename launcher or updater roots for repository tidiness alone;
- do not assume Pixel and Windows paths/interpreters are interchangeable;
- do not overwrite local state that release policy marks preserve-local;
- do not silently change release asset/source semantics.

## Tests

Substantive deployment changes require platform-relevant functional validation plus normal code test policy. Production promotion requires the designated end-to-end release check.

## WALTER

`WALTER.VENDOR` and `WALTER.RELEASE` are especially relevant here: cost/licensing/lock-in, provider dependence, hashes, compatibility and recovery should be inspected before promotion.

## Adoption pause

Current launcher/updater behavior and paths are frozen during Governance Adoption.