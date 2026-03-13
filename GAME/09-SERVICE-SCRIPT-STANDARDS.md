# Service Script Standards

**The bin/ script contract.** How scripts register as platform operations.

---

## The Header

Any script in `bin/` with a `CommandCenter Operation` marker in the first 20 lines becomes a registered operation.

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
# Category: local
# Health: /health
# Schedule: daily 02:00
# MaxMemory: 512M
# Timeout: 300
```

**Required:** `CommandCenter Operation` marker + `Name:`
**Optional:** `Port`, `Category`, `Health`, `Schedule`, `MaxMemory`, `Timeout`

## Rules

1. Marker must appear within first 20 lines
2. `Name:` is required — scripts without it are ignored
3. Script runs from project root (not from `bin/`)
4. Scripts must be executable (`chmod +x`)
5. A project can have any number of registered operations
6. Bash and Python scripts supported

## Standard Names (recommended)

| Script | Purpose |
|--------|---------|
| `bin/start.sh` | Start services |
| `bin/stop.sh` | Stop services |
| `bin/build.sh` | Build / compile |
| `bin/test.sh` | Run tests |
| `bin/deploy.sh` | Deploy |

## Interfaces

- **PROJECT-DISCOVERY:** reads headers during scan
- **OPERATIONS-ENGINE:** uses registered path to execute
- **CONTROL-PANEL:** renders operation buttons
- **MONITORING-HEARTBEATS:** uses declared port for health checks
