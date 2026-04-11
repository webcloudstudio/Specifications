# Screen: Prototypes Maintenance

| Field | Value |
|-------|-------|
| Version | 20260407 V1 |
| Route | `GET /prototypes/maintenance` |
| Parent | SCREEN-DEFAULT |
| Main Menu | Prototypes |
| Sub Menu | Maintenance |
| Tab Order | 1: List · 2: Configuration · 3: Validation · 4: Maintenance |
| Description | Maintenance operations for prototype specification directories. Runs Specifications bin/ scripts per prototype. Mirrors Projects / Maintenance. |

## Layout

Full-width list. One row per prototype. Maintenance operation buttons per row. Action bar at top.

## Prototype Row

| Element | Content |
|---------|---------|
| Status badge | `METADATA.md → status` — display only |
| Name | `METADATA.md → display_name` |
| Maintenance buttons | One button per applicable Specifications bin/ script (see Operations below) |

If a prototype has no applicable maintenance operations, the cell is empty.

## Maintenance Operations

Operations are sourced from `{SPECIFICATIONS_PATH}/bin/` scripts that have a `# Category: maintenance` header **and** accept a specification name argument (`# Args: Spec` or similar). Each such script appears as a button on every prototype row.

Standard Specifications maintenance scripts:

| Script | Name | Description |
|--------|------|-------------|
| `scorecard.sh` | Scorecard | Generate SCORECARD.md — project health dashboard |
| `spec_iterate.sh` | Spec Iterate | AI-powered specification gap analysis and quality scoring |
| `update_reference_gaps.sh` | Reference Gaps | Update REFERENCE_GAPS.md from specification vs prototype comparison |
| `tran_logger.sh` | Tran Logger | Extract bugs and ideas from AI session transaction logs |

Scripts not tagged `# Category: maintenance` are not shown here.

## Operation Button Behavior

Uses the standard operation button pattern from UI-GENERAL:

| State | Appearance |
|-------|------------|
| Idle | Button with script `# Name:` label |
| Running | Green pulsing indicator, "Running…" label |
| Done | Brief success flash, reverts to idle |
| Error | Red flash; click to view output |

Clicking a button:

1. `POST /api/prototypes/run/{name}/{script_name}`
2. Server runs `bash {SPECIFICATIONS_PATH}/bin/{script_name} {name}` as subprocess
3. Returns run ID; button polls `GET /api/runs/{run_id}` for status
4. Output viewable in a log drawer (same pattern as Projects / Maintenance)

## Action Bar

| Control | Behavior |
|---------|----------|
| Text filter | Client-side filter by prototype name |
| Status pills | Show/hide rows by status; default shows all |

## Data Flow

| Reads | Writes |
|-------|--------|
| `SPECIFICATIONS_PATH` directory scan | Files written by each script (SCORECARD.md, REFERENCE_GAPS.md, etc.) |
| `METADATA.md` per prototype | `op_runs` table (run record) |
| `bin/` script headers (Category, Name, Args) | `events` table (`prototype_maintenance_run`) |

## Open Questions

- Should output from maintenance scripts (SCORECARD.md, SPEC_SCORECARD.md) be linkable directly from this screen?
- Should `Run All` batch buttons appear per script (e.g., "Scorecard All") to run the script across all prototypes at once?
