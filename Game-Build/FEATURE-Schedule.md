# Feature: Scheduled Operations [ROADMAP]

Cron-based automated execution of bin/ scripts.

## Trigger

Scheduler loop checks every 60 seconds. Also catch-up on startup.

## Sequence

1. Query operations WHERE schedule IS NOT NULL AND schedule_enabled=true
2. Evaluate cron expression against current time
3. If match and not already run this minute: execute Run flow (FEATURE-Operations)
4. Update last_scheduled_run, calculate next_scheduled_run

## Startup Catch-Up

On platform start:
1. For each scheduled operation: compare last_scheduled_run against cron expression
2. If missed run detected: fire ONE immediate run (most recent only, no backfill cascade)
3. Record schedule_missed event

## Declaration

Scripts declare schedules via `# Schedule:` header:

```bash
#!/bin/bash
# CommandCenter Operation
# Category: maintenance
# Schedule: 0 2 * * *
```

## Open Questions

- UI to enable/disable schedules without editing script headers?
- Dashboard indicator for next scheduled run?
- Max missed runs to catch up (currently: 1)?
