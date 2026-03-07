# Process Monitor and Operations Management

The Processes tab provides centralized visibility into all background processes spawned by Command Center — servers, builds, deploys, ETL jobs, backups, and any other commands run through the operations engine, spawn service, or bin/ scripts.

> **Technology Reference**: See `stack/common.md` § Shell Scripts for the bin/ script standard (headers, logging, tee pattern).

## Design Principles

1. **Everything runs through one system** — bin/ scripts, Python operations, manual commands, and scheduled jobs all produce process records and log files
2. **Unified visibility** — one Processes page shows all running and completed work
3. **Log everything** — stdout and stderr captured to `data/logs/` via tee or pipe
4. **Operation categories** — processes are categorized for filtering and display

## Process Categories

| Category | Examples | Type | Source |
|----------|----------|------|--------|
| **Service** | Dev server start/stop | daemon | bin/start.sh, ops.py |
| **Build** | Compile, bundle, rebuild | batch | bin/build.sh, spawn.py |
| **Test** | Unit tests, lint | batch | bin/test.sh |
| **Deploy** | Push to production, publish | batch | bin/deploy.sh, spawn.py |
| **Database** | Migrations, backup, restore | batch | bin/migrate.sh, bin/backup.sh |
| **ETL/ELT** | Data extract, transform, load | batch | bin/etl_*.sh, Python scripts |
| **Operations** | Reorg, cleanup, maintenance | batch | bin/ops_*.sh |
| **Git** | Push, pull, status | batch | ops.py |
| **Scheduled** | Cron-triggered jobs | batch | Any of the above, triggered on schedule |

## Architecture

### Data Flow

```
User clicks operation button (Projects page)
  → ops.run_operation() or spawn.spawn_process()
    → subprocess.Popen (new session, output to log file)
    → Insert/update op_runs table
    → Monitor thread watches for exit

Scheduled job triggers (future)
  → spawn.spawn_process() with schedule metadata
    → Same subprocess pipeline

User visits Processes page
  → cleanup_dead_processes()
  → list_running_processes()
  → list_recent_processes()
  → Render processes.html with category filters
```

### Process Sources

All processes ultimately flow through two modules:

| Source | Module | Used By | op_id | Log Pattern |
|--------|--------|---------|-------|-------------|
| Project operations | `ops.py` | Start Server, Git Push, bin/ scripts | Set to operation ID | `{run_id}.log` |
| Spawn service | `spawn.py` | Rebuild, Preview, Push, any ad-hoc command | NULL | `{name}_{run_id}_{ts}.log` |

Both write to `data/logs/` and record in `op_runs` table.

### Running bin/ Scripts

When Command Center runs a bin/ script, the execution follows this path:

```
bin/start.sh clicked in UI
  → ops.run_operation() reads the operation record
  → subprocess.Popen(['bash', 'bin/start.sh'], ..., stdout=log_file, stderr=STDOUT)
  → Script's own tee logging writes to data/logs/ (via script preamble)
  → ops.py also captures output to its own log file
  → op_runs row tracks PID, status, timestamps
```

### Running Python Operations

Python scripts and modules can also be spawned as processes:

```python
# Spawning a Python operation
spawn_process(
    cmd='python -m etl.load_data --source api',
    cwd='/path/to/project',
    name='ETL Load',
    daemon=False,
    project_id=project_id
)
```

The spawn service handles Python operations identically to bash scripts — same log capture, same process tracking, same UI display.

### Process Lifecycle

```
starting  →  running  →  done
                     →  error (on startup failure)
```

- **starting**: Record created, PID not yet assigned
- **running**: Process spawned, PID recorded
- **done**: Process exited (normal or killed) OR dead PID detected
- **error**: Failed to spawn

### Dead Process Detection

Two cleanup functions run automatically:
- `ops.cleanup_dead_processes()` — called via context processor on every page load
- `spawn.cleanup_dead_processes()` — called when Processes page loads

Both use `os.kill(pid, 0)` to test if PID is alive, mark dead processes as 'done'.

## bin/ Script Integration

### Discovery

The scanner reads bin/ scripts with CommandCenter headers and creates operation records:

```bash
#!/bin/bash
# CommandCenter Operation
# Name: Database Backup
# Type: batch
# Port: (optional, for daemons)
```

Scripts without the `# CommandCenter Operation` header are still valid project scripts but won't appear in Command Center's UI.

### Standard Operations per Project Type

**All projects**:
| Script | Type | Purpose |
|--------|------|---------|
| `bin/start.sh` | daemon | Start the dev server |
| `bin/stop.sh` | batch | Stop the dev server |
| `bin/test.sh` | batch | Run test suite |
| `bin/backup.sh` | batch | Backup data/database |

**Django projects** (additional):
| Script | Type | Purpose |
|--------|------|---------|
| `bin/migrate.sh` | batch | makemigrations + migrate |
| `bin/shell.sh` | daemon | Django interactive shell |
| `bin/collectstatic.sh` | batch | Collect static files |

**Data projects** (additional):
| Script | Type | Purpose |
|--------|------|---------|
| `bin/etl_extract.sh` | batch | Extract data from source |
| `bin/etl_transform.sh` | batch | Transform/clean data |
| `bin/etl_load.sh` | batch | Load data to destination |
| `bin/reorg.sh` | batch | Database/file reorganization |

### Script Logging Standard

Every bin/ script follows the logging preamble from `stack/common.md`:

```bash
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')
SCRIPT_NAME=$(basename "$0" .sh)
LOG_FILE="$LOG_DIR/${SCRIPT_NAME}_${TIMESTAMP}.log"

echo "=== $SCRIPT_NAME started at $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Arguments: $*" | tee -a "$LOG_FILE"
echo "Working dir: $PROJECT_DIR" | tee -a "$LOG_FILE"
```

Log files are viewable from the Process Monitor via `/api/processes/log/{run_id}`.

## UI Components

### Running Processes Table
- Command (truncated to 60 chars)
- Category badge (Service, Build, Test, ETL, etc.)
- PID (green text)
- Started timestamp
- Elapsed time (computed: Ns / Nm Ns / Nh Nm)
- Stop button (with confirmation dialog)
- Log button (opens modal)

### Completed Processes Table
- Command (truncated)
- Category badge
- Status: Done (green) / Error (red)
- Completed timestamp
- Log button

### Category Filter
- Filter bar with toggleable category badges
- Click to show/hide process categories
- Persistent filter state via URL params or localStorage

### Log Viewer Modal
- Custom overlay (not Bootstrap modal)
- Fetches plain text from `/api/processes/log/{run_id}`
- Monospace green-on-dark display
- Close button and click-outside-to-close

### Auto-Refresh
- Checks `/api/processes/running` every 3 seconds
- Reloads page if running processes exist
- Stops polling when all processes complete

## Scheduled Operations (Future)

The Process Monitor framework supports scheduled execution:

```
schedule.json (per project or global):
{
  "jobs": [
    {
      "name": "Nightly Backup",
      "cmd": "bin/backup.sh",
      "schedule": "0 2 * * *",
      "category": "database"
    },
    {
      "name": "ETL Daily Load",
      "cmd": "bin/etl_load.sh --date yesterday",
      "schedule": "0 6 * * *",
      "category": "etl"
    }
  ]
}
```

Scheduled jobs would:
1. Be triggered by a scheduler (cron or internal timer)
2. Execute through `spawn_process()` like any other operation
3. Appear in the Processes page with a "scheduled" indicator
4. Log to `data/logs/` following the same pattern

## Enhancement Opportunities

1. **Unified view**: Show ops.py server processes alongside spawn.py processes in one table (currently spawn.py processes only)
2. **Live log streaming**: WebSocket or SSE-based log tailing instead of on-demand fetch
3. **Process output in real-time**: Show last N lines of output inline in the table row
4. **Category filters**: Filter by category (Service, Build, ETL, etc.)
5. **Log retention**: Auto-cleanup old log files (keep last N days)
6. **Process groups**: Group related processes (e.g., all processes for one project)
7. **Alerting**: Notify on process failure (email, webhook, or UI notification)
8. **Scheduling**: Built-in job scheduler for recurring operations
9. **ETL dashboard**: Summary view of data pipeline runs with success/failure rates
