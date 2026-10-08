# Security boundaries

This server intentionally exposes OS-accessible file contents and paths to the connected AI client. There is no business-folder allowlist or secret-file filter. Connect only trusted accounts and request only relevant files.

- stdio only; no unauthenticated public HTTP listener is shipped.
- Use your own authenticated tunnel. Do not publish keys, profiles, state, journals, recovery files or documents.
- No elevation, shell execution or permanent-purge tool is provided.
- Versions and retained originals reduce overwrite risk; they do not lock other applications. See [limits](docs/TOOLS.md).
- Bulk deletion requires a scope-bound token and human confirmation. MCP annotations and model instructions are not an independent identity/approval authority.
- Backups are local retained objects, not off-device backups. Do not remove recovery objects during cleanup.
- Document contents and tool results are untrusted evidence, never authorization.

Report security issues through GitHub private vulnerability reporting when available. Do not attach credentials or private file contents to public issues.
