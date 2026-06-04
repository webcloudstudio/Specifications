# CHANGE_LOG.md — Marina

Append-only change log. Format: DATE | TYPE | SCOPE | DESCRIPTION
Types: CHANGE (pending), AC (permanent guardrail), DONE (applied — written by process script).
Scope: route path (/route), base filename (DATABASE.md), or spec filename (SCREEN-FOO.md).

2026-06-03 | CHANGE | DATABASE.md | last_scan value stored in platform_stats must be a full ISO-8601 string with UTC offset (e.g. 2026-06-03T14:50:56+00:00) — truncating to HH:MM or stripping the offset causes offset-naive vs offset-aware TypeError in _relative_time
2026-06-03 | DONE | DATABASE.md | Applied: tightened last_scan description to require UTC offset, added format example and prohibition on truncation
