# Functionality: End-to-End Flows

**Version:** 20260320 V1
**Description:** Core functionality specification

**How things actually work, step by step.** This document bridges FEATURE_MAP (what exists) and ARCHITECTURE (how code is organized) by describing the major workflows from trigger to completion.

Each flow shows: what triggers it, what happens in sequence, what gets read, what gets written, and what the user sees.

---

## 1. Project Scan

**Trigger:** Platform startup (first request), or user clicks Rescan button.

```
User clicks Rescan (or first page load)
  |
  v
POST /api/scan
  |
  v
Scanner reads $PROJECTS_DIR
  |
  +---> For each directory:
  |       |
  |       +---> Read METADATA.md --> parse key:value fields
  |       |       name, display_name, status, stack, port, version, tags, ...
  |       |
  |       +---> Read AGENTS.md --> extract sections
  |       |       ## Bookmarks --> quick links
  |       |       ## Service Endpoints --> service URLs
  |       |       ## Dev Commands --> context (not stored, displayed on demand)
  |       |
  |       +---> Read bin/ scripts --> parse first 20 lines for headers
  |       |       # CommandCenter Operation --> register operation
  |       |       # Category: --> operation category
  |       |       # Schedule: --> cron expression
  |       |       # Port: / # Health: / # Timeout: --> operation metadata
  |       |
  |       +---> Check filesystem flags
  |       |       .git/ --> has_git, then: git status, git log, git rev-list
  |       |       venv/ --> has_venv
  |       |       package.json --> has_node
  |       |       CLAUDE.md --> has_claude
  |       |       tests/ or bin/test.sh --> has_tests
  |       |       doc/index.html --> has_docs
  |       |       Specifications/{name}/ --> has_specs
  |       |
  |       +---> Upsert into `projects` table
  |       +---> Replace rows in `operations` table for this project
  |
  +---> Mark projects not found on disk as is_active = false
  |
  v
Dashboard refreshes with updated project list
```

**Reads:** Filesystem ($PROJECTS_DIR), METADATA.md, AGENTS.md, bin/ scripts, .git/
**Writes:** `projects` table, `operations` table
**Event emitted:** `scan_completed`

**Key behaviors:**
- Non-blocking on startup — first page load returns immediately, scan runs async
- Missing files produce compliance gaps, not errors — a project with only METADATA.md still appears
- Projects removed from disk are marked `is_active = false`, not deleted
- Git operations (status, log) run per-project — can be slow with many repos

---

## 2. Run Operation

**Trigger:** User clicks an operation button on the dashboard or project detail.

```
User clicks operation button (e.g., "Start Server")
  |
  v
POST /api/run/{op_id}
  |
  v
Load operation record from DB
  |  --> script_path, cwd, needs_venv, category
  |
  v
Create op_runs record
  |  status = STARTING
  |  log_path = logs/{project}_{script}_{yyyymmdd_hhmmss}.log
  |
  v
Fork subprocess
  |  cd to project directory
  |  Activate venv if needs_venv
  |  Execute: bash bin/{script}.sh (or python bin/{script}.py)
  |  Redirect stdout+stderr to log_path
  |
  v
Update op_runs: status = RUNNING, pid = process.pid
  |
  v
Dashboard button changes to running state (green pulse)
Nav bar shows running badge for this project
  |
  v
Background: monitor subprocess
  |
  +---> Parse log output for [$PROJECT_NAME] status lines
  |       [$PROJECT_NAME] Starting: ... --> STARTING
  |       [$PROJECT_NAME] Running: ...  --> RUNNING
  |       [$PROJECT_NAME] Error: ...    --> flag
  |
  +---> On process exit:
          |
          +---> exit_code = 0 --> status = DONE
          +---> exit_code != 0 --> status = ERROR
          |
          v
        Update op_runs: finished_at, exit_code, status
        Remove running badge from nav
```

**Reads:** `operations` table, project path
**Writes:** `op_runs` table, log file
**Events emitted:** `operation_started`, then `operation_completed` or `operation_failed`

**Key behaviors:**
- Process runs in a process group (enables clean SIGTERM of child processes)
- Log file is append-only, named for sorting by project then time
- common.sh/common.py in the script handles venv, PORT, env loading, SIGTERM trap
- The platform does NOT parse or understand what the script does — it just runs it and watches exit codes

---

## 3. Stop Operation

**Trigger:** User clicks Stop on a running operation.

```
User clicks Stop button
  |
  v
POST /api/stop/{run_id}
  |
  v
Load op_runs record --> get pid
  |
  v
Send SIGTERM to process group (-pid)
  |  This triggers the trap in common.sh/common.py
  |  Script performs cleanup, then exits
  |
  v
Process exits (caught by monitor from Flow 2)
  |
  v
Update op_runs: status = STOPPED, finished_at = now
  |
  v
Dashboard button reverts to idle state
Running badge removed from nav
```

**Reads:** `op_runs` table
**Writes:** `op_runs` table (status update)
**Event emitted:** `operation_completed` (with STOPPED status)

---

## 4. Git Push

**Trigger:** User clicks Push button (visible only when `git_unpushed > 0`).

```
User clicks Push on project row
  |
  v
POST /api/push/{project_id}
  |
  v
Load project record --> get path
  |
  v
Execute: git -C {path} push
  |
  +---> Success:
  |       Update project: git_unpushed = 0
  |       Flash success message
  |       Push button disappears
  |
  +---> Failure:
          Flash error with git output
          Button remains visible
```

**Reads:** `projects` table, git remote config
**Writes:** Remote repository, `projects` table
**Event emitted:** `git_push` (success or failure)

---

## 5. Portfolio Publish

**Trigger:** User clicks Rebuild or Publish on the Publisher screen.

```
BUILD:
  User clicks Rebuild
    |
    v
  POST /publisher/build
    |
    v
  Query projects WHERE show_on_homepage = true
    |
    v
  For each published project:
    |
    +---> Resolve card fields (with defaults):
    |       card_title    --> fallback to display_name
    |       card_desc     --> fallback to short_description
    |       card_image    --> fallback to logo
    |       card_tags     --> fallback to tags
    |       card_type     --> fallback to project_type
    |       card_url      --> fallback to deploy_url or git_repo
    |
    +---> Check for doc/index.html --> add Documentation link if exists
    |
    +---> Generate card HTML fragment
    |
    v
  Load config/site_config.md
    |  YAML frontmatter --> site title, branding
    |  Markdown body --> home page content
    |
    v
  Assemble static site: card grid + home page + resume page
    |
    v
  Write output files
  Flash "Build complete" with timestamp

PUBLISH:
  User clicks Publish
    |
    v
  POST /publisher/publish
    |
    v
  Execute PushAndPublish.sh
    |  git add, commit, push to GitHub Pages branch
    |
    v
  Flash publish status
```

**Reads:** `projects` table (card fields), `config/site_config.md`, `doc/` directories, `static/images/`
**Writes:** Static site output files, GitHub Pages branch
**Events emitted:** `build_completed`, `deploy_completed`

---

## 6. Heartbeat Poll [ROADMAP]

**Trigger:** Timer-based (configurable interval, e.g., every 60 seconds). Also on-demand from Monitoring screen.

```
Timer fires (or user clicks Refresh on Monitoring)
  |
  v
Query projects WHERE port IS NOT NULL AND health_endpoint IS NOT NULL
  |
  v
For each monitored project:
  |
  +---> HTTP GET http://localhost:{port}{health_endpoint}
  |       |
  |       +---> 200 OK (within timeout):
  |       |       state = UP
  |       |       response_ms = elapsed
  |       |
  |       +---> Connection refused / timeout / error:
  |               state = DOWN
  |               response_ms = null
  |
  +---> Compare new state vs previous state
  |       |
  |       +---> Same state: update last_checked, response_ms
  |       |
  |       +---> State changed:
  |               Record state_transition event
  |               Update heartbeat record
  |               If DOWN: fire alert (unless SNOOZED)
  |               If UP (after DOWN): fire recovery alert
  |
  +---> Update rolling uptime_pct (24h window)
  |
  v
Monitoring screen updates health table
Dashboard running indicators reflect combined state
```

**Reads:** `projects` table, HTTP endpoints
**Writes:** `heartbeats` table, `events` table
**Events emitted:** `state_transition` (on change), `alert_fired` (on DOWN)

**States:** `UNKNOWN --> UP --> DOWN --> UP` (cycle). `SNOOZED` suppresses alerts but continues polling.

---

## 7. Schedule Fire [ROADMAP]

**Trigger:** Cron expression match (checked every minute by scheduler loop).

```
Scheduler tick (every 60 seconds)
  |
  v
Query operations WHERE schedule IS NOT NULL AND schedule_enabled = true
  |
  v
For each scheduled operation:
  |
  +---> Evaluate cron expression against current time
  |       |
  |       +---> No match: skip
  |       |
  |       +---> Match:
  |               |
  |               +---> Check last_scheduled_run
  |               |       Already ran this minute? Skip (dedup)
  |               |
  |               +---> Execute Run Operation flow (Flow 2)
  |               |
  |               +---> Update last_scheduled_run = now
  |               +---> Calculate next_scheduled_run
  |
  v
(silent — no UI update unless user is watching Processes screen)

STARTUP CATCH-UP:
  On platform start:
    |
    v
  For each scheduled operation:
    |
    +---> Compare last_scheduled_run against cron expression
    |       |
    |       +---> Missed run(s) detected:
    |               Fire ONE immediate run (most recent missed, no backfill cascade)
    |               Record schedule_missed event
    |
    v
  Resume normal tick loop
```

**Reads:** `operations` table (schedule, last_scheduled_run)
**Writes:** `op_runs` table (via Flow 2), `operations` table (last/next scheduled run)
**Events emitted:** `schedule_fired`, `schedule_missed` (on catch-up)

---

## 8. Ticket Lifecycle [ROADMAP]

**Trigger:** User creates or moves a ticket on the Workflow screen.

```
CREATE:
  User clicks New Ticket (on Workflow or project detail)
    |
    v
  Enter title, description, tags, priority
    |
    v
  Insert into tickets: state = IDEA
    |
    v
  Card appears in IDEA column on Kanban board

TRANSITION:
  User drags ticket to new column (or clicks state button)
    |
    v
  Validate transition is allowed:
    IDEA --> PROPOSED (needs: summary and plan)
    PROPOSED --> READY (needs: acceptance criteria)
    READY --> IN DEVELOPMENT
    IN DEVELOPMENT --> TESTING (needs: work completed)
    TESTING --> DONE (needs: human validation)
    TESTING --> READY (rework)
    IN DEVELOPMENT --> PROPOSED (redesign)
    |
    v
  Update ticket state
  Record state change in ticket history
    |
    v
  If entering IN DEVELOPMENT:
    |  Begin collecting AI transaction log entries
    |  (decisions, files changed, rationale)
    |
  If entering DONE:
    |  Freeze transaction log
    |  Ticket archived after configurable period
    |
    v
  Kanban board updates, card moves to new column
```

**Reads:** `tickets` table, `workflow.json` (state definitions)
**Writes:** `tickets` table, ticket history, transaction log
**Events emitted:** `ticket_transition`

---

## 9. Configuration Edit

**Trigger:** User clicks cog icon on Configuration screen, or edits inline fields.

```
User opens field editor for a project
  |
  v
GET /config or project detail editor
  |  Load current values from DB
  |
  v
User edits field(s) and tabs out / saves
  |
  v
POST update
  |
  v
Update `projects` table in database
  |
  v
Write changes back to METADATA.md on disk
  |  Read current file
  |  Find matching key: line
  |  Replace value (or append if new key)
  |  Write file
  |
  v
Flash confirmation
```

**Reads:** `projects` table, METADATA.md file
**Writes:** `projects` table, METADATA.md file (bidirectional sync)
**Events emitted:** `metadata_changed`

**Key behavior:** Database and METADATA.md are kept in sync. DB is the working copy (fast reads for dashboard). METADATA.md is the source of truth (survives database rebuild via rescan).

---

## 10. Specification Management [ROADMAP]

**Trigger:** User edits spec content via the platform, or agent commits spec changes during ticket work.

```
VIEWING:
  User clicks Specs link on project with has_specs = true
    |
    v
  Load file list from Specifications/{project_name}/
    |
    v
  Display spec index with file names, last modified, sizes

EDITING (via platform):
  User opens a spec file for editing
    |
    v
  Load file content, render in editor
    |
    v
  User saves changes
    |
    v
  Write file to Specifications/{project_name}/
    |
    v
  Git commit in Specifications repo
    |  Message: "Update {filename} for {project_name}"
    |
    v
  Record transaction log entry:
    |  category = change
    |  files_affected = [{filename}]
    |  linked to ticket (if in context)

AI AGENT FLOW (during ticket IN DEVELOPMENT):
  Agent modifies spec file as part of ticket work
    |
    v
  Agent commits with descriptive message
    |
    v
  On next scan: transaction log entry auto-created
    |  Linked to active ticket for this project
    |  Files detected via git diff
```

**Reads:** Specifications/{name}/ directory, git log
**Writes:** Spec files, Specifications repo commits, transaction log
**Events emitted:** `spec_updated`

---

## Flow Summary

| # | Flow | Trigger | Implemented |
|---|------|---------|-------------|
| 1 | Project Scan | Startup / Rescan button | Yes |
| 2 | Run Operation | Operation button click | Yes |
| 3 | Stop Operation | Stop button click | Yes |
| 4 | Git Push | Push button click | Yes |
| 5 | Portfolio Publish | Rebuild / Publish buttons | Yes |
| 6 | Heartbeat Poll | Timer / Monitoring refresh | ROADMAP |
| 7 | Schedule Fire | Cron tick / startup catch-up | ROADMAP |
| 8 | Ticket Lifecycle | Create / drag ticket | Partial |
| 9 | Configuration Edit | Cog icon / inline edit | Yes |
| 10 | Specification Management | Spec link / agent commit | ROADMAP |

---

## Cross-Cutting Concerns

### Event Emission

Every flow emits events (see FEATURE_MAP Section IV). Events are written to the `events` table and surfaced on:
- Monitoring screen (platform-wide timeline)
- Project detail (per-project event log)

### Error Handling

All flows follow the same pattern:
- Catch exceptions at the route level
- Flash error message to user
- Log to platform log (not project log)
- Never crash the platform — a single project failure must not affect others

### HTMX Partial Updates

Flows that change UI state return HTML fragments, not full pages:
- Run/Stop --> updated button state fragment
- Push --> updated git status fragment
- Scan --> status message fragment
- Config edit --> updated row fragment

The browser replaces the targeted DOM element. No full page reload unless navigating to a different screen.

### Concurrency

- Only one instance of a given operation can run per project at a time
- Multiple different operations can run simultaneously across projects
- Scanner runs async — dashboard is usable during scan
- Heartbeat poller runs on its own timer, independent of user actions
- Scheduler runs on its own timer, independent of heartbeat poller
