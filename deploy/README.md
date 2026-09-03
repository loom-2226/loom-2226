# Deployment

`loom_update.py` installs and validates a pinned LOOM runtime baseline on Android or Windows while preserving runtime-local campaign state.

Current flow:

1. Fetch the release manifest from the selected Git ref.
2. Download repository-backed code and canonical data payloads.
3. Download large media payloads through the GitHub Release Asset API.
4. Verify exact byte size when pinned.
5. Verify SHA-256 before replacement.
6. Preserve mutable campaign state/history/cache/output.
7. Back up replaced canonical files by release ID.
8. Install atomically where practical.
9. Support `update`, `validate`, and `status` commands.
10. Fail closed on required-file, size, source, or hash errors.

Authentication is device-local. Use `LOOM_GITHUB_TOKEN` or `~/.loom_github_token`; never commit credentials.

Default install roots:

- Android: `/storage/emulated/0/Documents/LOOM`
- Windows: `~/Documents/LOOM`

`LOOM_HOME` or `--root` may override the root explicitly.
