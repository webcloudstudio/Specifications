# Screen: Monitoring [ROADMAP]

**Version:** 20260320 V1  
**Description:** Spec for the Monitoring screen

Health status and event timeline for all monitored projects.

## Route

```
GET /monitoring
```

## Layout

Two sections: health status table + event timeline.

## Health Table

Projects with `port` + `health_endpoint` set:

| Column | Content |
|--------|---------|
| Project | display_name |
| Status | UP / DOWN / UNKNOWN (colored indicator) |
| Response time | ms (last check) |
| Uptime | Rolling 24h percentage |
| Last checked | Timestamp |

## Event Timeline

Chronological list of platform events (most recent first):

| Column | Content |
|--------|---------|
| Timestamp | When |
| Project | Which project (or "Platform") |
| Event | Type + summary |

## Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Refresh health | Click Refresh | Polls all health endpoints now |
| Filter events | Select event type / project | Client-side filter |

## Open Questions

- Poll interval configurable? Default 60 seconds.
- Alert/snooze mechanism for DOWN transitions?
- How many events to show before pagination?
