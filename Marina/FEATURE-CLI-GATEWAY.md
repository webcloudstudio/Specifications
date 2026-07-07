# Feature: CLI Gateway

| Field       | Value |
|-------------|-------|
| Version     | 20260707 V1 |
| Description | Local command-line wrapper for Marina project, workflow, run, health, and catalog operations. |
| Depends On  | FEATURE-BATCH-RUNNER.md, FEATURE-SERVICE-CATALOG.md, FEATURE-WORKFLOW-SERVICE.md |
| Provides    | `bin/marina-cli.sh` |

**Description:** Provides a shell entrypoint for scripts and operators to call Marina local APIs without
hand-writing curl commands.

## Trigger

- User or project script calls `bin/marina-cli.sh`.

## Commands

| Command | Result |
|---------|--------|
| `catalog` | Print service catalog JSON |
| `projects scan` | Trigger project scan |
| `run <project> <operation>` | Start operation and wait for result |
| `run <project> <operation> --no-wait` | Start operation and print run id |
| `status <run_id>` | Print run state |
| `workflow list` | Print workflow tickets |
| `health poll` | Trigger health poll |

## Reads

- Marina local URL from environment or configured port.

## Writes

- Whatever the invoked API writes.

## Open Questions
- None.
