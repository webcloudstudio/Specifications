# Feature: Operations

**Version:** 20260320 V1  
**Description:** Spec for the Operations feature

Run, stop, and monitor bin/ script execution.

## Run

**Trigger:** User clicks operation button.

1. Load operation record (script_path, cwd, needs_venv, category)
2. Create `op_runs` record: status=STARTING, log_path=`logs/{project}_{script}_{yyyymmdd_hhmmss}.log`
3. Fork subprocess: cd to project dir, activate venv if needed, execute script
4. Redirect stdout+stderr to log_path
5. Update op_runs: status=RUNNING, pid=process.pid
6. Dashboard button changes to running state

## Monitor (background)

- Parse log output for `[$PROJECT_NAME]` status lines
- On process exit: status=DONE (exit 0), ERROR (non-zero), STOPPED (SIGTERM)
- Update op_runs: finished_at, exit_code, status

## Stop

**Trigger:** User clicks Stop.

1. Load op_runs → get pid
2. Send SIGTERM to process group (`-pid`)
3. Script's common.sh trap handles cleanup
4. Process exits → monitor updates status to STOPPED

## Key Behaviors

- Process runs in a process group (clean SIGTERM of children)
- Log file is append-only, named for sorting
- common.sh/common.py handles venv, PORT, env, SIGTERM trap
- Platform does not understand what the script does — just runs it and watches exit codes
- One instance of a given operation per project at a time

## Open Questions

- Max concurrent operations across all projects?
- Log rotation / cleanup policy?
