# Screen: Prototypes Validation

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /prototypes/validation` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Prototypes |
| Sub Menu | Validation |
| Tab Order | 1: List · 2: Configuration · 3: Validation · 4: Maintenance |

Run and review specification validation checks across all prototype directories. Mirrors Projects / Validation.

## Layout

Full-width list. One row per prototype. Validation state summary and Validate button per row. Action bar at top.

## Prototype Row

| Element | Content |
|---------|---------|
| Status badge | `METADATA.md → status` — display only |
| Name | `METADATA.md → display_name` |
| Validation summary | Conformity level badge + issue count (see below) |
| `Validate` button | Runs checks for this prototype; refreshes the row |

## Validation Summary (per row)

| Element | Content |
|---------|---------|
| Conformity level badge | Highest specification level fully satisfied: IDEA / PROTOTYPE / ACTIVE / PRODUCTION |
| Issues count | Count of failing checks; amber if > 0, green if 0 |

Clicking the row or the issues count expands an inline detail panel showing check results by category.

### Check Groups

**Required Files**

| Check | Pass condition |
|-------|----------------|
| `METADATA.md` present | File exists |
| `README.md` present | File exists |
| `INTENT.md` present | File exists |
| `ARCHITECTURE.md` present | File exists |
| `FUNCTIONALITY.md` present | File exists |
| Required METADATA fields | `name`, `display_name`, `status`, `short_description` all non-empty |
| No template placeholders | No `{{` / `}}` tokens remaining in any file |
| Open Questions sections | All specification files end with `## Open Questions` section |

**Specification Conformity** (mirrors `bin/validate.sh` exit codes and checks)

| Level | Checks |
|-------|--------|
| IDEA | `METADATA.md` present with required fields |
| PROTOTYPE | All required files present; no template placeholders |
| ACTIVE | `DATABASE.md` present if spec references a database; UI screens present if spec has a UI |
| PRODUCTION | No unresolved Open Questions; `ACCEPTANCE_CRITERIA.md` present |

## Action Bar

| Control | Behavior |
|---------|----------|
| `Validate All` button | Runs checks for all visible prototypes sequentially via `POST /api/prototypes/validate-all`; updates rows as results arrive |
| Progress indicator | `N of M prototypes checked` — shown during batch run |
| `Show failing only` toggle | Hides rows with 0 failing checks |
| Text filter | Client-side filter by name |

## Validate Action

Clicking `Validate` on a row:

1. `POST /api/prototypes/validate/{name}`
2. Server runs `bash {SPECIFICATIONS_PATH}/bin/validate.sh {name}` as subprocess
3. Parses stdout for check results and conformity level
4. Returns updated row fragment (HTMX swap)

Output from `validate.sh` is shown in the expanded detail panel (truncated to 50 lines; scrollable).

## Data Flow

| Reads | Writes |
|-------|--------|
| `SPECIFICATIONS_PATH` directory scan | `events` table (`prototype_validated`) |
| `METADATA.md` + all specification files per prototype | Validation result cache (in-memory or `heartbeats` table with `heartbeat_type = 'spec_compliance'`) |
| `bin/validate.sh` output (via subprocess) | |

## Open Questions

- Should validation results be persisted between sessions, or recomputed on every page load? Persist in `heartbeats` table with `heartbeat_type = 'spec_compliance'`, same pattern as project validation.
- Should `Validate All` run on a schedule (e.g., nightly)? Configurable via `settings` table, same as project validation.
