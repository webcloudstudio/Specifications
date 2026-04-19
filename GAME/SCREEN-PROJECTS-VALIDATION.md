# Screen: Validation

| Field | Value |
|-------|-------|
| Version | 20260325 V1 |
| Route | `GET /project-validation` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Projects |
| Sub Menu | Validation |
| Tab Order | 1: Dashboard · 2: Configuration · 3: Validation · 4: Maintenance · 5: Setup |
| Description | Run and review project compliance checks across all registered projects. Renders SCREEN-DEFAULT with `columns=Validation`. Two validation categories: Repo/Project Quality and Workflow Conformity. |
| Depends On  | UI-GENERAL.md |

## Validation Column

Each project row shows a compact summary of its validation state plus a `Validate` button.

| Element | Content |
|---------|---------|
| Compliance level badge | Highest level fully satisfied: IDEA / PROTOTYPE / ACTIVE / PRODUCTION |
| Quality score | Fraction of quality checks passing (e.g. `5/7`) |
| Conformity score | Fraction of conformity checks passing (e.g. `3/4`) |
| Issues indicator | Count of failing checks; amber if > 0, green if 0 |
| `Validate` button | Runs all checks for this project; refreshes the row |

### Result Expansion

Clicking the issues indicator (or the project row) expands an inline detail panel below the row showing two check groups:

**Repo/Project Quality**

| Check | Description | Pass Indicator |
|-------|-------------|----------------|
| `has_git` | `.git/` directory present | ✓ / ✗ |
| `has_venv` | `venv/` or `.venv/` present | ✓ / ✗ |
| `has_claude` | `CLAUDE.md` present | ✓ / ✗ |
| `has_docs` | `doc[s]/index.html` present | ✓ / ✗ |
| `has_tests` | `tests/` or `bin/test.sh` present | ✓ / ✗ |
| `has_specs` | Matching entry in Specifications repo | ✓ / ✗ |
| `version_format` | `projects.version` matches `YYYY-MM-DD.N` | ✓ / ✗ |

**Workflow Conformity** (mirrors `bin/project_manager.py` compliance levels)

| Level | Checks |
|-------|--------|
| IDEA | `METADATA.md` present; required fields: `display_name`, `status`, `short_description` |
| PROTOTYPE | `AGENTS.md` present with `CLAUDE_RULES_START` marker; `common.sh` and `common.py` in `bin/` |
| ACTIVE | `git_repo` set; `port` set; `health` endpoint set; `version` field present |
| PRODUCTION | `desired_state: running`; `has_docs = true`; `has_tests = true`; `namespace` != development |

Each level shows: ✓ (all checks pass) or ✗ N issues (N failing checks).

## Batch Controls

Action bar above the table (rendered in the project sub-bar area):

| Control | Behavior |
|---------|----------|
| `Validate All` button | Runs checks for all visible projects sequentially; updates rows as results arrive |
| Progress indicator | Shown during batch run: `N of M projects checked` |
| `Show failing only` toggle | Filters to rows with at least one failing check |

## Validate Action

Clicking `Validate` on a row (or `Validate All`):

1. Calls `POST /api/validate/{project_id}`
2. Server runs all checks against the project's filesystem and DB state
3. Updates `heartbeats` table: `heartbeat_type = 'compliance'`, `current_state` = highest passing level, detail in JSON
4. Returns updated row fragment (HTMX swap)

No external tools run — checks are purely filesystem and DB reads. Validation is fast (< 1 second per project).

## Metrics Summary Bar

Above the table: aggregate counts across all visible projects.

| Metric | Content |
|--------|---------|
| Compliant | Projects with 0 failing checks |
| Needs attention | Projects with 1–3 failing checks |
| Non-compliant | Projects with > 3 failing checks |
| Average conformity | Mean compliance level across all projects |

## Data Flow

| Reads | Writes |
|-------|--------|
| `projects` table (filesystem flags, metadata) | `heartbeats` table (compliance state) |
| Filesystem (presence checks for each project path) | `events` table (`compliance` event on state change) |
| SPECIFICATIONS_PATH (has_specs check) | |
| `operations` table (bin/ script headers for PROTOTYPE check) | |

## Open Questions

- Should validation results be persisted between sessions? Yes — results are stored in the `heartbeats` table (`heartbeat_type = 'compliance'`). The Validation screen shows the last stored result; clicking `Validate` refreshes it. Results survive restart.
- Should `Validate All` run automatically on a schedule? Yes — wire to the scheduler loop via a `validation_schedule` key in the `settings` table (e.g., `0 2 * * *` for 2am nightly). Add to SCREEN-SETTINGS-GENERAL.md fields when implemented.
- Should failing PRODUCTION checks surface as alerts on the Monitoring screen? Yes — compliance state changes (from the `heartbeats` table) should appear in the Monitoring event timeline as `compliance` event type. Existing event pipeline handles this; no new mechanism needed.
