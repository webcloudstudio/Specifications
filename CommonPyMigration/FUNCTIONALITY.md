# FUNCTIONALITY: Common.py Migration

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | High-level feature index — one paragraph per feature. |

## Feature Index

**STEP.1 — Parity Audit**
Compare `bin/common.py` and `bin/common.sh` behavior-by-behavior. Document every capability in common.sh and verify it exists in common.py with identical behavior. The audit output is a gate: the migration cannot proceed until parity is confirmed or gaps are resolved.

**STEP.2 — Fallback Shell Template**
Update `RulesEngine/templates/common.sh` to add a Python availability check at the top. When Python 3 is present, the script sets a mode flag and defers complex logic to `common.py`. When Python is absent, all existing behavior runs as before. This is the new canonical `common.sh` template for all projects.

**STEP.3 — Migration Script v1.01.sh**
Create `UpdateScripts/v1.01.sh` — a migration runner that loops through the `projects/` directory, identifies projects that own the restricted list of common scripts, replaces `bin/common.sh` with the new template, and reports conformance. The restricted list includes `common.sh`, `start.sh`, `stop.sh`, `test.sh`, and scripts carrying the CommandCenter header.

**STEP.4 — ProjectValidate.sh Updates**
Add `--summary` mode to `ProjectValidate.sh` that displays a color-coded conformance report across all standard scripts. Categories: uses common.sh, Python availability handling, complexity score (should convert to Python), ease to convert to `.bat`. The summary should be metrics-first with visual indicators (color, counts).

## Open Questions

- None at this level; see individual FEATURE-STEP files.
