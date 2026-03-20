# Feature: Heartbeat Monitoring [ROADMAP]

Periodic health polling for projects with a port and health endpoint.

## Trigger

Timer-based (default 60s interval). Also on-demand from Monitoring screen.

## Sequence

1. Query projects WHERE port IS NOT NULL AND health_endpoint IS NOT NULL
2. For each: HTTP GET http://localhost:{port}{health_endpoint}
3. 200 OK within timeout → state=UP, record response_ms
4. Connection refused / timeout / error → state=DOWN
5. Compare new state vs previous → if changed, record state_transition event
6. Update rolling 24h uptime percentage

## States

```
UNKNOWN → UP → DOWN → UP (cycle)
SNOOZED = suppresses alerts, continues polling
```

## Open Questions

- Alert mechanism (flash on dashboard? email? webhook?)
- Snooze duration and UI
- Store heartbeat history or just current state + rolling average?
