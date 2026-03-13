# Monitoring & Health Checks [ROADMAP]

**Service health polling and alerting.** Polls running services, alerts on failure, tracks uptime.

---

## Capabilities

- Health polling via declared Port and health endpoint
- Liveness check: is the service responding?
- Readiness check: is it ready for traffic?
- States: UNKNOWN → UP → DOWN → SNOOZED
- In-UI alerts on state transitions
- Uptime history and incident log
- Silence alerts temporarily per project

## How It Works

Polls each service that declares a port in bin/ headers or METADATA.md. HTTP response to health endpoint = UP. Connection refused/timeout/error = DOWN.

## Screens

**Health Indicators (inline):** Per-project badge (UP/DOWN/UNKNOWN), last checked, response time.

**Monitoring Dashboard:** All monitored services table. Incident log below.

**Alerts:** Banner or toast on state change.

## Future

- Webhook/email/OS notifications
- Auto-restart on failure (integration with OPERATIONS-ENGINE)
