# Operations Engine

Two modules handle process execution: `ops.py` for project operations (servers, one-shot commands) and `spawn.py` for generic process spawning (used by the publish pipeline).

## ops.py — Project Operation Execution

### Command Classification

Commands are classified as **server** (long-running) or **one-shot** based on keyword matching:

```python
SERVER_KEYWORDS = ['runserver', 'flask run', 'npm run dev', 'npm start', 'serve']
```

`is_server_command(cmd)` → True if any keyword appears in the command string.

### Server Operations (`_run_server`)

1. Check for existing running op_run for this op_id; if PID alive, return error
2. Pre-insert `op_runs` record with `status='starting'`, `pid=0` to get a `run_id`
3. Write startup header to `data/logs/{run_id}.log`
4. Spawn process:
   - Shell: `/bin/bash` (required for `source` builtin)
   - Venv activation: `source {venv}/bin/activate && {cmd}` if `needs_venv=1`
   - Output: `({cmd}) >> {log_path} 2>&1`
   - Session: `start_new_session=True` (enables `os.killpg`)
   - Env: `PYTHONUNBUFFERED=1`
5. Update op_run with actual PID, status='running'
6. Spawn daemon monitor thread: `proc.wait()` then mark status='done' and append exit code to log
7. Return `{pid: int}` to caller

### One-Shot Operations (`_run_oneshot`)

1. Execute `subprocess.run()` with 30-second timeout
2. Capture stdout+stderr
3. Return `{output: str}` on success or `{error: str}` on failure

### Stop Operation (`stop_operation`)

1. Query all running op_runs for the given op_id
2. Kill process group: `os.killpg(os.getpgid(pid), SIGTERM)`
3. Mark status='done' in DB

### Dead Process Cleanup (`cleanup_dead_processes`)

Called on every page load via context processor. Checks all running op_runs, marks any with dead PIDs as 'done'. Uses `os.kill(pid, 0)` to test process existence.

## spawn.py — Generic Process Spawning Service

Used by the publish pipeline (rebuild, preview, push) and the Processes page.

### `spawn_process(cmd, cwd, name, daemon=False, project_id=None)`

1. Validate `cwd` exists
2. Insert `op_runs` record (`op_id=NULL`, stores `cmd` and `name`)
3. Create timestamped log file: `data/logs/{name}_{run_id}_{timestamp}.log`
4. Write header: name, start time, working dir, command, type (daemon/batch)
5. Spawn process same as ops.py (bash shell, new session, unbuffered)
6. For batch (non-daemon): spawn monitor thread that calls `proc.wait()`, writes exit status, marks 'done'
7. For daemon: no monitor — runs until manually stopped
8. Return `{run_id, pid, log_path}` or `{error: str}`

### `stop_process(run_id)`

1. Look up process record by run_id
2. Kill process group via SIGTERM
3. Mark status='done'
4. Append termination message to log file

### `get_log_content(run_id)`

Searches `data/logs/` for a file matching `*_{run_id}_*.log` and returns its contents.

### `list_running_processes()` / `list_recent_processes(limit=20)`

Query op_runs, enrich each row with computed `elapsed` time string and `log_path`.

### Elapsed Time Computation

Parses `started_at` ISO timestamp, computes delta from now:
- `< 60s` → `"Ns"`
- `< 3600s` → `"Nm Ns"`
- `>= 3600s` → `"Nh Nm"`

## Log Files

All logs stored in `data/logs/`:

| Source   | Filename Pattern                     | Created By      |
|----------|--------------------------------------|-----------------|
| ops.py   | `{run_id}.log`                       | _run_server()   |
| spawn.py | `{name}_{run_id}_{YYYYMMDD_HHMMSS}.log` | spawn_process() |

Log format:
```
=== {name} ===
Started: 2024-01-15 10:30:00
Working dir: /path/to/project
Command: flask run --port 5001
Type: daemon

--- Output ---
[process stdout/stderr follows]

--- Process exited with code 0 ---
Ended: 2024-01-15 10:35:00
```
