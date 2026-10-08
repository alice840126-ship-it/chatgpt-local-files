# Validation — 2026-10-09

This standalone package inherits the tested filesystem engine from AI Workspace Kit. It excludes memory, artifact indexing, checkpoints, publication, native chat history and live deployment configuration.

- macOS / Python 3.14.5 / MCP SDK 2.2.0.
- The 17 filesystem regression tests cover version conflicts, same-size/mtime edits, no-clobber, binary/UTF-8 reads, directory operations, bulk-delete confirmation binding, concurrent calls, macOS metadata, retained race bytes and failed journal completion.
- A fresh non-editable installation runs outside the checkout. The installed self-check starts a real stdio MCP subprocess and verifies exactly 14 file tools, create → edit → actual reread → stale-version rejection → recoverable delete → restore.
- The skill frontmatter is validated separately; independent review examines tool routing, stale conflict and human confirmation boundaries.
- Source and committed history are scanned for secrets before publication.

No new standalone-package ChatGPT registration, recipient OS permission grant, physical SSD test, login service or voice call is claimed. The original engine had live ChatGPT file operations; this establishes lineage, not a new user's connection success. Follow SETUP.md and test an actual chat on your own account.

The root plugin manifest packages the reusable skill. It does not bundle a working per-user tunnel connection: each recipient must register their own MCP. GitHub source publication is separate from public ChatGPT directory approval.
