# Feature: Service Script Standards (bin/ Contract)

**spec_v3 · 2026-03-10**

---

## Purpose

The Service Script Standards define the contract that project shell scripts must follow
to be automatically discovered and registered as operations in GAME. Any script that
follows the contract becomes a clickable button with zero additional configuration.

---

## User Interactions

- Project maintainers write bin/ scripts with standard headers
- GAME discovers and registers them automatically on scan (no UI needed)
- Registered operations appear as buttons in the CONTROL-PANEL
- Users can see operation name, category, and declared port in the UI

---

## UI Screens

No dedicated UI screen — this is a contract specification, not a UI feature.

Discovery results are surfaced through CONTROL-PANEL (buttons) and PROJECT-DISCOVERY
(compliance indicators).

---

## Inputs & Outputs

- **Inputs:**
  - Shell script files located in `bin/` within any project directory
- **Outputs:**
  - Operation registry entries (name, category, command path, declared port)
  - Consumed by OPERATIONS-ENGINE and CONTROL-PANEL

---

## Interfaces With

- PROJECT-DISCOVERY: reads bin/ headers during scan; produces operation registry
- OPERATIONS-ENGINE: uses registered command path to execute the operation
- CONTROL-PANEL: displays operation buttons derived from the registry
- MONITORING-HEARTBEATS: uses declared port for health checks

---

## Contracts

### The CommandCenter Operation Header

Any bash script in a project's `bin/` directory that includes a `CommandCenter Operation`
marker in the first 20 lines is registered as an operation.

**Required fields:**
```bash
#!/bin/bash
# CommandCenter Operation
# Name: [Human-readable operation name]
```

**Optional fields:**
```bash
# Port: [integer]        ← declared service port; used for health checks and display
# Category: [local|remote]  ← defaults to "local" if omitted
```

**Complete example:**
```bash
#!/bin/bash
# CommandCenter Operation
# Name: Service Start
# Port: 8000
# Category: local

source venv/bin/activate
./run_server.sh --port 8000
```

### Rules

1. The `CommandCenter Operation` marker must appear within the first 20 lines.
2. `Name:` is required. Scripts without a Name: are ignored.
3. All other fields are optional.
4. The script is run from the project's root directory (not from `bin/`).
5. Scripts without the marker are valid shell scripts but are not registered with GAME.
6. A project may have any number of registered operations.
7. The command path registered is relative to the project root (e.g., `bin/start.sh`).

### Naming Conventions (recommended, not enforced)

| Script name | Typical purpose |
|-------------|----------------|
| `bin/start.sh` | Start development server |
| `bin/stop.sh` | Stop development server |
| `bin/build.sh` | Run build pipeline |
| `bin/test.sh` | Run test suite |
| `bin/deploy.sh` | Deploy to production |

### Platform Notes

Scripts must be valid bash scripts (WSL/Linux bash). Windows `.bat` or PowerShell
scripts are not currently supported.

Scripts should be executable (`chmod +x`). GAME will attempt to run them directly;
permission errors are surfaced in the process log.

---

## State Machine

Not applicable — this is a static contract, not a stateful process.

---

## Out of Scope

- Executing scripts → OPERATIONS-ENGINE
- Displaying buttons → CONTROL-PANEL
- Health checking using declared ports → MONITORING-HEARTBEATS
- Non-bash script types → not planned
