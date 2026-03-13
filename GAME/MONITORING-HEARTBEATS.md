# Feature: Monitoring & Heartbeats

**spec_v4 · 2026-03-11 · [ROADMAP]**

---

## Purpose

Polls running services and tells the user when something goes down. Closes the loop
between "I started the server" and "the server is actually healthy."

---

## What the User Can Do

- See health status (UP / DOWN / UNKNOWN) per service in the dashboard
- Get notified when a service goes down or comes back up
- View health history: uptime %, recent incidents
- Silence alerts temporarily for a project

---

## Screens

### Health Indicators (inline, Control Panel)

Per-project: health badge (UP green / DOWN red / UNKNOWN gray), last checked time,
response time.

### Monitoring Dashboard

Table of all monitored services: project, endpoint, status, last checked, response time,
uptime %. Incident log below.

### Alert Notification (in-UI)

Banner or toast when a service changes state. Links to the project and its log.

---

## How It Works

The platform polls each service that has declared a port in its bin/ header. A
successful HTTP response to the declared endpoint = UP. Connection refused, timeout,
or error response = DOWN.

Port and health path come from the Operations Contract (THE-CONTRACT.md §1).

---

## Alert Channels

Initial: in-UI notification only.
Future: webhook, email, OS notification. [TBD]

---

## States

```
UNKNOWN → UP → DOWN → UP  (with alert on each transition)
                    → SNOOZED (alerts suppressed; still polled)
```

---

## Out of Scope

- Automatic restart on failure → possible future integration with OPERATIONS-ENGINE
- External (cloud-hosted) service monitoring → not planned
- Performance benchmarking → out of scope
