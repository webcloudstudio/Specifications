# Screen: Monitoring [ROADMAP]

**Service health dashboard.** Polls running services, shows status, alerts on failure.

---

## Layout

Health table with all monitored services. Incident log below.

## Health Table

| Column | Description |
|--------|-------------|
| Project name | From METADATA.md |
| Endpoint | `port` + `health` from METADATA.md |
| Status badge | UP (green) / DOWN (red) / UNKNOWN (gray) |
| Last checked | Timestamp (yyyymmdd_hhmmss) |
| Response time | Milliseconds |
| Uptime % | Rolling 24h |

## Incident Log

Timeline of state changes. Per row: timestamp, project, previous state → new state.

## Alerts

Banner or toast notification when a service changes state. Links to the project.

## How It Works

Polls each service that declares `port:` and `health:` in METADATA.md. HTTP GET to health endpoint. Response = UP. Connection refused / timeout / error = DOWN.

States: `UNKNOWN → UP → DOWN → UP` (alert on each transition). SNOOZED suppresses alerts but continues polling.

## Data Flow

| Reads | Writes |
|-------|--------|
| METADATA.md (port, health) | Health status → dashboard |
| Process engine (running state) | Alert events |
