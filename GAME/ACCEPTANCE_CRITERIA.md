# Acceptance Criteria

**Version:** 20260323 V1
**Build-ref:** oneshot/GAME/2026-03-22.1
**Purpose:** Testable MUST/MUST NOT statements discovered during prototype iteration.

> Format: Grouped by topic. Each group has a `**Target:**` line naming the spec file(s) it refines. Each criterion uses MUST/MUST NOT. When folded into the target spec, move to `## Folded` at the bottom.

---

## Documentation Serving
**Target:** FUNCTIONALITY.md (Flow 1), SCREEN-PROJECT.md

- Documentation MUST be served from a single `docs/` directory per project
- The master file is index.html.
- If documentation is produced in `doc/`, change the process to move it to `docs/`.
- Application documentation MUST resolve CSS and asset references that use relative paths within the `docs/` directory tree.
- Scanner MUST detect `docs/index.html` for the `has_docs` flag.

## Default Landing Screen
**Target:** SCREEN-PROJECTS-WELCOME.md, UI-GENERAL.md

- `GET /` MUST redirect to `/welcome` — Welcome is the default landing screen.
- The Welcome tab MUST be active (highlighted) when the application first loads.
- The top navigation brand link MUST navigate to `/welcome`, not `/`.

## Environment Setup
**Target:** ARCHITECTURE.md (Configuration section)

- Only `SECRET_KEY` and `PROJECTS_DIR` are required to start the application.
- `PROJECTS_DIR` SHOULD be set to the parent directory of the GAME project (e.g. `..` resolved to an absolute path).
- `APP_PORT` is NOT a valid env var — configuration reads `GAME_PORT`; port also defaults from `METADATA.md`.
- All other env vars (`DATABASE_PATH`, `GAME_PORT`, `FLASK_DEBUG`, `FLASK_ENV`) are optional with working defaults and MUST NOT be required for a first run.

## Script Conventions
**Target:** ARCHITECTURE.md, FUNCTIONALITY.md (Flow 2)

- bin/ shell scripts MUST NOT contain Windows line endings (CR+LF).
- Test suite SHOULD verify no `\r` exists in any `.sh` or `.py` file under `bin/`.

---

## Folded
<!-- Criteria that have been incorporated into their target spec files. Keep for history. -->

