# Specification Scorecard: GAME

**Generated:** 2026-03-26
**Status:** PROTOTYPE

## Dimension Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Completeness | 7/10 | All core screens and flows are specified; CLI gateway, has_tests/has_specs schema, and 3 screen specifications remain unwritten. |
| Buildability | 8/10 | ARCHITECTURE.md names every module with entry points, DATABASE.md has full schemas, and FUNCTIONALITY.md has 13 concrete flows — an agent could build the core platform without guessing. |
| Internal Consistency | 7/10 | DATABASE.md defers healthcheck table schemas to FEATURE-HEALTHCHECK.md while claiming to be the authoritative source; `tickets` table is superseded but retained; tag_colors.json migration path is informal. |
| Architecture Clarity | 9/10 | All five backend modules are documented with signatures and threading model; routes table is complete and current; directory layout and configuration variables are fully specified. |
| Screen Coverage | 7/10 | 15 screen specifications cover all navigable surfaces; SCREEN-PROTOTYPES-DETAIL, SCREEN-SETTINGS-LOGFILTER, and SCREEN-SETTINGS-WORKFLOWS are missing despite being referenced or implied by existing screens. |
| Rules Alignment | 8/10 | METADATA.md, AGENTS.md, and directory layout conform to PROTOTYPE-level rules; `docs/` is used correctly; no tests/ or bin/test.sh yet, which is only required at ACTIVE. |
| Open Questions Hygiene | 8/10 | Open Questions sections are substantive and actionable (ARCHITECTURE.md resolves one inline; DATABASE.md lists five concrete deferred decisions), with no empty placeholder sections found. |
| **Overall** | **7.7/10** | Weighted average — strong core, specification gaps concentrated in secondary screens and the CLI gateway. |

## Gap Summary

| Priority | Open | Closed | Total |
|----------|------|--------|-------|
| P0 | 2 | 3 | 5 |
| P1 | 2 | 8 | 10 |
| P2 | 4 | 1 | 5 |
| P3+ | 26 | 5 | 31 |

## Priority Actions

1. **[P0] CLI/Bash Gateway** — write `FEATURE-CLI-GATEWAY.md` specifying `bin/game-cli.sh` commands (catalog, run, health, status, log) so the platform is usable headlessly from other project scripts.
2. **[P1] has_tests / has_specs schema** — add `has_tests` and `has_specs` columns to the `projects` table in DATABASE.md and the Field Source Mapping table; they are referenced by SCREEN-PROJECTS-VALIDATION.md but have no schema definition.
3. **[P2] Log filter rule editor** — write `SCREEN-SETTINGS-LOGFILTER.md` for the `log_filter` table UI; without it, operators must edit classification rules directly in SQLite, making production log tuning impractical.
4. **[P2] Prototype detail view** — write `SCREEN-PROTOTYPES-DETAIL.md` for `GET /prototypes/{name}`; the route is referenced in SCREEN-PROTOTYPES-LIST.md and ARCHITECTURE.md but the screen itself is unspecified.
5. **[P2] AI agent submission mechanism** — resolve how READY tickets are handed off to an AI agent (queue, webhook, or direct Claude API call) and write either a concrete flow in FUNCTIONALITY.md or a new `FEATURE-AI-SUBMISSION.md`.

## What This Specification Does Well

- **Architecture depth:** Every backend module (`scanner.py`, `ops.py`, `spawn.py`, `publisher.py`, `monitoring.py`, `scheduler.py`) is named, described, and given a function signature — unusually complete for a PROTOTYPE specification.
- **Route completeness:** The routes table covers 30+ endpoints with method, path, return type, and trigger, giving an agent a full map of the HTTP surface without reading any code.
- **Database schema rigour:** All production tables have column-level definitions with types, defaults, and source attribution; the field source mapping table removes ambiguity about where every DB column originates.
- **UI standards:** `UI-GENERAL.md` defines a consistent design language (dark theme, HTMX conventions, badge styles, filter bar patterns) that lets any screen specification stay concise by cross-referencing rather than repeating layout rules.

## Regenerate

```bash
bash bin/spec_iterate.sh GAME
```
