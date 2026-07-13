# FEATURE: Parity Audit

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Compare common.sh and common.py behavior and document any gaps before migration begins. |
| Phase       | 1 |

## Trigger

Manual / one-time research step. Output is `data/common_parity_audit.md`.

## Comparison Matrix

For each behavior, verify: does common.py do the same thing as common.sh?

| Behavior | common.sh | common.py | Status |
|----------|-----------|-----------|--------|
| `SCRIPT_NAME` derivation | `basename "$0" .sh` | `os.path.splitext(os.path.basename(script_file))[0]` | Equivalent |
| `PROJECT_DIR` derivation | `dirname $SCRIPT_DIR` | `os.path.dirname(os.path.dirname(os.path.abspath(script_file)))` | Equivalent |
| `cd $PROJECT_DIR` | `cd "$PROJECT_DIR"` | `os.chdir(self.project_dir)` | Equivalent |
| `PROJECT_NAME` from METADATA | `grep "^name:" METADATA.md` | `self._get_metadata("name")` | Equivalent |
| `PORT` from METADATA | `grep "^port:" METADATA.md` | `self._get_metadata("port")` | Equivalent |
| `DISPLAY_NAME` from METADATA | `grep "^display_name:" METADATA.md` | `self._get_metadata("display_name")` | Equivalent |
| venv activation | `.venv/bin/activate` or `venv/bin/activate` | Not present — Python scripts run directly | **Gap** |
| Load `.secrets` (parent dir) | `source $PROJECTS_DIR/.secrets` | `self._load_env(os.path.join(projects_dir, ".secrets"))` | Equivalent |
| Load `.env` (project dir) | `source $PROJECT_DIR/.env` | `self._load_env(os.path.join(self.project_dir, ".env"))` | Equivalent |
| Log file creation | `logs/${SCRIPT_NAME}_$(date).log` | `logs/${project_name}_${script_name}_${ts}.log` | Near-equivalent (naming differs slightly) |
| `tee` stdout+file | `exec > >(tee -a "$LOG_FILE") 2>&1` | Python logging FileHandler + StreamHandler | Equivalent |
| Starting message | `[$PROJECT_NAME] Starting: $SCRIPT_NAME` | `[{project_name}] Starting: {script_name}` | Equivalent |
| Exit OK message | `[$PROJECT_NAME] EXIT - OK` | `[{project_name}] EXIT - OK` | Equivalent |
| Exit ERROR message | `[$PROJECT_NAME] EXIT - ERROR (code=$c)` | `[{project_name}] EXIT - ERROR: {msg}` | Near-equivalent (format differs) |
| SIGTERM trap | `trap 'exit 0' SIGTERM SIGINT` | `signal.signal(SIGTERM, ...)` | Equivalent |
| `heartbeat()` | `curl -sf POST /api/heartbeat` | `urllib.request.urlopen(POST /api/heartbeat)` | Equivalent |
| `log_event()` | `curl -sf POST /api/events` | `urllib.request.urlopen(POST /api/events)` | Equivalent |
| `log_info()` etc. helpers | `log_info()`, `log_warn()`, etc. | `ctx.logger.info()` etc. | Equivalent (different API) |
| `log_build_command` | In `lib_log.sh` (sourced by setup.sh) | Not present in common.py | **Gap (lib_log.sh specific)** |
| Log format `YYYY-MM-DD HH:MM:SS LEVEL [ProjectName] msg` | Via `log_info` helpers | File handler: `%(asctime)s %(levelname)s %(message)s` — missing `[ProjectName]` in non-started messages | **Gap** |

## Known Gaps to Resolve

1. **venv activation**: common.py does not activate a venv because Python scripts are invoked via `python3 bin/script.py` after venv is active in the shell. This is fine if the calling `.sh` script activates the venv first. Document this requirement.
2. **Log naming**: common.sh writes `${SCRIPT_NAME}_YYYYMMDD_HHMMSS.log`; common.py writes `${project_name}_${script_name}_YYYYMMDD_HHMMSS.log`. The extra prefix is fine but document as the standard.
3. **Log format for intermediate messages**: common.py's FileHandler does not include `[ProjectName]` in every log line. Fix: update the formatter to `%(asctime)s %(levelname)-8s [%(name)s] %(message)s` or update each log call to include it. The AGENTS.md contract says `[ProjectName]` should appear in all log lines.
4. **Exit code in exit message**: common.sh includes `(code=$c)` in the exit error message; common.py includes the exception message string. Both are useful — document that they can differ.

## Success Criteria

- Parity audit document is written and reviewed.
- All gaps either resolved (common.py updated) or explicitly accepted with rationale.
- The decision on gap resolution is approved before STEP.2 template update begins.

## Open Questions

- Should the log format fix (Gap 3) go into common.py now, or be deferred and tracked in the BUSINESS_RULES as a known deviation?
- Should common.py gain a `log_info()` / `log_warn()` wrapper API to match common.sh's named helpers for consistency?
