# Deployment

Deployment tooling will install a pinned, verified LOOM release onto desktop or Android while preserving runtime-local campaign state.

Target flow:

1. Fetch an approved release manifest.
2. Download required code and canonical data payloads.
3. Verify SHA-256 before replacement.
4. Preserve mutable campaign state/history/cache/output.
5. Install atomically where practical.
6. Run compatibility/self-tests.
7. Refuse launch on a failed lock or required-file check.

The updater is intentionally not active until the initial baseline payload is complete and promoted.
