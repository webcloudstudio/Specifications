# Patch: 001 — Fix documentation path from doc/ to docs/
**Type:** patch
**Scope:** Scanner (has_docs detection), Portfolio builder, Flask doc proxy, ARCHITECTURE.md references

## Intent
The documentation directory was renamed from `doc/` to `docs/`. All prototype code that checks for or references `doc/index.html` must be updated to `docs/index.html`. The Flask proxy route pattern itself is unchanged — only the detection and link-generation logic changes.

## Changes Required
- Scanner `has_docs` flag: check for `docs/index.html` not `doc/index.html`
- Portfolio builder: check `docs/index.html` when generating documentation link on cards
- Any other code referencing `doc/index.html` as a path to detect or serve

## Open Questions
None.
