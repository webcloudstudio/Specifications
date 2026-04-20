# Feature: Health Check & Event Ingestor

**Version:** 20260323 V1
**Description:** Service endpoint polling, per-project heartbeat API, and incremental log-event ingestion

Three capabilities unified under one feature:

1. **Service Health Poller** — periodic HTTP/TCP checks against catalog endpoints; updates `heartbeats` rows.
2. **Heartbeat API** — `common.py` / `common.sh` helpers that any project script can call to record operational state.
3. **Log Event Ingestor** — incremental scan of project log files; classifies lines as start/stop/error/junk; writes to `events`.

---

## Trigger

| Capability | Trigger |
|---|---|
| Service Health Poller | Scheduler fires every `health_check_interval` seconds per project; also on `POST /api/health/poll` |
| Heartbeat API | Called explicitly by project scripts via `common.py` or `common.sh` |
| Log Ingestor | Scheduler fires every 60 seconds; also on `POST /api/logs/ingest` |
| Provides    | POST /api/health/poll, POST /api/logs/ingest |
| Version     | 20260419 V1 |
| Description |  |

---

## Service Health Poller

For each project with a known port or `health_endpoint`:

1. Determine check type from `health_check_type`: `http` (default), `tcp`, or `none`.
2. Perform check with 5-second timeout.
   - `http`: HTTP GET `http://localhost:{port}{health_endpoint}`. State = `UP` (2xx), `DEGRADED` (non-2xx), `DOWN` (timeout / connection refused).
   - `tcp`: TCP connect to `localhost:{port}`. State = `UP` or `DOWN`.
3. Upsert one row in `heartbeats` where `heartbeat_type = service_health`: set `current_state`, `last_checked`, `response_ms`.
4. Append one row to `health_check_log` (raw history, 24h retention).
5. On state change (UP↔DOWN or UP↔DEGRADED): append one row to `events`.
   - DOWN or DEGRADED → `event_type = alert_fired`
   - Recovered to UP → `event_type = state_transition`
6. Recompute `uptime_pct` from the 24h window in `health_check_log`; write back to `heartbeats`.

Projects with `desired_state = on-demand` are checked only if they have an explicit `health_check_type` set (not defaulting to http). Projects without a port and without a `health_check_type` override default to `none`.

### Service Catalog extension

Add to `projects` (scanned from `METADATA.md`, writable from catalog UI):

| Column | Type | Default | Description |
|---|---|---|---|
| `health_check_type` | TEXT | `http` | `http` / `tcp` / `none` |
| `health_check_interval` | INTEGER | 60 | Seconds between polls |

`METADATA.md` keys: `health_check_type:`, `health_check_interval:`. Existing `health_endpoint` and `port` columns are used as-is.

---

## Heartbeat API

Projects call these from `bin/` scripts to record operational state. GAME must be reachable on `localhost:$GAME_PORT`.

### common.py additions

```python
def heartbeat(program, system, state, message="", subsystem=None):
    """
    Record script heartbeat to GAME.
    state: OK | WARNING | ERROR | CRITICAL
    Never raises — silently skips if GAME unreachable.
    """

def log_event(program, system, severity, message, subsystem=None):
    """
    Append a script event to GAME.
    severity: INFORMATION | WARNING | ERROR | CRITICAL
    Never raises — silently skips if GAME unreachable.
    """
```

Port resolution: reads `$GAME_PORT` env var, then `~/.game_port`, then defaults to 5000.

### common.sh additions

```bash
heartbeat <program> <system> <state> [message]
# state: OK WARNING ERROR CRITICAL

log_event <program> <system> <severity> [message]
# severity: INFORMATION WARNING ERROR CRITICAL
```

Same port resolution as Python. Both functions are no-ops (exit 0) if GAME is unreachable.

### New API endpoints

| Method | Path | Body | Action |
|---|---|---|---|
| POST | `/api/heartbeat` | `{program, system, subsystem?, state, message?}` | Upsert `heartbeats`; append to `events` on state change |
| POST | `/api/events` | `{program, system, subsystem?, severity, message}` | Append `events` row |

Always returns 200. No error propagation back to the calling script.

### Heartbeat upsert semantics

- One `heartbeats` row per `(project_id, heartbeat_type)` where `heartbeat_type = 'script:' + program`.
- Every call: update `current_state`, `last_checked`.
- State change: append `events` row with `event_type = state_transition`.
- Dedup: if state unchanged and `last_checked` < 60 seconds ago, skip the `events` write.
- Project lookup: match `program` to `projects.name` (exact, case-insensitive). If no match, store with `project_id = NULL`.

---

## Log Event Ingestor

Incrementally scans log files for all active projects. Runs on a 60-second schedule.

### Log discovery

For each active project: scan `{project.path}/data/logs/*.log`. Tracks read position per file in `log_positions`. Only reads new bytes since last recorded offset. On file truncation (current size < stored `file_size`), reset offset to 0.

### Classification

Lines are matched against `log_filter` rules in `sort_order` order; first match wins.

Default seed rules:

| Pattern (case-insensitive) | Classification | Event type written |
|---|---|---|
| `start(ed\|ing)\|listen(ing)? on port\|server up` | `start` | `state_transition` |
| `stop(ped\|ping)\|shutdown\|exit(ing)?\|terminated` | `stop` | `state_transition` |
| `CRITICAL\|FATAL\|EXCEPTION\|Traceback` | `critical` | `alert_fired` |
| `\bERROR\b` | `error` | `alert_fired` |
| `\bWARN(ING)?\b` | `warning` | `alert_fired` |
| *(anything else)* | `junk` | *(skip — not stored)* |

Lines classified as `junk` are discarded. All other classifications produce one `events` row with `source = 'log_ingestor'` and the log line in `summary`.

### Condensing

Consecutive identical `(project_id, classification, message_text)` tuples within a single ingest pass increment a repeat counter in the last inserted `events.detail` JSON rather than inserting duplicate rows. Mirrors gem's `MlpEvent -condense` behavior.

---

## New Tables

### health_check_log

Raw poll history. Rows older than 24 hours are deleted on each ingest pass.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | |
| project_id | INTEGER FK | References projects.id |
| checked_at | TEXT | Timestamp (yyyymmdd_hhmmss) |
| state | TEXT | UP / DEGRADED / DOWN |
| response_ms | INTEGER | NULL for TCP and failed checks |
| check_type | TEXT | http / tcp |

### log_positions

Ingestion cursor per file.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | |
| project_id | INTEGER FK | References projects.id |
| log_path | TEXT | Absolute path to log file |
| file_size | INTEGER | Last known size; truncation detected when current < this |
| byte_offset | INTEGER | Next byte to read |
| last_ingested | TEXT | Timestamp of last pass |

### log_filter

Classification rules. Editable; seeded with defaults on first startup.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | |
| pattern | TEXT | Regex (Python re syntax) |
| classification | TEXT | `start` / `stop` / `critical` / `error` / `warning` / `junk` |
| program | TEXT | NULL = applies to all programs |
| sort_order | INTEGER | Lower = matched first |
| is_active | INTEGER | 1 = enabled |

---

## Reads / Writes

| Reads | Writes |
|---|---|
| `projects` (port, health_endpoint, health_check_type, health_check_interval, desired_state) | `heartbeats` (upsert on each poll / heartbeat API call) |
| `heartbeats` (previous state for change detection) | `events` (on state change, error classification) |
| `log_positions` (byte offset per file) | `log_positions` (updated after each ingest pass) |
| `log_filter` (classification rules) | `health_check_log` (one row per poll; 24h retained) |
| Log files (incremental via byte offset) | `projects.health_check_type`, `health_check_interval` (on scan) |
| `health_check_log` (uptime computation) | |

---

## New Routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/heartbeat` | Record script heartbeat |
| POST | `/api/events` | Record script event |
| POST | `/api/health/poll` | Trigger immediate health poll (all projects) |
| GET | `/api/health/{name}` | Current health status for one project |
| POST | `/api/logs/ingest` | Trigger immediate log ingest pass |

---

## Open Questions

- Should `log_filter` rules be editable from a UI screen or config file only?
- Should TCP and HTTP checks run in parallel (asyncio) or sequentially?
- Should the heartbeat API accept a `heartbeat_minutes` parameter (like gem's `-heartbeat` flag) to auto-suppress re-alarming for N minutes?
- Should `health_check_log` retention be configurable, or is 24h fixed?
