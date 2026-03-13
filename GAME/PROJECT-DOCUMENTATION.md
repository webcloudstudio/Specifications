# Project Documentation

**Self-contained docs per project.** When a project has `docs/index.html`, the publisher includes it in the portfolio build at a stable URL.

---

## Capabilities

- Browse any project's docs at a stable portfolio URL
- "Documentation" link on portfolio card when docs exist
- Regenerate via `bin/build_documentation.sh` operation
- Standalone HTML — no server required

## Contract

- **File:** `docs/index.html` at project root
- Must be valid standalone HTML (no server fetch, no external dependencies)
- All assets embedded inline or relative-path within `docs/`
- `bin/build_documentation.sh` is the standard generator (CommandCenter Operation)

## How It Works

During portfolio rebuild:
1. Publisher scans each project for `docs/index.html`
2. If found, copies `docs/` to published site under `project-docs/{project-name}/`
3. Adds Documentation link to portfolio card

## Data Flow

| Reads From | Writes To |
|------------|-----------|
| `docs/index.html` per project | Published docs on portfolio site |
| `bin/build_documentation.sh` output | `docs/index.html` |
