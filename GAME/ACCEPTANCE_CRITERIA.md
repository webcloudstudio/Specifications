# Acceptance Criteria

**Version:** 20260323 V1
**Build-ref:** oneshot/GAME/2026-03-22.1
**Purpose:** Testable MUST/MUST NOT statements discovered during prototype iteration.

> Format: Grouped by topic. Each group has a `**Target:**` line naming the spec file(s) it refines. Each criterion uses MUST/MUST NOT. When folded into the target spec, move to `## Folded` at the bottom.

---

## Documentation Serving
**Target:** FUNCTIONALITY.md (Flow 1), SCREEN-PROJECT.md

- Documentation MUST be served from a single `docs/` directory per project. There is no `doc/` directory — all documentation lives in `docs/`.
- Doc route MUST resolve CSS and asset references that use relative paths within the `docs/` directory tree.
- Scanner MUST detect `docs/index.html` for the `has_docs` flag.

## Script Conventions
**Target:** ARCHITECTURE.md, FUNCTIONALITY.md (Flow 2)

- bin/ shell scripts MUST NOT contain Windows line endings (CR+LF).
- bin/ scripts MUST use Unix line endings (LF only).
- Test suite SHOULD verify no `\r` exists in any `.sh` or `.py` file under `bin/`.

---

## Folded
<!-- Criteria that have been incorporated into their target spec files. Keep for history. -->

