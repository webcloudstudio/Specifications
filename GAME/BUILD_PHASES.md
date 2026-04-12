# Build Phases — GAME

This file is consumed by `bin/oneshot_phased.sh`. Each `## Phase N: Name` block
defines one phase. Recognized fields:

- `specs:` — comma-separated glob patterns of spec files to include in the phase
  prompt as load-bearing, authoritative content (placed at the bottom of the
  prompt for recency).
- `context:` — comma-separated additional context files (e.g. UI-GENERAL.md,
  FUNCTIONALITY.md). The driver always includes METADATA.md and ARCHITECTURE.md
  by default; use `context:` to add more without making them load-bearing.
- `copy:` — bullet list of `src -> dst` pairs. `src` is relative to the
  Prototyper repo root; `dst` is relative to the target project. Files are
  copied verbatim before the LLM runs (saves tokens, locks conventions).
- `instructions:` — `|` block, free-form prose injected into the phase prompt.
- `smoke:` — bullet list of bash commands run after the phase. `${PORT}` is
  substituted with the project port. The driver restarts the app between
  phases, so smoke tests can curl localhost.

Phases run in file order. A phase with no `specs:` is verify-only (no LLM call).

---

## Phase 1: Scaffold
specs: DATABASE.md
context: UI-GENERAL.md
copy:
  - RulesEngine/templates/common.sh -> bin/common.sh
  - RulesEngine/templates/common.py -> bin/common.py
  - RulesEngine/gitignore           -> .gitignore
  - RulesEngine/templates/index.html -> index.html
instructions: |
  Build the foundation only — no screens, no features yet.

  Files to create:
    - app/__init__.py with create_app() factory
    - app/db.py with sqlite WAL setup, schema init from DATABASE.md (every table),
      additive migrations via _add_column_if_missing helper
    - app/config.py for env-loaded config (PORT, PROJECTS_DIR, SPECIFICATIONS_PATH)
    - run.py at the project root that calls create_app() and app.run()
    - bin/start.sh and bin/stop.sh following stack/common.md EXACTLY:
        * start.sh runs run.py in the FOREGROUND under tee — NO nohup, NO &
        * logs go to logs/${PROJECT}_${SCRIPT}_${YYYYMMDD_HHMMSS}.log
        * NEVER write to dotfiles like .game.log or .app.log
        * stop.sh terminates by port (lsof -ti :${PORT} | xargs kill) — no orphans
    - app/templates/base.html and app/templates/_nav_top.html with the
      two-line header and bi-* icons specified in UI-GENERAL.md
    - app/static/js/app.js (empty file is fine — must EXIST so other phases don't 404)
    - logs/ directory (mkdir; the start script will populate it)

  Build empty blueprint stubs for every screen group so later phases can
  attach routes without restructuring: app/views/welcome.py, projects.py,
  prototypes.py, monitoring.py, catalog.py, publisher.py, workflow.py,
  settings.py, voice.py, help.py. Each registers its blueprint and returns
  a placeholder index route.

  Do NOT create screen templates yet beyond base.html + _nav_top.html.
  Do NOT implement any business logic yet — just the scaffolding.
smoke:
  - test -f bin/start.sh
  - test -f bin/stop.sh
  - test -f app/static/js/app.js
  - test -f run.py
  - "! grep -q nohup bin/start.sh"
  - "! grep -qE '\.(game|app)\.log' bin/start.sh bin/common.sh app/__init__.py 2>/dev/null"
  - curl -sf -o /dev/null -w '%{http_code}' http://localhost:${PORT}/ | grep -qE '^(200|302|404)$'

## Phase 2: Welcome + Projects
specs: SCREEN-WELCOME-*.md, SCREEN-PROJECTS-*.md, FEATURE-SERVICE-CATALOG.md
context: UI-GENERAL.md
instructions: |
  Build the welcome screens and the entire Projects screen group + the
  scanner that produces the data they display.

  Critical correctness items from prior build failures:
    - SCREEN-WELCOME-SUMMARY.md defines a "START HERE" card with SIX specific
      rows (Application Name, Projects Dir, Specifications Path, Startup Scan,
      Homepage URL, GitHub SSH). Build EXACTLY those rows. Do NOT invent
      generic dashboard tiles, "Recent Activity", or "Operations" stats.
    - The startup scan runs as a background thread STARTED INSIDE create_app(),
      not wired to @app.before_request. The welcome page surfaces the count
      via a DB query that handles the empty-during-scan case gracefully
      (e.g. "Scanning..." until the scan completes).
    - Projects Dashboard, Detail, Configuration, Validation, Maintenance, and
      Setup are all real screens with the layouts specified in their files.
    - FEATURE-SERVICE-CATALOG defines how operations are discovered from each
      project's bin/ headers. Wire it into the scanner.
smoke:
  - curl -sf http://localhost:${PORT}/ -o /dev/null
  - curl -sf http://localhost:${PORT}/welcome/summary -o /dev/null
  - curl -sf http://localhost:${PORT}/welcome/projects -o /dev/null
  - curl -sf http://localhost:${PORT}/projects -o /dev/null

## Phase 3: Prototypes
specs: SCREEN-PROTOTYPES-*.md
context: UI-GENERAL.md
instructions: |
  Build the four Prototypes screens (List, Configuration, Validation,
  Maintenance). They read from SPECIFICATIONS_PATH, not the database.
  Reuse the projects blueprint patterns from Phase 2.
smoke:
  - curl -sf http://localhost:${PORT}/prototypes -o /dev/null

## Phase 4: Monitoring + Health
specs: SCREEN-MONITORING-*.md, FEATURE-HEALTHCHECK.md
context: UI-GENERAL.md
instructions: |
  Build Monitoring (overview), Scheduler, and Processes screens, plus the
  health-check poller. The poller runs as TWO background threads started
  inside create_app() (NOT before_request, NOT lazy). Tables: heartbeats,
  health_check_log, log_positions, log_filter — they should already exist
  from Phase 1's DATABASE.md scaffold.
smoke:
  - curl -sf http://localhost:${PORT}/monitoring -o /dev/null

## Phase 5: Catalog
specs: SCREEN-CATALOG.md, FEATURE-ServiceInterfaces.md, FEATURE-CLI-GATEWAY.md, FEATURE-MCP-Hosting.md
context: UI-GENERAL.md
instructions: |
  Build the Service Catalog screen and supporting features. The catalog
  consumes the operations and services tables populated by the scanner from
  Phase 2 and the service-interface discovery from FEATURE-ServiceInterfaces.
smoke:
  - curl -sf http://localhost:${PORT}/api/catalog -o /dev/null

## Phase 6: Workflow
specs: SCREEN-WORKFLOW-*.md, FEATURE-Workflow-Service.md
context: UI-GENERAL.md
instructions: |
  Build the three Workflow screens (Kanban, Add Ticket, Manage) and the
  workflow service. Tables: spec_tickets, workflow_types, workflow_templates,
  workflow_instances, workflow_history.
smoke:
  - curl -sf http://localhost:${PORT}/workflow -o /dev/null

## Phase 7: Publisher
specs: SCREEN-PUBLISHER.md, HOMEPAGE.md, FEATURE-HOMEPAGE-PUBLISHER.md
context: UI-GENERAL.md
instructions: |
  Build the Publisher screen and the homepage publisher feature. The
  publisher is a Jinja2-based static site builder — no npm, no JS build.
  Output goes to $PUBLISHER_TARGET (env var).
smoke:
  - curl -sf http://localhost:${PORT}/publisher -o /dev/null

## Phase 8: Settings + Help + Default
specs: SCREEN-SETTINGS-*.md, SCREEN-HELP.md, SCREEN-DEFAULT.md, SCREEN-VOICEFORWARD-MOBILE.md, FEATURE-VOICEFORWARD.md, FEATURE-AsyncQueue.md, FEATURE-BatchRunner.md
context: UI-GENERAL.md
instructions: |
  Build the remaining leaf screens: Settings (General, Tags, Help, Voice,
  Voice-Docs), the Help shell, the Default landing/redirect, and the
  VoiceForward mobile recorder. Plus the supporting features.

  SCREEN-HELP specifies a docs/index.html iframe when the file exists, with
  a centered muted "Documentation not built" fallback. Build EXACTLY that —
  do NOT hardcode 4 generic help cards.
smoke:
  - curl -sf http://localhost:${PORT}/settings/general -o /dev/null
  - curl -sf http://localhost:${PORT}/help -o /dev/null

## Phase 9: Verify
instructions: |
  Verify-only phase — no LLM call. Asserts that all the anti-patterns from
  prior failed builds are absent and that key files exist.
smoke:
  - "! grep -rn nohup bin/"
  - "! grep -rnE '\.(game|app)\.log' bin/ app/ run.py 2>/dev/null"
  - test -f app/static/js/app.js
  - test -f bin/start.sh
  - test -f bin/stop.sh
  - find logs -maxdepth 1 -name "${PROJECT}_*.log" | head -1 | grep -q .
